"""
智能路由器模块

根据解析的命令和消息内容，决定使用哪个 AI 执行器
"""
import logging
from typing import Optional

from .models import ParsedCommand
from .executor_registry import ExecutorRegistry, ExecutorNotAvailableError, AIExecutor
from .command_parser import CommandParser

logger = logging.getLogger(__name__)


class SmartRouter:
    """智能路由器
    
    根据用户指令和消息内容智能选择 API 层或 CLI 层
    
    路由策略：
    1. 显式指定优先：如果用户使用了命令前缀，直接使用指定的提供商和层
    2. 智能判断：检测 CLI 关键词，如果包含则使用 CLI 层，否则使用默认层
    3. 降级策略：如果指定的执行器不可用，尝试降级到其他层
    """
    
    def __init__(
        self,
        executor_registry: ExecutorRegistry,
        default_provider: str = "claude",
        default_layer: str = "api"
    ):
        """初始化智能路由器
        
        Args:
            executor_registry: 执行器注册表
            default_provider: 默认 AI 提供商
            default_layer: 默认执行层（api 或 cli）
        """
        self.executor_registry = executor_registry
        self.default_provider = default_provider
        self.default_layer = default_layer
        self.command_parser = CommandParser()
        
        logger.info(
            f"SmartRouter initialized with default provider={default_provider}, "
            f"default layer={default_layer}"
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
        
        # 如果用户显式指定，直接使用指定的执行器
        if parsed_command.explicit:
            logger.info(
                f"User explicitly specified: provider={provider}, layer={layer}"
            )
            try:
                return self.get_executor(provider, layer)
            except ExecutorNotAvailableError as e:
                # 显式指定的执行器不可用，尝试降级
                logger.warning(
                    f"Explicitly specified executor {provider}/{layer} not available: {e.reason}"
                )
                return self._fallback(provider, layer)
        
        # 智能判断：检测是否需要 CLI 层
        if self.command_parser.detect_cli_keywords(parsed_command.message):
            layer = "cli"
            logger.info(
                f"CLI keywords detected in message, routing to CLI layer"
            )
        else:
            layer = self.default_layer
            logger.debug(
                f"No CLI keywords detected, using default layer: {layer}"
            )
        
        # 使用默认提供商（如果没有显式指定）
        provider = self.default_provider
        
        # 获取执行器，如果不可用则降级
        try:
            return self.get_executor(provider, layer)
        except ExecutorNotAvailableError as e:
            logger.warning(
                f"Executor {provider}/{layer} not available: {e.reason}, attempting fallback"
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
    
    def _fallback(self, provider: str, original_layer: str) -> AIExecutor:
        """降级策略：尝试使用另一层的执行器
        
        Args:
            provider: 提供商名称
            original_layer: 原始执行层
            
        Returns:
            AIExecutor: 降级后的执行器
            
        Raises:
            ExecutorNotAvailableError: 如果降级失败（所有执行器都不可用）
        """
        # 确定降级目标层
        fallback_layer = "cli" if original_layer == "api" else "api"
        
        logger.info(
            f"Attempting fallback: {provider}/{original_layer} -> {provider}/{fallback_layer}"
        )
        
        try:
            executor = self.get_executor(provider, fallback_layer)
            logger.warning(
                f"Fallback successful: using {provider}/{fallback_layer} "
                f"instead of {provider}/{original_layer}"
            )
            return executor
        except ExecutorNotAvailableError as e:
            # 降级失败，所有执行器都不可用
            logger.error(
                f"Fallback failed: {provider}/{fallback_layer} also not available: {e.reason}"
            )
            raise ExecutorNotAvailableError(
                provider,
                original_layer,
                f"Both {original_layer} and {fallback_layer} layers are unavailable. "
                f"Original: {e.reason}"
            )
