"""
消息发送器

负责向飞书发送消息，支持不同的发送策略。
"""
import json
import logging
from typing import Optional
from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
    CreateImageRequest,
    CreateImageRequestBody,
    CreateFileRequest,
    CreateFileRequestBody
)
import os

logger = logging.getLogger(__name__)


class MessageSender:
    """消息发送器
    
    根据聊天类型选择合适的发送策略：
    - p2p（私聊）：发送新消息
    - group（群聊）：回复消息
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def __init__(self, client: LarkClient):
        """初始化消息发送器
        
        Args:
            client: 飞书客户端
        """
        self.client = client
    
    def _chunk_text(self, text: str) -> list[str]:
        """将文本分割成符合飞书消息长度限制的块
        
        Args:
            text: 原始文本
            
        Returns:
            分割后的文本块列表
        """
        max_length = 4000
        chunks: list[str] = []
        rest = text
        
        while rest:
            if len(rest) <= max_length:
                chunks.append(rest)
                break
            
            # 尝试在换行符处分割
            chunk = rest[:max_length]
            last_nl = chunk.rfind('\n')
            
            if last_nl > max_length * 0.8:
                # 如果换行符在文本的后20%，就在这里分割
                chunks.append(chunk[:last_nl + 1])
                rest = rest[last_nl + 1:].lstrip('\n ')
            else:
                # 否则在空格处分割
                last_space = chunk.rfind(' ')
                if last_space > max_length * 0.8:
                    chunks.append(chunk[:last_space + 1])
                    rest = rest[last_space + 1:].lstrip('\n ')
                else:
                    # 实在找不到合适的分割点，就在最大长度处分割
                    chunks.append(chunk)
                    rest = rest[max_length:].lstrip('\n ')
        
        return chunks
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片 key，如果上传失败返回 None
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # 直接使用文件上传方式
            import requests
            import json
            
            # 从环境变量加载配置
            def load_env():
                env_path = os.path.join(os.path.dirname(__file__), '../../..', '.env')
                config = {}
                if os.path.exists(env_path):
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                key, value = line.split('=', 1)
                                config[key.strip()] = value.strip()
                return config
            
            config = load_env()
            app_id = config.get('FEISHU_APP_ID')
            app_secret = config.get('FEISHU_APP_SECRET')
            
            if not app_id or not app_secret:
                logger.error("FEISHU_APP_ID or FEISHU_APP_SECRET not found in .env file")
                return None
            
            # 获取租户访问令牌
            token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
            payload = {
                "app_id": app_id,
                "app_secret": app_secret
            }
            
            token_response = requests.post(token_url, json=payload)
            token_data = token_response.json()
            
            if token_data.get("code") != 0:
                logger.error(f"Failed to get tenant access token: {token_data.get('msg')}")
                return None
            
            token = token_data.get("tenant_access_token")
            
            # 上传图片
            upload_url = "https://open.feishu.cn/open-apis/im/v1/images"
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            with open(image_path, 'rb') as f:
                files = {
                    'image': f
                }
                data = {
                    'image_type': 'message'
                }
                
                response = requests.post(upload_url, headers=headers, files=files, data=data)
            
            data = response.json()
            if data.get("code") != 0:
                logger.error(f"Failed to upload image: code={data.get('code')}, msg={data.get('msg')}")
                return None
            
            image_key = data.get("data", {}).get("image_key")
            if not image_key:
                logger.error("Failed to get image_key from response")
                return None
            
            logger.info(f"Successfully uploaded image: {image_key}")
            return image_key
        except Exception as e:
            logger.error(f"Error uploading image: {e}", exc_info=True)
            return None
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """上传文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件 key，如果上传失败返回 None
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # 打开文件以二进制模式读取
            with open(file_path, 'rb') as f:
                request = CreateFileRequest.builder()\
                    .request_body(
                        CreateFileRequestBody.builder()\
                            .file_type("stream")\
                            .file_name(file_name)\
                            .file(f)\
                            .build()
                    )\
                    .build()
                
                response = self.client.im.v1.file.create(request)
            
            if not response.success():
                logger.error(f"Failed to upload file: code={response.code}, msg={response.msg}")
                return None
            
            file_key = response.data.file_key
            logger.info(f"Successfully uploaded file: {file_key}")
            return file_key
        except Exception as e:
            logger.error(f"Error uploading file: {e}", exc_info=True)
            return None
    
    def send_message(
        self,
        chat_type: str,
        chat_id: str,
        message_id: str,
        content: str,
        msg_type: str = "post"
    ) -> bool:
        """发送消息
        
        根据聊天类型和参数选择发送策略：
        - p2p: 使用 send_new_message 发送到私聊
        - group + message_id: 使用 reply_message 回复消息
        - group + no message_id: 使用 send_new_message 发送到群聊
        
        Args:
            chat_type: 聊天类型（p2p, group 等）
            chat_id: 聊天 ID (用于发送新消息)
            message_id: 消息 ID (用于回复消息)
            content: 消息内容
            msg_type: 消息类型 ("text", "post", "image", "file")
            
        Returns:
            True 如果发送成功
        """
        try:
            # 验证消息类型
            valid_msg_types = ["text", "post", "image", "file"]
            if msg_type not in valid_msg_types:
                logger.error(f"Invalid msg_type: {msg_type}")
                return False
            
            # 详细日志
            logger.info(f"Sending message: type={msg_type}, chat_type={chat_type}, content_length={len(content) if content else 0}")
            
            # 对于图片和文件类型，需要先上传
            if msg_type in ["image", "file"]:
                if msg_type == "image":
                    media_key = self.upload_image(content)
                else:
                    media_key = self.upload_file(content)
                
                if not media_key:
                    return False
                
                # 直接发送，不需要分块
                if chat_type == "p2p":
                    return self.send_new_message(chat_id, media_key, msg_type=msg_type)
                elif chat_type == "group":
                    if message_id:
                        return self.reply_message(message_id, media_key, msg_type=msg_type)
                    else:
                        return self.send_new_message(chat_id, media_key, msg_type=msg_type)
                else:
                    return self.send_new_message(chat_id, media_key, msg_type=msg_type)
            else:
                # 文本类型消息
                # 检查消息长度并分块发送
                if content and len(content) > 4000:
                    logger.info(f"Message too long, splitting into chunks")
                    chunks = self._chunk_text(content)
                    logger.info(f"Split message into {len(chunks)} chunks")
                    
                    # 发送第一个块
                    first_chunk = chunks[0]
                    if chat_type == "p2p":
                        success = self.send_new_message(chat_id, first_chunk, msg_type=msg_type)
                    elif chat_type == "group":
                        if message_id:
                            success = self.reply_message(message_id, first_chunk, msg_type=msg_type)
                        else:
                            success = self.send_new_message(chat_id, first_chunk, msg_type=msg_type)
                    else:
                        success = self.send_new_message(chat_id, first_chunk, msg_type=msg_type)
                    
                    if not success:
                        return False
                    
                    # 发送剩余的块
                    for i, chunk in enumerate(chunks[1:], 1):
                        logger.info(f"Sending chunk {i+1}/{len(chunks)}")
                        if chat_type == "p2p":
                            success = self.send_new_message(chat_id, chunk, msg_type=msg_type)
                        elif chat_type == "group":
                            # 对于群聊，后续块作为新消息发送
                            success = self.send_new_message(chat_id, chunk, msg_type=msg_type)
                        else:
                            success = self.send_new_message(chat_id, chunk, msg_type=msg_type)
                        
                        if not success:
                            return False
                    
                    return True
                else:
                    # 消息长度正常，直接发送
                    if chat_type == "p2p":
                        return self.send_new_message(chat_id, content, msg_type=msg_type)
                    elif chat_type == "group":
                        if message_id:
                            return self.reply_message(message_id, content, msg_type=msg_type)
                        else:
                            return self.send_new_message(chat_id, content, msg_type=msg_type)
                    else:
                        return self.send_new_message(chat_id, content, msg_type=msg_type)
        except Exception as e:
            logger.error(f"Failed to send message: {e}", exc_info=True)
            return False
    
    def send_new_message(self, receive_id: str, content: str, receive_id_type: str = "chat_id", msg_type: str = "post") -> bool:
        """发送新消息
        
        Args:
            receive_id: 接收者 ID
            content: 消息内容
            receive_id_type: ID 类型 ("chat_id", "open_id", "user_id", "union_id")
            msg_type: 消息类型 ("text", "post", "image", "file")
            
        Returns:
            True 如果发送成功
        """
        try:
            if msg_type == "post":
                # 构建 post 格式内容
                post_content = {
                    "zh_cn": {
                        "content": [[{"tag": "md", "text": content or ""}]]
                    }
                }
                content_json = json.dumps(post_content, ensure_ascii=False)
            elif msg_type == "text":
                content_json = json.dumps({"text": self._escape_json(content or "")}, ensure_ascii=False)
            elif msg_type == "image":
                content_json = json.dumps({"image_key": content}, ensure_ascii=False)
            elif msg_type == "file":
                content_json = json.dumps({"file_key": content}, ensure_ascii=False)
            else:
                logger.error(f"Unsupported msg_type: {msg_type}")
                return False
                
            request = CreateMessageRequest.builder() \
                .receive_id_type(receive_id_type) \
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(receive_id)
                    .msg_type(msg_type)
                    .content(content_json)
                    .build()
                ) \
                .build()
            
            response = self.client.im.v1.message.create(request)
            
            if not response.success():
                logger.error(
                    f"Failed to send new message: code={response.code}, "
                    f"msg={response.msg}, log_id={response.get_log_id()}, "
                    f"receive_id_type={receive_id_type}"
                )
                return False
            
            logger.info(f"Successfully sent new message: receive_id_type={receive_id_type}, receive_id={receive_id[:20] if len(receive_id) > 20 else receive_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending new message: {e}", exc_info=True)
            return False
    
    def reply_message(self, message_id: str, content: str, msg_type: str = "post") -> bool:
        """回复消息（用于群聊）
        
        Args:
            message_id: 要回复的消息 ID
            content: 消息内容
            msg_type: 消息类型 ("text", "post", "image", "file")
            
        Returns:
            True 如果发送成功
        """
        try:
            if msg_type == "post":
                # 构建 post 格式内容
                post_content = {
                    "zh_cn": {
                        "content": [[{"tag": "md", "text": content or ""}]]
                    }
                }
                content_json = json.dumps(post_content, ensure_ascii=False)
            elif msg_type == "text":
                content_json = json.dumps({"text": self._escape_json(content or "")}, ensure_ascii=False)
            elif msg_type == "image":
                content_json = json.dumps({"image_key": content}, ensure_ascii=False)
            elif msg_type == "file":
                content_json = json.dumps({"file_key": content}, ensure_ascii=False)
            else:
                logger.error(f"Unsupported msg_type: {msg_type}")
                return False
                
            request = ReplyMessageRequest.builder() \
                .message_id(message_id) \
                .request_body(
                    ReplyMessageRequestBody.builder()
                    .msg_type(msg_type)
                    .content(content_json)
                    .build()
                ) \
                .build()
            
            response = self.client.im.v1.message.reply(request)
            
            if not response.success():
                logger.error(
                    f"Failed to reply message: code={response.code}, "
                    f"msg={response.msg}, log_id={response.get_log_id()}"
                )
                return False
            
            logger.info(f"Successfully replied to message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error replying message: {e}", exc_info=True)
            return False
    
    def _escape_json(self, text: str) -> str:
        """转义 JSON 字符串中的特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            转义后的文本
        """
        if text is None:
            return ""
        return text.replace('\\', '\\\\') \
                   .replace('"', '\\"') \
                   .replace('\n', '\\n') \
                   .replace('\r', '\\r') \
                   .replace('\t', '\\t')
