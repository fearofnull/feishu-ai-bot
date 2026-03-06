"""
智能路由器模块

根据解析的命令和消息内容，决定使用哪个 AI 执行器
"""
import logging
from typing import Optional

from feishu_bot.models import ParsedCommand
from feishu_bot.core.executor_registry import ExecutorRegistry, ExecutorNotAvailableError, AIExecutor
from feishu_bot.utils.command_parser import CommandParser
from feishu_bot.utils.intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)


class SmartRouter:
    """智能路由器
    
    根据用户指令和消息内容智能选择 API 层或 CLI 层
    
    路由策略：
    1. 显式指定优先：如果用户使用了命令前缀，直接使用指定的提供商和层
    2. AI意图分类：使用AI判断用户意图，决定是否需要CLI层（推荐）
    3. 关键词降级：如果AI不可用，使用关键词检测作为降级方案
    4. 降级策略：如果指定的执行器不可用，尝试降级到其他层
    """
    
    def __init__(
        self,
        executor_registry: ExecutorRegistry,
        default_provider: str = "claude",
        default_layer: str = "api",
        default_cli_provider: Optional[str] = None,
        use_ai_intent_classification: bool = True,
        unified_api_interface: Optional[AIExecutor] = None
    ):
        """初始化智能路由器
        
        Args:
            executor_registry: 执行器注册表
            default_provider: 默认 AI 提供商
            default_layer: 默认执行层（api 或 cli）
            default_cli_provider: CLI层专用默认提供商（如果不设置则自动检测第一个可用的CLI）
            use_ai_intent_classification: 是否使用AI进行意图分类（推荐开启）
            unified_api_interface: 统一API接口实例（可选）
        """
        self.executor_registry = executor_registry
        self.default_provider = default_provider
        self.default_layer = default_layer
        self.default_cli_provider = default_cli_provider  # 可能为None，稍后自动检测
        self.command_parser = CommandParser()
        self.use_ai_intent_classification = use_ai_intent_classification
        self.unified_api_interface = unified_api_interface
        
        # 初始化意图分类器（延迟初始化API执行器）
        self.intent_classifier = None
        
        logger.info(
            f"SmartRouter initialized with default provider={default_provider}, "
            f"default layer={default_layer}, "
            f"default CLI provider={self.default_cli_provider or 'auto-detect'}, "
            f"ai_intent_classification={use_ai_intent_classification}, "
            f"unified_api={'enabled' if unified_api_interface else 'disabled'}"
        )
    
    def route(self, parsed_command: ParsedCommand) -> AIExecutor:
        """根据解析的命令选择合适的执行器
        
        Args:
            parsed_command: 解析后的命令
            
        Returns:
            AIExecutor: 选择的执行器
            
        Raises:
            ExecutorNotAvailableError: 如果所有执行器都不可用
        """
        provider = parsed_command.provider
        layer = parsed_command.execution_layer
        message_preview = parsed_command.message[:50] + "..." if len(parsed_command.message) > 50 else parsed_command.message
        
        # 特殊处理：如果provider是"unified"，使用统一API接口
        if provider == "unified":
            if self.unified_api_interface is None:
                logger.error("[ROUTING] Unified API interface not configured")
                raise ExecutorNotAvailableError(
                    "unified",
                    "api",
                    "Unified API interface not configured. Please configure provider settings."
                )
            
            logger.info("[ROUTING] Using Unified API interface for @gpt command")
            logger.debug(f"[ROUTING] Message: '{message_preview}'")
            
            # 返回统一API接口作为执行器
            # 注意：UnifiedAPIInterface需要实现AIExecutor接口
            return self.unified_api_interface
        
        # 如果用户显式指定，直接使用指定的执行器
        if parsed_command.explicit:
            logger.info(
                f"[ROUTING] Explicit prefix detected → provider={provider}, layer={layer}"
            )
            logger.debug(f"[ROUTING] Message: '{message_preview}'")
            try:
                executor = self.get_executor(provider, layer)
                logger.info(f"[ROUTING] ✅ Using {provider}/{layer} (explicit)")
                return executor
            except ExecutorNotAvailableError as e:
                # 显式指定的执行器不可用，尝试降级
                logger.warning(
                    f"[ROUTING] ⚠️  Explicitly specified executor {provider}/{layer} not available: {e.reason}"
                )
                return self._fallback(provider, layer)
        
        # 智能判断：使用AI或关键词检测是否需要 CLI 层
        if self.use_ai_intent_classification:
            # 使用AI进行意图分类
            needs_cli = self._classify_intent_with_ai(parsed_command.message)
        else:
            # 使用关键词检测（传统方式）
            needs_cli = self.command_parser.detect_cli_keywords(parsed_command.message)
        
        if needs_cli:
            layer = "cli"
            # 如果未设置default_cli_provider，自动检测第一个可用的CLI
            if self.default_cli_provider:
                provider = self.default_cli_provider
            else:
                provider = self._get_first_available_cli_provider()
                if not provider:
                    # 没有可用的CLI执行器
                    logger.error("[ROUTING] No CLI executor available")
                    raise ExecutorNotAvailableError(
                        "cli",
                        "cli",
                        "No CLI executor configured. Please install Claude Code CLI or Gemini CLI and configure TARGET_PROJECT_DIR."
                    )
            logger.info(
                f"[ROUTING] Intent classification: needs CLI layer, using provider={provider}"
            )
            logger.debug(f"[ROUTING] Message: '{message_preview}'")
        else:
            layer = self.default_layer
            provider = self.default_provider  # 使用通用默认提供商
            logger.info(
                f"[ROUTING] Intent classification: using default layer: {layer}, provider={provider}"
            )
            logger.debug(f"[ROUTING] Message: '{message_preview}'")
        
        # 使用默认提供商（如果没有显式指定）
        # provider 变量已在上面的 needs_cli 判断中设置
        
        # 获取执行器，如果不可用则降级
        try:
            executor = self.get_executor(provider, layer)
            logger.info(f"[ROUTING] ✅ Using {provider}/{layer} (smart routing)")
            return executor
        except ExecutorNotAvailableError as e:
            logger.warning(
                f"[ROUTING] ⚠️  Executor {provider}/{layer} not available: {e.reason}, attempting fallback"
            )
            return self._fallback(provider, layer)
    
    def get_executor(self, provider: str, layer: str) -> AIExecutor:
        """通过 ExecutorRegistry 获取指定执行器
        
        Args:
            provider: 提供商名称
            layer: 执行层
            
        Returns:
            AIExecutor: 执行器实例
            
        Raises:
            ExecutorNotAvailableError: 如果执行器不可用
        """
        return self.executor_registry.get_executor(provider, layer)
    
    def _classify_intent_with_ai(self, message: str) -> bool:
        """使用AI分类用户意图，判断是否需要CLI层
        
        Args:
            message: 用户消息
            
        Returns:
            bool: True 如果需要CLI层
        """
        # 延迟初始化意图分类器
        if self.intent_classifier is None:
            # 获取一个可用的API执行器用于意图分类
            api_executor = self._get_api_executor_for_classification()
            if api_executor is None:
                logger.warning(
                    "[ROUTING] No API executor available for intent classification, "
                    "falling back to keyword detection"
                )
                return self.command_parser.detect_cli_keywords(message)
            
            self.intent_classifier = IntentClassifier(
                api_executor=api_executor,
                use_cache=True
            )
        
        # 使用AI分类
        try:
            classification = self.intent_classifier.classify(message)
            logger.info(
                f"[ROUTING] Intent classification result: needs_cli={classification.needs_cli}, "
                f"confidence={classification.confidence:.2f}, category={classification.category}"
            )
            return classification.needs_cli
        except Exception as e:
            logger.warning(
                f"[ROUTING] Intent classification failed: {e}, "
                f"falling back to keyword detection"
            )
            return self.command_parser.detect_cli_keywords(message)
    
    def _get_api_executor_for_classification(self) -> Optional[AIExecutor]:
        """获取用于意图分类的API执行器
        
        优先使用轻量级、快速的API（如OpenAI）
        
        Returns:
            Optional[AIExecutor]: API执行器，如果没有可用的返回None
        """
        # 优先级：openai > gemini > claude（OpenAI通常更快更便宜）
        preferred_providers = ["openai", "gemini", "claude"]
        
        for provider in preferred_providers:
            try:
                executor = self.executor_registry.get_executor(provider, "api")
                logger.debug(f"[ROUTING] Using {provider}/api for intent classification")
                return executor
            except ExecutorNotAvailableError:
                continue
        
        return None
    
    def _get_first_available_cli_provider(self) -> Optional[str]:
        """获取第一个可用的CLI提供商
        
        当DEFAULT_CLI_PROVIDER未设置时，自动检测可用的CLI执行器
        
        Returns:
            Optional[str]: 第一个可用的CLI提供商名称，如果没有可用的返回None
        """
        # 优先级：claude > gemini（Claude Code CLI更成熟）
        preferred_cli_providers = ["claude", "gemini"]
        
        for provider in preferred_cli_providers:
            try:
                executor = self.executor_registry.get_executor(provider, "cli")
                logger.info(f"[ROUTING] Auto-detected available CLI provider: {provider}")
                return provider
            except ExecutorNotAvailableError:
                continue
        
        logger.warning("[ROUTING] No CLI executor available for auto-detection")
        return None
    
    def _fallback(self, provider: str, original_layer: str) -> AIExecutor:
        """降级策略：尝试使用其他可用的执行器
        
        降级顺序：
        1. 同provider的另一层（api ↔ cli）
        2. 其他provider的同一层
        3. 其他provider的另一层
        
        Args:
            provider: 提供商名称
            original_layer: 原始执行层
            
        Returns:
            AIExecutor: 降级后的执行器
            
        Raises:
            ExecutorNotAvailableError: 如果降级失败（所有执行器都不可用）
        """
        # 策略1: 尝试同provider的另一层
        fallback_layer = "cli" if original_layer == "api" else "api"
        
        logger.info(
            f"[ROUTING] Fallback strategy 1: {provider}/{original_layer} -> {provider}/{fallback_layer}"
        )
        
        try:
            executor = self.get_executor(provider, fallback_layer)
            logger.warning(
                f"[ROUTING] ✅ Fallback successful: using {provider}/{fallback_layer}"
            )
            return executor
        except ExecutorNotAvailableError:
            logger.debug(f"[ROUTING] Strategy 1 failed: {provider}/{fallback_layer} not available")
        
        # 策略2: 尝试其他provider的同一层
        alternative_providers = ["claude", "gemini", "openai"]
        alternative_providers.remove(provider) if provider in alternative_providers else None
        
        for alt_provider in alternative_providers:
            logger.info(
                f"[ROUTING] Fallback strategy 2: {provider}/{original_layer} -> {alt_provider}/{original_layer}"
            )
            try:
                executor = self.get_executor(alt_provider, original_layer)
                logger.warning(
                    f"[ROUTING] ✅ Fallback successful: using {alt_provider}/{original_layer}"
                )
                return executor
            except ExecutorNotAvailableError:
                logger.debug(f"[ROUTING] Strategy 2 failed: {alt_provider}/{original_layer} not available")
        
        # 策略3: 尝试其他provider的另一层
        for alt_provider in alternative_providers:
            logger.info(
                f"[ROUTING] Fallback strategy 3: {provider}/{original_layer} -> {alt_provider}/{fallback_layer}"
            )
            try:
                executor = self.get_executor(alt_provider, fallback_layer)
                logger.warning(
                    f"[ROUTING] ✅ Fallback successful: using {alt_provider}/{fallback_layer}"
                )
                return executor
            except ExecutorNotAvailableError:
                logger.debug(f"[ROUTING] Strategy 3 failed: {alt_provider}/{fallback_layer} not available")
        
        # 所有降级策略都失败
        logger.error(
            f"[ROUTING] ❌ All fallback strategies failed. No executor available."
        )
        raise ExecutorNotAvailableError(
            provider,
            original_layer,
            f"No executor available. Tried: {provider}/{original_layer}, "
            f"{provider}/{fallback_layer}, and all alternative providers."
        )
