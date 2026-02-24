"""
SmartRouter 属性测试

使用 Hypothesis 进行基于属性的测试，验证智能路由器的通用正确性属性
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock
from feishu_bot.smart_router import SmartRouter
from feishu_bot.executor_registry import ExecutorRegistry, ExecutorNotAvailableError, AIExecutor
from feishu_bot.models import ParsedCommand, ExecutionResult


class MockExecutor(AIExecutor):
    """模拟执行器用于测试"""
    
    def __init__(self, provider: str, layer: str, available: bool = True):
        self.provider = provider
        self.layer = layer
        self._available = available
    
    def execute(self, user_prompt, conversation_history=None, additional_params=None):
        return ExecutionResult(
            success=True,
            stdout=f"Mock response from {self.provider}/{self.layer}",
            stderr="",
            error_message=None,
            execution_time=0.1
        )
    
    def is_available(self):
        return self._available
    
    def get_provider_name(self):
        return self.provider


class TestSmartRouterProperties:
    """SmartRouter 属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.registry = ExecutorRegistry()
        
        # 注册模拟执行器
        self.claude_api = MockExecutor("claude", "api", available=True)
        self.claude_cli = MockExecutor("claude", "cli", available=True)
        self.gemini_api = MockExecutor("gemini", "api", available=True)
        self.gemini_cli = MockExecutor("gemini", "cli", available=True)
        self.openai_api = MockExecutor("openai", "api", available=True)
        
        self.registry.register_api_executor("claude", self.claude_api)
        self.registry.register_cli_executor("claude", self.claude_cli)
        self.registry.register_api_executor("gemini", self.gemini_api)
        self.registry.register_cli_executor("gemini", self.gemini_cli)
        self.registry.register_api_executor("openai", self.openai_api)
        
        self.router = SmartRouter(
            executor_registry=self.registry,
            default_provider="claude",
            default_layer="api"
        )
    
    # Feature: feishu-ai-bot, Property 38: 智能路由显式指定优先
    # Validates: Requirements 13.1
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini", "openai"]),
        layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_explicit_specification_uses_specified_executor(self, provider, layer, message):
        """
        Property 38: 智能路由显式指定优先 - 使用指定的执行器
        
        For any explicitly specified AI provider and execution layer (explicit=true),
        Smart_Router should use the specified executor without intelligent judgment,
        ignoring CLI keyword detection.
        
        Validates: Requirements 13.1
        """
        # Skip if the combination is not registered
        if provider == "openai" and layer == "cli":
            # OpenAI CLI is not registered in our setup
            pytest.skip("OpenAI CLI not registered")
        
        # Create a parsed command with explicit=True
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=layer,
            message=message,
            explicit=True
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify the correct executor was selected
        assert executor.get_provider_name() == provider, \
            f"Expected provider '{provider}', got '{executor.get_provider_name()}'"
        assert executor.layer == layer, \
            f"Expected layer '{layer}', got '{executor.layer}'"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        cli_keyword=st.sampled_from([
            "查看代码", "view code", "修改文件", "modify file",
            "执行命令", "execute command", "分析项目", "analyze project"
        ]),
        prefix_text=st.text(min_size=0, max_size=50),
        suffix_text=st.text(min_size=0, max_size=50)
    )
    def test_explicit_api_ignores_cli_keywords(self, provider, cli_keyword, prefix_text, suffix_text):
        """
        Property 38: 智能路由显式指定优先 - 显式 API 忽略 CLI 关键词
        
        For any message with explicit API layer specification (explicit=true, layer="api"),
        even if the message contains CLI keywords, Smart_Router should use the API layer
        as explicitly specified, not route to CLI layer.
        
        Validates: Requirements 13.1
        """
        # Create a message containing CLI keywords
        message = f"{prefix_text}{cli_keyword}{suffix_text}"
        
        # Create a parsed command with explicit=True and layer="api"
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer="api",
            message=message,
            explicit=True
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify API layer was used despite CLI keywords
        assert executor.layer == "api", \
            f"Expected API layer for explicit specification, got '{executor.layer}' " \
            f"even though message contains CLI keyword '{cli_keyword}'"
        assert executor.get_provider_name() == provider
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(
                keyword.lower() in x.lower()
                for keyword in [
                    "查看代码", "view code", "修改文件", "modify file",
                    "执行命令", "execute command", "分析项目", "analyze project",
                    "代码库", "codebase", "项目结构", "project structure"
                ]
            )
        )
    )
    def test_explicit_cli_without_keywords(self, provider, message):
        """
        Property 38: 智能路由显式指定优先 - 显式 CLI 无需关键词
        
        For any message with explicit CLI layer specification (explicit=true, layer="cli"),
        even if the message does NOT contain CLI keywords, Smart_Router should use the CLI layer
        as explicitly specified.
        
        Validates: Requirements 13.1
        """
        # Create a parsed command with explicit=True and layer="cli"
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer="cli",
            message=message,
            explicit=True
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify CLI layer was used despite no CLI keywords
        assert executor.layer == "cli", \
            f"Expected CLI layer for explicit specification, got '{executor.layer}' " \
            f"even though message does not contain CLI keywords"
        assert executor.get_provider_name() == provider
    
    @settings(max_examples=100)
    @given(
        explicit_provider=st.sampled_from(["claude", "gemini", "openai"]),
        explicit_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_explicit_overrides_default_provider(self, explicit_provider, explicit_layer, message):
        """
        Property 38: 智能路由显式指定优先 - 显式指定覆盖默认提供商
        
        For any explicitly specified provider (explicit=true),
        Smart_Router should use the specified provider, not the default provider,
        even if the default provider is different.
        
        Validates: Requirements 13.1
        """
        # Skip if the combination is not registered
        if explicit_provider == "openai" and explicit_layer == "cli":
            pytest.skip("OpenAI CLI not registered")
        
        # Router has default_provider="claude"
        # Create a parsed command with explicit=True and different provider
        parsed_command = ParsedCommand(
            provider=explicit_provider,
            execution_layer=explicit_layer,
            message=message,
            explicit=True
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify the explicitly specified provider was used, not the default
        assert executor.get_provider_name() == explicit_provider, \
            f"Expected explicitly specified provider '{explicit_provider}', " \
            f"got '{executor.get_provider_name()}' (default is 'claude')"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_explicit_specification_consistency(self, provider, layer, message):
        """
        Property 38: 智能路由显式指定优先 - 显式指定一致性
        
        For any explicitly specified command (explicit=true),
        multiple calls to route() with the same ParsedCommand should always
        return an executor with the same provider and layer.
        
        Validates: Requirements 13.1
        """
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=layer,
            message=message,
            explicit=True
        )
        
        # Route the command multiple times
        executor1 = self.router.route(parsed_command)
        executor2 = self.router.route(parsed_command)
        executor3 = self.router.route(parsed_command)
        
        # Verify consistency
        assert executor1.get_provider_name() == executor2.get_provider_name() == executor3.get_provider_name() == provider
        assert executor1.layer == executor2.layer == executor3.layer == layer
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_explicit_vs_implicit_different_results(self, provider, message):
        """
        Property 38: 智能路由显式指定优先 - 显式与隐式结果可能不同
        
        For any message, when explicit=true with layer="cli", the router should use CLI layer.
        When explicit=false with the same message (no CLI keywords), the router should use
        the default layer (API), demonstrating that explicit specification takes priority
        over intelligent judgment.
        
        Validates: Requirements 13.1
        """
        # Ensure message has no CLI keywords for this test
        if any(keyword.lower() in message.lower() for keyword in [
            "查看代码", "view code", "修改文件", "modify file",
            "执行命令", "execute command", "分析项目", "analyze project",
            "代码库", "codebase", "项目结构", "project structure"
        ]):
            # Skip messages with CLI keywords as they would route to CLI anyway
            return
        
        # Explicit CLI specification
        explicit_command = ParsedCommand(
            provider=provider,
            execution_layer="cli",
            message=message,
            explicit=True
        )
        explicit_executor = self.router.route(explicit_command)
        
        # Implicit routing (no explicit specification)
        implicit_command = ParsedCommand(
            provider=self.router.default_provider,  # Will use default
            execution_layer=self.router.default_layer,  # Will use default
            message=message,
            explicit=False
        )
        implicit_executor = self.router.route(implicit_command)
        
        # Explicit should use CLI, implicit should use default (API)
        assert explicit_executor.layer == "cli", \
            "Explicit CLI specification should use CLI layer"
        assert implicit_executor.layer == "api", \
            "Implicit routing without CLI keywords should use default API layer"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini", "openai"]),
        layer=st.sampled_from(["api", "cli"]),
        message_parts=st.lists(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            min_size=1,
            max_size=5
        )
    )
    def test_explicit_specification_with_complex_messages(self, provider, layer, message_parts):
        """
        Property 38: 智能路由显式指定优先 - 复杂消息的显式指定
        
        For any complex message (multiple parts, special characters, etc.),
        when explicitly specified (explicit=true), Smart_Router should use
        the specified executor regardless of message content complexity.
        
        Validates: Requirements 13.1
        """
        # Skip if the combination is not registered
        if provider == "openai" and layer == "cli":
            pytest.skip("OpenAI CLI not registered")
        
        # Create a complex message
        message = " ".join(message_parts)
        
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=layer,
            message=message,
            explicit=True
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify the specified executor was used
        assert executor.get_provider_name() == provider
        assert executor.layer == layer
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_explicit_specification_returns_working_executor(self, provider, layer, message):
        """
        Property 38: 智能路由显式指定优先 - 返回可工作的执行器
        
        For any explicitly specified command (explicit=true),
        the returned executor should be functional and able to execute commands.
        
        Validates: Requirements 13.1
        """
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=layer,
            message=message,
            explicit=True
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify the executor is functional
        assert executor.is_available(), \
            f"Executor {provider}/{layer} should be available"
        
        # Verify the executor can execute
        result = executor.execute(message)
        assert result is not None, \
            "Executor should return a result"
        assert isinstance(result, ExecutionResult), \
            "Executor should return an ExecutionResult"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_explicit_specification_both_layers_work(self, provider, message):
        """
        Property 38: 智能路由显式指定优先 - 两层都可显式指定
        
        For any provider that supports both API and CLI layers,
        explicit specification should work for both layers independently.
        
        Validates: Requirements 13.1
        """
        # Test API layer
        api_command = ParsedCommand(
            provider=provider,
            execution_layer="api",
            message=message,
            explicit=True
        )
        api_executor = self.router.route(api_command)
        assert api_executor.layer == "api"
        assert api_executor.get_provider_name() == provider
        
        # Test CLI layer
        cli_command = ParsedCommand(
            provider=provider,
            execution_layer="cli",
            message=message,
            explicit=True
        )
        cli_executor = self.router.route(cli_command)
        assert cli_executor.layer == "cli"
        assert cli_executor.get_provider_name() == provider
        
        # Verify they are different executors
        assert api_executor.layer != cli_executor.layer, \
            "API and CLI executors should be different"
    
    # Feature: feishu-ai-bot, Property 39: 智能路由降级策略
    # Validates: Requirements 13.4, 13.5, 13.6
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        original_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_when_executor_unavailable(self, provider, original_layer, message):
        """
        Property 39: 智能路由降级策略 - 执行器不可用时降级
        
        For any specified executor that is not available,
        Smart_Router should attempt to fallback to another layer (API→CLI or CLI→API).
        The fallback executor should be from the same provider but different layer.
        
        Validates: Requirements 13.4
        """
        # Create a new registry with one layer unavailable
        registry = ExecutorRegistry()
        
        # Determine which layer should be available and which unavailable
        fallback_layer = "cli" if original_layer == "api" else "api"
        
        # Register only the fallback layer as available
        if fallback_layer == "api":
            available_executor = MockExecutor(provider, "api", available=True)
            registry.register_api_executor(provider, available_executor)
        else:
            available_executor = MockExecutor(provider, "cli", available=True)
            registry.register_cli_executor(provider, available_executor)
        
        # Create router with this registry
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer=original_layer
        )
        
        # Create a parsed command requesting the unavailable layer
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=original_layer,
            message=message,
            explicit=True
        )
        
        # Route should fallback to the available layer
        executor = router.route(parsed_command)
        
        # Verify fallback occurred
        assert executor.layer == fallback_layer, \
            f"Expected fallback to {fallback_layer} layer when {original_layer} unavailable, " \
            f"got {executor.layer}"
        assert executor.get_provider_name() == provider, \
            f"Expected same provider {provider} after fallback, got {executor.get_provider_name()}"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        original_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_raises_error_when_all_unavailable(self, provider, original_layer, message):
        """
        Property 39: 智能路由降级策略 - 所有执行器不可用时抛出错误
        
        For any provider, when both API and CLI layers are unavailable,
        Smart_Router should raise ExecutorNotAvailableError indicating
        that no executor is available.
        
        Validates: Requirements 13.5
        """
        # Create a new registry with no executors registered
        registry = ExecutorRegistry()
        
        # Create router with empty registry
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer=original_layer
        )
        
        # Create a parsed command
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=original_layer,
            message=message,
            explicit=True
        )
        
        # Route should raise ExecutorNotAvailableError
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            router.route(parsed_command)
        
        # Verify error details
        error = exc_info.value
        assert error.provider == provider, \
            f"Error should indicate provider {provider}, got {error.provider}"
        assert error.layer == original_layer, \
            f"Error should indicate original layer {original_layer}, got {error.layer}"
        assert "unavailable" in error.reason.lower(), \
            f"Error reason should mention unavailability, got: {error.reason}"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        original_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_preserves_provider(self, provider, original_layer, message):
        """
        Property 39: 智能路由降级策略 - 降级保持提供商不变
        
        For any fallback scenario, the fallback executor should be from
        the same provider as originally requested, only the layer should change.
        
        Validates: Requirements 13.4
        """
        # Create a new registry with one layer unavailable
        registry = ExecutorRegistry()
        
        # Determine fallback layer
        fallback_layer = "cli" if original_layer == "api" else "api"
        
        # Register only the fallback layer
        if fallback_layer == "api":
            available_executor = MockExecutor(provider, "api", available=True)
            registry.register_api_executor(provider, available_executor)
        else:
            available_executor = MockExecutor(provider, "cli", available=True)
            registry.register_cli_executor(provider, available_executor)
        
        # Create router
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer=original_layer
        )
        
        # Create parsed command
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=original_layer,
            message=message,
            explicit=True
        )
        
        # Route with fallback
        executor = router.route(parsed_command)
        
        # Verify provider is preserved
        assert executor.get_provider_name() == provider, \
            f"Fallback should preserve provider {provider}, got {executor.get_provider_name()}"
        
        # Verify layer changed
        assert executor.layer != original_layer, \
            f"Fallback should change layer from {original_layer}, but got same layer"
        assert executor.layer == fallback_layer, \
            f"Fallback should use {fallback_layer} layer, got {executor.layer}"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_api_to_cli(self, provider, message):
        """
        Property 39: 智能路由降级策略 - API 层降级到 CLI 层
        
        For any provider, when API layer is unavailable but CLI layer is available,
        Smart_Router should fallback from API to CLI.
        
        Validates: Requirements 13.4
        """
        # Create registry with only CLI available
        registry = ExecutorRegistry()
        cli_executor = MockExecutor(provider, "cli", available=True)
        registry.register_cli_executor(provider, cli_executor)
        
        # Create router
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer="api"
        )
        
        # Request API layer (unavailable)
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer="api",
            message=message,
            explicit=True
        )
        
        # Should fallback to CLI
        executor = router.route(parsed_command)
        
        assert executor.layer == "cli", \
            f"Should fallback from API to CLI, got {executor.layer}"
        assert executor.get_provider_name() == provider
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_cli_to_api(self, provider, message):
        """
        Property 39: 智能路由降级策略 - CLI 层降级到 API 层
        
        For any provider, when CLI layer is unavailable but API layer is available,
        Smart_Router should fallback from CLI to API.
        
        Validates: Requirements 13.4
        """
        # Create registry with only API available
        registry = ExecutorRegistry()
        api_executor = MockExecutor(provider, "api", available=True)
        registry.register_api_executor(provider, api_executor)
        
        # Create router
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer="cli"
        )
        
        # Request CLI layer (unavailable)
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer="cli",
            message=message,
            explicit=True
        )
        
        # Should fallback to API
        executor = router.route(parsed_command)
        
        assert executor.layer == "api", \
            f"Should fallback from CLI to API, got {executor.layer}"
        assert executor.get_provider_name() == provider
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        original_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_returns_functional_executor(self, provider, original_layer, message):
        """
        Property 39: 智能路由降级策略 - 降级返回可用执行器
        
        For any fallback scenario, the returned executor should be functional
        and able to execute commands successfully.
        
        Validates: Requirements 13.4
        """
        # Create registry with fallback layer available
        registry = ExecutorRegistry()
        fallback_layer = "cli" if original_layer == "api" else "api"
        
        if fallback_layer == "api":
            executor = MockExecutor(provider, "api", available=True)
            registry.register_api_executor(provider, executor)
        else:
            executor = MockExecutor(provider, "cli", available=True)
            registry.register_cli_executor(provider, executor)
        
        # Create router
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer=original_layer
        )
        
        # Request unavailable layer
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=original_layer,
            message=message,
            explicit=True
        )
        
        # Get fallback executor
        fallback_executor = router.route(parsed_command)
        
        # Verify executor is functional
        assert fallback_executor.is_available(), \
            "Fallback executor should be available"
        
        # Verify executor can execute
        result = fallback_executor.execute(message)
        assert result is not None
        assert isinstance(result, ExecutionResult)
        assert result.success, \
            "Fallback executor should execute successfully"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        original_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_fallback_consistency(self, provider, original_layer, message):
        """
        Property 39: 智能路由降级策略 - 降级一致性
        
        For any fallback scenario, multiple calls with the same unavailable executor
        should consistently fallback to the same alternative executor.
        
        Validates: Requirements 13.4
        """
        # Create registry with fallback layer available
        registry = ExecutorRegistry()
        fallback_layer = "cli" if original_layer == "api" else "api"
        
        if fallback_layer == "api":
            executor = MockExecutor(provider, "api", available=True)
            registry.register_api_executor(provider, executor)
        else:
            executor = MockExecutor(provider, "cli", available=True)
            registry.register_cli_executor(provider, executor)
        
        # Create router
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer=original_layer
        )
        
        # Request unavailable layer multiple times
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=original_layer,
            message=message,
            explicit=True
        )
        
        executor1 = router.route(parsed_command)
        executor2 = router.route(parsed_command)
        executor3 = router.route(parsed_command)
        
        # Verify consistency
        assert executor1.layer == executor2.layer == executor3.layer == fallback_layer, \
            "Fallback should consistently use the same layer"
        assert executor1.get_provider_name() == executor2.get_provider_name() == executor3.get_provider_name() == provider, \
            "Fallback should consistently use the same provider"
    
    @settings(max_examples=100)
    @given(
        provider=st.sampled_from(["claude", "gemini"]),
        original_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip())
    )
    def test_no_fallback_when_original_available(self, provider, original_layer, message):
        """
        Property 39: 智能路由降级策略 - 原执行器可用时不降级
        
        For any executor that is available, Smart_Router should use it directly
        without attempting fallback, even if a fallback executor is also available.
        
        Validates: Requirements 13.4
        """
        # Create registry with both layers available
        registry = ExecutorRegistry()
        
        api_executor = MockExecutor(provider, "api", available=True)
        cli_executor = MockExecutor(provider, "cli", available=True)
        
        registry.register_api_executor(provider, api_executor)
        registry.register_cli_executor(provider, cli_executor)
        
        # Create router
        router = SmartRouter(
            executor_registry=registry,
            default_provider=provider,
            default_layer=original_layer
        )
        
        # Request original layer (available)
        parsed_command = ParsedCommand(
            provider=provider,
            execution_layer=original_layer,
            message=message,
            explicit=True
        )
        
        # Should use original layer, not fallback
        executor = router.route(parsed_command)
        
        assert executor.layer == original_layer, \
            f"Should use original layer {original_layer} when available, " \
            f"not fallback to {executor.layer}"
        assert executor.get_provider_name() == provider
    
    # Feature: feishu-ai-bot, Property 46: 路由层选择一致性
    # Validates: Requirements 13.2, 13.3
    
    @settings(max_examples=100)
    @given(
        cli_keyword=st.sampled_from([
            "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
            "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
            "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
            "分析项目", "analyze project", "项目结构", "project structure"
        ]),
        prefix_text=st.text(min_size=0, max_size=50),
        suffix_text=st.text(min_size=0, max_size=50)
    )
    def test_implicit_routing_with_cli_keywords_uses_cli_layer(self, cli_keyword, prefix_text, suffix_text):
        """
        Property 46: 路由层选择一致性 - CLI 关键词路由到 CLI 层
        
        For any message without explicit specification (explicit=false) that contains
        CLI keywords, Smart_Router should route to CLI layer, regardless of the
        default layer setting.
        
        Validates: Requirements 13.2
        """
        # Create a message containing CLI keywords
        message = f"{prefix_text}{cli_keyword}{suffix_text}"
        
        # Create a parsed command with explicit=False (implicit routing)
        parsed_command = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify CLI layer was selected due to CLI keywords
        assert executor.layer == "cli", \
            f"Expected CLI layer for message with CLI keyword '{cli_keyword}', " \
            f"got '{executor.layer}'"
        assert executor.get_provider_name() == self.router.default_provider, \
            f"Expected default provider '{self.router.default_provider}', " \
            f"got '{executor.get_provider_name()}'"
    
    @settings(max_examples=100)
    @given(
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(
                keyword.lower() in x.lower()
                for keyword in [
                    "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
                    "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
                    "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
                    "分析项目", "analyze project", "项目结构", "project structure"
                ]
            )
        )
    )
    def test_implicit_routing_without_cli_keywords_uses_default_layer(self, message):
        """
        Property 46: 路由层选择一致性 - 无 CLI 关键词路由到默认层
        
        For any message without explicit specification (explicit=false) that does NOT
        contain CLI keywords, Smart_Router should route to the default layer (API layer).
        
        Validates: Requirements 13.3
        """
        # Create a parsed command with explicit=False (implicit routing)
        parsed_command = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify default layer (API) was selected
        assert executor.layer == self.router.default_layer, \
            f"Expected default layer '{self.router.default_layer}' for message without CLI keywords, " \
            f"got '{executor.layer}'"
        assert executor.get_provider_name() == self.router.default_provider, \
            f"Expected default provider '{self.router.default_provider}', " \
            f"got '{executor.get_provider_name()}'"
    
    @settings(max_examples=100)
    @given(
        cli_keyword=st.sampled_from([
            "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
            "修改文件", "modify file", "读取文件", "read file"
        ]),
        prefix_text=st.text(min_size=0, max_size=30),
        suffix_text=st.text(min_size=0, max_size=30)
    )
    def test_implicit_routing_consistency_with_cli_keywords(self, cli_keyword, prefix_text, suffix_text):
        """
        Property 46: 路由层选择一致性 - CLI 关键词路由一致性
        
        For any message with CLI keywords, multiple calls to route() should
        consistently select the CLI layer.
        
        Validates: Requirements 13.2
        """
        # Create a message containing CLI keywords
        message = f"{prefix_text}{cli_keyword}{suffix_text}"
        
        # Create a parsed command with explicit=False
        parsed_command = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command multiple times
        executor1 = self.router.route(parsed_command)
        executor2 = self.router.route(parsed_command)
        executor3 = self.router.route(parsed_command)
        
        # Verify consistency - all should select CLI layer
        assert executor1.layer == executor2.layer == executor3.layer == "cli", \
            f"Routing should consistently select CLI layer for messages with CLI keywords"
        assert executor1.get_provider_name() == executor2.get_provider_name() == executor3.get_provider_name()
    
    @settings(max_examples=100)
    @given(
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(
                keyword.lower() in x.lower()
                for keyword in [
                    "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
                    "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
                    "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
                    "分析项目", "analyze project", "项目结构", "project structure"
                ]
            )
        )
    )
    def test_implicit_routing_consistency_without_cli_keywords(self, message):
        """
        Property 46: 路由层选择一致性 - 无 CLI 关键词路由一致性
        
        For any message without CLI keywords, multiple calls to route() should
        consistently select the default layer (API).
        
        Validates: Requirements 13.3
        """
        # Create a parsed command with explicit=False
        parsed_command = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command multiple times
        executor1 = self.router.route(parsed_command)
        executor2 = self.router.route(parsed_command)
        executor3 = self.router.route(parsed_command)
        
        # Verify consistency - all should select default layer (API)
        assert executor1.layer == executor2.layer == executor3.layer == self.router.default_layer, \
            f"Routing should consistently select default layer for messages without CLI keywords"
        assert executor1.get_provider_name() == executor2.get_provider_name() == executor3.get_provider_name()
    
    @settings(max_examples=100)
    @given(
        cli_keyword=st.sampled_from([
            "查看代码", "view code", "修改文件", "modify file", "执行命令", "execute command"
        ]),
        non_cli_text=st.text(min_size=1, max_size=100).filter(
            lambda x: x.strip() and not any(
                keyword.lower() in x.lower()
                for keyword in [
                    "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
                    "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
                    "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
                    "分析项目", "analyze project", "项目结构", "project structure"
                ]
            )
        )
    )
    def test_implicit_routing_layer_selection_differs_by_keywords(self, cli_keyword, non_cli_text):
        """
        Property 46: 路由层选择一致性 - 关键词决定层选择
        
        For any two messages, one with CLI keywords and one without,
        the router should select different layers: CLI for the message with keywords,
        and default (API) for the message without keywords.
        
        Validates: Requirements 13.2, 13.3
        """
        # Message with CLI keywords
        message_with_cli = f"请帮我{cli_keyword}"
        parsed_with_cli = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message_with_cli,
            explicit=False
        )
        
        # Message without CLI keywords
        message_without_cli = non_cli_text
        parsed_without_cli = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message_without_cli,
            explicit=False
        )
        
        # Route both commands
        executor_with_cli = self.router.route(parsed_with_cli)
        executor_without_cli = self.router.route(parsed_without_cli)
        
        # Verify different layers are selected
        assert executor_with_cli.layer == "cli", \
            f"Message with CLI keyword '{cli_keyword}' should route to CLI layer"
        assert executor_without_cli.layer == self.router.default_layer, \
            f"Message without CLI keywords should route to default layer"
        assert executor_with_cli.layer != executor_without_cli.layer, \
            "Messages with and without CLI keywords should route to different layers"
    
    @settings(max_examples=100)
    @given(
        cli_keyword=st.sampled_from([
            "查看代码", "VIEW CODE", "修改文件", "MODIFY FILE", "执行命令", "EXECUTE COMMAND"
        ]),
        prefix_text=st.text(min_size=0, max_size=30),
        suffix_text=st.text(min_size=0, max_size=30)
    )
    def test_implicit_routing_case_insensitive_cli_detection(self, cli_keyword, prefix_text, suffix_text):
        """
        Property 46: 路由层选择一致性 - CLI 关键词大小写不敏感
        
        For any message with CLI keywords in any case (uppercase, lowercase, mixed),
        Smart_Router should detect the keywords and route to CLI layer.
        
        Validates: Requirements 13.2
        """
        # Create a message with CLI keyword in various cases
        message = f"{prefix_text}{cli_keyword}{suffix_text}"
        
        # Create a parsed command with explicit=False
        parsed_command = ParsedCommand(
            provider=self.router.default_provider,
            execution_layer=self.router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command
        executor = self.router.route(parsed_command)
        
        # Verify CLI layer was selected regardless of case
        assert executor.layer == "cli", \
            f"Expected CLI layer for message with CLI keyword '{cli_keyword}' (case-insensitive), " \
            f"got '{executor.layer}'"
    
    @settings(max_examples=100)
    @given(
        default_layer=st.sampled_from(["api", "cli"]),
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(
                keyword.lower() in x.lower()
                for keyword in [
                    "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
                    "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
                    "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
                    "分析项目", "analyze project", "项目结构", "project structure"
                ]
            )
        )
    )
    def test_implicit_routing_respects_default_layer_without_keywords(self, default_layer, message):
        """
        Property 46: 路由层选择一致性 - 无关键词时遵循默认层配置
        
        For any message without CLI keywords, Smart_Router should respect
        the configured default layer setting.
        
        Validates: Requirements 13.3
        """
        # Create a router with specific default layer
        router = SmartRouter(
            executor_registry=self.registry,
            default_provider="claude",
            default_layer=default_layer
        )
        
        # Create a parsed command with explicit=False
        parsed_command = ParsedCommand(
            provider=router.default_provider,
            execution_layer=router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command
        executor = router.route(parsed_command)
        
        # Verify the configured default layer was used
        assert executor.layer == default_layer, \
            f"Expected configured default layer '{default_layer}' for message without CLI keywords, " \
            f"got '{executor.layer}'"
    
    @settings(max_examples=100)
    @given(
        cli_keyword=st.sampled_from([
            "查看代码", "view code", "修改文件", "modify file"
        ]),
        default_layer=st.sampled_from(["api", "cli"])
    )
    def test_implicit_routing_cli_keywords_override_default_layer(self, cli_keyword, default_layer):
        """
        Property 46: 路由层选择一致性 - CLI 关键词覆盖默认层
        
        For any message with CLI keywords, Smart_Router should route to CLI layer
        regardless of the default layer configuration (even if default is API).
        
        Validates: Requirements 13.2
        """
        # Create a router with specific default layer
        router = SmartRouter(
            executor_registry=self.registry,
            default_provider="claude",
            default_layer=default_layer
        )
        
        # Create a message with CLI keywords
        message = f"请帮我{cli_keyword}"
        
        # Create a parsed command with explicit=False
        parsed_command = ParsedCommand(
            provider=router.default_provider,
            execution_layer=router.default_layer,
            message=message,
            explicit=False
        )
        
        # Route the command
        executor = router.route(parsed_command)
        
        # Verify CLI layer was selected, overriding default layer
        assert executor.layer == "cli", \
            f"Expected CLI layer for message with CLI keyword '{cli_keyword}', " \
            f"got '{executor.layer}' (default layer was '{default_layer}')"
