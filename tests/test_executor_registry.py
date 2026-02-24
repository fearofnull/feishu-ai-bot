"""
单元测试 - ExecutorRegistry

测试执行器注册表的核心功能，包括执行器注册、获取、可用性检查和元数据管理。

Feature: feishu-ai-bot
Requirements: 13.7, 16.5
"""
import os
import tempfile
import shutil
import json
import pytest
from typing import Dict, List, Optional, Any

from feishu_bot.executor_registry import (
    ExecutorRegistry,
    ExecutorNotAvailableError,
    AIExecutor
)
from feishu_bot.models import ExecutorMetadata, ExecutionResult


# Mock Executor for testing
class MockAPIExecutor(AIExecutor):
    """Mock API 执行器用于测试"""
    
    def __init__(self, provider: str, available: bool = True):
        self.provider = provider
        self.available = available
    
    def execute(
        self,
        user_prompt: str,
        conversation_history: Optional[List[Any]] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            stdout=f"Mock {self.provider} API response",
            stderr="",
            error_message=None,
            execution_time=0.1
        )
    
    def is_available(self) -> bool:
        return self.available
    
    def get_provider_name(self) -> str:
        return self.provider


class MockCLIExecutor(AIExecutor):
    """Mock CLI 执行器用于测试"""
    
    def __init__(self, provider: str, available: bool = True):
        self.provider = provider
        self.available = available
    
    def execute(
        self,
        user_prompt: str,
        conversation_history: Optional[List[Any]] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            stdout=f"Mock {self.provider} CLI response",
            stderr="",
            error_message=None,
            execution_time=0.5
        )
    
    def is_available(self) -> bool:
        return self.available
    
    def get_provider_name(self) -> str:
        return self.provider


def create_temp_config():
    """创建临时配置文件并返回路径"""
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "executor_config.json")
    return temp_dir, config_path


def cleanup_temp_config(temp_dir):
    """清理临时配置目录"""
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestExecutorRegistration:
    """测试执行器注册功能"""
    
    def test_register_api_executor_without_metadata(self):
        """测试注册 API 执行器（不带元数据）"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude")
        
        registry.register_api_executor("claude", executor)
        
        # 验证执行器已注册
        assert "claude" in registry.api_executors
        assert registry.api_executors["claude"] == executor
    
    def test_register_api_executor_with_metadata(self):
        """测试注册 API 执行器（带元数据）"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude")
        metadata = ExecutorMetadata(
            name="Claude API",
            provider="claude",
            layer="api",
            version="1.0.0",
            description="Claude API Executor",
            capabilities=["chat", "code_analysis"],
            command_prefixes=["@claude", "@claude-api"],
            priority=1,
            config_required=["api_key"]
        )
        
        registry.register_api_executor("claude", executor, metadata)
        
        # 验证执行器已注册
        assert "claude" in registry.api_executors
        assert registry.api_executors["claude"] == executor
        
        # 验证元数据已存储
        assert "claude_api" in registry.executor_metadata
        assert registry.executor_metadata["claude_api"] == metadata
    
    def test_register_cli_executor_without_metadata(self):
        """测试注册 CLI 执行器（不带元数据）"""
        registry = ExecutorRegistry()
        executor = MockCLIExecutor("gemini")
        
        registry.register_cli_executor("gemini", executor)
        
        # 验证执行器已注册
        assert "gemini" in registry.cli_executors
        assert registry.cli_executors["gemini"] == executor
    
    def test_register_cli_executor_with_metadata(self):
        """测试注册 CLI 执行器（带元数据）"""
        registry = ExecutorRegistry()
        executor = MockCLIExecutor("gemini")
        metadata = ExecutorMetadata(
            name="Gemini CLI",
            provider="gemini",
            layer="cli",
            version="1.0.0",
            description="Gemini CLI Executor",
            capabilities=["code_analysis", "file_operations"],
            command_prefixes=["@gemini-cli"],
            priority=2,
            config_required=["target_directory"]
        )
        
        registry.register_cli_executor("gemini", executor, metadata)
        
        # 验证执行器已注册
        assert "gemini" in registry.cli_executors
        assert registry.cli_executors["gemini"] == executor
        
        # 验证元数据已存储
        assert "gemini_cli" in registry.executor_metadata
        assert registry.executor_metadata["gemini_cli"] == metadata
    
    def test_register_multiple_executors(self):
        """测试注册多个执行器"""
        registry = ExecutorRegistry()
        
        # 注册多个 API 执行器
        registry.register_api_executor("claude", MockAPIExecutor("claude"))
        registry.register_api_executor("gemini", MockAPIExecutor("gemini"))
        registry.register_api_executor("openai", MockAPIExecutor("openai"))
        
        # 注册多个 CLI 执行器
        registry.register_cli_executor("claude", MockCLIExecutor("claude"))
        registry.register_cli_executor("gemini", MockCLIExecutor("gemini"))
        
        # 验证所有执行器已注册
        assert len(registry.api_executors) == 3
        assert len(registry.cli_executors) == 2
        assert "claude" in registry.api_executors
        assert "gemini" in registry.api_executors
        assert "openai" in registry.api_executors
        assert "claude" in registry.cli_executors
        assert "gemini" in registry.cli_executors


