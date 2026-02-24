"""
Gemini API 执行器单元测试

测试 GeminiAPIExecutor 的具体实现，包括消息格式化、API 调用和错误处理。
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.gemini_api_executor import GeminiAPIExecutor
from feishu_bot.models import ExecutionResult, Message


def test_gemini_executor_initialization():
    """测试 Gemini 执行器的初始化"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel') as mock_model:
            executor = GeminiAPIExecutor(
                api_key="test_key",
                model="gemini-1.5-pro",
                timeout=30
            )
            
            assert executor.api_key == "test_key"
            assert executor.model == "gemini-1.5-pro"
            assert executor.timeout == 30
            assert executor.client is not None


def test_gemini_executor_default_model():
    """测试 Gemini 执行器的默认模型"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            
            assert executor.model == "gemini-2.0-flash-exp"
            assert executor.timeout == 60


def test_get_provider_name():
    """测试 get_provider_name 方法"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            assert executor.get_provider_name() == "gemini-api"


def test_format_messages_without_history():
    """测试不带对话历史的消息格式化"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            messages = executor.format_messages("Hello Gemini")
            
            assert len(messages) == 1
            assert messages[0]["role"] == "user"
            assert messages[0]["parts"] == ["Hello Gemini"]


def test_format_messages_with_history():
    """测试带对话历史的消息格式化"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            history = [
                Message(role="user", content="What is Python?", timestamp=1000),
                Message(role="assistant", content="Python is a programming language.", timestamp=1001),
                Message(role="user", content="Tell me more", timestamp=1002),
                Message(role="assistant", content="Python is versatile and easy to learn.", timestamp=1003),
            ]
            
            messages = executor.format_messages("What about its history?", history)
            
            assert len(messages) == 5
            assert messages[0]["role"] == "user"
            assert messages[0]["parts"] == ["What is Python?"]
            assert messages[1]["role"] == "model"  # assistant -> model
            assert messages[1]["parts"] == ["Python is a programming language."]
            assert messages[2]["role"] == "user"
            assert messages[2]["parts"] == ["Tell me more"]
            assert messages[3]["role"] == "model"  # assistant -> model
            assert messages[3]["parts"] == ["Python is versatile and easy to learn."]
            assert messages[4]["role"] == "user"
            assert messages[4]["parts"] == ["What about its history?"]


