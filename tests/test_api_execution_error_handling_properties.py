"""
API 执行错误处理属性测试

使用 Hypothesis 进行基于属性的测试，验证 API 执行错误处理的通用正确性属性。
测试所有三个 API 执行器（Claude API、Gemini API、OpenAI API）的错误处理行为。
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
from feishu_bot.claude_api_executor import ClaudeAPIExecutor
from feishu_bot.gemini_api_executor import GeminiAPIExecutor
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.models import ExecutionResult
import anthropic
import openai


class TestAPIExecutionErrorHandlingProperties:
    """API 执行错误处理属性测试类"""
    
    # Feature: feishu-ai-bot, Property 44: API 执行错误处理
    # Validates: Requirements 14.4, 14.5, 14.6
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_message=st.text(min_size=1, max_size=200)
    )
    def test_claude_api_error_returns_failure_result(self, user_prompt, error_message):
        """
        Property 44: API 执行错误处理 - Claude API 错误返回失败结果
        
        For any Claude API error (APIError), the executor should return
        an ExecutionResult with:
        - success=False
        - error_message is not None and contains error information
        - stderr contains error information
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Mock the Anthropic client to raise APIError
        # anthropic.APIError requires message, request, and body parameters
        mock_request = Mock()
        api_error = anthropic.APIError(message=error_message, request=mock_request, body=None)
        
        with patch.object(executor.client.messages, 'create', side_effect=api_error):
            result = executor.execute(user_prompt)
        
        # Verify error result structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object even on error"
        
        assert result.success is False, \
            "API error should result in success=False"
        
        assert result.error_message is not None, \
            "error_message should not be None on API error"
        
        assert len(result.error_message) > 0, \
            "error_message should be non-empty on API error"
        
        assert "Claude API error" in result.error_message or "error" in result.error_message.lower(), \
            f"error_message should indicate API error, got: {result.error_message}"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error information"
        
        assert result.stdout == "", \
            "stdout should be empty on error"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_message=st.text(min_size=1, max_size=200)
    )
    def test_gemini_api_error_returns_failure_result(self, user_prompt, error_message):
        """
        Property 44: API 执行错误处理 - Gemini API 错误返回失败结果
        
        For any Gemini API error (Exception), the executor should return
        an ExecutionResult with:
        - success=False
        - error_message is not None and contains error information
        - stderr contains error information
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Mock the Gemini client to raise Exception
        api_error = Exception(error_message)
        
        with patch.object(executor.client, 'generate_content', side_effect=api_error):
            result = executor.execute(user_prompt)
        
        # Verify error result structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object even on error"
        
        assert result.success is False, \
            "API error should result in success=False"
        
        assert result.error_message is not None, \
            "error_message should not be None on API error"
        
        assert len(result.error_message) > 0, \
            "error_message should be non-empty on API error"
        
        assert "Gemini API error" in result.error_message or "error" in result.error_message.lower(), \
            f"error_message should indicate API error, got: {result.error_message}"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error information"
        
        assert result.stdout == "", \
            "stdout should be empty on error"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_message=st.text(min_size=1, max_size=200)
    )
    def test_openai_api_error_returns_failure_result(self, user_prompt, error_message):
        """
        Property 44: API 执行错误处理 - OpenAI API 错误返回失败结果
        
        For any OpenAI API error (APIError), the executor should return
        an ExecutionResult with:
        - success=False
        - error_message is not None and contains error information
        - stderr contains error information
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Mock the OpenAI client to raise APIError
        # openai.APIError requires message, request, and body parameters
        mock_request = Mock()
        api_error = openai.APIError(message=error_message, request=mock_request, body=None)
        
        with patch.object(executor.client.chat.completions, 'create', side_effect=api_error):
            result = executor.execute(user_prompt)
        
        # Verify error result structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object even on error"
        
        assert result.success is False, \
            "API error should result in success=False"
        
        assert result.error_message is not None, \
            "error_message should not be None on API error"
        
        assert len(result.error_message) > 0, \
            "error_message should be non-empty on API error"
        
        assert "OpenAI API error" in result.error_message or "error" in result.error_message.lower(), \
            f"error_message should indicate API error, got: {result.error_message}"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error information"
        
        assert result.stdout == "", \
            "stdout should be empty on error"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        provider=st.sampled_from(["claude", "gemini", "openai"])
    )
    def test_all_api_executors_error_response_consistency(self, user_prompt, provider):
        """
        Property 44: API 执行错误处理 - 所有 API 执行器错误响应一致性
        
        For any API error across all three executors (Claude, Gemini, OpenAI),
        the ExecutionResult structure should be consistent:
        - All have success=False
        - All have non-None error_message
        - All have non-empty stderr
        - All have empty stdout
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        error_message = "API quota exceeded"
        
        # Create executor and simulate error based on provider
        if provider == "claude":
            executor = ClaudeAPIExecutor(api_key="test_key")
            mock_request = Mock()
            api_error = anthropic.APIError(message=error_message, request=mock_request, body=None)
            with patch.object(executor.client.messages, 'create', side_effect=api_error):
                result = executor.execute(user_prompt)
        elif provider == "gemini":
            executor = GeminiAPIExecutor(api_key="test_key")
            api_error = Exception(error_message)
            with patch.object(executor.client, 'generate_content', side_effect=api_error):
                result = executor.execute(user_prompt)
        else:  # openai
            executor = OpenAIAPIExecutor(api_key="test_key")
            mock_request = Mock()
            api_error = openai.APIError(message=error_message, request=mock_request, body=None)
            with patch.object(executor.client.chat.completions, 'create', side_effect=api_error):
                result = executor.execute(user_prompt)
        
        # Verify consistent error response structure across all providers
        assert isinstance(result, ExecutionResult), \
            f"{provider} executor should return ExecutionResult on error"
        assert result.success is False, \
            f"{provider} executor should have success=False on error"
        assert result.error_message is not None, \
            f"{provider} executor should have non-None error_message"
        assert len(result.error_message) > 0, \
            f"{provider} executor should have non-empty error_message"
        assert len(result.stderr) > 0, \
            f"{provider} executor should have non-empty stderr"
        assert result.stdout == "", \
            f"{provider} executor should have empty stdout on error"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_claude_api_network_error_handling(self, user_prompt):
        """
        Property 44: API 执行错误处理 - Claude API 网络错误处理
        
        For any network-related error (connection error, timeout),
        the executor should return an ExecutionResult with success=False
        and descriptive error information.
        
        Validates: Requirements 14.5, 14.6
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Simulate network error
        network_error = Exception("Connection timeout")
        
        with patch.object(executor.client.messages, 'create', side_effect=network_error):
            result = executor.execute(user_prompt)
        
        # Verify error handling
        assert result.success is False, \
            "Network error should result in success=False"
        
        assert result.error_message is not None, \
            "error_message should not be None on network error"
        
        assert "error" in result.error_message.lower() or "timeout" in result.error_message.lower(), \
            f"error_message should indicate network/timeout error, got: {result.error_message}"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error information"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_gemini_api_network_error_handling(self, user_prompt):
        """
        Property 44: API 执行错误处理 - Gemini API 网络错误处理
        
        For any network-related error (connection error, timeout),
        the executor should return an ExecutionResult with success=False
        and descriptive error information.
        
        Validates: Requirements 14.5, 14.6
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Simulate network error
        network_error = Exception("Connection timeout")
        
        with patch.object(executor.client, 'generate_content', side_effect=network_error):
            result = executor.execute(user_prompt)
        
        # Verify error handling
        assert result.success is False, \
            "Network error should result in success=False"
        
        assert result.error_message is not None, \
            "error_message should not be None on network error"
        
        assert "error" in result.error_message.lower() or "timeout" in result.error_message.lower(), \
            f"error_message should indicate network/timeout error, got: {result.error_message}"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error information"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_openai_api_network_error_handling(self, user_prompt):
        """
        Property 44: API 执行错误处理 - OpenAI API 网络错误处理
        
        For any network-related error (connection error, timeout),
        the executor should return an ExecutionResult with success=False
        and descriptive error information.
        
        Validates: Requirements 14.5, 14.6
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Simulate network error
        network_error = Exception("Connection timeout")
        
        with patch.object(executor.client.chat.completions, 'create', side_effect=network_error):
            result = executor.execute(user_prompt)
        
        # Verify error handling
        assert result.success is False, \
            "Network error should result in success=False"
        
        assert result.error_message is not None, \
            "error_message should not be None on network error"
        
        assert "error" in result.error_message.lower() or "timeout" in result.error_message.lower(), \
            f"error_message should indicate network/timeout error, got: {result.error_message}"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error information"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_type=st.sampled_from([
            "quota_exceeded",
            "model_unavailable",
            "invalid_request",
            "authentication_error"
        ])
    )
    def test_claude_api_various_error_types(self, user_prompt, error_type):
        """
        Property 44: API 执行错误处理 - Claude API 各种错误类型处理
        
        For any type of API error (quota exceeded, model unavailable, etc.),
        the executor should return an ExecutionResult with success=False
        and appropriate error information.
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Create error message based on error type
        error_messages = {
            "quota_exceeded": "API quota exceeded",
            "model_unavailable": "Model is currently unavailable",
            "invalid_request": "Invalid request parameters",
            "authentication_error": "Authentication failed"
        }
        error_message = error_messages[error_type]
        
        # Simulate API error
        mock_request = Mock()
        api_error = anthropic.APIError(message=error_message, request=mock_request, body=None)
        
        with patch.object(executor.client.messages, 'create', side_effect=api_error):
            result = executor.execute(user_prompt)
        
        # Verify error handling for all error types
        assert result.success is False, \
            f"{error_type} should result in success=False"
        
        assert result.error_message is not None, \
            f"error_message should not be None for {error_type}"
        
        assert len(result.error_message) > 0, \
            f"error_message should be non-empty for {error_type}"
        
        assert len(result.stderr) > 0, \
            f"stderr should contain error information for {error_type}"
        
        assert result.stdout == "", \
            f"stdout should be empty for {error_type}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_type=st.sampled_from([
            "quota_exceeded",
            "model_unavailable",
            "invalid_request",
            "authentication_error"
        ])
    )
    def test_gemini_api_various_error_types(self, user_prompt, error_type):
        """
        Property 44: API 执行错误处理 - Gemini API 各种错误类型处理
        
        For any type of API error (quota exceeded, model unavailable, etc.),
        the executor should return an ExecutionResult with success=False
        and appropriate error information.
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Create error message based on error type
        error_messages = {
            "quota_exceeded": "API quota exceeded",
            "model_unavailable": "Model is currently unavailable",
            "invalid_request": "Invalid request parameters",
            "authentication_error": "Authentication failed"
        }
        error_message = error_messages[error_type]
        
        # Simulate API error
        api_error = Exception(error_message)
        
        with patch.object(executor.client, 'generate_content', side_effect=api_error):
            result = executor.execute(user_prompt)
        
        # Verify error handling for all error types
        assert result.success is False, \
            f"{error_type} should result in success=False"
        
        assert result.error_message is not None, \
            f"error_message should not be None for {error_type}"
        
        assert len(result.error_message) > 0, \
            f"error_message should be non-empty for {error_type}"
        
        assert len(result.stderr) > 0, \
            f"stderr should contain error information for {error_type}"
        
        assert result.stdout == "", \
            f"stdout should be empty for {error_type}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_type=st.sampled_from([
            "quota_exceeded",
            "model_unavailable",
            "invalid_request",
            "authentication_error"
        ])
    )
    def test_openai_api_various_error_types(self, user_prompt, error_type):
        """
        Property 44: API 执行错误处理 - OpenAI API 各种错误类型处理
        
        For any type of API error (quota exceeded, model unavailable, etc.),
        the executor should return an ExecutionResult with success=False
        and appropriate error information.
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Create error message based on error type
        error_messages = {
            "quota_exceeded": "API quota exceeded",
            "model_unavailable": "Model is currently unavailable",
            "invalid_request": "Invalid request parameters",
            "authentication_error": "Authentication failed"
        }
        error_message = error_messages[error_type]
        
        # Simulate API error
        mock_request = Mock()
        api_error = openai.APIError(message=error_message, request=mock_request, body=None)
        
        with patch.object(executor.client.chat.completions, 'create', side_effect=api_error):
            result = executor.execute(user_prompt)
        
        # Verify error handling for all error types
        assert result.success is False, \
            f"{error_type} should result in success=False"
        
        assert result.error_message is not None, \
            f"error_message should not be None for {error_type}"
        
        assert len(result.error_message) > 0, \
            f"error_message should be non-empty for {error_type}"
        
        assert len(result.stderr) > 0, \
            f"stderr should contain error information for {error_type}"
        
        assert result.stdout == "", \
            f"stdout should be empty for {error_type}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        provider=st.sampled_from(["claude", "gemini", "openai"])
    )
    def test_api_error_stderr_contains_error_details(self, user_prompt, provider):
        """
        Property 44: API 执行错误处理 - stderr 包含错误详情
        
        For any API error, the stderr field should contain the error details
        from the exception, providing useful debugging information.
        
        Validates: Requirements 14.6
        """
        error_message = "Detailed API error information"
        
        # Create executor and simulate error based on provider
        if provider == "claude":
            executor = ClaudeAPIExecutor(api_key="test_key")
            mock_request = Mock()
            api_error = anthropic.APIError(message=error_message, request=mock_request, body=None)
            with patch.object(executor.client.messages, 'create', side_effect=api_error):
                result = executor.execute(user_prompt)
        elif provider == "gemini":
            executor = GeminiAPIExecutor(api_key="test_key")
            api_error = Exception(error_message)
            with patch.object(executor.client, 'generate_content', side_effect=api_error):
                result = executor.execute(user_prompt)
        else:  # openai
            executor = OpenAIAPIExecutor(api_key="test_key")
            mock_request = Mock()
            api_error = openai.APIError(message=error_message, request=mock_request, body=None)
            with patch.object(executor.client.chat.completions, 'create', side_effect=api_error):
                result = executor.execute(user_prompt)
        
        # Verify stderr contains error details
        assert len(result.stderr) > 0, \
            f"{provider} executor should have non-empty stderr on error"
        
        # stderr should contain some part of the error message
        assert error_message in result.stderr or "error" in result.stderr.lower(), \
            f"{provider} executor stderr should contain error details, got: {result.stderr}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        provider=st.sampled_from(["claude", "gemini", "openai"])
    )
    def test_api_error_execution_time_is_zero(self, user_prompt, provider):
        """
        Property 44: API 执行错误处理 - 错误时执行时间为零
        
        For any API error, the execution_time should be 0 since
        no successful execution occurred.
        
        Validates: Requirements 14.4
        """
        error_message = "API error"
        
        # Create executor and simulate error based on provider
        if provider == "claude":
            executor = ClaudeAPIExecutor(api_key="test_key")
            mock_request = Mock()
            api_error = anthropic.APIError(message=error_message, request=mock_request, body=None)
            with patch.object(executor.client.messages, 'create', side_effect=api_error):
                result = executor.execute(user_prompt)
        elif provider == "gemini":
            executor = GeminiAPIExecutor(api_key="test_key")
            api_error = Exception(error_message)
            with patch.object(executor.client, 'generate_content', side_effect=api_error):
                result = executor.execute(user_prompt)
        else:  # openai
            executor = OpenAIAPIExecutor(api_key="test_key")
            mock_request = Mock()
            api_error = openai.APIError(message=error_message, request=mock_request, body=None)
            with patch.object(executor.client.chat.completions, 'create', side_effect=api_error):
                result = executor.execute(user_prompt)
        
        # Verify execution_time is 0 on error
        assert result.execution_time == 0, \
            f"{provider} executor should have execution_time=0 on error, got {result.execution_time}"
