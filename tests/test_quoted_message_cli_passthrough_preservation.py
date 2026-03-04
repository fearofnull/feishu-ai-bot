# -*- coding: utf-8 -*-
"""
引用消息CLI传递保留性测试

此测试用于验证非bug条件下的行为保持不变。
测试在未修复的代码上运行，确认基线行为正确。

关键: 此测试必须在未修复代码上通过 - 通过确认基线行为正确
这些测试验证修复不会引入回归

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**
"""
import json
import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings, assume
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

from feishu_bot.feishu_bot import FeishuBot
from feishu_bot.config import BotConfig
from feishu_bot.models import ExecutionResult


class TestQuotedMessageCLIPassthroughPreservation:
    """引用消息CLI传递保留性测试类
    
    Property 2: Preservation - Non-Quoted Message Behavior
    
    测试非bug条件下的行为保持不变：
    1. 非引用消息发送给CLI执行器 - 应该只接收当前消息
    2. 引用消息发送给API执行器 - 应该接收组合消息（已经正常工作）
    """
    
    def test_non_quoted_message_to_cli_executor_receives_only_current_message(self):
        """
        Property 2.1: Preservation - 非引用消息到CLI执行器
        测试用例: 发送非引用消息给CLI执行器
        
        **Validates: Requirement 3.1**
        
        期望行为: CLI执行器应该只接收当前消息（不进行消息组合）
        这是现有的正确行为，修复后必须保持不变
        """
        # 准备测试数据
        current_message_text = "hello"
        
        # 创建模拟配置
        mock_config = Mock(spec=BotConfig)
        mock_config.app_id = "test_app_id"
        mock_config.app_secret = "test_app_secret"
        mock_config.cache_size = 100
        mock_config.session_storage_path = "./data/test_sessions.json"
        mock_config.max_session_messages = 10
        mock_config.session_timeout = 3600
        mock_config.default_provider = "gemini"
        mock_config.default_layer = "api"
        mock_config.default_cli_provider = "gemini"
        mock_config.use_ai_intent_classification = False
        mock_config.ai_timeout = 600
        mock_config.target_directory = "/test/target"
        mock_config.gemini_cli_target_dir = "/test/target"
        mock_config.claude_cli_target_dir = None
        mock_config.claude_api_key = None
        mock_config.gemini_api_key = None
        mock_config.openai_api_key = None
        mock_config.openai_base_url = None
        mock_config.openai_model = None
        
        # 捕获传递给CLI执行器的参数
        captured_user_prompt = None
        
        def mock_cli_execute(user_prompt, additional_params=None):
            nonlocal captured_user_prompt
            captured_user_prompt = user_prompt
            print(f"\n[CLI EXECUTOR] Received user_prompt:")
            print(f"  {user_prompt[:200] if user_prompt else 'None'}...")
            return ExecutionResult(
                success=True,
                stdout="Execution successful",
                stderr="",
                error_message=None,
                execution_time=1.0
            )
        
        with patch('feishu_bot.feishu_bot.LarkClient') as mock_lark_client_class, \
             patch('feishu_bot.feishu_bot.WebSocketClient'), \
             patch('feishu_bot.executors.gemini_cli_executor.GeminiCLIExecutor') as mock_gemini_cli_class:
            
            # 设置飞书客户端mock
            mock_lark_client = Mock()
            mock_lark_client_class.builder.return_value.app_id.return_value.app_secret.return_value.build.return_value = mock_lark_client
            
            # 设置CLI执行器mock
            mock_gemini_cli = Mock()
            mock_gemini_cli.execute.side_effect = mock_cli_execute
            mock_gemini_cli.get_provider_name.return_value = "gemini-cli"
            mock_gemini_cli.verify_directory.return_value = True
            mock_gemini_cli._verify_directory_exists.return_value = True
            mock_gemini_cli_class.return_value = mock_gemini_cli
            
            # 创建机器人实例
            bot = FeishuBot(mock_config)
            
            # Mock the smart router to return our mocked CLI executor
            bot.smart_router.route = Mock(return_value=mock_gemini_cli)
            
            # 构造消息接收事件（无parent_id，即非引用消息）
            event_data = Mock(spec=P2ImMessageReceiveV1)
            event_data.event = Mock()
            event_data.event.message = Mock()
            event_data.event.message.message_id = "msg_test_123"
            event_data.event.message.chat_id = "chat_test_123"
            event_data.event.message.chat_type = "p2p"
            event_data.event.message.message_type = "text"
            event_data.event.message.content = json.dumps({"text": f"@gemini-cli {current_message_text}"})
            # 关键: 没有parent_id，表示这不是引用消息
            event_data.event.message.parent_id = None
            event_data.event.sender = Mock()
            event_data.event.sender.sender_id = Mock()
            event_data.event.sender.sender_id.user_id = "user_test_123"
            
            # 调用消息处理方法
            print(f"\n[TEST] Calling _handle_message_receive for non-quoted message...")
            bot._handle_message_receive(event_data)
            
            # 验证CLI执行器被调用
            print(f"\n[TEST] Verifying CLI executor was called...")
            assert mock_gemini_cli.execute.called, "CLI executor should be called"
            
            # 验证传递给CLI执行器的消息
            print(f"\n[VERIFICATION]")
            print(f"Expected message (current only):")
            print(f"  {current_message_text}")
            print(f"\nActual captured user_prompt:")
            print(f"  {captured_user_prompt}")
            
            # 关键断言: CLI执行器应该只接收当前消息，不包含引用内容
            assert captured_user_prompt is not None, "CLI executor should receive a message"
            
            # 验证不包含引用消息标记
            assert "引用消息" not in captured_user_prompt, \
                f"CLI executor should NOT receive quoted content marker for non-quoted messages. Got: {captured_user_prompt}"
            
            # 验证只包含当前消息
            assert current_message_text in captured_user_prompt, \
                f"CLI executor should receive current message '{current_message_text}'. Got: {captured_user_prompt}"
            
            print(f"\n✅ Test passed! CLI executor received only the current message (no combination).")
    
    def test_quoted_message_to_api_executor_receives_combined_message(self):
        """
        Property 2.2: Preservation - 引用消息到API执行器
        测试用例: 引用卡片消息并发送给API执行器
        
        **Validates: Requirement 3.2**
        
        期望行为: API执行器应该接收组合消息（包含引用内容和当前消息）
        这是现有的正确行为，修复后必须保持不变
        """
        # 准备测试数据
        quoted_card_content = "Error: File not found"
        current_message_text = "explain this"
        parent_id = "parent_msg_123"
        
        # 期望的组合消息
        expected_combined_message = f"引用消息：[卡片消息]\n{quoted_card_content}\n\n当前消息：{current_message_text}"
        
        # 创建模拟配置
        mock_config = Mock(spec=BotConfig)
        mock_config.app_id = "test_app_id"
        mock_config.app_secret = "test_app_secret"
        mock_config.cache_size = 100
        mock_config.session_storage_path = "./data/test_sessions.json"
        mock_config.max_session_messages = 10
        mock_config.session_timeout = 3600
        mock_config.default_provider = "openai"
        mock_config.default_layer = "api"
        mock_config.default_cli_provider = "gemini"
        mock_config.use_ai_intent_classification = False
        mock_config.ai_timeout = 600
        mock_config.target_directory = "/test/target"
        mock_config.gemini_cli_target_dir = "/test/target"
        mock_config.claude_cli_target_dir = None
        mock_config.claude_api_key = None
        mock_config.gemini_api_key = "test_key"
        mock_config.openai_api_key = "test_key"
        mock_config.openai_base_url = None
        mock_config.openai_model = "gpt-4"
        
        # 捕获传递给API执行器的参数
        captured_user_prompt = None
        
        def mock_api_execute(user_prompt, conversation_history=None):
            nonlocal captured_user_prompt
            captured_user_prompt = user_prompt
            print(f"\n[API EXECUTOR] Received user_prompt:")
            print(f"  {user_prompt[:200] if user_prompt else 'None'}...")
            return ExecutionResult(
                success=True,
                stdout="Execution successful",
                stderr="",
                error_message=None,
                execution_time=1.0
            )
        
        with patch('feishu_bot.feishu_bot.LarkClient') as mock_lark_client_class, \
             patch('feishu_bot.feishu_bot.WebSocketClient'), \
             patch('feishu_bot.executors.openai_api_executor.OpenAIAPIExecutor') as mock_openai_api_class:
            
            # 设置飞书客户端mock
            mock_lark_client = Mock()
            mock_lark_client_class.builder.return_value.app_id.return_value.app_secret.return_value.build.return_value = mock_lark_client
            
            # 模拟引用的卡片消息API响应
            mock_quoted_response = Mock()
            mock_quoted_response.success.return_value = True
            mock_quoted_response.data.message.message_type = "interactive"
            mock_quoted_response.data.message.content = json.dumps({
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",
                            "content": quoted_card_content
                        }
                    }
                ]
            })
            mock_lark_client.im.v1.message.get.return_value = mock_quoted_response
            
            # 设置API执行器mock
            mock_openai_api = Mock()
            mock_openai_api.execute.side_effect = mock_api_execute
            mock_openai_api.get_provider_name.return_value = "openai-api"
            mock_openai_api_class.return_value = mock_openai_api
            
            # 创建机器人实例
            bot = FeishuBot(mock_config)
            
            # Mock the smart router to return our mocked API executor
            bot.smart_router.route = Mock(return_value=mock_openai_api)
            
            # 构造消息接收事件（有parent_id，即引用消息）
            event_data = Mock(spec=P2ImMessageReceiveV1)
            event_data.event = Mock()
            event_data.event.message = Mock()
            event_data.event.message.message_id = "msg_test_123"
            event_data.event.message.chat_id = "chat_test_123"
            event_data.event.message.chat_type = "p2p"
            event_data.event.message.message_type = "text"
            event_data.event.message.content = json.dumps({"text": f"@openai-api {current_message_text}"})
            event_data.event.message.parent_id = parent_id  # 引用消息
            event_data.event.sender = Mock()
            event_data.event.sender.sender_id = Mock()
            event_data.event.sender.sender_id.user_id = "user_test_123"
            
            # 调用消息处理方法
            print(f"\n[TEST] Calling _handle_message_receive for quoted message to API executor...")
            bot._handle_message_receive(event_data)
            
            # 验证API执行器被调用
            print(f"\n[TEST] Verifying API executor was called...")
            assert mock_openai_api.execute.called, "API executor should be called"
            
            # 验证传递给API执行器的消息
            print(f"\n[VERIFICATION]")
            print(f"Expected combined message:")
            print(f"  {expected_combined_message}")
            print(f"\nActual captured user_prompt:")
            print(f"  {captured_user_prompt}")
            
            # 关键断言: API执行器应该接收完整的组合消息
            assert captured_user_prompt is not None, "API executor should receive a message"
            
            # 验证包含引用内容标记
            assert "引用消息" in captured_user_prompt, \
                f"API executor should receive quoted content marker. Got: {captured_user_prompt[:200]}"
            
            # 验证包含引用的卡片内容
            assert quoted_card_content in captured_user_prompt, \
                f"API executor should receive quoted card content '{quoted_card_content}'. Got: {captured_user_prompt[:200]}"
            
            # 验证包含当前消息标记
            assert "当前消息" in captured_user_prompt, \
                f"API executor should receive current message marker. Got: {captured_user_prompt[:200]}"
            
            # 验证包含当前消息文本
            assert current_message_text in captured_user_prompt, \
                f"API executor should receive current message '{current_message_text}'. Got: {captured_user_prompt[:200]}"
            
            print(f"\n✅ Test passed! API executor received the complete combined message (existing behavior preserved).")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
