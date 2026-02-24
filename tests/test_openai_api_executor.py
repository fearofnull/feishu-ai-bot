"""
OpenAI API 执行器单元测试

测试 OpenAIAPIExecutor 的具体实现，包括消息格式化、API 调用和错误处理。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.models import ExecutionResult, Message
import openai


def test_openai_executor_initialization():
    """测试 OpenAI 执行器的初始化"""
    executor = OpenAIAPIExecutor(
        api_key="test_key",
        model="gpt-4o-mini",
        timeout=30
    )
    
    assert executor.api_key == "test_key"
    assert executor.model == "gpt-4o-mini"
    assert executor.timeout == 30
    assert executor.client is not None


def test_openai_executor_default_model():
    """测试 OpenAI 执行器的默认模型"""
    executor = OpenAIAPIExecutor(api_key="test_key")
    
    assert executor.model == "gpt-4o"
    assert executor.timeout == 60


def test_get_provider_name():
    """测试 get_provider_name 方法"""
    executor = OpenAIAPIExecutor(api_key="test_key")
    assert executor.get_provider_name() == "openai-api"


def test_format_messages_without_history():
    """测试不带对话历史的消息格式化"""
    executor = OpenAIAPIExecutor(api_key="test_key")
    messages = executor.format_messages("Hello GPT")
    
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello GPT"


def test_format_messages_with_history():
    """测试带对话历史的消息格式化"""
    executor = OpenAIAPIExecutor(api_key="test_key")
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


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_success(mock_openai_class):
    """测试成功的 API 调用"""
    # 模拟 API 响应
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "This is GPT's response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    result = executor.execute("Hello GPT")
    
    assert result.success is True
    assert result.stdout == "This is GPT's response"
    assert result.stderr == ""
    assert result.error_message is None
    assert result.execution_time > 0


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_with_conversation_history(mock_openai_class):
    """测试带对话历史的 API 调用"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Response with context"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="Previous question", timestamp=1000),
        Message(role="assistant", content="Previous answer", timestamp=1001),
    ]
    
    result = executor.execute("Follow-up question", conversation_history=history)
    
    assert result.success is True
    assert result.stdout == "Response with context"
    
    # 验证调用参数包含历史消息
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]["messages"]
    assert len(messages) == 3
    assert messages[0]["content"] == "Previous question"
    assert messages[1]["content"] == "Previous answer"
    assert messages[2]["content"] == "Follow-up question"


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_with_additional_params(mock_openai_class):
    """测试带额外参数的 API 调用"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    params = {
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    
    result = executor.execute("Test prompt", additional_params=params)
    
    assert result.success is True
    
    # 验证调用参数包含额外参数
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["temperature"] == 0.7
    assert call_args[1]["max_tokens"] == 2000


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_api_error(mock_openai_class):
    """测试 API 错误处理"""
    mock_client = Mock()
    # 模拟 OpenAI API 错误
    # OpenAI APIError requires a message, request, and body parameter
    mock_request = Mock()
    api_error = openai.APIError(
        message="API quota exceeded",
        request=mock_request,
        body=None
    )
    mock_client.chat.completions.create.side_effect = api_error
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is False
    assert result.stdout == ""
    assert "API quota exceeded" in result.stderr
    assert "OpenAI API error" in result.error_message
    assert result.execution_time == 0


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_unexpected_error(mock_openai_class):
    """测试意外错误处理"""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("Unexpected error")
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is False
    assert result.stdout == ""
    assert "Unexpected error" in result.stderr
    assert "Unexpected error" in result.error_message
    assert result.execution_time == 0


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_uses_correct_model(mock_openai_class):
    """测试使用正确的模型"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key", model="gpt-4-turbo")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    
    # 验证使用指定的模型
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4-turbo"


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_without_optional_params(mock_openai_class):
    """测试不带可选参数的 API 调用"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    
    # 验证调用参数不包含可选参数
    call_args = mock_client.chat.completions.create.call_args
    assert "temperature" not in call_args[1]
    assert "max_tokens" not in call_args[1]
    # 但应该包含必需参数
    assert "model" in call_args[1]
    assert "messages" in call_args[1]


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_preserves_message_order(mock_openai_class):
    """测试消息顺序保持一致"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="First", timestamp=1000),
        Message(role="assistant", content="Second", timestamp=1001),
        Message(role="user", content="Third", timestamp=1002),
    ]
    
    result = executor.execute("Fourth", conversation_history=history)
    
    assert result.success is True
    
    # 验证消息顺序
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]["messages"]
    assert len(messages) == 4
    assert messages[0]["content"] == "First"
    assert messages[1]["content"] == "Second"
    assert messages[2]["content"] == "Third"
    assert messages[3]["content"] == "Fourth"


def test_format_messages_with_empty_history():
    """测试空对话历史的消息格式化"""
    executor = OpenAIAPIExecutor(api_key="test_key")
    messages = executor.format_messages("Hello", conversation_history=[])
    
    # 空历史应该只包含当前消息
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_format_messages_with_special_characters():
    """测试包含特殊字符的消息格式化"""
    executor = OpenAIAPIExecutor(api_key="test_key")
    special_text = "Hello\n\nThis has:\n- Special chars: @#$%\n- Emojis: 😀🎉\n- Unicode: 你好世界"
    messages = executor.format_messages(special_text)
    
    assert len(messages) == 1
    assert messages[0]["content"] == special_text


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_with_empty_response(mock_openai_class):
    """测试 API 返回空响应的情况"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = ""
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    assert result.stdout == ""
    assert result.error_message is None


@patch('feishu_bot.openai_api_executor.openai.OpenAI')
def test_execute_with_long_conversation_history(mock_openai_class):
    """测试长对话历史的处理"""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "Response"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    executor = OpenAIAPIExecutor(api_key="test_key")
    
    # 创建一个包含 20 轮对话的历史
    history = []
    for i in range(20):
        history.append(Message(role="user", content=f"Question {i}", timestamp=1000 + i * 2))
        history.append(Message(role="assistant", content=f"Answer {i}", timestamp=1001 + i * 2))
    
    result = executor.execute("Final question", conversation_history=history)
    
    assert result.success is True
    
    # 验证所有历史消息都被包含
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]["messages"]
    assert len(messages) == 41  # 20 * 2 + 1 (current message)