def test_format_messages_converts_assistant_to_model():
    """测试消息格式化时将 assistant 角色转换为 model"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            history = [
                Message(role="assistant", content="I am an assistant", timestamp=1000),
            ]
            
            messages = executor.format_messages("Hello", history)
            
            # 验证 assistant 被转换为 model
            assert messages[0]["role"] == "model"
            assert messages[0]["parts"] == ["I am an assistant"]


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_success_without_history(mock_model_class, mock_configure):
    """测试成功的 API 调用（无对话历史）"""
    # 模拟 API 响应
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "This is Gemini's response"
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    result = executor.execute("Hello Gemini")
    
    assert result.success is True
    assert result.stdout == "This is Gemini's response"
    assert result.stderr == ""
    assert result.error_message is None
    assert result.execution_time > 0


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_success_with_history(mock_model_class, mock_configure):
    """测试成功的 API 调用（带对话历史，使用 chat 模式）"""
    # 模拟 chat 模式
    mock_model = Mock()
    mock_chat = Mock()
    mock_response = Mock()
    mock_response.text = "Response with context"
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="Previous question", timestamp=1000),
        Message(role="assistant", content="Previous answer", timestamp=1001),
    ]
    
    result = executor.execute("Follow-up question", conversation_history=history)
    
    assert result.success is True
    assert result.stdout == "Response with context"
    
    # 验证使用了 chat 模式
    mock_model.start_chat.assert_called_once()
    call_args = mock_model.start_chat.call_args
    history_arg = call_args[1]["history"]
    assert len(history_arg) == 2
    assert history_arg[0]["role"] == "user"
    assert history_arg[0]["parts"] == ["Previous question"]
    assert history_arg[1]["role"] == "model"  # assistant -> model
    assert history_arg[1]["parts"] == ["Previous answer"]
    
    # 验证发送了当前消息
    mock_chat.send_message.assert_called_once_with(
        "Follow-up question",
        generation_config=None
    )


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_with_additional_params(mock_model_class, mock_configure):
    """测试带额外参数的 API 调用"""
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "Response"
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    params = {
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    
    result = executor.execute("Test prompt", additional_params=params)
    
    assert result.success is True
    
    # 验证调用参数包含额外参数
    call_args = mock_model.generate_content.call_args
    generation_config = call_args[1]["generation_config"]
    assert generation_config["temperature"] == 0.7
    assert generation_config["max_output_tokens"] == 2000


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_with_history_and_params(mock_model_class, mock_configure):
    """测试带对话历史和额外参数的 API 调用"""
    mock_model = Mock()
    mock_chat = Mock()
    mock_response = Mock()
    mock_response.text = "Response"
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="Previous", timestamp=1000),
    ]
    params = {
        "temperature": 0.5,
    }
    
    result = executor.execute("Test", conversation_history=history, additional_params=params)
    
    assert result.success is True
    
    # 验证 chat 模式使用了额外参数
    call_args = mock_chat.send_message.call_args
    generation_config = call_args[1]["generation_config"]
    assert generation_config["temperature"] == 0.5


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_api_error(mock_model_class, mock_configure):
    """测试 API 错误处理"""
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("API quota exceeded")
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is False
    assert result.stdout == ""
    assert "API quota exceeded" in result.stderr
    assert "Gemini API error" in result.error_message
    assert result.execution_time == 0


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_unexpected_error(mock_model_class, mock_configure):
    """测试意外错误处理"""
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("Unexpected error")
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is False
    assert result.stdout == ""
    assert "Unexpected error" in result.stderr
    assert "Gemini API error" in result.error_message
    assert result.execution_time == 0


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_chat_mode_error(mock_model_class, mock_configure):
    """测试 chat 模式下的错误处理"""
    mock_model = Mock()
    mock_chat = Mock()
    mock_chat.send_message.side_effect = Exception("Chat error")
    mock_model.start_chat.return_value = mock_chat
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    history = [
        Message(role="user", content="Previous", timestamp=1000),
    ]
    
    result = executor.execute("Test", conversation_history=history)
    
    assert result.success is False
    assert "Chat error" in result.stderr
    assert "Gemini API error" in result.error_message


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_uses_correct_model(mock_model_class, mock_configure):
    """测试使用正确的模型"""
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "Response"
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key", model="gemini-1.5-pro")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    
    # 验证使用指定的模型（在初始化时传递）
    mock_model_class.assert_called_with("gemini-1.5-pro")


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_without_generation_config_when_no_params(mock_model_class, mock_configure):
    """测试没有额外参数时不传递 generation_config"""
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "Response"
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    
    # 验证没有传递 generation_config（或为 None）
    call_args = mock_model.generate_content.call_args
    generation_config = call_args[1].get("generation_config")
    assert generation_config is None


def test_api_key_configuration():
    """测试 API 密钥配置"""
    with patch('feishu_bot.gemini_api_executor.genai.configure') as mock_configure:
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="my_test_key")
            
            # 验证 genai.configure 被调用并传入了正确的 API 密钥
            mock_configure.assert_called_once_with(api_key="my_test_key")


def test_format_messages_with_empty_history():
    """测试空对话历史的消息格式化"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            messages = executor.format_messages("Hello", conversation_history=[])
            
            # 空历史应该只包含当前消息
            assert len(messages) == 1
            assert messages[0]["role"] == "user"
            assert messages[0]["parts"] == ["Hello"]


def test_format_messages_with_special_characters():
    """测试包含特殊字符的消息格式化"""
    with patch('feishu_bot.gemini_api_executor.genai.configure'):
        with patch('feishu_bot.gemini_api_executor.genai.GenerativeModel'):
            executor = GeminiAPIExecutor(api_key="test_key")
            special_text = "Hello\n\nThis has:\n- Special chars: @#$%\n- Emojis: 😀🎉\n- Unicode: 你好世界"
            messages = executor.format_messages(special_text)
            
            assert len(messages) == 1
            assert messages[0]["parts"] == [special_text]


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_with_empty_response(mock_model_class, mock_configure):
    """测试 API 返回空响应的情况"""
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = ""
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    result = executor.execute("Test prompt")
    
    assert result.success is True
    assert result.stdout == ""
    assert result.error_message is None


@patch('feishu_bot.gemini_api_executor.genai.configure')
@patch('feishu_bot.gemini_api_executor.genai.GenerativeModel')
def test_execute_with_long_conversation_history(mock_model_class, mock_configure):
    """测试长对话历史的处理"""
    mock_model = Mock()
    mock_chat = Mock()
    mock_response = Mock()
    mock_response.text = "Response"
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_model_class.return_value = mock_model
    
    executor = GeminiAPIExecutor(api_key="test_key")
    
    # 创建一个包含 20 轮对话的历史
    history = []
    for i in range(20):
        history.append(Message(role="user", content=f"Question {i}", timestamp=1000 + i * 2))
        history.append(Message(role="assistant", content=f"Answer {i}", timestamp=1001 + i * 2))
    
    result = executor.execute("Final question", conversation_history=history)
    
    assert result.success is True
    
    # 验证所有历史消息都被包含
    call_args = mock_model.start_chat.call_args
    history_arg = call_args[1]["history"]
    assert len(history_arg) == 40  # 20 * 2