class TestExecutorRetrieval:
    """测试执行器获取功能"""
    
    def test_get_available_api_executor(self):
        """测试获取可用的 API 执行器"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude", available=True)
        registry.register_api_executor("claude", executor)
        
        # 获取执行器
        retrieved = registry.get_executor("claude", "api")
        
        # 验证返回正确的执行器
        assert retrieved == executor
    
    def test_get_available_cli_executor(self):
        """测试获取可用的 CLI 执行器"""
        registry = ExecutorRegistry()
        executor = MockCLIExecutor("gemini", available=True)
        registry.register_cli_executor("gemini", executor)
        
        # 获取执行器
        retrieved = registry.get_executor("gemini", "cli")
        
        # 验证返回正确的执行器
        assert retrieved == executor
    
    def test_get_unregistered_executor_raises_error(self):
        """测试获取未注册的执行器抛出异常"""
        registry = ExecutorRegistry()
        
        # 尝试获取未注册的执行器
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            registry.get_executor("nonexistent", "api")
        
        # 验证异常信息
        assert exc_info.value.provider == "nonexistent"
        assert exc_info.value.layer == "api"
        assert "not registered" in exc_info.value.reason
    
    def test_get_unavailable_executor_raises_error(self):
        """测试获取不可用的执行器抛出异常"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude", available=False)
        registry.register_api_executor("claude", executor)
        
        # 尝试获取不可用的执行器
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            registry.get_executor("claude", "api")
        
        # 验证异常信息
        assert exc_info.value.provider == "claude"
        assert exc_info.value.layer == "api"
        assert exc_info.value.reason is not None
    
    def test_get_executor_with_wrong_layer(self):
        """测试使用错误的层获取执行器"""
        registry = ExecutorRegistry()
        # 只注册 API 执行器
        registry.register_api_executor("claude", MockAPIExecutor("claude"))
        
        # 尝试作为 CLI 执行器获取
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            registry.get_executor("claude", "cli")
        
        assert exc_info.value.provider == "claude"
        assert exc_info.value.layer == "cli"


