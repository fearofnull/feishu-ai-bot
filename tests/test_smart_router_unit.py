"""
SmartRouter 单元测试

测试智能路由器的具体场景和边界情况
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
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


class TestSmartRouterExplicitRouting:
    """测试显式指定路由"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.registry = ExecutorRegistry()
        
        # 注册所有执行器
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
    
    def test_explicit_claude_api(self):
        """测试显式指定 Claude API"""
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello, Claude!",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        assert executor.get_provider_name() == "claude"
        assert executor.layer == "api"
        assert executor is self.claude_api
    
    def test_explicit_claude_cli(self):
        """测试显式指定 Claude CLI"""
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="cli",
            message="查看代码",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        assert executor.get_provider_name() == "claude"
        assert executor.layer == "cli"
        assert executor is self.claude_cli
    
    def test_explicit_gemini_api(self):
        """测试显式指定 Gemini API"""
        parsed_command = ParsedCommand(
            provider="gemini",
            execution_layer="api",
            message="Hello, Gemini!",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        assert executor.get_provider_name() == "gemini"
        assert executor.layer == "api"
        assert executor is self.gemini_api
    
    def test_explicit_gemini_cli(self):
        """测试显式指定 Gemini CLI"""
        parsed_command = ParsedCommand(
            provider="gemini",
            execution_layer="cli",
            message="分析项目",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        assert executor.get_provider_name() == "gemini"
        assert executor.layer == "cli"
        assert executor is self.gemini_cli
    
    def test_explicit_openai_api(self):
        """测试显式指定 OpenAI API"""
        parsed_command = ParsedCommand(
            provider="openai",
            execution_layer="api",
            message="Hello, GPT!",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        assert executor.get_provider_name() == "openai"
        assert executor.layer == "api"
        assert executor is self.openai_api
    
    def test_explicit_api_ignores_cli_keywords(self):
        """测试显式指定 API 时忽略 CLI 关键词"""
        # 消息包含 CLI 关键词，但显式指定 API
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="请帮我查看代码",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        # 应该使用 API 层，而不是 CLI 层
        assert executor.layer == "api"
        assert executor is self.claude_api
    
    def test_explicit_cli_without_keywords(self):
        """测试显式指定 CLI 时无需 CLI 关键词"""
        # 消息不包含 CLI 关键词，但显式指定 CLI
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="cli",
            message="Hello, how are you?",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        # 应该使用 CLI 层
        assert executor.layer == "cli"
        assert executor is self.claude_cli
    
    def test_explicit_overrides_default_provider(self):
        """测试显式指定覆盖默认提供商"""
        # 默认提供商是 claude，但显式指定 gemini
        parsed_command = ParsedCommand(
            provider="gemini",
            execution_layer="api",
            message="Hello!",
            explicit=True
        )
        
        executor = self.router.route(parsed_command)
        
        assert executor.get_provider_name() == "gemini"
        assert executor is self.gemini_api


class TestSmartRouterIntelligentRouting:
    """测试智能判断路由"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.registry = ExecutorRegistry()
        
        # 注册执行器
        self.claude_api = MockExecutor("claude", "api", available=True)
        self.claude_cli = MockExecutor("claude", "cli", available=True)
        
        self.registry.register_api_executor("claude", self.claude_api)
        self.registry.register_cli_executor("claude", self.claude_cli)
        
        self.router = SmartRouter(
            executor_registry=self.registry,
            default_provider="claude",
            default_layer="api"
        )
    
    def test_implicit_routing_with_cli_keywords_chinese(self):
        """测试隐式路由检测中文 CLI 关键词"""
        cli_keywords = [
            "查看代码", "分析代码", "修改文件", "读取文件",
            "执行命令", "运行脚本", "分析项目", "代码库"
        ]
        
        for keyword in cli_keywords:
            parsed_command = ParsedCommand(
                provider="claude",
                execution_layer="api",
                message=f"请帮我{keyword}",
                explicit=False
            )
            
            executor = self.router.route(parsed_command)
            
            assert executor.layer == "cli", \
                f"Message with CLI keyword '{keyword}' should route to CLI layer"
            assert executor is self.claude_cli
    
    def test_implicit_routing_with_cli_keywords_english(self):
        """测试隐式路由检测英文 CLI 关键词"""
        cli_keywords = [
            "view code", "analyze code", "modify file", "read file",
            "execute command", "run script", "analyze project", "codebase"
        ]
        
        for keyword in cli_keywords:
            parsed_command = ParsedCommand(
                provider="claude",
                execution_layer="api",
                message=f"Please help me {keyword}",
                explicit=False
            )
            
            executor = self.router.route(parsed_command)
            
            assert executor.layer == "cli", \
                f"Message with CLI keyword '{keyword}' should route to CLI layer"
            assert executor is self.claude_cli
    
    def test_implicit_routing_without_cli_keywords(self):
        """测试隐式路由无 CLI 关键词时使用默认层"""
        messages = [
            "Hello, how are you?",
            "What is the weather today?",
            "Explain quantum physics",
            "翻译这段文字",
            "写一首诗"
        ]
        
        for message in messages:
            parsed_command = ParsedCommand(
                provider="claude",
                execution_layer="api",
                message=message,
                explicit=False
            )
            
            executor = self.router.route(parsed_command)
            
            assert executor.layer == "api", \
                f"Message without CLI keywords should route to default API layer"
            assert executor is self.claude_api
    
    def test_implicit_routing_uses_default_provider(self):
        """测试隐式路由使用默认提供商"""
        parsed_command = ParsedCommand(
            provider="claude",  # 这个值在隐式路由时会被忽略
            execution_layer="api",
            message="Hello!",
            explicit=False
        )
        
        executor = self.router.route(parsed_command)
        
        # 应该使用默认提供商 claude
        assert executor.get_provider_name() == "claude"
        assert executor is self.claude_api
    
    def test_implicit_routing_cli_keywords_case_insensitive(self):
        """测试 CLI 关键词检测大小写不敏感"""
        messages = [
            "VIEW CODE",
            "View Code",
            "view code",
            "查看代码",
            "MODIFY FILE",
            "Modify File"
        ]
        
        for message in messages:
            parsed_command = ParsedCommand(
                provider="claude",
                execution_layer="api",
                message=message,
                explicit=False
            )
            
            executor = self.router.route(parsed_command)
            
            assert executor.layer == "cli", \
                f"CLI keyword detection should be case-insensitive for '{message}'"
    
    def test_implicit_routing_partial_keyword_match(self):
        """测试 CLI 关键词部分匹配"""
        messages = [
            "我想查看代码库的结构",
            "Can you help me view code in this file?",
            "需要修改文件内容",
            "Please analyze project structure"
        ]
        
        for message in messages:
            parsed_command = ParsedCommand(
                provider="claude",
                execution_layer="api",
                message=message,
                explicit=False
            )
            
            executor = self.router.route(parsed_command)
            
            assert executor.layer == "cli", \
                f"Message containing CLI keywords should route to CLI layer: '{message}'"


class TestSmartRouterFallbackStrategy:
    """测试降级策略"""
    
    def test_fallback_api_to_cli_when_api_unavailable(self):
        """测试 API 不可用时降级到 CLI"""
        registry = ExecutorRegistry()
        
        # 只注册 CLI 执行器
        cli_executor = MockExecutor("claude", "cli", available=True)
        registry.register_cli_executor("claude", cli_executor)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 显式请求 API（不可用）
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello!",
            explicit=True
        )
        
        # 应该降级到 CLI
        executor = router.route(parsed_command)
        
        assert executor.layer == "cli"
        assert executor is cli_executor
    
    def test_fallback_cli_to_api_when_cli_unavailable(self):
        """测试 CLI 不可用时降级到 API"""
        registry = ExecutorRegistry()
        
        # 只注册 API 执行器
        api_executor = MockExecutor("claude", "api", available=True)
        registry.register_api_executor("claude", api_executor)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="cli"
        )
        
        # 显式请求 CLI（不可用）
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="cli",
            message="查看代码",
            explicit=True
        )
        
        # 应该降级到 API
        executor = router.route(parsed_command)
        
        assert executor.layer == "api"
        assert executor is api_executor
    
    def test_fallback_preserves_provider(self):
        """测试降级保持提供商不变"""
        registry = ExecutorRegistry()
        
        # 注册 gemini CLI 和 claude API（交叉注册）
        gemini_cli = MockExecutor("gemini", "cli", available=True)
        claude_api = MockExecutor("claude", "api", available=True)
        
        registry.register_cli_executor("gemini", gemini_cli)
        registry.register_api_executor("claude", claude_api)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="gemini",
            default_layer="api"
        )
        
        # 请求 gemini API（不可用）
        parsed_command = ParsedCommand(
            provider="gemini",
            execution_layer="api",
            message="Hello!",
            explicit=True
        )
        
        # 应该降级到 gemini CLI，而不是 claude API
        executor = router.route(parsed_command)
        
        assert executor.get_provider_name() == "gemini"
        assert executor.layer == "cli"
        assert executor is gemini_cli
    
    def test_no_fallback_when_original_available(self):
        """测试原执行器可用时不降级"""
        registry = ExecutorRegistry()
        
        # 注册两个层的执行器
        api_executor = MockExecutor("claude", "api", available=True)
        cli_executor = MockExecutor("claude", "cli", available=True)
        
        registry.register_api_executor("claude", api_executor)
        registry.register_cli_executor("claude", cli_executor)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 请求 API（可用）
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello!",
            explicit=True
        )
        
        # 应该使用原始的 API 执行器，不降级
        executor = router.route(parsed_command)
        
        assert executor.layer == "api"
        assert executor is api_executor
    
    def test_fallback_implicit_routing_with_cli_keywords(self):
        """测试隐式路由检测到 CLI 关键词但 CLI 不可用时降级"""
        registry = ExecutorRegistry()
        
        # 只注册 API 执行器
        api_executor = MockExecutor("claude", "api", available=True)
        registry.register_api_executor("claude", api_executor)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 消息包含 CLI 关键词（应该路由到 CLI，但 CLI 不可用）
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="请帮我查看代码",
            explicit=False
        )
        
        # 应该降级到 API
        executor = router.route(parsed_command)
        
        assert executor.layer == "api"
        assert executor is api_executor


class TestSmartRouterAllExecutorsUnavailable:
    """测试所有执行器不可用的情况"""
    
    def test_raises_error_when_all_executors_unavailable(self):
        """测试所有执行器都不可用时抛出错误"""
        registry = ExecutorRegistry()
        
        # 不注册任何执行器
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello!",
            explicit=True
        )
        
        # 应该抛出 ExecutorNotAvailableError
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            router.route(parsed_command)
        
        error = exc_info.value
        assert error.provider == "claude"
        assert error.layer == "api"
        assert "unavailable" in error.reason.lower()
    
    def test_error_message_indicates_both_layers_unavailable(self):
        """测试错误消息指示两个层都不可用"""
        registry = ExecutorRegistry()
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello!",
            explicit=True
        )
        
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            router.route(parsed_command)
        
        error = exc_info.value
        # 错误消息应该提到两个层都不可用
        assert "api" in error.reason.lower() or "cli" in error.reason.lower()
        assert "both" in error.reason.lower() or "unavailable" in error.reason.lower()
    
    def test_error_for_implicit_routing_when_all_unavailable(self):
        """测试隐式路由时所有执行器不可用抛出错误"""
        registry = ExecutorRegistry()
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 隐式路由
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello!",
            explicit=False
        )
        
        with pytest.raises(ExecutorNotAvailableError):
            router.route(parsed_command)
    
    def test_error_for_cli_keywords_when_all_unavailable(self):
        """测试包含 CLI 关键词但所有执行器不可用时抛出错误"""
        registry = ExecutorRegistry()
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 包含 CLI 关键词
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="请帮我查看代码",
            explicit=False
        )
        
        with pytest.raises(ExecutorNotAvailableError):
            router.route(parsed_command)


class TestSmartRouterDefaultConfiguration:
    """测试默认提供商和层配置"""
    
    def test_default_provider_claude(self):
        """测试默认提供商为 claude"""
        registry = ExecutorRegistry()
        
        claude_api = MockExecutor("claude", "api", available=True)
        gemini_api = MockExecutor("gemini", "api", available=True)
        
        registry.register_api_executor("claude", claude_api)
        registry.register_api_executor("gemini", gemini_api)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 隐式路由应该使用默认提供商 claude
        parsed_command = ParsedCommand(
            provider="gemini",  # 这个值在隐式路由时会被忽略
            execution_layer="api",
            message="Hello!",
            explicit=False
        )
        
        executor = router.route(parsed_command)
        
        assert executor.get_provider_name() == "claude"
        assert executor is claude_api
    
    def test_default_provider_gemini(self):
        """测试默认提供商为 gemini"""
        registry = ExecutorRegistry()
        
        claude_api = MockExecutor("claude", "api", available=True)
        gemini_api = MockExecutor("gemini", "api", available=True)
        
        registry.register_api_executor("claude", claude_api)
        registry.register_api_executor("gemini", gemini_api)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="gemini",
            default_layer="api"
        )
        
        # 隐式路由应该使用默认提供商 gemini
        parsed_command = ParsedCommand(
            provider="claude",  # 这个值在隐式路由时会被忽略
            execution_layer="api",
            message="Hello!",
            explicit=False
        )
        
        executor = router.route(parsed_command)
        
        assert executor.get_provider_name() == "gemini"
        assert executor is gemini_api
    
    def test_default_layer_api(self):
        """测试默认层为 API"""
        registry = ExecutorRegistry()
        
        api_executor = MockExecutor("claude", "api", available=True)
        cli_executor = MockExecutor("claude", "cli", available=True)
        
        registry.register_api_executor("claude", api_executor)
        registry.register_cli_executor("claude", cli_executor)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 隐式路由无 CLI 关键词应该使用默认层 API
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="cli",  # 这个值在隐式路由时会被忽略
            message="Hello!",
            explicit=False
        )
        
        executor = router.route(parsed_command)
        
        assert executor.layer == "api"
        assert executor is api_executor
    
    def test_default_layer_cli(self):
        """测试默认层为 CLI"""
        registry = ExecutorRegistry()
        
        api_executor = MockExecutor("claude", "api", available=True)
        cli_executor = MockExecutor("claude", "cli", available=True)
        
        registry.register_api_executor("claude", api_executor)
        registry.register_cli_executor("claude", cli_executor)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="cli"
        )
        
        # 隐式路由无 CLI 关键词应该使用默认层 CLI
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",  # 这个值在隐式路由时会被忽略
            message="Hello!",
            explicit=False
        )
        
        executor = router.route(parsed_command)
        
        assert executor.layer == "cli"
        assert executor is cli_executor
    
    def test_cli_keywords_override_default_layer(self):
        """测试 CLI 关键词覆盖默认层配置"""
        registry = ExecutorRegistry()
        
        api_executor = MockExecutor("claude", "api", available=True)
        cli_executor = MockExecutor("claude", "cli", available=True)
        
        registry.register_api_executor("claude", api_executor)
        registry.register_cli_executor("claude", cli_executor)
        
        # 默认层设置为 API
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 消息包含 CLI 关键词
        parsed_command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="请帮我查看代码",
            explicit=False
        )
        
        # 应该使用 CLI 层，覆盖默认的 API 层
        executor = router.route(parsed_command)
        
        assert executor.layer == "cli"
        assert executor is cli_executor
    
    def test_default_configuration_consistency(self):
        """测试默认配置的一致性"""
        registry = ExecutorRegistry()
        
        claude_api = MockExecutor("claude", "api", available=True)
        registry.register_api_executor("claude", claude_api)
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        # 多次隐式路由应该一致使用默认配置
        messages = ["Hello!", "How are you?", "What's the weather?"]
        
        for message in messages:
            parsed_command = ParsedCommand(
                provider="claude",
                execution_layer="api",
                message=message,
                explicit=False
            )
            
            executor = router.route(parsed_command)
            
            assert executor.get_provider_name() == "claude"
            assert executor.layer == "api"
            assert executor is claude_api
    
    def test_router_initialization_with_defaults(self):
        """测试路由器初始化时的默认值"""
        registry = ExecutorRegistry()
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="claude",
            default_layer="api"
        )
        
        assert router.default_provider == "claude"
        assert router.default_layer == "api"
        assert router.executor_registry is registry
    
    def test_router_initialization_with_custom_defaults(self):
        """测试路由器初始化时的自定义默认值"""
        registry = ExecutorRegistry()
        
        router = SmartRouter(
            executor_registry=registry,
            default_provider="gemini",
            default_layer="cli"
        )
        
        assert router.default_provider == "gemini"
        assert router.default_layer == "cli"
