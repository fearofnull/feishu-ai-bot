"""
数据模型定义
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import time


@dataclass
class ExecutionResult:
    """AI 执行结果"""
    success: bool
    stdout: str
    stderr: str
    error_message: Optional[str]
    execution_time: float


@dataclass
class Message:
    """会话中的单条消息"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: int = field(default_factory=lambda: int(time.time()))


@dataclass
class Session:
    """用户会话"""
    session_id: str
    user_id: str
    created_at: int
    last_active: int
    messages: List[Message] = field(default_factory=list)
    
    def is_expired(self, timeout: int) -> bool:
        """检查会话是否过期
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            True 如果会话已过期
        """
        return (time.time() - self.last_active) > timeout
    
    def should_rotate(self, max_messages: int) -> bool:
        """检查是否需要轮换会话
        
        Args:
            max_messages: 最大消息数
            
        Returns:
            True 如果需要轮换
        """
        return len(self.messages) >= max_messages


@dataclass
class ParsedCommand:
    """解析后的用户命令"""
    provider: str  # AI 提供商：claude, gemini, openai
    execution_layer: str  # 执行层：api 或 cli
    message: str  # 去除前缀后的实际消息内容
    explicit: bool  # 是否显式指定（用户使用了前缀）


@dataclass
class ExecutorMetadata:
    """执行器元数据"""
    name: str
    provider: str
    layer: str  # "api" 或 "cli"
    version: str
    description: str
    capabilities: List[str]
    command_prefixes: List[str]
    priority: int  # 优先级（数字越小优先级越高）
    config_required: List[str]  # 必需的配置项


@dataclass
class MessageReceiveEvent:
    """飞书消息接收事件"""
    message_id: str
    chat_id: str
    chat_type: str  # "p2p" 或 "group"
    message_type: str  # "text", "image", "file" 等
    content: str  # JSON 字符串
    parent_id: Optional[str]  # 引用消息的 ID
    sender_id: str
    create_time: int



@dataclass
class SessionConfig:
    """会话配置"""
    session_id: str  # chat_id 或 user_id
    session_type: str  # "user" 或 "group"
    target_project_dir: Optional[str]
    response_language: Optional[str]
    default_provider: Optional[str]
    default_layer: Optional[str]
    default_cli_provider: Optional[str]
    created_by: Optional[str]  # 创建者 user_id
    created_at: str  # ISO 格式时间戳
    updated_by: Optional[str]  # 最后更新者 user_id
    updated_at: str  # ISO 格式时间戳
    update_count: int  # 更新次数
