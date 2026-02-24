"""
消息处理器模块
负责解析和处理飞书消息，包括文本消息和引用消息
"""
import json
import logging
from typing import Optional
from lark_oapi.api.im.v1 import GetMessageRequest, GetMessageResponse
from lark_oapi import Client as LarkClient

from .cache import DeduplicationCache

logger = logging.getLogger(__name__)


class MessageHandler:
    """消息处理器
    
    负责解析飞书消息内容，处理引用消息，并组合消息
    """
    
    def __init__(self, client: LarkClient, dedup_cache: DeduplicationCache):
        """初始化消息处理器
        
        Args:
            client: 飞书 API 客户端
            dedup_cache: 消息去重缓存
        """
        self.client = client
        self.dedup_cache = dedup_cache
    
    def parse_message_content(self, message) -> str:
        """解析消息内容，提取文本内容
        
        Args:
            message: 飞书消息对象（EventMessage 或 dict），包含 message_type 和 content 字段
            
        Returns:
            提取的文本内容
            
        Raises:
            ValueError: 如果消息类型不是文本或解析失败
        """
        # 处理 EventMessage 对象或字典
        if hasattr(message, 'message_type'):
            # EventMessage 对象
            message_type = message.message_type
            content_str = message.content
        else:
            # 字典
            message_type = message.get("message_type", "")
            content_str = message.get("content", "{}")
        
        # 检查消息类型
        if message_type != "text":
            error_msg = f"不支持的消息类型: {message_type}。请发送文本消息。"
            logger.warning(error_msg)
            raise ValueError(error_msg)
        
        # 解析消息内容
        try:
            content = json.loads(content_str)
            text = content.get("text", "")
            
            if not text:
                raise ValueError("消息内容为空")
            
            logger.debug(f"成功解析文本消息: {text[:50]}...")
            return text
            
        except json.JSONDecodeError as e:
            error_msg = f"消息内容 JSON 解析失败: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"消息解析失败: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_quoted_message(self, parent_id: str) -> Optional[str]:
        """获取引用消息的内容
        
        调用飞书 API 获取引用消息，支持文本消息和卡片消息（interactive）
        
        Args:
            parent_id: 引用消息的 ID
            
        Returns:
            引用消息的文本内容，如果获取失败返回 None
        """
        if not parent_id:
            return None
        
        try:
            logger.info(f"正在获取引用消息: {parent_id}")
            
            # 构建请求
            request = GetMessageRequest.builder() \
                .message_id(parent_id) \
                .build()
            
            # 调用 API
            response: GetMessageResponse = self.client.im.v1.message.get(request)
            
            # 检查响应
            if not response.success():
                logger.warning(
                    f"获取引用消息失败: code={response.code}, "
                    f"msg={response.msg}, log_id={response.get_log_id()}"
                )
                return None
            
            # 提取消息内容
            quoted_message = response.data.message
            message_type = quoted_message.message_type
            
            logger.debug(f"引用消息类型: {message_type}")
            
            # 处理文本消息
            if message_type == "text":
                content = json.loads(quoted_message.content)
                text = content.get("text", "")
                logger.info(f"成功获取引用的文本消息: {text[:50]}...")
                return text
            
            # 处理卡片消息（interactive）
            elif message_type == "interactive":
                # 卡片消息通常包含复杂的 JSON 结构
                # 尝试提取可读的文本内容
                try:
                    content = json.loads(quoted_message.content)
                    # 卡片消息可能有多种格式，尝试提取标题或内容
                    if "header" in content:
                        title = content["header"].get("title", {}).get("content", "")
                        if title:
                            logger.info(f"成功获取引用的卡片消息标题: {title[:50]}...")
                            return f"[卡片消息] {title}"
                    
                    # 如果没有标题，返回通用提示
                    logger.info("引用的卡片消息无法提取文本内容")
                    return "[卡片消息]"
                    
                except Exception as e:
                    logger.warning(f"解析卡片消息内容失败: {e}")
                    return "[卡片消息]"
            
            # 其他消息类型
            else:
                logger.warning(f"不支持的引用消息类型: {message_type}")
                return f"[{message_type} 消息]"
        
        except Exception as e:
            logger.error(f"获取引用消息时发生异常: {e}", exc_info=True)
            return None
    
    def combine_messages(self, quoted: Optional[str], current: str) -> str:
        """组合引用消息和当前消息
        
        Args:
            quoted: 引用消息内容，可以为 None
            current: 当前消息内容
            
        Returns:
            组合后的消息字符串
        """
        if quoted:
            combined = f"引用消息：{quoted}\n\n当前消息：{current}"
            logger.debug(f"组合消息: 引用消息长度={len(quoted)}, 当前消息长度={len(current)}")
            return combined
        else:
            logger.debug(f"无引用消息，返回当前消息: 长度={len(current)}")
            return current
