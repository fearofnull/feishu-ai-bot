"""
OpenAI API 消息格式化属性测试

使用 Hypothesis 进行基于属性的测试，验证 OpenAI API 消息格式化的通用正确性属性
"""
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.openai_api_executor import OpenAIAPIExecutor
from feishu_bot.models import Message


class TestOpenAIAPIMessageFormattingProperties:
    """OpenAI API 消息格式化属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 使用虚拟 API key 进行测试（不会实际调用 API）
        self.executor = OpenAIAPIExecutor(api_key="test_key")
    
    # Feature: feishu-ai-bot, Property 42: OpenAI API 消息格式化
    # Validates: Requirements 15.4
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500)
    )
    def test_format_messages_with_no_history(self, user_prompt):
        """
        Property 42: OpenAI API 消息格式化 - 无对话历史
        
        For any user prompt without conversation history,
        format_messages should return a list with a single message
        containing role="user" and the user prompt as content.
        
        Validates: Requirements 15.4
        """
        messages = self.executor.format_messages(user_prompt, conversation_history=None)
        
        # Should return a list with exactly one message
        assert isinstance(messages, list), "format_messages should return a list"
        assert len(messages) == 1, \
            f"Expected 1 message for no history, got {len(messages)}"
        
        # The message should have correct structure
        message = messages[0]
        assert isinstance(message, dict), "Each message should be a dict"
        assert "role" in message, "Message should have 'role' field"
        assert "content" in message, "Message should have 'content' field"
        
        # The message should be a user message with the prompt
        assert message["role"] == "user", \
            f"Expected role 'user', got '{message['role']}'"
        assert message["content"] == user_prompt, \
            f"Expected content '{user_prompt}', got '{message['content']}'"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=200)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_format_messages_with_history(self, user_prompt, history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 包含对话历史
        
        For any user prompt with conversation history,
        format_messages should return a list containing all historical messages
        followed by the current user message, maintaining the order.
        
        Validates: Requirements 15.4
        """
        # Create Message objects from history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # Should return history + current message
        expected_length = len(history_messages) + 1
        assert len(messages) == expected_length, \
            f"Expected {expected_length} messages, got {len(messages)}"
        
        # Verify all historical messages are included in order
        for i, (expected_role, expected_content) in enumerate(history_messages):
            assert messages[i]["role"] == expected_role, \
                f"Message {i}: expected role '{expected_role}', got '{messages[i]['role']}'"
            assert messages[i]["content"] == expected_content, \
                f"Message {i}: expected content '{expected_content}', got '{messages[i]['content']}'"
        
        # Verify the last message is the current user prompt
        last_message = messages[-1]
        assert last_message["role"] == "user", \
            f"Last message should be 'user', got '{last_message['role']}'"
        assert last_message["content"] == user_prompt, \
            f"Last message content should be '{user_prompt}', got '{last_message['content']}'"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        num_history_messages=st.integers(min_value=0, max_value=20)
    )
    def test_format_messages_preserves_order(self, user_prompt, num_history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 保持消息顺序
        
        For any conversation history, format_messages should preserve
        the order of messages exactly as they appear in the history.
        
        Validates: Requirements 15.4
        """
        # Create alternating user/assistant messages
        conversation_history = []
        for i in range(num_history_messages):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Message {i}"
            conversation_history.append(Message(role=role, content=content, timestamp=1000000 + i))
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # Verify order is preserved
        for i, hist_msg in enumerate(conversation_history):
            assert messages[i]["role"] == hist_msg.role, \
                f"Message {i}: role order not preserved"
            assert messages[i]["content"] == hist_msg.content, \
                f"Message {i}: content order not preserved"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=200)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_format_messages_uses_correct_roles(self, user_prompt, history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 使用正确的角色
        
        For any conversation history, format_messages should use
        "user" and "assistant" roles as required by OpenAI API
        (same as Claude API format).
        
        Validates: Requirements 15.4
        """
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # All messages should have valid roles
        valid_roles = {"user", "assistant"}
        for i, message in enumerate(messages):
            assert message["role"] in valid_roles, \
                f"Message {i}: invalid role '{message['role']}', expected one of {valid_roles}"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=200)
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_format_messages_always_ends_with_user(self, user_prompt, history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 总是以用户消息结束
        
        For any conversation history and user prompt,
        format_messages should always end with a user message
        (the current prompt).
        
        Validates: Requirements 15.4
        """
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ] if history_messages else None
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # Last message should always be user
        assert len(messages) > 0, "Should have at least one message"
        assert messages[-1]["role"] == "user", \
            f"Last message should be 'user', got '{messages[-1]['role']}'"
        assert messages[-1]["content"] == user_prompt, \
            f"Last message should contain user prompt"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=200)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_format_messages_structure_consistency(self, user_prompt, history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 消息结构一致性
        
        For any formatted messages, each message should have
        the same structure: a dict with "role" and "content" keys.
        
        Validates: Requirements 15.4
        """
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # All messages should have consistent structure
        for i, message in enumerate(messages):
            assert isinstance(message, dict), \
                f"Message {i}: should be a dict, got {type(message)}"
            assert set(message.keys()) == {"role", "content"}, \
                f"Message {i}: should have exactly 'role' and 'content' keys, got {message.keys()}"
            assert isinstance(message["role"], str), \
                f"Message {i}: role should be string"
            assert isinstance(message["content"], str), \
                f"Message {i}: content should be string"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        num_messages=st.integers(min_value=1, max_value=50)
    )
    def test_format_messages_handles_long_history(self, user_prompt, num_messages):
        """
        Property 42: OpenAI API 消息格式化 - 处理长对话历史
        
        For any conversation history of varying lengths,
        format_messages should correctly format all messages
        without loss or corruption.
        
        Validates: Requirements 15.4
        """
        # Create a long conversation history
        conversation_history = []
        for i in range(num_messages):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Message number {i} with some content"
            conversation_history.append(Message(role=role, content=content, timestamp=1000000 + i))
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # Should have all history messages + current prompt
        assert len(messages) == num_messages + 1, \
            f"Expected {num_messages + 1} messages, got {len(messages)}"
        
        # Verify no messages were lost or corrupted
        for i in range(num_messages):
            assert messages[i]["content"] == f"Message number {i} with some content", \
                f"Message {i} content was corrupted or lost"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        special_chars=st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs",),  # Exclude surrogates
                min_codepoint=0x20,
                max_codepoint=0x10FFFF
            ),
            min_size=1,
            max_size=100
        )
    )
    def test_format_messages_handles_special_characters(self, user_prompt, special_chars):
        """
        Property 42: OpenAI API 消息格式化 - 处理特殊字符
        
        For any user prompt or history containing special characters,
        format_messages should preserve them without modification.
        
        Validates: Requirements 15.4
        """
        # Create history with special characters
        conversation_history = [
            Message(role="user", content=special_chars, timestamp=1000000),
            Message(role="assistant", content=f"Response to: {special_chars}", timestamp=1000001)
        ]
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # Verify special characters are preserved
        assert messages[0]["content"] == special_chars, \
            "Special characters in history should be preserved"
        assert messages[1]["content"] == f"Response to: {special_chars}", \
            "Special characters in history response should be preserved"
        assert messages[2]["content"] == user_prompt, \
            "Special characters in user prompt should be preserved"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500)
    )
    def test_format_messages_empty_history_equivalent_to_none(self, user_prompt):
        """
        Property 42: OpenAI API 消息格式化 - 空历史等同于无历史
        
        For any user prompt, format_messages with empty history list
        should produce the same result as with None history.
        
        Validates: Requirements 15.4
        """
        messages_with_none = self.executor.format_messages(user_prompt, conversation_history=None)
        messages_with_empty = self.executor.format_messages(user_prompt, conversation_history=[])
        
        # Both should produce identical results
        assert len(messages_with_none) == len(messages_with_empty), \
            "Empty history and None history should produce same length"
        assert messages_with_none == messages_with_empty, \
            "Empty history and None history should produce identical messages"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=200)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_format_messages_does_not_modify_input(self, user_prompt, history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 不修改输入
        
        For any conversation history, format_messages should not
        modify the input history list or Message objects.
        
        Validates: Requirements 15.4
        """
        # Create conversation history
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        # Store original values
        original_length = len(conversation_history)
        original_messages = [(msg.role, msg.content, msg.timestamp) for msg in conversation_history]
        
        # Call format_messages
        self.executor.format_messages(user_prompt, conversation_history)
        
        # Verify input was not modified
        assert len(conversation_history) == original_length, \
            "format_messages should not modify history list length"
        
        for i, msg in enumerate(conversation_history):
            orig_role, orig_content, orig_timestamp = original_messages[i]
            assert msg.role == orig_role, \
                f"Message {i}: role should not be modified"
            assert msg.content == orig_content, \
                f"Message {i}: content should not be modified"
            assert msg.timestamp == orig_timestamp, \
                f"Message {i}: timestamp should not be modified"
    
    @settings(max_examples=100)
    @given(
        user_prompts=st.lists(
            st.text(min_size=1, max_size=200),
            min_size=2,
            max_size=5
        )
    )
    def test_format_messages_idempotent_for_same_input(self, user_prompts):
        """
        Property 42: OpenAI API 消息格式化 - 相同输入产生相同输出
        
        For any user prompt and history, calling format_messages
        multiple times with the same input should produce identical results.
        
        Validates: Requirements 15.4
        """
        # Create a conversation history
        conversation_history = []
        for i, prompt in enumerate(user_prompts[:-1]):
            conversation_history.append(Message(role="user", content=prompt, timestamp=1000000 + i * 2))
            conversation_history.append(Message(role="assistant", content=f"Response {i}", timestamp=1000001 + i * 2))
        
        current_prompt = user_prompts[-1]
        
        # Call format_messages multiple times
        result1 = self.executor.format_messages(current_prompt, conversation_history)
        result2 = self.executor.format_messages(current_prompt, conversation_history)
        result3 = self.executor.format_messages(current_prompt, conversation_history)
        
        # All results should be identical
        assert result1 == result2, "First and second calls should produce identical results"
        assert result2 == result3, "Second and third calls should produce identical results"
        assert result1 == result3, "First and third calls should produce identical results"
    
    @settings(max_examples=100)
    @given(
        user_prompt=st.text(min_size=1, max_size=500),
        history_messages=st.lists(
            st.tuples(
                st.sampled_from(["user", "assistant"]),
                st.text(min_size=1, max_size=200)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_format_messages_role_preservation(self, user_prompt, history_messages):
        """
        Property 42: OpenAI API 消息格式化 - 角色保持不变
        
        For any conversation history with user and assistant messages,
        format_messages should preserve the roles exactly as they are
        (unlike Gemini which converts assistant to model).
        
        Validates: Requirements 15.4
        """
        conversation_history = [
            Message(role=role, content=content, timestamp=1000000 + i)
            for i, (role, content) in enumerate(history_messages)
        ]
        
        messages = self.executor.format_messages(user_prompt, conversation_history)
        
        # Verify roles are preserved exactly
        for i, (expected_role, _) in enumerate(history_messages):
            assert messages[i]["role"] == expected_role, \
                f"Message {i}: role should be preserved as '{expected_role}', got '{messages[i]['role']}'"
        
        # Verify no role conversion happened (unlike Gemini)
        assistant_count_input = sum(1 for role, _ in history_messages if role == "assistant")
        assistant_count_output = sum(1 for msg in messages[:-1] if msg["role"] == "assistant")
        assert assistant_count_input == assistant_count_output, \
            "All assistant roles should be preserved without conversion"
