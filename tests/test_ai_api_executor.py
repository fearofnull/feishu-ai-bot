"""
AI API 执行器抽象基类单元测试
"""
import pytest
from feishu_bot.ai_api_executor import AIAPIExecutor
from feishu_bot.models import ExecutionResult, Message


class ConcreteAPIExecutor(AIAPIExecutor):
    """用于测试的具体实现"""
    
    def execute(self, user_prompt, conversation_history=None, additional_params=None):
        return ExecutionResult(
            success=True,
            stdout="Test response",
            stderr="",
            error_message=None,
            execution_time=0.5
        )
    
    def get_provider_name(self):
        return "test-api"
    
    def format_messages(self, user_prompt, conversation_history=None):
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_prompt})
        return messages


def test_abstract_base_class_cannot_be_instantiated():
    """测试抽象基类不能直接实例化"""
    with pytest.raises(TypeError):
        AIAPIExecutor(api_key="test_key")


def test_concrete_executor_initialization():
    """测试具体执行器的初始化"""
    executor = ConcreteAPIExecutor(
        api_key="test_key",
        model="test-model",
        timeout=30
    )
    
    assert executor.api_key == "test_key"
    assert executor.model == "test-model"
    assert executor.timeout == 30


def test_concrete_executor_default_values():
    """测试具体执行器的默认值"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    
    assert executor.api_key == "test_key"
    assert executor.model is None
    assert executor.timeout == 60


def test_execute_method():
    """测试 execute 方法"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.stdout == "Test response"


def test_get_provider_name():
    """测试 get_provider_name 方法"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    assert executor.get_provider_name() == "test-api"


def test_format_messages_without_history():
    """测试不带对话历史的消息格式化"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    messages = executor.format_messages("Hello")
    
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_format_messages_with_history():
    """测试带对话历史的消息格式化"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="First message", timestamp=1000),
        Message(role="assistant", content="First response", timestamp=1001),
    ]
    
    messages = executor.format_messages("Second message", history)
    
    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "First message"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "First response"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Second message"


def test_execute_with_conversation_history():
    """测试带对话历史的执行"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="Previous question", timestamp=1000),
        Message(role="assistant", content="Previous answer", timestamp=1001),
    ]
    
    result = executor.execute("New question", conversation_history=history)
    
    assert isinstance(result, ExecutionResult)
    assert result.success is True


def test_execute_with_additional_params():
    """测试带额外参数的执行"""
    executor = ConcreteAPIExecutor(api_key="test_key")
    params = {"temperature": 0.7, "max_tokens": 1000}
    
    result = executor.execute("Test prompt", additional_params=params)
    
    assert isinstance(result, ExecutionResult)
    assert result.success is True
