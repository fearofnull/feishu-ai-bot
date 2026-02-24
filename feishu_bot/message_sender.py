"""
消息发送器
"""
import json
import logging
from typing import Any
from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

logger = logging.getLogger(__name__)


class MessageSender:
    """根据聊天类型发送消息到飞书"""
    
    def __init__(self, client: LarkClient):
        """初始化消息发送器
        
        Args:
            client: 飞书 API 客户端
        """
        self.client = client
    
    def send_message(
        self,
        chat_type: str,
        chat_id: str,
        message_id: str,
        content: str
    ) -> None:
        """发送消息，根据聊天类型选择策略
        
        Args:
            chat_type: 聊天类型（p2p 或 group）
            chat_id: 聊天 ID
            message_id: 消息 ID（用于回复）
            content: 消息内容
            
        Raises:
            Exception: 如果发送失败
        """
        if chat_type == "p2p":
            self.send_new_message(chat_id, content)
        else:
            self.reply_message(message_id, content)
    
    def send_new_message(self, chat_id: str, content: str) -> None:
        """发送新消息（私聊）
        
        Args:
            chat_id: 聊天 ID
            content: 消息内容
            
        Raises:
            Exception: 如果发送失败
        """
        content_json = json.dumps({"text": content})
        
        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(content_json)
                .build()
            )
            .build()
        )
        
        response = self.client.im.v1.message.create(request)
        
        if not response.success():
            error_msg = (
                f"client.im.v1.message.create failed, "
                f"code: {response.code}, "
                f"msg: {response.msg}, "
                f"log_id: {response.get_log_id()}"
            )
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info(f"Successfully sent new message to chat {chat_id}")
    
    def reply_message(self, message_id: str, content: str) -> None:
        """回复消息（群聊）
        
        Args:
            message_id: 要回复的消息 ID
            content: 消息内容
            
        Raises:
            Exception: 如果回复失败
        """
        content_json = json.dumps({"text": content})
        
        request = (
            ReplyMessageRequest.builder()
            .message_id(message_id)
            .request_body(
                ReplyMessageRequestBody.builder()
                .content(content_json)
                .msg_type("text")
                .build()
            )
            .build()
        )
        
        response = self.client.im.v1.message.reply(request)
        
        if not response.success():
            error_msg = (
                f"client.im.v1.message.reply failed, "
                f"code: {response.code}, "
                f"msg: {response.msg}, "
                f"log_id: {response.get_log_id()}"
            )
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info(f"Successfully replied to message {message_id}")
