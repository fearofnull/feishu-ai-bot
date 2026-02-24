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


class TestAPIExecutionErrorProperties:
    """API 执行错误处理属性测试类"""
    
    # Feature: feishu-ai-bot, Property 44: API 执行错误处理
    # Validates: Requirements 14.4, 14.5, 14.6
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_claude_api_missing_key_error(self, user_prompt):
        """
        Property 44: API 执行错误处理 - Claude API 密钥缺失错误
        
        For any API call with missing or invalid API key, the executor should return
        an ExecutionResult with:
        - success=False
        - stdout empty
        - stderr containing error details
        - error_message containing descriptive error information
        - execution_time=0
        
        Validates: Requirements 14.4
        """
        # Create executor with invalid API key
        executor = ClaudeAPIExecutor(api_key="invalid_key")
        
        # Mock the Anthropic client to raise AuthenticationError
        error_message = "Invalid API key"
        mock_error = anthropic.AuthenticationError(
            error_message,
            response=Mock(status_code=401),
            body=None
        )
        
        with patch.object(executor.client.messages, 'create', side_effect=mock_error):
            result = executor.execute(user_prompt)
        
        # Verify error response structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object even on error"
        
        assert result.success is False, \
            "API call with invalid key should have success=False"
        
        assert result.stdout == "", \
            f"stdout should be empty on error, got '{result.stdout}'"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error details"
        
        assert result.error_message is not None, \
            "error_message should not be None on error"
        
        assert "API key" in result.error_message or "Authentication" in result.error_message, \
            f"error_message should mention API key or authentication issue, got '{result.error_message}'"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on error, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_gemini_api_missing_key_error(self, user_prompt):
        """
        Property 44: API 执行错误处理 - Gemini API 密钥缺失错误
        
        For any Gemini API call with missing or invalid API key, the executor
        should return an ExecutionResult with success=False and descriptive error.
        
        Validates: Requirements 14.4
        """
        # Create executor with invalid API key
        executor = GeminiAPIExecutor(api_key="invalid_key")
        
        # Mock the Gemini client to raise an exception
        error_message = "API key not valid"
        
        with patch.object(executor.client, 'generate_content', side_effect=Exception(error_message)):
            result = executor.execute(user_prompt)
        
        # Verify error response structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object even on error"
        
        assert result.success is False, \
            "API call with invalid key should have success=False"
        
        assert result.stdout == "", \
            f"stdout should be empty on error, got '{result.stdout}'"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error details"
        
        assert result.error_message is not None, \
            "error_message should not be None on error"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on error, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_openai_api_missing_key_error(self, user_prompt):
        """
        Property 44: API 执行错误处理 - OpenAI API 密钥缺失错误
        
        For any OpenAI API call with missing or invalid API key, the executor
        should return an ExecutionResult with success=False and descriptive error.
        
        Validates: Requirements 14.4
        """
        # Create executor with invalid API key
        executor = OpenAIAPIExecutor(api_key="invalid_key")
        
        # Mock the OpenAI client to raise AuthenticationError
        error_message = "Incorrect API key provided"
        mock_error = openai.AuthenticationError(
            error_message,
            response=Mock(status_code=401),
            body=None
        )
        
        with patch.object(executor.client.chat.completions, 'create', side_effect=mock_error):
            result = executor.execute(user_prompt)
        
        # Verify error response structure
        assert isinstance(result, ExecutionResult), \
            "execute() should return an ExecutionResult object even on error"
        
        assert result.success is False, \
            "API call with invalid key should have success=False"
        
        assert result.stdout == "", \
            f"stdout should be empty on error, got '{result.stdout}'"
        
        assert len(result.stderr) > 0, \
            "stderr should contain error details"
        
        assert result.error_message is not None, \
            "error_message should not be None on error"
        
        assert "API key" in result.error_message or "Authentication" in result.error_message, \
            f"error_message should mention API key or authentication issue, got '{result.error_message}'"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on error, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_claude_api_timeout_error(self, user_prompt):
        """
        Property 44: API 执行错误处理 - Claude API 超时错误
        
        For any API call that times out, the executor should return
        an ExecutionResult with success=False and timeout error message.
        
        Validates: Requirements 14.5
        """
        executor = ClaudeAPIExecutor(api_key="test_key", timeout=1)
        
        # Mock the Anthropic client to raise APITimeoutError
        error_message = "Request timed out"
        mock_error = anthropic.APITimeoutError(request=Mock())
        
        with patch.object(executor.client.messages, 'create', side_effect=mock_error):
            result = executor.execute(user_prompt)
        
        # Verify timeout error response
        assert result.success is False, \
            "Timed out API call should have success=False"
        
        assert result.stdout == "", \
            "stdout should be empty on timeout"
        
        assert len(result.stderr) > 0, \
            "stderr should contain timeout error details"
        
        assert result.error_message is not None, \
            "error_message should not be None on timeout"
        
        assert "timeout" in result.error_message.lower() or "timed out" in result.error_message.lower(), \
            f"error_message should mention timeout, got '{result.error_message}'"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on timeout, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_gemini_api_timeout_error(self, user_prompt):
        """
        Property 44: API 执行错误处理 - Gemini API 超时错误
        
        For any Gemini API call that times out, the executor should return
        an ExecutionResult with success=False and timeout error message.
        
        Validates: Requirements 14.5
        """
        executor = GeminiAPIExecutor(api_key="test_key", timeout=1)
        
        # Mock the Gemini client to raise timeout exception
        error_message = "Request timed out after 1 seconds"
        
        with patch.object(executor.client, 'generate_content', side_effect=TimeoutError(error_message)):
            result = executor.execute(user_prompt)
        
        # Verify timeout error response
        assert result.success is False, \
            "Timed out API call should have success=False"
        
        assert result.stdout == "", \
            "stdout should be empty on timeout"
        
        assert len(result.stderr) > 0, \
            "stderr should contain timeout error details"
        
        assert result.error_message is not None, \
            "error_message should not be None on timeout"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on timeout, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_openai_api_timeout_error(self, user_prompt):
        """
        Property 44: API 执行错误处理 - OpenAI API 超时错误
        
        For any OpenAI API call that times out, the executor should return
        an ExecutionResult with success=False and timeout error message.
        
        Validates: Requirements 14.5
        """
        executor = OpenAIAPIExecutor(api_key="test_key", timeout=1)
        
        # Mock the OpenAI client to raise APITimeoutError
        error_message = "Request timed out"
        mock_error = openai.APITimeoutError(request=Mock())
        
        with patch.object(executor.client.chat.completions, 'create', side_effect=mock_error):
            result = executor.execute(user_prompt)
        
        # Verify timeout error response
        assert result.success is False, \
            "Timed out API call should have success=False"
        
        assert result.stdout == "", \
            "stdout should be empty on timeout"
        
        assert len(result.stderr) > 0, \
            "stderr should contain timeout error details"
        
        assert result.error_message is not None, \
            "error_message should not be None on timeout"
        
        assert "timeout" in result.error_message.lower() or "timed out" in result.error_message.lower(), \
            f"error_message should mention timeout, got '{result.error_message}'"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on timeout, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_type=st.sampled_from([
            "rate_limit_error",
            "quota_exceeded",
            "model_unavailable",
            "invalid_request"
        ])
    )
    def test_claude_api_various_errors(self, user_prompt, error_type):
        """
        Property 44: API 执行错误处理 - Claude API 各种错误类型
        
        For any API error (quota exceeded, model unavailable, rate limit, etc.),
        the executor should return an ExecutionResult with success=False and
        descriptive error message.
        
        Validates: Requirements 14.6
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Create appropriate error based on error_type
        if error_type == "rate_limit_error":
            error_message = "Rate limit exceeded"
            mock_error = anthropic.RateLimitError(
                error_message,
                response=Mock(status_code=429),
                body=None
            )
        elif error_type == "quota_exceeded":
            error_message = "You have exceeded your API quota"
            mock_error = anthropic.APIError(
                error_message,
                request=Mock(),
                body=None
            )
        elif error_type == "model_unavailable":
            error_message = "Model is currently unavailable"
            mock_error = anthropic.APIError(
                error_message,
                request=Mock(),
                body=None
            )
        else:  # invalid_request
            error_message = "Invalid request parameters"
            mock_error = anthropic.BadRequestError(
                error_message,
                response=Mock(status_code=400),
                body=None
            )
        
        with patch.object(executor.client.messages, 'create', side_effect=mock_error):
            result = executor.execute(user_prompt)
        
        # Verify error response
        assert result.success is False, \
            f"API call with {error_type} should have success=False"
        
        assert result.stdout == "", \
            f"stdout should be empty on {error_type}"
        
        assert len(result.stderr) > 0, \
            f"stderr should contain error details for {error_type}"
        
        assert result.error_message is not None, \
            f"error_message should not be None on {error_type}"
        
        assert "error" in result.error_message.lower() or "API" in result.error_message, \
            f"error_message should be descriptive for {error_type}, got '{result.error_message}'"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on {error_type}, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_type=st.sampled_from([
            "quota_exceeded",
            "model_unavailable",
            "invalid_request"
        ])
    )
    def test_gemini_api_various_errors(self, user_prompt, error_type):
        """
        Property 44: API 执行错误处理 - Gemini API 各种错误类型
        
        For any Gemini API error (quota exceeded, model unavailable, etc.),
        the executor should return an ExecutionResult with success=False and
        descriptive error message.
        
        Validates: Requirements 14.6
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Create appropriate error message based on error_type
        if error_type == "quota_exceeded":
            error_message = "Quota exceeded for quota metric"
        elif error_type == "model_unavailable":
            error_message = "Model is currently unavailable"
        else:  # invalid_request
            error_message = "Invalid request: missing required field"
        
        with patch.object(executor.client, 'generate_content', side_effect=Exception(error_message)):
            result = executor.execute(user_prompt)
        
        # Verify error response
        assert result.success is False, \
            f"API call with {error_type} should have success=False"
        
        assert result.stdout == "", \
            f"stdout should be empty on {error_type}"
        
        assert len(result.stderr) > 0, \
            f"stderr should contain error details for {error_type}"
        
        assert result.error_message is not None, \
            f"error_message should not be None on {error_type}"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on {error_type}, got {result.execution_time}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        error_type=st.sampled_from([
            "rate_limit_error",
            "quota_exceeded",
            "model_unavailable",
            "invalid_request"
        ])
    )
    def test_openai_api_various_errors(self, user_prompt, error_type):
        """
        Property 44: API 执行错误处理 - OpenAI API 各种错误类型
        
        For any OpenAI API error (quota exceeded, model unavailable, rate limit, etc.),
        the executor should return an ExecutionResult with success=False and
        descriptive error message.
        
        Validates: Requirements 14.6
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Create appropriate error based on error_type
        if error_type == "rate_limit_error":
            error_message = "Rate limit reached"
            mock_error = openai.RateLimitError(
                error_message,
                response=Mock(status_code=429),
                body=None
            )
        elif error_type == "quota_exceeded":
            error_message = "You exceeded your current quota"
            mock_error = openai.APIError(
                error_message,
                request=Mock(),
                body=None
            )
        elif error_type == "model_unavailable":
            error_message = "The model is currently overloaded"
            mock_error = openai.APIError(
                error_message,
                request=Mock(),
                body=None
            )
        else:  # invalid_request
            error_message = "Invalid request: missing required parameter"
            mock_error = openai.BadRequestError(
                error_message,
                response=Mock(status_code=400),
                body=None
            )
        
        with patch.object(executor.client.chat.completions, 'create', side_effect=mock_error):
            result = executor.execute(user_prompt)
        
        # Verify error response
        assert result.success is False, \
            f"API call with {error_type} should have success=False"
        
        assert result.stdout == "", \
            f"stdout should be empty on {error_type}"
        
        assert len(result.stderr) > 0, \
            f"stderr should contain error details for {error_type}"
        
        assert result.error_message is not None, \
            f"error_message should not be None on {error_type}"
        
        assert "error" in result.error_message.lower() or "API" in result.error_message, \
            f"error_message should be descriptive for {error_type}, got '{result.error_message}'"
        
        assert result.execution_time == 0, \
            f"execution_time should be 0 on {error_type}, got {result.execution_time}"
    
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
        - All have empty stdout
        - All have non-empty stderr
        - All have non-None error_message
        - All have execution_time=0
        
        Validates: Requirements 14.4, 14.5, 14.6
        """
        # Create executor and mock error based on provider
        if provider == "claude":
            executor = ClaudeAPIExecutor(api_key="test_key")
            mock_error = anthropic.APIError("API error", request=Mock(), body=None)
            with patch.object(executor.client.messages, 'create', side_effect=mock_error):
                result = executor.execute(user_prompt)
        elif provider == "gemini":
            executor = GeminiAPIExecutor(api_key="test_key")
            with patch.object(executor.client, 'generate_content', side_effect=Exception("API error")):
                result = executor.execute(user_prompt)
        else:  # openai
            executor = OpenAIAPIExecutor(api_key="test_key")
            mock_error = openai.APIError("API error", request=Mock(), body=None)
            with patch.object(executor.client.chat.completions, 'create', side_effect=mock_error):
                result = executor.execute(user_prompt)
        
        # Verify consistent error response structure across all providers
        assert isinstance(result, ExecutionResult), \
            f"{provider} executor should return ExecutionResult on error"
        assert result.success is False, \
            f"{provider} executor should have success=False on error"
        assert result.stdout == "", \
            f"{provider} executor should have empty stdout on error"
        assert len(result.stderr) > 0, \
            f"{provider} executor should have non-empty stderr on error"
        assert result.error_message is not None, \
            f"{provider} executor should have non-None error_message on error"
        assert result.execution_time == 0, \
            f"{provider} executor should have execution_time=0 on error"
