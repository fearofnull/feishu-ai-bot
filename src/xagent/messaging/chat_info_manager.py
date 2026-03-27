"""
群聊信息管理器

负责从飞书 API 获取群聊信息，包括群名称等
"""
import logging
from typing import Optional, Dict, Any
from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import GetChatRequest

logger = logging.getLogger(__name__)


class ChatInfoManager:
    """群聊信息管理器
    
    提供获取飞书群聊信息的功能，特别是群名称
    """
    
    def __init__(self, client: LarkClient):
        """初始化群聊信息管理器
        
        Args:
            client: 飞书 API 客户端
        """
        self.client = client
        self._chat_info_cache: Dict[str, Any] = {}
    
    def get_chat_name(self, chat_id: str) -> Optional[str]:
        """获取群聊名称
        
        Args:
            chat_id: 群聊 ID
            
        Returns:
            群聊名称，获取失败时返回 None
        """
        try:
            # 先尝试从缓存获取
            if chat_id in self._chat_info_cache:
                cached_data = self._chat_info_cache[chat_id]
                if cached_data and isinstance(cached_data, dict):
                    return cached_data.get('name')
            
            # 调用飞书 API 获取群聊信息
            request = GetChatRequest.builder().chat_id(chat_id).build()
            response = self.client.im.v1.chat.get(request)
            
            if not response.success():
                logger.warning(
                    f"Failed to get chat info for {chat_id}: "
                    f"code={response.code}, msg={response.msg}"
                )
                return None
            
            # 提取群名称
            chat_data = response.data
            if chat_data and hasattr(chat_data, 'name'):
                chat_name = chat_data.name
                # 缓存群信息
                self._chat_info_cache[chat_id] = {
                    'name': chat_name,
                    'id': chat_id
                }
                logger.info(f"Retrieved chat name for {chat_id}: {chat_name}")
                return chat_name
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting chat name for {chat_id}: {e}", exc_info=True)
            return None
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取完整的群聊信息
        
        Args:
            chat_id: 群聊 ID
            
        Returns:
            群聊信息字典，获取失败时返回 None
        """
        try:
            # 先尝试从缓存获取
            if chat_id in self._chat_info_cache:
                return self._chat_info_cache[chat_id]
            
            # 调用飞书 API 获取群聊信息
            request = GetChatRequest.builder().chat_id(chat_id).build()
            response = self.client.im.v1.chat.get(request)
            
            if not response.success():
                logger.warning(
                    f"Failed to get chat info for {chat_id}: "
                    f"code={response.code}, msg={response.msg}"
                )
                return None
            
            # 提取群信息
            chat_data = response.data
            if chat_data:
                info = {
                    'id': chat_id,
                    'name': getattr(chat_data, 'name', None),
                    'description': getattr(chat_data, 'description', None),
                    'owner_id': getattr(chat_data, 'owner_id', None),
                    'owner_id_type': getattr(chat_data, 'owner_id_type', None),
                }
                # 缓存群信息
                self._chat_info_cache[chat_id] = info
                logger.info(f"Retrieved chat info for {chat_id}: {info}")
                return info
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting chat info for {chat_id}: {e}", exc_info=True)
            return None
    
    def clear_cache(self, chat_id: Optional[str] = None) -> None:
        """清除缓存
        
        Args:
            chat_id: 要清除的群聊 ID，如果为 None 则清除所有缓存
        """
        if chat_id is None:
            self._chat_info_cache.clear()
            logger.info("Cleared all chat info cache")
        else:
            if chat_id in self._chat_info_cache:
                del self._chat_info_cache[chat_id]
                logger.info(f"Cleared cache for chat {chat_id}")

