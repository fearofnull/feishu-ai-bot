"""
Feishu AI Bot Package

飞书 AI 机器人包，提供与多个 AI 提供商集成的能力。
"""

__version__ = "1.0.0"

from .cache import DeduplicationCache
from .command_parser import CommandParser
from .config import BotConfig
from .message_handler import MessageHandler
from .executor_registry import (
    ExecutorRegistry,
    ExecutorNotAvailableError,
    AIExecutor,
)
from .smart_router import SmartRouter
from .ai_api_executor import AIAPIExecutor
from .claude_api_executor import ClaudeAPIExecutor
from .gemini_api_executor import GeminiAPIExecutor
from .ai_cli_executor import AICLIExecutor
from .claude_cli_executor import ClaudeCodeCLIExecutor
from .gemini_cli_executor import GeminiCLIExecutor
from .models import (
    ExecutionResult,
    Message,
    Session,
    ParsedCommand,
    ExecutorMetadata,
    MessageReceiveEvent,
)

__all__ = [
    "DeduplicationCache",
    "CommandParser",
    "BotConfig",
    "MessageHandler",
    "ExecutorRegistry",
    "ExecutorNotAvailableError",
    "AIExecutor",
    "SmartRouter",
    "AIAPIExecutor",
    "ClaudeAPIExecutor",
    "GeminiAPIExecutor",
    "AICLIExecutor",
    "ClaudeCodeCLIExecutor",
    "GeminiCLIExecutor",
    "ExecutionResult",
    "Message",
    "Session",
    "ParsedCommand",
    "ExecutorMetadata",
    "MessageReceiveEvent",
]
