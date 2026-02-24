"""
API 执行成功响应属性测试

使用 Hypothesis 进行基于属性的测试，验证 API 执行成功响应的通用正确性属性。
测试所有三个 API 执行器（Claude API、Gemini API、OpenAI API）的成功响应行为。
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.claude_api_executor import ClaudeAPIExecutor
from feishu_bot.gemini_api_executor import GeminiAPIExecutor
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.models import Message, ExecutionResult


class TestAPIExecutionSuccessProperties:
    """API 执行成功响应属性测试类"""
    
    # Feature: feishu-ai-bot, Property 43: API 执行成功响应
    # Validates: Requirements 14.7
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500)
    )
    def test_claude_api_success_response_structure(self, user_prompt, api_response_content):
        """
        Property 43: API 执行成功响应 - Claude API 成功响应结构
        
        For any successful Claude API call, the executor should return
        an ExecutionResult with:
        - success=True
        - stdout containing the AI response content (non-empty)
        - stderr empty
        - error_message=None
        - execution_time > 0
        
        Validates: Requirements 14.7
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Mock the Anthropic client to simulate successful API response
        mock_response = Mock()
        mock_response.content = [Mock(text=api_response_content)]
        
        with patch.object(executor.client.messages, 'create', return_value=mock_response):
            result = executor.execute(user_prompt)
        
        # Verify ExecutionResult structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object"
        
        # Verify success response properties
        assert result.success is True, \
            "Successful API call should have success=True"
        
        assert result.stdout == api_response_content, \
            f"stdout should contain API response content, expected '{api_response_content}', got '{result.stdout}'"
        
        assert len(result.stdout) > 0, \
            "stdout should be non-empty for successful API call"
        
        assert result.stderr == "", \
            f"stderr should be empty for successful API call, got '{result.stderr}'"
        
        assert result.error_message is None, \
            f"error_message should be None for successful API call, got '{result.error_message}'"
        
        assert result.execution_time > 0, \
            f"execution_time should be positive, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500)
    )
    def test_gemini_api_success_response_structure(self, user_prompt, api_response_content):
        """
        Property 43: API 执行成功响应 - Gemini API 成功响应结构
        
        For any successful Gemini API call, the executor should return
        an ExecutionResult with:
        - success=True
        - stdout containing the AI response content (non-empty)
        - stderr empty
        - error_message=None
        - execution_time > 0
        
        Validates: Requirements 14.7
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Mock the Gemini client to simulate successful API response
        mock_response = Mock()
        mock_response.text = api_response_content
        
        with patch.object(executor.client, 'generate_content', return_value=mock_response):
            result = executor.execute(user_prompt)
        
        # Verify ExecutionResult structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object"
        
        # Verify success response properties
        assert result.success is True, \
            "Successful API call should have success=True"
        
        assert result.stdout == api_response_content, \
            f"stdout should contain API response content, expected '{api_response_content}', got '{result.stdout}'"
        
        assert len(result.stdout) > 0, \
            "stdout should be non-empty for successful API call"
        
        assert result.stderr == "", \
            f"stderr should be empty for successful API call, got '{result.stderr}'"
        
        assert result.error_message is None, \
            f"error_message should be None for successful API call, got '{result.error_message}'"
        
        assert result.execution_time > 0, \
            f"execution_time should be positive, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500)
    )
    def test_openai_api_success_response_structure(self, user_prompt, api_response_content):
        """
        Property 43: API 执行成功响应 - OpenAI API 成功响应结构
        
        For any successful OpenAI API call, the executor should return
        an ExecutionResult with:
        - success=True
        - stdout containing the AI response content (non-empty)
        - stderr empty
        - error_message=None
        - execution_time > 0
        
        Validates: Requirements 14.7
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Mock the OpenAI client to simulate successful API response
        mock_choice = Mock()
        mock_choice.message.content = api_response_content
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(executor.client.chat.completions, 'create', return_value=mock_response):
            result = executor.execute(user_prompt)
        
        # Verify ExecutionResult structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object"
        
        # Verify success response properties
        assert result.success is True, \
            "Successful API call should have success=True"
        
        assert result.stdout == api_response_content, \
            f"stdout should contain API response content, expected '{api_response_content}', got '{result.stdout}'"
        
        assert len(result.stdout) > 0, \
            "stdout should be non-empty for successful API call"
        
        assert result.stderr == "", \
            f"stderr should be empty for successful API call, got '{result.stderr}'"
        
        assert result.error_message is None, \
            f"error_message should be None for successful API call, got '{result.error_message}'"
        
        assert result.execution_time > 0, \
            f"execution_time should be positive, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=0,
            max_size=5
        )
    )
    def test_claude_api_success_with_conversation_history(
        self, user_prompt, api_response_content, history_messages
    ):
        """
        Property 43: API 执行成功响应 - Claude API 带对话历史的成功响应
        
        For any successful Claude API call with conversation history,
        the executor should return a valid ExecutionResult with success=True,
        regardless of the conversation history length.
        
        Validates: Requirements 14.7
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ] if history_messages else None
        
        # Mock the Anthropic client
        mock_response = Mock()
        mock_response.content = [Mock(text=api_response_content)]
        
        with patch.object(executor.client.messages, 'create', return_value=mock_response):
            result = executor.execute(user_prompt, conversation_history)
        
        # Verify success response
        assert result.success is True, \
            "Successful API call with history should have success=True"
        assert result.stdout == api_response_content, \
            "stdout should contain API response content"
        assert result.stderr == "", \
            "stderr should be empty"
        assert result.error_message is None, \
            "error_message should be None"
        assert result.execution_time > 0, \
            "execution_time should be positive"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=0,
            max_size=5
        )
    )
    def test_gemini_api_success_with_conversation_history(
        self, user_prompt, api_response_content, history_messages
    ):
        """
        Property 43: API 执行成功响应 - Gemini API 带对话历史的成功响应
        
        For any successful Gemini API call with conversation history,
        the executor should return a valid ExecutionResult with success=True,
        regardless of the conversation history length.
        
        Validates: Requirements 14.7
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ] if history_messages else None
        
        # Mock the Gemini client
        mock_response = Mock()
        mock_response.text = api_response_content
        
        if conversation_history:
            # Mock chat mode
            mock_chat = Mock()
            mock_chat.send_message = Mock(return_value=mock_response)
            with patch.object(executor.client, 'start_chat', return_value=mock_chat):
                result = executor.execute(user_prompt, conversation_history)
        else:
            # Mock single generation mode
            with patch.object(executor.client, 'generate_content', return_value=mock_response):
                result = executor.execute(user_prompt, conversation_history)
        
        # Verify success response
        assert result.success is True, \
            "Successful API call with history should have success=True"
        assert result.stdout == api_response_content, \
            "stdout should contain API response content"
        assert result.stderr == "", \
            "stderr should be empty"
        assert result.error_message is None, \
            "error_message should be None"
        assert result.execution_time > 0, \
            "execution_time should be positive"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=0,
            max_size=5
        )
    )
    def test_openai_api_success_with_conversation_history(
        self, user_prompt, api_response_content, history_messages
    ):
        """
        Property 43: API 执行成功响应 - OpenAI API 带对话历史的成功响应
        
        For any successful OpenAI API call with conversation history,
        the executor should return a valid ExecutionResult with success=True,
        regardless of the conversation history length.
        
        Validates: Requirements 14.7
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ] if history_messages else None
        
        # Mock the OpenAI client
        mock_choice = Mock()
        mock_choice.message.content = api_response_content
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(executor.client.chat.completions, 'create', return_value=mock_response):
            result = executor.execute(user_prompt, conversation_history)
        
        # Verify success response
        assert result.success is True, \
            "Successful API call with history should have success=True"
        assert result.stdout == api_response_content, \
            "stdout should contain API response content"
        assert result.stderr == "", \
            "stderr should be empty"
        assert result.error_message is None, \
            "error_message should be None"
        assert result.execution_time > 0, \
            "execution_time should be positive"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500),
        provider=st.sampled_from(["claude", "gemini", "openai"])
    )
    def test_all_api_executors_success_response_consistency(
        self, user_prompt, api_response_content, provider
    ):
        """
        Property 43: API 执行成功响应 - 所有 API 执行器响应一致性
        
        For any successful API call across all three executors (Claude, Gemini, OpenAI),
        the ExecutionResult structure should be consistent:
        - All have success=True
        - All have non-empty stdout
        - All have empty stderr
        - All have error_message=None
        - All have positive execution_time
        
        Validates: Requirements 14.7
        """
        # Create executor based on provider
        if provider == "claude":
            executor = ClaudeAPIExecutor(api_key="test_key")
            mock_response = Mock()
            mock_response.content = [Mock(text=api_response_content)]
            with patch.object(executor.client.messages, 'create', return_value=mock_response):
                result = executor.execute(user_prompt)
        elif provider == "gemini":
            executor = GeminiAPIExecutor(api_key="test_key")
            mock_response = Mock()
            mock_response.text = api_response_content
            with patch.object(executor.client, 'generate_content', return_value=mock_response):
                result = executor.execute(user_prompt)
        else:  # openai
            executor = OpenAIAPIExecutor(api_key="test_key")
            mock_choice = Mock()
            mock_choice.message.content = api_response_content
            mock_response = Mock()
            mock_response.choices = [mock_choice]
            with patch.object(executor.client.chat.completions, 'create', return_value=mock_response):
                result = executor.execute(user_prompt)
        
        # Verify consistent response structure across all providers
        assert isinstance(result, ExecutionResult), \
            f"{provider} executor should return ExecutionResult"
        assert result.success is True, \
            f"{provider} executor should have success=True"
        assert len(result.stdout) > 0, \
            f"{provider} executor should have non-empty stdout"
        assert result.stderr == "", \
            f"{provider} executor should have empty stderr"
        assert result.error_message is None, \
            f"{provider} executor should have error_message=None"
        assert result.execution_time > 0, \
            f"{provider} executor should have positive execution_time"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500),
        max_tokens=st.integers(min_value=100, max_value=8000),
        temperature=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_claude_api_success_with_additional_params(
        self, user_prompt, api_response_content, max_tokens, temperature
    ):
        """
        Property 43: API 执行成功响应 - Claude API 带额外参数的成功响应
        
        For any successful Claude API call with additional parameters
        (max_tokens, temperature), the executor should still return
        a valid ExecutionResult with success=True.
        
        Validates: Requirements 14.7
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        additional_params = {
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Mock the Anthropic client
        mock_response = Mock()
        mock_response.content = [Mock(text=api_response_content)]
        
        with patch.object(executor.client.messages, 'create', return_value=mock_response):
            result = executor.execute(user_prompt, additional_params=additional_params)
        
        # Verify success response with additional params
        assert result.success is True, \
            "Successful API call with additional params should have success=True"
        assert result.stdout == api_response_content, \
            "stdout should contain API response content"
        assert result.stderr == "", \
            "stderr should be empty"
        assert result.error_message is None, \
            "error_message should be None"
        assert result.execution_time > 0, \
            "execution_time should be positive"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        api_response_content=st.text(min_size=1, max_size=500)
    )
    def test_api_success_response_stdout_matches_api_content(
        self, user_prompt, api_response_content
    ):
        """
        Property 43: API 执行成功响应 - stdout 内容与 API 响应完全匹配
        
        For any successful API call, the stdout field in ExecutionResult
        should exactly match the content returned by the API, with no
        modifications or truncation.
        
        Validates: Requirements 14.7
        """
        # Test Claude API
        claude_executor = ClaudeAPIExecutor(api_key="test_key")
        mock_response = Mock()
        mock_response.content = [Mock(text=api_response_content)]
        
        with patch.object(claude_executor.client.messages, 'create', return_value=mock_response):
            claude_result = claude_executor.execute(user_prompt)
        
        assert claude_result.stdout == api_response_content, \
            "Claude API stdout should exactly match API response content"
        
        # Test Gemini API
        gemini_executor = GeminiAPIExecutor(api_key="test_key")
        mock_response = Mock()
        mock_response.text = api_response_content
        
        with patch.object(gemini_executor.client, 'generate_content', return_value=mock_response):
            gemini_result = gemini_executor.execute(user_prompt)
        
        assert gemini_result.stdout == api_response_content, \
            "Gemini API stdout should exactly match API response content"
        
        # Test OpenAI API
        openai_executor = OpenAIAPIExecutor(api_key="test_key")
        mock_choice = Mock()
        mock_choice.message.content = api_response_content
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_executor.client.chat.completions, 'create', return_value=mock_response):
            openai_result = openai_executor.execute(user_prompt)
        
        assert openai_result.stdout == api_response_content, \
            "OpenAI API stdout should exactly match API response content"