class TestExecutorAvailability:
    """测试执行器可用性检查功能"""
    
    def test_is_executor_available_returns_true_for_available(self):
        """测试可用执行器返回 True"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude", available=True)
        registry.register_api_executor("claude", executor)
        
        # 检查可用性
        assert registry.is_executor_available("claude", "api") is True
    
    def test_is_executor_available_returns_false_for_unavailable(self):
        """测试不可用执行器返回 False"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude", available=False)
        registry.register_api_executor("claude", executor)
        
        # 检查可用性
        assert registry.is_executor_available("claude", "api") is False
    
    def test_is_executor_available_returns_false_for_unregistered(self):
        """测试未注册执行器返回 False"""
        registry = ExecutorRegistry()
        
        # 检查未注册执行器的可用性
        assert registry.is_executor_available("nonexistent", "api") is False
    
    def test_availability_cache_works(self):
        """测试可用性缓存功能"""
        registry = ExecutorRegistry()
        
        # 创建一个可以改变可用性的执行器
        class DynamicExecutor(MockAPIExecutor):
            def __init__(self):
                super().__init__("dynamic", available=True)
                self.check_count = 0
            
            def is_available(self) -> bool:
                self.check_count += 1
                return self.available
        
        executor = DynamicExecutor()
        registry.register_api_executor("dynamic", executor)
        
        # 第一次检查
        registry.is_executor_available("dynamic", "api")
        first_count = executor.check_count
        
        # 第二次检查（应该使用缓存）
        registry.is_executor_available("dynamic", "api")
        second_count = executor.check_count
        
        # 验证第二次没有调用 is_available（使用了缓存）
        assert second_count == first_count
    
    def test_clear_availability_cache(self):
        """测试清除可用性缓存"""
        registry = ExecutorRegistry()
        
        # 创建一个可以改变可用性的执行器
        class DynamicExecutor(MockAPIExecutor):
            def __init__(self):
                super().__init__("dynamic", available=True)
                self.check_count = 0
            
            def is_available(self) -> bool:
                self.check_count += 1
                return self.available
        
        executor = DynamicExecutor()
        registry.register_api_executor("dynamic", executor)
        
        # 第一次检查
        registry.is_executor_available("dynamic", "api")
        first_count = executor.check_count
        
        # 清除缓存
        registry.clear_availability_cache()
        
        # 第二次检查（应该重新调用 is_available）
        registry.is_executor_available("dynamic", "api")
        second_count = executor.check_count
        
        # 验证第二次调用了 is_available
        assert second_count > first_count
    
    def test_list_available_executors_all(self):
        """测试列出所有可用执行器"""
        registry = ExecutorRegistry()
        
        # 注册多个执行器（部分可用，部分不可用）
        registry.register_api_executor("claude", MockAPIExecutor("claude", available=True))
        registry.register_api_executor("gemini", MockAPIExecutor("gemini", available=False))
        registry.register_cli_executor("claude", MockCLIExecutor("claude", available=True))
        registry.register_cli_executor("openai", MockCLIExecutor("openai", available=False))
        
        # 列出所有可用执行器
        available = registry.list_available_executors()
        
        # 验证只返回可用的执行器
        assert "claude/api" in available
        assert "claude/cli" in available
        assert "gemini/api" not in available
        assert "openai/cli" not in available
        assert len(available) == 2
    
    def test_list_available_executors_api_only(self):
        """测试只列出 API 层可用执行器"""
        registry = ExecutorRegistry()
        
        registry.register_api_executor("claude", MockAPIExecutor("claude", available=True))
        registry.register_api_executor("gemini", MockAPIExecutor("gemini", available=True))
        registry.register_cli_executor("claude", MockCLIExecutor("claude", available=True))
        
        # 只列出 API 执行器
        available = registry.list_available_executors(layer="api")
        
        # 验证只返回 API 执行器
        assert "claude/api" in available
        assert "gemini/api" in available
        assert "claude/cli" not in available
        assert len(available) == 2
    
    def test_list_available_executors_cli_only(self):
        """测试只列出 CLI 层可用执行器"""
        registry = ExecutorRegistry()
        
        registry.register_api_executor("claude", MockAPIExecutor("claude", available=True))
        registry.register_cli_executor("claude", MockCLIExecutor("claude", available=True))
        registry.register_cli_executor("gemini", MockCLIExecutor("gemini", available=True))
        
        # 只列出 CLI 执行器
        available = registry.list_available_executors(layer="cli")
        
        # 验证只返回 CLI 执行器
        assert "claude/cli" in available
        assert "gemini/cli" in available
        assert "claude/api" not in available
        assert len(available) == 2


