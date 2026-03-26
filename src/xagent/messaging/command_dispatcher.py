"""
命令分发器模块

负责处理配置命令和会话命令的分发
"""
import logging
from typing import Optional, Tuple

from ..session.session_manager import SessionManager
from .message_sender import MessageSender
from ..core.executor_registry import ExecutorRegistry

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """命令分发器
    
    负责处理特殊命令的分发：
    1. 配置命令（/setdir, /lang, /model 等）
    2. 会话命令（/new, /clear 等）
    """
    
    def __init__(
        self,
        unified_config,
        session_manager: SessionManager,
        message_sender: MessageSender,
        executor_registry: ExecutorRegistry
    ):
        """初始化命令分发器
        
        Args:
            unified_config: 统一配置管理器
            session_manager: 会话管理器
            message_sender: 消息发送器
            executor_registry: 执行器注册表
        """
        self.unified_config = unified_config
        self.session_manager = session_manager
        self.message_sender = message_sender
        self.executor_registry = executor_registry
    
    def dispatch(
        self,
        session_id: str,
        session_type: str,
        user_id: Optional[str],
        message: str,
        chat_type: str,
        chat_id: str,
        message_id: str
    ) -> bool:
        """分发命令
        
        Args:
            session_id: 会话 ID
            session_type: 会话类型
            user_id: 用户 ID
            message: 消息内容
            chat_type: 聊天类型
            chat_id: 聊天 ID
            message_id: 消息 ID
            
        Returns:
            True 如果命令已被处理，False 表示不是特殊命令
        """
        if self._handle_config_command(
            session_id, session_type, user_id, message,
            chat_type, chat_id, message_id
        ):
            return True
        
        if self._handle_session_command(
            user_id, message, chat_type, chat_id, message_id
        ):
            return True
        
        return False
    
    def _handle_config_command(
        self,
        session_id: str,
        session_type: str,
        user_id: Optional[str],
        message: str,
        chat_type: str,
        chat_id: str,
        message_id: str
    ) -> bool:
        """处理配置命令"""
        if not self.unified_config.is_config_command(message):
            return False
        
        response = self.unified_config.handle_config_command(
            session_id, session_type, user_id, message
        )
        
        if response:
            self.message_sender.send_message(
                chat_type, chat_id, message_id, response
            )
            return True
        
        return False
    
    def _handle_session_command(
        self,
        user_id: Optional[str],
        message: str,
        chat_type: str,
        chat_id: str,
        message_id: str
    ) -> bool:
        """处理会话命令"""
        if not self.session_manager.is_session_command(message):
            return False
        
        response = self.session_manager.handle_session_command(user_id, chat_id, message)
        
        message_lower = message.lower().strip()
        if message_lower in [cmd.lower() for cmd in self.session_manager.NEW_SESSION_COMMANDS]:
            self._clear_cli_sessions(user_id)
        
        if response:
            self.message_sender.send_message(
                chat_type, chat_id, message_id, response
            )
            return True
        
        return False
    
    def _clear_cli_sessions(self, user_id: Optional[str]):
        """清除所有 CLI 会话"""
        if not user_id:
            return
        
        for provider in ["claude", "gemini", "qwen"]:
            try:
                cli_executor = self.executor_registry.get_executor(provider, "cli")
                if hasattr(cli_executor, 'clear_session'):
                    cli_executor.clear_session(user_id)
            except Exception as e:
                logger.debug(f"Could not clear {provider} CLI session: {e}")
