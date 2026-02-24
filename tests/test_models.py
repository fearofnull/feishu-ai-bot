"""
数据模型单元测试
测试 ExecutorMetadata 和其他数据类的基本功能
"""
import pytest
from feishu_bot.models import ExecutorMetadata, ExecutionResult, Message, Session, ParsedCommand


class TestExecutorMetadata:
    """ExecutorMetadata 测试类"""
    
    def test_create_executor_metadata(self):
        """测试创建 ExecutorMetadata 实例"""
        metadata = ExecutorMetadata(
            name="Claude API Executor",
            provider="claude",
            layer="api",
            version="1.0.0",
            description="Claude API executor for general questions",
            capabilities=["text_generation", "conversation"],
            command_prefixes=["@claude", "@claude-api"],
            priority=1,
            config_required=["api_key"]
        )
        
        assert metadata.name == "Claude API Executor"
        assert metadata.provider == "claude"
        assert metadata.layer == "api"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Claude API executor for general questions"
        assert metadata.capabilities == ["text_generation", "conversation"]
        assert metadata.command_prefixes == ["@claude", "@claude-api"]
        assert metadata.priority == 1
        assert metadata.config_required == ["api_key"]
    
    def test_executor_metadata_with_multiple_capabilities(self):
        """测试具有多个能力的 ExecutorMetadata"""
        metadata = ExecutorMetadata(
            name="Claude Code CLI Executor",
            provider="claude",
            layer="cli",
            version="1.0.0",
            description="Claude Code CLI for code analysis",
            capabilities=["code_analysis", "file_operations", "command_execution"],
            command_prefixes=["@claude-cli", "@code"],
            priority=2,
            config_required=["target_directory"]
        )
        
        assert len(metadata.capabilities) == 3
        assert "code_analysis" in metadata.capabilities
        assert "file_operations" in metadata.capabilities
        assert "command_execution" in metadata.capabilities
    
    def test_executor_metadata_with_multiple_prefixes(self):
        """测试具有多个命令前缀的 ExecutorMetadata"""
        metadata = ExecutorMetadata(
            name="OpenAI API Executor",
            provider="openai",
            layer="api",
            version="1.0.0",
            description="OpenAI API executor",
            capabilities=["text_generation"],
            command_prefixes=["@openai", "@gpt", "@chatgpt"],
            priority=3,
            config_required=["api_key"]
        )
        
        assert len(metadata.command_prefixes) == 3
        assert "@openai" in metadata.command_prefixes
        assert "@gpt" in metadata.command_prefixes
        assert "@chatgpt" in metadata.command_prefixes
    
    def test_executor_metadata_priority_ordering(self):
        """测试 ExecutorMetadata 优先级排序"""
        metadata1 = ExecutorMetadata(
            name="High Priority",
            provider="claude",
            layer="api",
            version="1.0.0",
            description="High priority executor",
            capabilities=["text_generation"],
            command_prefixes=["@claude"],
            priority=1,
            config_required=["api_key"]
        )
        
        metadata2 = ExecutorMetadata(
            name="Low Priority",
            provider="gemini",
            layer="api",
            version="1.0.0",
            description="Low priority executor",
            capabilities=["text_generation"],
            command_prefixes=["@gemini"],
            priority=5,
            config_required=["api_key"]
        )
        
        # 优先级数字越小，优先级越高
        assert metadata1.priority < metadata2.priority
    
    def test_executor_metadata_empty_lists(self):
        """测试 ExecutorMetadata 空列表字段"""
        metadata = ExecutorMetadata(
            name="Minimal Executor",
            provider="test",
            layer="api",
            version="1.0.0",
            description="Minimal executor",
            capabilities=[],
            command_prefixes=[],
            priority=1,
            config_required=[]
        )
        
        assert metadata.capabilities == []
        assert metadata.command_prefixes == []
        assert metadata.config_required == []


class TestExecutionResult:
    """ExecutionResult 测试类"""
    
    def test_create_success_result(self):
        """测试创建成功的执行结果"""
        result = ExecutionResult(
            success=True,
            stdout="Output text",
            stderr="",
            error_message=None,
            execution_time=1.5
        )
        
        assert result.success is True
        assert result.stdout == "Output text"
        assert result.stderr == ""
        assert result.error_message is None
        assert result.execution_time == 1.5
    
    def test_create_failure_result(self):
        """测试创建失败的执行结果"""
        result = ExecutionResult(
            success=False,
            stdout="",
            stderr="Error output",
            error_message="Command failed",
            execution_time=0.5
        )
        
        assert result.success is False
        assert result.stdout == ""
        assert result.stderr == "Error output"
        assert result.error_message == "Command failed"
        assert result.execution_time == 0.5


class TestParsedCommand:
    """ParsedCommand 测试类"""
    
    def test_create_explicit_command(self):
        """测试创建显式指定的命令"""
        command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="Hello, world!",
            explicit=True
        )
        
        assert command.provider == "claude"
        assert command.execution_layer == "api"
        assert command.message == "Hello, world!"
        assert command.explicit is True
    
    def test_create_implicit_command(self):
        """测试创建隐式命令"""
        command = ParsedCommand(
            provider="claude",
            execution_layer="api",
            message="What is Python?",
            explicit=False
        )
        
        assert command.provider == "claude"
        assert command.execution_layer == "api"
        assert command.message == "What is Python?"
        assert command.explicit is False
