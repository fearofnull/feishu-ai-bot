"""
API 对话历史上下文属性测试

使用 Hypothesis 进行基于属性的测试，验证 API 执行器正确处理对话历史上下文的通用正确性属性。
测试所有三个 API 执行器（Claude API、Gemini API、OpenAI API）的对话历史上下文行为。
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, MagicMock, call
from feishu_bot.claude_api_executor import ClaudeAPIExecutor
from feishu_bot.gemini_api_executor import GeminiAPIExecutor
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.models import Message, ExecutionResult


class TestAPIConversationHistoryProperties:
    """API 对话历史上下文属性测试类"""
    
    # Feature: feishu-ai-bot, Property 45: API 对话历史上下文
    # Validates: Requirements 14.8, 15.1, 15.6
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_claude_api_includes_conversation_history_in_request(
        self, user_prompt, history_messages
    ):
        """
        Property 45: API 对话历史上下文 - Claude API 在请求中包含对话历史
        
        For any API call with conversation history, the executor should
        include all historical messages in the API request, properly formatted
        according to the API's requirements.
        
        Validates: Requirements 14.8, 15.1, 15.6
        """
        executor = ClaudeAPIExecutor(api_key="test_key")
        
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        # Mock the Anthropic client
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        
        with patch.object(executor.client.messages, 'create', return_value=mock_response) as mock_create:
            result = executor.execute(user_prompt, conversation_history)
            
            # Verify the API was called
            assert mock_create.called, "API should be called"
            
            # Get the actual call arguments
            call_args = mock_create.call_args
            messages_sent = call_args.kwargs['messages']
            
            # Verify all history messages are included
            assert len(messages_sent) == len(history_messages) + 1, \
                f"Expected {len(history_messages) + 1} messages in API request, got {len(messages_sent)}"
            
            # Verify history messages are in correct order
            for i, (expected_role, expected_content) in enumerate(history_messages):
                assert messages_sent[i]['role'] == expected_role, \
                    f"Message {i}: expected role '{expected_role}', got '{messages_sent[i]['role']}'"
                assert messages_sent[i]['content'] == expected_content, \
                    f"Message {i}: expected content '{expected_content}', got '{messages_sent[i]['content']}'"
            
            # Verify current prompt is the last message
            assert messages_sent[-1]['role'] == 'user', \
                "Last message should be user prompt"
            assert messages_sent[-1]['content'] == user_prompt, \
                "Last message should contain current prompt"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_gemini_api_includes_conversation_history_in_request(
        self, user_prompt, history_messages
    ):
        """
        Property 45: API 对话历史上下文 - Gemini API 在请求中包含对话历史
        
        For any API call with conversation history, the Gemini executor should
        use chat mode and include all historical messages, with "assistant"
        role converted to "model" role.
        
        Validates: Requirements 14.8, 15.1, 15.3, 15.6
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        # Mock the Gemini client
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_chat = Mock()
        mock_chat.send_message = Mock(return_value=mock_response)
        
        with patch.object(executor.client, 'start_chat', return_value=mock_chat) as mock_start_chat:
            result = executor.execute(user_prompt, conversation_history)
            
            # Verify chat mode was used
            assert mock_start_chat.called, "Chat mode should be used for conversation history"
            
            # Get the history passed to start_chat
            call_args = mock_start_chat.call_args
            history_sent = call_args.kwargs['history']
            
            # Verify all history messages are included
            assert len(history_sent) == len(history_messages), \
                f"Expected {len(history_messages)} messages in chat history, got {len(history_sent)}"
            
            # Verify history messages are properly formatted
            for i, (expected_role, expected_content) in enumerate(history_messages):
                # Gemini converts "assistant" to "model"
                expected_gemini_role = "user" if expected_role == "user" else "model"
                assert history_sent[i]['role'] == expected_gemini_role, \
                    f"Message {i}: expected role '{expected_gemini_role}', got '{history_sent[i]['role']}'"
                assert history_sent[i]['parts'] == [expected_content], \
                    f"Message {i}: expected parts '[{expected_content}]', got '{history_sent[i]['parts']}'"
            
            # Verify current prompt was sent via send_message
            assert mock_chat.send_message.called, "Current prompt should be sent via send_message"
            sent_prompt = mock_chat.send_message.call_args[0][0]
            assert sent_prompt == user_prompt, \
                f"Expected prompt '{user_prompt}', got '{sent_prompt}'"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_openai_api_includes_conversation_history_in_request(
        self, user_prompt, history_messages
    ):
        """
        Property 45: API 对话历史上下文 - OpenAI API 在请求中包含对话历史
        
        For any API call with conversation history, the OpenAI executor should
        include all historical messages in the API request, maintaining
        "user" and "assistant" roles.
        
        Validates: Requirements 14.8, 15.1, 15.4, 15.6
        """
        executor = OpenAIAPIExecutor(api_key="test_key")
        
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        # Mock the OpenAI client
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(executor.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            result = executor.execute(user_prompt, conversation_history)
            
            # Verify the API was called
            assert mock_create.called, "API should be called"
            
            # Get the actual call arguments
            call_args = mock_create.call_args
            messages_sent = call_args.kwargs['messages']
            
            # Verify all history messages are included
            assert len(messages_sent) == len(history_messages) + 1, \
                f"Expected {len(history_messages) + 1} messages in API request, got {len(messages_sent)}"
            
            # Verify history messages are in correct order
            for i, (expected_role, expected_content) in enumerate(history_messages):
                assert messages_sent[i]['role'] == expected_role, \
                    f"Message {i}: expected role '{expected_role}', got '{messages_sent[i]['role']}'"
                assert messages_sent[i]['content'] == expected_content, \
                    f"Message {i}: expected content '{expected_content}', got '{messages_sent[i]['content']}'"
            
            # Verify current prompt is the last message
            assert messages_sent[-1]['role'] == 'user', \
                "Last message should be user prompt"
            assert messages_sent[-1]['content'] == user_prompt, \
                "Last message should contain current prompt"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_conversation_history_order_preserved_in_api_request(
        self, user_prompt, history_messages
    ):
        """
        Property 45: API 对话历史上下文 - 对话历史顺序在 API 请求中保持一致
        
        For any conversation history, the order of messages in the API request
        should exactly match the order in the session's conversation history.
        
        Validates: Requirements 15.6
        """
        # Test with Claude API
        claude_executor = ClaudeAPIExecutor(api_key="test_key")
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        
        with patch.object(claude_executor.client.messages, 'create', return_value=mock_response) as mock_create:
            claude_executor.execute(user_prompt, conversation_history)
            
            messages_sent = mock_create.call_args.kwargs['messages']
            
            # Verify order is preserved (excluding the last user prompt)
            for i in range(len(history_messages)):
                expected_role, expected_content = history_messages[i]
                assert messages_sent[i]['role'] == expected_role, \
                    f"Claude API: Message {i} role order not preserved"
                assert messages_sent[i]['content'] == expected_content, \
                    f"Claude API: Message {i} content order not preserved"
        
        # Test with OpenAI API
        openai_executor = OpenAIAPIExecutor(api_key="test_key")
        
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_executor.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            openai_executor.execute(user_prompt, conversation_history)
            
            messages_sent = mock_create.call_args.kwargs['messages']
            
            # Verify order is preserved
            for i in range(len(history_messages)):
                expected_role, expected_content = history_messages[i]
                assert messages_sent[i]['role'] == expected_role, \
                    f"OpenAI API: Message {i} role order not preserved"
                assert messages_sent[i]['content'] == expected_content, \
                    f"OpenAI API: Message {i} content order not preserved"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200)
    )
    def test_empty_conversation_history_only_sends_current_prompt(
        self, user_prompt
    ):
        """
        Property 45: API 对话历史上下文 - 空对话历史时仅发送当前提示
        
        When conversation history is empty or None, the API request should
        only contain the current user message.
        
        Validates: Requirements 15.5
        """
        # Test with Claude API
        claude_executor = ClaudeAPIExecutor(api_key="test_key")
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        
        with patch.object(claude_executor.client.messages, 'create', return_value=mock_response) as mock_create:
            # Test with None history
            claude_executor.execute(user_prompt, conversation_history=None)
            messages_sent = mock_create.call_args.kwargs['messages']
            assert len(messages_sent) == 1, \
                "Claude API: Should only send current prompt when history is None"
            assert messages_sent[0]['role'] == 'user', \
                "Claude API: Single message should be user role"
            assert messages_sent[0]['content'] == user_prompt, \
                "Claude API: Single message should contain user prompt"
            
            # Test with empty history
            claude_executor.execute(user_prompt, conversation_history=[])
            messages_sent = mock_create.call_args.kwargs['messages']
            assert len(messages_sent) == 1, \
                "Claude API: Should only send current prompt when history is empty"
        
        # Test with Gemini API
        gemini_executor = GeminiAPIExecutor(api_key="test_key")
        
        mock_response = Mock()
        mock_response.text = "Test response"
        
        with patch.object(gemini_executor.client, 'generate_content', return_value=mock_response) as mock_generate:
            # Test with None history (should use generate_content, not chat mode)
            gemini_executor.execute(user_prompt, conversation_history=None)
            assert mock_generate.called, \
                "Gemini API: Should use generate_content for None history"
            sent_prompt = mock_generate.call_args[0][0]
            assert sent_prompt == user_prompt, \
                "Gemini API: Should send user prompt directly"
            
            # Test with empty history
            gemini_executor.execute(user_prompt, conversation_history=[])
            assert mock_generate.called, \
                "Gemini API: Should use generate_content for empty history"
        
        # Test with OpenAI API
        openai_executor = OpenAIAPIExecutor(api_key="test_key")
        
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_executor.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            # Test with None history
            openai_executor.execute(user_prompt, conversation_history=None)
            messages_sent = mock_create.call_args.kwargs['messages']
            assert len(messages_sent) == 1, \
                "OpenAI API: Should only send current prompt when history is None"
            assert messages_sent[0]['role'] == 'user', \
                "OpenAI API: Single message should be user role"
            assert messages_sent[0]['content'] == user_prompt, \
                "OpenAI API: Single message should contain user prompt"
            
            # Test with empty history
            openai_executor.execute(user_prompt, conversation_history=[])
            messages_sent = mock_create.call_args.kwargs['messages']
            assert len(messages_sent) == 1, \
                "OpenAI API: Should only send current prompt when history is empty"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        num_history_messages=st.integers(min_value=1, max_value=20)
    )
    def test_conversation_history_length_matches_session_history(
        self, user_prompt, num_history_messages
    ):
        """
        Property 45: API 对话历史上下文 - 对话历史长度与会话历史匹配
        
        For any conversation history, the number of historical messages
        included in the API request should match the number of messages
        in the session's conversation history.
        
        Validates: Requirements 14.8, 15.1
        """
        # Create conversation history with specific length
        conversation_history = []
        for i in range(num_history_messages):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Message {i}"
            conversation_history.append(Message(role=role, content=content, timestamp=1000000 + i))
        
        # Test with Claude API
        claude_executor = ClaudeAPIExecutor(api_key="test_key")
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        
        with patch.object(claude_executor.client.messages, 'create', return_value=mock_response) as mock_create:
            claude_executor.execute(user_prompt, conversation_history)
            messages_sent = mock_create.call_args.kwargs['messages']
            
            # Should have all history + current prompt
            assert len(messages_sent) == num_history_messages + 1, \
                f"Claude API: Expected {num_history_messages + 1} messages, got {len(messages_sent)}"
        
        # Test with Gemini API
        gemini_executor = GeminiAPIExecutor(api_key="test_key")
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_chat = Mock()
        mock_chat.send_message = Mock(return_value=mock_response)
        
        with patch.object(gemini_executor.client, 'start_chat', return_value=mock_chat) as mock_start_chat:
            gemini_executor.execute(user_prompt, conversation_history)
            history_sent = mock_start_chat.call_args.kwargs['history']
            
            # Should have all history (current prompt sent separately)
            assert len(history_sent) == num_history_messages, \
                f"Gemini API: Expected {num_history_messages} messages in history, got {len(history_sent)}"
        
        # Test with OpenAI API
        openai_executor = OpenAIAPIExecutor(api_key="test_key")
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_executor.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            openai_executor.execute(user_prompt, conversation_history)
            messages_sent = mock_create.call_args.kwargs['messages']
            
            # Should have all history + current prompt
            assert len(messages_sent) == num_history_messages + 1, \
                f"OpenAI API: Expected {num_history_messages + 1} messages, got {len(messages_sent)}"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_conversation_history_does_not_modify_session_history(
        self, user_prompt, history_messages
    ):
        """
        Property 45: API 对话历史上下文 - 不修改会话历史
        
        For any conversation history, the API executor should not modify
        the original conversation history list or Message objects.
        
        Validates: Requirements 14.8
        """
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        # Store original values
        original_length = len(conversation_history)
        original_messages = [(msg.role, msg.content, msg.timestamp) for msg in conversation_history]
        
        # Test with Claude API
        claude_executor = ClaudeAPIExecutor(api_key="test_key")
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        
        with patch.object(claude_executor.client.messages, 'create', return_value=mock_response):
            claude_executor.execute(user_prompt, conversation_history)
        
        # Verify history was not modified
        assert len(conversation_history) == original_length, \
            "Claude API: Should not modify history list length"
        
        for i, msg in enumerate(conversation_history):
            orig_role, orig_content, orig_timestamp = original_messages[i]
            assert msg.role == orig_role, \
                f"Claude API: Message {i} role should not be modified"
            assert msg.content == orig_content, \
                f"Claude API: Message {i} content should not be modified"
            assert msg.timestamp == orig_timestamp, \
                f"Claude API: Message {i} timestamp should not be modified"
        
        # Test with Gemini API
        gemini_executor = GeminiAPIExecutor(api_key="test_key")
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_chat = Mock()
        mock_chat.send_message = Mock(return_value=mock_response)
        
        with patch.object(gemini_executor.client, 'start_chat', return_value=mock_chat):
            gemini_executor.execute(user_prompt, conversation_history)
        
        # Verify history was not modified
        assert len(conversation_history) == original_length, \
            "Gemini API: Should not modify history list length"
        
        for i, msg in enumerate(conversation_history):
            orig_role, orig_content, orig_timestamp = original_messages[i]
            assert msg.role == orig_role, \
                f"Gemini API: Message {i} role should not be modified"
            assert msg.content == orig_content, \
                f"Gemini API: Message {i} content should not be modified"
            assert msg.timestamp == orig_timestamp, \
                f"Gemini API: Message {i} timestamp should not be modified"
        
        # Test with OpenAI API
        openai_executor = OpenAIAPIExecutor(api_key="test_key")
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(openai_executor.client.chat.completions, 'create', return_value=mock_response):
            openai_executor.execute(user_prompt, conversation_history)
        
        # Verify history was not modified
        assert len(conversation_history) == original_length, \
            "OpenAI API: Should not modify history list length"
        
        for i, msg in enumerate(conversation_history):
            orig_role, orig_content, orig_timestamp = original_messages[i]
            assert msg.role == orig_role, \
                f"OpenAI API: Message {i} role should not be modified"
            assert msg.content == orig_content, \
                f"OpenAI API: Message {i} content should not be modified"
            assert msg.timestamp == orig_timestamp, \
                f"OpenAI API: Message {i} timestamp should not be modified"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_gemini_api_converts_assistant_to_model_role(
        self, user_prompt, history_messages
    ):
        """
        Property 45: API 对话历史上下文 - Gemini API 将 assistant 角色转换为 model
        
        For any conversation history with "assistant" role messages,
        Gemini API executor should convert them to "model" role in the
        API request, as required by Gemini API format.
        
        Validates: Requirements 15.3
        """
        executor = GeminiAPIExecutor(api_key="test_key")
        
        # Create conversation history with assistant messages
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        # Mock the Gemini client
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_chat = Mock()
        mock_chat.send_message = Mock(return_value=mock_response)
        
        with patch.object(executor.client, 'start_chat', return_value=mock_chat) as mock_start_chat:
            executor.execute(user_prompt, conversation_history)
            
            history_sent = mock_start_chat.call_args.kwargs['history']
            
            # Verify role conversion
            for i, (original_role, _) in enumerate(history_messages):
                expected_role = "user" if original_role == "user" else "model"
                actual_role = history_sent[i]['role']
                
                assert actual_role == expected_role, \
                    f"Message {i}: expected role '{expected_role}', got '{actual_role}'"
                
                # Specifically check assistant -> model conversion
                if original_role == "assistant":
                    assert actual_role == "model", \
                        f"Message {i}: 'assistant' role should be converted to 'model', got '{actual_role}'"
    
    @settings(max_examples=20, deadline=None)
    @given(
        user_prompt=st.text(min_size=1, max_size=200),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=100)
            ),
            min_size=1,
            max_size=10
        ),
        provider=st.sampled_from(["claude", "openai"])
    )
    def test_claude_and_openai_preserve_user_assistant_roles(
        self, user_prompt, history_messages, provider
    ):
        """
        Property 45: API 对话历史上下文 - Claude 和 OpenAI 保持 user/assistant 角色
        
        For any conversation history, Claude and OpenAI API executors
        should preserve "user" and "assistant" roles without conversion.
        
        Validates: Requirements 15.2, 15.4
        """
        if provider == "claude":
            executor = ClaudeAPIExecutor(api_key="test_key")
            mock_response = Mock()
            mock_response.content = [Mock(text="Test response")]
            mock_method = executor.client.messages.create
            patch_target = 'create'
        else:  # openai
            executor = OpenAIAPIExecutor(api_key="test_key")
            mock_choice = Mock()
            mock_choice.message.content = "Test response"
            mock_response = Mock()
            mock_response.choices = [mock_choice]
            mock_method = executor.client.chat.completions.create
            patch_target = 'create'
        
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        with patch.object(mock_method.__self__, patch_target, return_value=mock_response) as mock_create:
            executor.execute(user_prompt, conversation_history)
            
            messages_sent = mock_create.call_args.kwargs['messages']
            
            # Verify roles are preserved (excluding last user prompt)
            for i, (original_role, _) in enumerate(history_messages):
                actual_role = messages_sent[i]['role']
                assert actual_role == original_role, \
                    f"{provider} API: Message {i} role should be preserved as '{original_role}', got '{actual_role}'"