class TestMetadataManagement:
    """测试元数据管理功能"""
    
    def test_get_executor_metadata_exists(self):
        """测试获取存在的执行器元数据"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude")
        metadata = ExecutorMetadata(
            name="Claude API",
            provider="claude",
            layer="api",
            version="1.0.0",
            description="Claude API Executor",
            capabilities=["chat", "code_analysis"],
            command_prefixes=["@claude", "@claude-api"],
            priority=1,
            config_required=["api_key"]
        )
        
        registry.register_api_executor("claude", executor, metadata)
        
        # 获取元数据
        retrieved = registry.get_executor_metadata("claude", "api")
        
        # 验证元数据正确
        assert retrieved == metadata
        assert retrieved.name == "Claude API"
        assert retrieved.provider == "claude"
        assert retrieved.layer == "api"
        assert retrieved.version == "1.0.0"
        assert retrieved.capabilities == ["chat", "code_analysis"]
        assert retrieved.command_prefixes == ["@claude", "@claude-api"]
        assert retrieved.priority == 1
        assert retrieved.config_required == ["api_key"]
    
    def test_get_executor_metadata_not_exists(self):
        """测试获取不存在的执行器元数据"""
        registry = ExecutorRegistry()
        
        # 获取不存在的元数据
        retrieved = registry.get_executor_metadata("nonexistent", "api")
        
        # 验证返回 None
        assert retrieved is None
    
    def test_metadata_used_in_unavailability_reason(self):
        """测试元数据用于生成不可用原因"""
        registry = ExecutorRegistry()
        executor = MockAPIExecutor("claude", available=False)
        metadata = ExecutorMetadata(
            name="Claude API",
            provider="claude",
            layer="api",
            version="1.0.0",
            description="Claude API Executor",
            capabilities=["chat"],
            command_prefixes=["@claude"],
            priority=1,
            config_required=["api_key", "model"]
        )
        
        registry.register_api_executor("claude", executor, metadata)
        
        # 尝试获取不可用的执行器
        with pytest.raises(ExecutorNotAvailableError) as exc_info:
            registry.get_executor("claude", "api")
        
        # 验证错误原因包含必需配置信息
        assert "api_key" in exc_info.value.reason or "model" in exc_info.value.reason


class TestConfigurationLoading:
    """测试从配置文件加载功能"""
    
    def test_load_from_config_file(self):
        """测试从配置文件加载执行器元数据"""
        temp_dir, config_path = create_temp_config()
        try:
            # 创建配置文件
            config = {
                "executors": [
                    {
                        "provider": "claude",
                        "layer": "api",
                        "name": "Claude API",
                        "version": "1.0.0",
                        "description": "Claude API Executor",
                        "capabilities": ["chat", "code_analysis"],
                        "command_prefixes": ["@claude", "@claude-api"],
                        "priority": 1,
                        "config_required": ["api_key"]
                    },
                    {
                        "provider": "gemini",
                        "layer": "cli",
                        "name": "Gemini CLI",
                        "version": "1.0.0",
                        "description": "Gemini CLI Executor",
                        "capabilities": ["code_analysis", "file_operations"],
                        "command_prefixes": ["@gemini-cli"],
                        "priority": 2,
                        "config_required": ["target_directory"]
                    }
                ]
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
            
            # 从配置文件创建注册表
            registry = ExecutorRegistry(config_path=config_path)
            
            # 验证元数据已加载
            claude_metadata = registry.get_executor_metadata("claude", "api")
            assert claude_metadata is not None
            assert claude_metadata.name == "Claude API"
            assert claude_metadata.provider == "claude"
            assert claude_metadata.layer == "api"
            
            gemini_metadata = registry.get_executor_metadata("gemini", "cli")
            assert gemini_metadata is not None
            assert gemini_metadata.name == "Gemini CLI"
            assert gemini_metadata.provider == "gemini"
            assert gemini_metadata.layer == "cli"
        finally:
            cleanup_temp_config(temp_dir)
    
    def test_load_from_nonexistent_config_file(self):
        """测试从不存在的配置文件加载（应该不报错）"""
        # 使用不存在的配置文件路径
        registry = ExecutorRegistry(config_path="/nonexistent/path/config.json")
        
        # 验证注册表仍然可以正常工作
        assert len(registry.api_executors) == 0
        assert len(registry.cli_executors) == 0
        assert len(registry.executor_metadata) == 0
    
    def test_load_from_invalid_config_file(self):
        """测试从无效的配置文件加载（应该不报错）"""
        temp_dir, config_path = create_temp_config()
        try:
            # 创建无效的配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("invalid json content {{{")
            
            # 从无效配置文件创建注册表（应该不报错）
            registry = ExecutorRegistry(config_path=config_path)
            
            # 验证注册表仍然可以正常工作
            assert len(registry.api_executors) == 0
            assert len(registry.cli_executors) == 0
        finally:
            cleanup_temp_config(temp_dir)
    
    def test_load_config_with_missing_fields(self):
        """测试加载缺少字段的配置（应该使用默认值）"""
        temp_dir, config_path = create_temp_config()
        try:
            # 创建缺少部分字段的配置
            config = {
                "executors": [
                    {
                        "provider": "claude",
                        "layer": "api"
                        # 缺少其他字段
                    }
                ]
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
            
            # 从配置文件创建注册表
            registry = ExecutorRegistry(config_path=config_path)
            
            # 验证元数据已加载（使用默认值）
            metadata = registry.get_executor_metadata("claude", "api")
            assert metadata is not None
            assert metadata.provider == "claude"
            assert metadata.layer == "api"
            assert metadata.version == "1.0.0"  # 默认值
            assert metadata.capabilities == []  # 默认值
        finally:
            cleanup_temp_config(temp_dir)


class TestEdgeCases:
    """测试边界情况"""
    
    def test_register_same_provider_different_layers(self):
        """测试注册相同提供商的不同层执行器"""
        registry = ExecutorRegistry()
        
        # 注册相同提供商的 API 和 CLI 执行器
        api_executor = MockAPIExecutor("claude")
        cli_executor = MockCLIExecutor("claude")
        
        registry.register_api_executor("claude", api_executor)
        registry.register_cli_executor("claude", cli_executor)
        
        # 验证两个执行器都已注册
        assert registry.get_executor("claude", "api") == api_executor
        assert registry.get_executor("claude", "cli") == cli_executor
    
    def test_overwrite_existing_executor(self):
        """测试覆盖已存在的执行器"""
        registry = ExecutorRegistry()
        
        # 注册第一个执行器
        executor1 = MockAPIExecutor("claude")
        registry.register_api_executor("claude", executor1)
        
        # 注册第二个执行器（覆盖第一个）
        executor2 = MockAPIExecutor("claude")
        registry.register_api_executor("claude", executor2)
        
        # 验证第二个执行器覆盖了第一个
        assert registry.get_executor("claude", "api") == executor2
        assert registry.get_executor("claude", "api") != executor1
    
    def test_empty_registry(self):
        """测试空注册表"""
        registry = ExecutorRegistry()
        
        # 验证空注册表的行为
        assert len(registry.api_executors) == 0
        assert len(registry.cli_executors) == 0
        assert len(registry.executor_metadata) == 0
        assert len(registry.list_available_executors()) == 0
        
        # 尝试获取执行器应该抛出异常
        with pytest.raises(ExecutorNotAvailableError):
            registry.get_executor("any", "api")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
