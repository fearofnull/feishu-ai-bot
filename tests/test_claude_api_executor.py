"""
Claude API 执行器单元测试

测试 ClaudeAPIExecutor 的具体实现，包括消息格式化、API 调用和错误处理。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.claude_api_executor import ClaudeAPIExecutor
from feishu_bot.models import ExecutionResult, Message
import anthropic


def test_claude_executor_initialization():
    """测试 Claude 执行器的初始化"""
    executor = ClaudeAPIExecutor(
        api_key="test_key",
        model="claude-3-opus-20240229",
        timeout=30
    )
    
    assert executor.api_key == "test_key"
    assert executor.model == "claude-3-opus-20240229"
    assert executor.timeout == 30
    assert executor.client is not None


def test_claude_executor_default_model():
    """测试 Claude 执行器的默认模型"""
    executor = ClaudeAPIExecutor(api_key="test_key")
    
    assert executor.model == "claude-3-5-sonnet-20241022"
    assert executor.timeout == 60


def test_get_provider_name():
    """测试 get_provider_name 方法"""
    executor = ClaudeAPIExecutor(api_key="test_key")
    assert executor.get_provider_name() == "claude-api"


def test_format_messages_without_history():
    """测试不带对话历史的消息格式化"""
    executor = ClaudeAPIExecutor(api_key="test_key")
    messages = executor.format_messages("Hello Claude")
    
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello Claude"


def test_format_messages_with_history():
    """测试带对话历史的消息格式化"""
    executor = ClaudeAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="What is Python?", timestamp=1000),
        Message(role="assistant", content="Python is a programming language.", timestamp=1001),
        Message(role="user", content="Tell me more", timestamp=1002),
        Message(role="assistant", content="Python is versatile and easy to learn.", timestamp=1003),
    ]
    
    messages = executor.format_messages("What about its history?", history)
    
    assert len(messages) == 5
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is Python?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Python is a programming language."
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Tell me more"
    assert messages[3]["role"] == "assistant"
    assert messages[3]["content"] == "Python is versatile and easy to learn."
    assert messages[4]["role"] == "user"
    assert messages[4]["content"] == "What about its history?"


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_success(mock_anthropic_class):
    """测试成功的 API 调用"""
    # 模拟 API 响应
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="This is Claude's response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    result = executor.execute("Hello Claude")
    
    assert result.success is True
    assert result.stdout == "This is Claude's response"
    assert result.stderr == ""
    assert result.error_message is None
    assert result.execution_time > 0


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_with_conversation_history(mock_anthropic_class):
    """测试带对话历史的 API 调用"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Response with context")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="Previous question", timestamp=1000),
        Message(role="assistant", content="Previous answer", timestamp=1001),
    ]
    
    result = executor.execute("Follow-up question", conversation_history=history)
    
    assert result.success is True
    assert result.stdout == "Response with context"
    
    # 验证调用参数包含历史消息
    call_args = mock_client.messages.create.call_args
    messages = call_args[1]["messages"]
    assert len(messages) == 3
    assert messages[0]["content"] == "Previous question"
    assert messages[1]["content"] == "Previous answer"
    assert messages[2]["content"] == "Follow-up question"


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_with_additional_params(mock_anthropic_class):
    """测试带额外参数的 API 调用"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    params = {
        "temperature": 0.7,
        "max_tokens": 2000,
        "system": "You are a helpful assistant"
    }
    
    result = executor.execute("Test prompt", additional_params=params)
    
    assert result.success is True
    
    # 验证调用参数包含额外参数
    call_args = mock_client.messages.create.call_args
    assert call_args[1]["temperature"] == 0.7
    assert call_args[1]["max_tokens"] == 2000
    assert call_args[1]["system"] == "You are a helpful assistant"


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_api_error(mock_anthropic_class):
    """测试 API 错误处理"""
    mock_client = Mock()
    # Simulate an API error by raising an exception with APIError in the message
    mock_client.messages.create.side_effect = Exception("anthropic.APIError: API quota exceeded")
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is False
    assert result.stdout == ""
    assert "API quota exceeded" in result.stderr
    assert "Unexpected error" in result.error_message
    assert result.execution_time == 0


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_unexpected_error(mock_anthropic_class):
    """测试意外错误处理"""
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("Unexpected error")
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is False
    assert result.stdout == ""
    assert "Unexpected error" in result.stderr
    assert "Unexpected error" in result.error_message
    assert result.execution_time == 0


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_default_max_tokens(mock_anthropic_class):
    """测试默认 max_tokens 参数"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    
    # 验证默认 max_tokens 为 4096
    call_args = mock_client.messages.create.call_args
    assert call_args[1]["max_tokens"] == 4096


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_uses_correct_model(mock_anthropic_class):
    """测试使用正确的模型"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key", model="claude-3-opus-20240229")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    
    # 验证使用指定的模型
    call_args = mock_client.messages.create.call_args
    assert call_args[1]["model"] == "claude-3-opus-20240229"


def test_format_messages_with_empty_history():
    """测试空对话历史的消息格式化"""
    executor = ClaudeAPIExecutor(api_key="test_key")
    messages = executor.format_messages("Hello", conversation_history=[])
    
    # 空历史应该只包含当前消息
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_format_messages_with_special_characters():
    """测试包含特殊字符的消息格式化"""
    executor = ClaudeAPIExecutor(api_key="test_key")
    special_text = "Hello\n\nThis has:\n- Special chars: @#$%\n- Emojis: 😀🎉\n- Unicode: 你好世界"
    messages = executor.format_messages(special_text)
    
    assert len(messages) == 1
    assert messages[0]["content"] == special_text


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_with_empty_response(mock_anthropic_class):
    """测试 API 返回空响应的情况"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    assert result.stdout == ""
    assert result.error_message is None


@patch('feishu_bot.claude_api_executor.anthropic.Anthropic')
def test_execute_with_long_conversation_history(mock_anthropic_class):
    """测试长对话历史的处理"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client
    
    executor = ClaudeAPIExecutor(api_key="test_key")
    
    # 创建一个包含 20 轮对话的历史
    history = []
    for i in range(20):
        history.append(Message(role="user", content=f"Question {i}", timestamp=1000 + i * 2))
        history.append(Message(role="assistant", content=f"Answer {i}", timestamp=1001 + i * 2))
    
    result = executor.execute("Final question", conversation_history=history)
    
    assert result.success is True
    
    # 验证所有历史消息都被包含
    call_args = mock_client.messages.create.call_args
    messages = call_args[1]["messages"]
    assert len(messages) == 41  # 20 * 2 + 1 (current message)
