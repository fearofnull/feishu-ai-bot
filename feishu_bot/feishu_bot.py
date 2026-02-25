"""
飞书 AI 机器人主应用类
"""
import logging
import json
from typing import Optional
from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

from .config import BotConfig
from .cache import DeduplicationCache
from .message_handler import MessageHandler
from .session_manager import SessionManager
from .command_parser import CommandParser
from .executor_registry import ExecutorRegistry
from .smart_router import SmartRouter
from .response_formatter import ResponseFormatter
from .message_sender import MessageSender
from .event_handler import EventHandler
from .websocket_client import WebSocketClient

# API Executors
from .claude_api_executor import ClaudeAPIExecutor
from .gemini_api_executor import GeminiAPIExecutor
from .openai_api_executor import OpenAIAPIExecutor

# CLI Executors
from .claude_cli_executor import ClaudeCodeCLIExecutor
from .gemini_cli_executor import GeminiCLIExecutor

from .models import ExecutorMetadata

logger = logging.getLogger(__name__)


class FeishuBot:
    """飞书 AI 机器人主应用类"""
    
    def __init__(self, config: BotConfig):
        """初始化飞书机器人
        
        Args:
            config: 机器人配置
        """
        self.config = config
        
        # 初始化飞书客户端
        self.client = LarkClient.builder() \
            .app_id(config.app_id) \
            .app_secret(config.app_secret) \
            .build()
        
        # 初始化核心组件
        self.dedup_cache = DeduplicationCache(max_size=config.cache_size)
        self.message_handler = MessageHandler(self.client, self.dedup_cache)
        self.session_manager = SessionManager(
            storage_path=config.session_storage_path,
            max_messages=config.max_session_messages,
            session_timeout=config.session_timeout
        )
        self.command_parser = CommandParser()
        self.executor_registry = ExecutorRegistry()
        self.response_formatter = ResponseFormatter()
        self.message_sender = MessageSender(self.client)
        
        # 初始化并注册执行器
        self._register_executors()
        
        # 初始化智能路由器
        self.smart_router = SmartRouter(
            executor_registry=self.executor_registry,
            default_provider=config.default_provider,
            default_layer=config.default_layer,
            default_cli_provider=config.default_cli_provider,
            use_ai_intent_classification=config.use_ai_intent_classification
        )
        
        # 初始化事件处理器和 WebSocket 客户端
        self.event_handler = EventHandler()
        self.event_handler.register_message_receive_handler(
            self._handle_message_receive
        )
        
        self.ws_client = WebSocketClient(
            app_id=config.app_id,
            app_secret=config.app_secret,
            event_handler=self.event_handler
        )
        
        logger.info("FeishuBot initialized successfully")
    
    def _register_executors(self) -> None:
        """注册所有 AI 执行器"""
        # 注册 Claude API 执行器
        if self.config.claude_api_key:
            try:
                claude_api = ClaudeAPIExecutor(
                    api_key=self.config.claude_api_key,
                    timeout=self.config.ai_timeout
                )
                claude_api_metadata = ExecutorMetadata(
                    name="Claude API",
                    provider="claude",
                    layer="api",
                    version="1.0.0",
                    description="Anthropic Claude API for general Q&A",
                    capabilities=["general_qa", "text_generation", "analysis"],
                    command_prefixes=["@claude-api", "@claude"],
                    priority=1,
                    config_required=["api_key"]
                )
                self.executor_registry.register_api_executor(
                    "claude", claude_api, claude_api_metadata
                )
                logger.info("Registered Claude API executor")
            except Exception as e:
                logger.warning(f"Failed to register Claude API executor: {e}")
        
        # 注册 Gemini API 执行器
        if self.config.gemini_api_key:
            try:
                gemini_api = GeminiAPIExecutor(
                    api_key=self.config.gemini_api_key,
                    timeout=self.config.ai_timeout
                )
                gemini_api_metadata = ExecutorMetadata(
                    name="Gemini API",
                    provider="gemini",
                    layer="api",
                    version="1.0.0",
                    description="Google Gemini API for general Q&A",
                    capabilities=["general_qa", "text_generation", "analysis"],
                    command_prefixes=["@gemini-api", "@gemini"],
                    priority=2,
                    config_required=["api_key"]
                )
                self.executor_registry.register_api_executor(
                    "gemini", gemini_api, gemini_api_metadata
                )
                logger.info("Registered Gemini API executor")
            except Exception as e:
                logger.warning(f"Failed to register Gemini API executor: {e}")
        
        # 注册 OpenAI API 执行器
        if self.config.openai_api_key:
            try:
                openai_api = OpenAIAPIExecutor(
                    api_key=self.config.openai_api_key,
                    base_url=self.config.openai_base_url,
                    model=self.config.openai_model,
                    timeout=self.config.ai_timeout
                )
                openai_api_metadata = ExecutorMetadata(
                    name="OpenAI API",
                    provider="openai",
                    layer="api",
                    version="1.0.0",
                    description="OpenAI API for general Q&A",
                    capabilities=["general_qa", "text_generation", "analysis"],
                    command_prefixes=["@openai", "@gpt"],
                    priority=3,
                    config_required=["api_key"]
                )
                self.executor_registry.register_api_executor(
                    "openai", openai_api, openai_api_metadata
                )
                logger.info("Registered OpenAI API executor")
            except Exception as e:
                logger.warning(f"Failed to register OpenAI API executor: {e}")
        
        # 注册 Claude Code CLI 执行器
        claude_cli_dir = self.config.claude_cli_target_dir or self.config.target_directory
        if claude_cli_dir:
            try:
                claude_cli = ClaudeCodeCLIExecutor(
                    target_dir=claude_cli_dir,
                    timeout=self.config.ai_timeout,
                    use_native_session=True,
                    session_storage_path=self.config.session_storage_path
                )
                claude_cli_metadata = ExecutorMetadata(
                    name="Claude Code CLI",
                    provider="claude",
                    layer="cli",
                    version="1.0.0",
                    description="Claude Code CLI for code analysis and operations",
                    capabilities=["code_analysis", "file_operations", "command_execution"],
                    command_prefixes=["@claude-cli", "@code"],
                    priority=1,
                    config_required=["target_directory"]
                )
                self.executor_registry.register_cli_executor(
                    "claude", claude_cli, claude_cli_metadata
                )
                logger.info(f"Registered Claude Code CLI executor (target: {claude_cli_dir})")
            except Exception as e:
                logger.warning(f"Failed to register Claude Code CLI executor: {e}")
        
        # 注册 Gemini CLI 执行器
        gemini_cli_dir = self.config.gemini_cli_target_dir or self.config.target_directory
        if gemini_cli_dir:
            try:
                gemini_cli = GeminiCLIExecutor(
                    target_dir=gemini_cli_dir,
                    timeout=self.config.ai_timeout,
                    use_native_session=True,
                    session_storage_path=self.config.session_storage_path
                )
                gemini_cli_metadata = ExecutorMetadata(
                    name="Gemini CLI",
                    provider="gemini",
                    layer="cli",
                    version="1.0.0",
                    description="Gemini CLI for code analysis and operations",
                    capabilities=["code_analysis", "file_operations", "command_execution"],
                    command_prefixes=["@gemini-cli"],
                    priority=2,
                    config_required=["target_directory"]
                )
                self.executor_registry.register_cli_executor(
                    "gemini", gemini_cli, gemini_cli_metadata
                )
                logger.info(f"Registered Gemini CLI executor (target: {gemini_cli_dir})")
            except Exception as e:
                logger.warning(f"Failed to register Gemini CLI executor: {e}")
    
    def _handle_message_receive(self, data: P2ImMessageReceiveV1) -> None:
        """处理接收到的消息
        
        Args:
            data: 飞书消息接收事件
        """
        try:
            message_id = data.event.message.message_id
            chat_id = data.event.message.chat_id
            chat_type = data.event.message.chat_type
            sender_id = data.event.sender.sender_id.user_id
            
            logger.info(f"Received message {message_id} from user {sender_id}")
            
            # 1. 消息去重
            if self.dedup_cache.is_processed(message_id):
                logger.info(f"Message {message_id} already processed, skipping")
                return
            
            self.dedup_cache.mark_processed(message_id)
            
            # 2. 消息解析
            message_content = self.message_handler.parse_message_content(
                data.event.message
            )
            
            if message_content.startswith("解析消息失败") or message_content.startswith("parse message failed"):
                # 非文本消息，直接返回错误
                self.message_sender.send_message(
                    chat_type, chat_id, message_id, message_content
                )
                return
            
            # 处理引用消息
            if hasattr(data.event.message, 'parent_id') and data.event.message.parent_id:
                quoted_content = self.message_handler.get_quoted_message(
                    data.event.message.parent_id
                )
                if quoted_content:
                    message_content = self.message_handler.combine_messages(
                        quoted_content, message_content
                    )
            
            # 3. 命令解析
            parsed_command = self.command_parser.parse_command(message_content)
            
            # 4. 会话命令检查
            if self._handle_session_command(
                sender_id, parsed_command.message, chat_type, chat_id, message_id
            ):
                return
            
            # 5. 智能路由
            try:
                executor = self.smart_router.route(parsed_command)
            except Exception as e:
                error_msg = f"路由失败：{str(e)}"
                logger.error(error_msg)
                response = self.response_formatter.format_error(
                    message_content, error_msg
                )
                self.message_sender.send_message(
                    chat_type, chat_id, message_id, response
                )
                return
            
            # 6. AI 执行
            try:
                # 获取对话历史
                conversation_history = self.session_manager.get_conversation_history(
                    sender_id
                )
                
                # 获取执行器元数据
                provider_name = executor.get_provider_name()  # e.g., "openai-api", "claude-cli"
                
                # 解析 provider 和 layer
                if "-" in provider_name:
                    parts = provider_name.rsplit("-", 1)  # 从右边分割一次
                    provider = parts[0]  # e.g., "openai", "claude"
                    layer = parts[1]     # e.g., "api", "cli"
                else:
                    # 兜底：如果没有连字符，假设是 API
                    provider = provider_name
                    layer = "api"
                
                executor_metadata = self.executor_registry.get_executor_metadata(provider, layer)
                executor_name = executor_metadata.name if executor_metadata else None
                
                # 执行 AI
                if executor.get_provider_name().endswith("-api"):
                    # API 层：传递对话历史
                    result = executor.execute(
                        parsed_command.message,
                        conversation_history=conversation_history
                    )
                else:
                    # CLI 层：使用原生会话
                    result = executor.execute(
                        parsed_command.message,
                        additional_params={"user_id": sender_id}
                    )
                
                # 7. 响应格式化
                if result.success:
                    response = self.response_formatter.format_response(
                        message_content, result.stdout, executor_name=executor_name
                    )
                else:
                    response = self.response_formatter.format_error(
                        message_content, result.error_message or result.stderr, executor_name=executor_name
                    )
                
                # 8. 消息发送
                self.message_sender.send_message(
                    chat_type, chat_id, message_id, response
                )
                
                # 9. 会话历史更新
                self.session_manager.add_message(sender_id, "user", parsed_command.message)
                self.session_manager.add_message(
                    sender_id, "assistant", result.stdout if result.success else result.error_message
                )
                
                logger.info(f"Successfully processed message {message_id}")
                
            except Exception as e:
                error_msg = f"AI 执行失败：{str(e)}"
                logger.error(error_msg, exc_info=True)
                response = self.response_formatter.format_error(
                    message_content, error_msg
                )
                self.message_sender.send_message(
                    chat_type, chat_id, message_id, response
                )
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            # 尝试发送错误消息给用户
            try:
                error_response = f"处理消息时发生错误：{str(e)}"
                self.message_sender.send_message(
                    data.event.message.chat_type,
                    data.event.message.chat_id,
                    data.event.message.message_id,
                    error_response
                )
            except:
                pass
    
    def _handle_session_command(
        self,
        user_id: str,
        message: str,
        chat_type: str,
        chat_id: str,
        message_id: str
    ) -> bool:
        """处理会话命令
        
        Args:
            user_id: 用户 ID
            message: 消息内容
            chat_type: 聊天类型
            chat_id: 聊天 ID
            message_id: 消息 ID
            
        Returns:
            True 如果是会话命令并已处理
        """
        # 检查是否为会话命令
        if not self.session_manager.is_session_command(message):
            return False
        
        # 使用 session_manager 处理命令
        response = self.session_manager.handle_session_command(user_id, message)
        
        # 如果是新会话命令，额外清除 CLI 会话
        message_lower = message.lower().strip()
        if message_lower in [cmd.lower() for cmd in self.session_manager.NEW_SESSION_COMMANDS]:
            for provider in ["claude", "gemini"]:
                try:
                    cli_executor = self.executor_registry.get_executor(provider, "cli")
                    if hasattr(cli_executor, 'clear_session'):
                        cli_executor.clear_session(user_id)
                except:
                    pass
        
        # 发送响应
        if response:
            self.message_sender.send_message(
                chat_type, chat_id, message_id, response
            )
            return True
        
        return False
    
    def start(self) -> None:
        """启动机器人"""
        logger.info("Starting FeishuBot...")
        self.ws_client.start()
    
    def stop(self) -> None:
        """停止机器人"""
        logger.info("Stopping FeishuBot...")
        self.ws_client.stop()
