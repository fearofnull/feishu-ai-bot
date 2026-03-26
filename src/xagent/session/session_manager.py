"""
会话管理器 - 管理用户会话，维护对话历史
"""
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from filelock import FileLock

from ..models import Session, Message
from ..help.help_loader import get_help_message


logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器
    
    负责创建、存储和管理用户会话，支持：
    - 会话创建和检索
    - 消息追加和历史查询
    - 会话轮换（超过最大消息数或超时）
    - 会话持久化（JSON 文件存储）
    - 会话命令处理（/new, /session, /history）
    - 过期会话清理
    """
    
    NEW_SESSION_COMMANDS = ["/new", "新会话"]
    SESSION_INFO_COMMANDS = ["/session", "会话信息"]
    HISTORY_COMMANDS = ["/history", "历史记录"]
    HELP_COMMANDS = ["/help", "帮助", "help"]
    CLEANUP_COMMANDS = ["/cleanup", "清理会话"]
    
    def __init__(
        self,
        storage_path: str = "./data/sessions.json",
        max_messages: int = 50,
        session_timeout: int = 86400
    ):
        """初始化会话管理器
        
        Args:
            storage_path: 会话存储路径
            max_messages: 单个会话最大消息数
            session_timeout: 会话超时时间（秒），默认 24 小时
        """
        self.storage_path = storage_path
        self.max_messages = max_messages
        self.session_timeout = session_timeout
        self.sessions: Dict[str, Session] = {}
        self.chat_to_active_session: Dict[str, str] = {}
        
        storage_dir = os.path.dirname(storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)
        
        self.archive_dir = os.path.join(storage_dir, "archived_sessions")
        os.makedirs(self.archive_dir, exist_ok=True)
        
        self.lock_path = f"{storage_path}.lock"
        
        self.load_sessions()
        
        logger.info(
            f"SessionManager initialized: storage={storage_path}, "
            f"max_messages={max_messages}, timeout={session_timeout}s"
        )
    
    def get_or_create_session(self, user_id: Optional[str], chat_id: str) -> Session:
        """获取或创建用户会话
        
        Args:
            user_id: 用户 ID
            chat_id: 飞书会话 ID
            
        Returns:
            用户的活跃会话
        """
        if chat_id in self.chat_to_active_session:
            session_id = self.chat_to_active_session[chat_id]
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                if session.is_expired(self.session_timeout) or session.should_rotate(self.max_messages):
                    logger.info(
                        f"Session rotation triggered for chat {chat_id}: "
                        f"expired={session.is_expired(self.session_timeout)}, "
                        f"should_rotate={session.should_rotate(self.max_messages)}"
                    )
                    return self.create_new_session(user_id, chat_id)
                
                session.last_active = int(time.time())
                if user_id and session.user_id != user_id:
                    session.user_id = user_id
                self.save_sessions()
                return session
        
        return self.create_new_session(user_id, chat_id)
    
    def add_message(self, user_id: Optional[str], chat_id: str, role: str, content: str) -> None:
        """添加消息到会话历史
        
        Args:
            user_id: 用户 ID
            chat_id: 飞书会话 ID
            role: 消息角色（user 或 assistant）
            content: 消息内容
        """
        session = self.get_or_create_session(user_id, chat_id)
        message = Message(role=role, content=content)
        session.messages.append(message)
        session.last_active = int(time.time())
        if user_id and session.user_id != user_id:
            session.user_id = user_id
        self.save_sessions()
        
        logger.debug(
            f"Message added to session {session.session_id}: "
            f"role={role}, content_length={len(content)}"
        )
    
    def get_conversation_history(
        self,
        chat_id: str,
        max_messages: Optional[int] = None
    ) -> List[Message]:
        """获取会话的对话历史
        
        Args:
            chat_id: 飞书会话 ID
            max_messages: 最大返回消息数（None 表示返回所有）
            
        Returns:
            消息列表
        """
        if chat_id not in self.chat_to_active_session:
            return []
        
        session_id = self.chat_to_active_session[chat_id]
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id].messages
        
        if max_messages is not None and max_messages > 0:
            return messages[-max_messages:]
        
        return messages
    
    def create_new_session(self, user_id: Optional[str], chat_id: str) -> Session:
        """为用户创建新会话
        
        Args:
            user_id: 用户 ID
            chat_id: 飞书会话 ID
            
        Returns:
            新创建的会话
        """
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id or "",
            chat_id=chat_id,
            created_at=int(time.time()),
            last_active=int(time.time()),
            messages=[]
        )
        
        self.sessions[session.session_id] = session
        self.chat_to_active_session[chat_id] = session.session_id
        self.save_sessions()
        
        logger.info(f"Created new session {session.session_id} for chat {chat_id}")
        return session
    
    def get_session_info(self, chat_id: str) -> Dict[str, Any]:
        """获取会话信息（ID、消息数、创建时间等）
        
        Args:
            chat_id: 飞书会话 ID
            
        Returns:
            包含会话信息的字典
        """
        if chat_id not in self.chat_to_active_session:
            return {
                "exists": False,
                "message": "No active session found"
            }
        
        session_id = self.chat_to_active_session[chat_id]
        if session_id not in self.sessions:
            return {
                "exists": False,
                "message": "No active session found"
            }
        
        session = self.sessions[session_id]
        return {
            "exists": True,
            "session_id": session.session_id,
            "chat_id": session.chat_id,
            "user_id": session.user_id,
            "message_count": len(session.messages),
            "created_at": session.created_at,
            "last_active": session.last_active,
            "age_seconds": int(time.time()) - session.created_at
        }
    
    def format_history_for_ai(self, chat_id: str) -> str:
        """将对话历史格式化为 AI 可读的上下文
        
        Args:
            chat_id: 飞书会话 ID
            
        Returns:
            格式化的对话历史字符串
        """
        messages = self.get_conversation_history(chat_id)
        
        if not messages:
            return ""
        
        lines = ["Previous conversation:"]
        for msg in messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{role_label}: {msg.content}")
        
        return "\n".join(lines)
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话，返回清理数量
        
        Returns:
            清理的会话数量
        """
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.sessions[session_id]
            self._archive_session(session)
            del self.sessions[session_id]
            if session.chat_id in self.chat_to_active_session:
                if self.chat_to_active_session[session.chat_id] == session_id:
                    del self.chat_to_active_session[session.chat_id]
            logger.info(f"Cleaned up expired session {session_id}")
        
        if expired_sessions:
            self.save_sessions()
        
        return len(expired_sessions)
    
    def save_sessions(self) -> None:
        """持久化所有会话到存储"""
        try:
            with FileLock(self.lock_path, timeout=10):
                data = {
                    "sessions": {
                        session_id: self._session_to_dict(session)
                        for session_id, session in self.sessions.items()
                    },
                    "chat_to_active_session": self.chat_to_active_session
                }
                
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.debug(f"Saved {len(self.sessions)} sessions to {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def load_sessions(self) -> None:
        """从存储加载会话"""
        if not os.path.exists(self.storage_path):
            logger.info("No existing sessions file found, starting fresh")
            return
        
        try:
            with FileLock(self.lock_path, timeout=10):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sessions_data = data.get("sessions", {})
                self.sessions = {
                    session_id: self._dict_to_session(session_dict)
                    for session_id, session_dict in sessions_data.items()
                }
                
                self.chat_to_active_session = data.get("chat_to_active_session", {})
                
                logger.info(f"Loaded {len(self.sessions)} sessions from {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.sessions = {}
            self.chat_to_active_session = {}
    
    def _session_to_dict(self, session: Session) -> Dict[str, Any]:
        """将 Session 对象转换为字典
        
        Args:
            session: Session 对象
            
        Returns:
            字典表示
        """
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "chat_id": session.chat_id,
            "created_at": session.created_at,
            "last_active": session.last_active,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in session.messages
            ]
        }
    
    def _dict_to_session(self, data: Dict[str, Any]) -> Session:
        """从字典恢复 Session 对象
        
        Args:
            data: 字典数据
            
        Returns:
            Session 对象
        """
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in data.get("messages", [])
        ]
        
        return Session(
            session_id=data["session_id"],
            user_id=data["user_id"],
            chat_id=data.get("chat_id", ""),
            created_at=data["created_at"],
            last_active=data["last_active"],
            messages=messages
        )
    
    def _archive_session(self, session: Session) -> None:
        """归档会话到归档目录
        
        Args:
            session: 要归档的会话
        """
        try:
            safe_chat_id = self._sanitize_filename(session.chat_id)
            timestamp = int(time.time())
            filename = f"{safe_chat_id}_{session.session_id}_{timestamp}.json"
            archive_path = os.path.join(self.archive_dir, filename)
            
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(self._session_to_dict(session), f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Archived session to {archive_path}")
        
        except Exception as e:
            logger.error(f"Failed to archive session {session.session_id}: {e}")
    
    def _sanitize_filename(self, filename: Optional[str]) -> str:
        """清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        if filename is None:
            return "null"
        
        invalid_chars = '<>:"/\\|?*\x00'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = ''.join(c if ord(c) >= 32 else '_' for c in filename)
        if len(filename) > 100:
            filename = filename[:100]
        return filename
    
    def is_session_command(self, message: str) -> bool:
        """检查消息是否为会话命令
        
        Args:
            message: 用户消息
            
        Returns:
            True 如果是会话命令
        """
        message_lower = message.strip().lower()
        
        import re
        message_lower = re.sub(r'^@[^\s]+\s*', '', message_lower)
        
        return (
            message_lower in [cmd.lower() for cmd in self.NEW_SESSION_COMMANDS] or
            message_lower in [cmd.lower() for cmd in self.SESSION_INFO_COMMANDS] or
            message_lower in [cmd.lower() for cmd in self.HISTORY_COMMANDS] or
            message_lower in [cmd.lower() for cmd in self.HELP_COMMANDS] or
            message_lower in [cmd.lower() for cmd in self.CLEANUP_COMMANDS]
        )
    
    def handle_session_command(self, user_id: Optional[str], chat_id: str, message: str) -> Optional[str]:
        """处理会话命令
        
        Args:
            user_id: 用户 ID
            chat_id: 飞书会话 ID
            message: 用户消息
            
        Returns:
            命令响应消息，如果不是会话命令则返回 None
        """
        message_lower = message.strip().lower()
        
        import re
        message_lower = re.sub(r'^@[^\s]+\s*', '', message_lower)
        
        if message_lower in [cmd.lower() for cmd in self.HELP_COMMANDS]:
            return self._get_help_message()
        
        if message_lower in [cmd.lower() for cmd in self.NEW_SESSION_COMMANDS]:
            self.create_new_session(user_id, chat_id)
            return "✅ 已创建新会话 / New session created"
        
        if message_lower in [cmd.lower() for cmd in self.SESSION_INFO_COMMANDS]:
            info = self.get_session_info(chat_id)
            if not info["exists"]:
                return "ℹ️ 当前没有活跃会话 / No active session"
            
            return (
                f"📊 会话信息 / Session Info:\n"
                f"- Session ID: {info['session_id'][:8]}...\n"
                f"- 消息数 / Messages: {info['message_count']}\n"
                f"- 会话时长 / Age: {info['age_seconds']}s"
            )
        
        if message_lower in [cmd.lower() for cmd in self.HISTORY_COMMANDS]:
            messages = self.get_conversation_history(chat_id)
            if not messages:
                return "ℹ️ 当前会话没有历史记录 / No history in current session"
            
            lines = ["📜 对话历史 / Conversation History:"]
            for i, msg in enumerate(messages, 1):
                role_label = "👤 User" if msg.role == "user" else "🤖 Assistant"
                content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                lines.append(f"{i}. {role_label}: {content_preview}")
            
            return "\n".join(lines)
        
        if message_lower in [cmd.lower() for cmd in self.CLEANUP_COMMANDS]:
            cleaned_count = self.cleanup_expired_sessions()
            return f"✅ 清理完成 / Cleanup completed: 清理了 {cleaned_count} 个过期会话 / cleaned {cleaned_count} expired sessions"
        
        return None
    
    def _get_help_message(self) -> str:
        """获取帮助信息
        
        Returns:
            包含所有可用命令的帮助文本
        """
        return get_help_message()
