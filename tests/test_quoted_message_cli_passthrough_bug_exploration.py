"""
引用消息CLI传递Bug条件探索性测试

此测试用于在未修复的代码上暴露反例，演示bug的存在。
测试编码了期望行为 - 在实现修复后通过时将验证修复正确。

关键: 此测试必须在未修复代码上失败 - 失败确认bug存在
不要在测试失败时尝试修复测试或代码

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""
import json
import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings, HealthCheck
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

from feishu_bot.feishu_bot import FeishuBot
from feishu_bot.config import BotConfig
from feishu_bot.models import ExecutionResult


class TestQuotedMessageCLIPassthroughBugExploration:
    """引用消息CLI传递Bug条件探索性测试类
    
    Property 1: Fault Condition - CLI Executors Receive Combined Messages
    
    测试当用户引用卡片消息并发送给CLI执行器时，CLI执行器应该接收到
    完整的组合消息（格式："引用消息：{quoted}\n\n当前消息：{current}"）
    
    期望行为: CLI执行器接收包含引用内容和当前消息的完整组合消息
    当前行为（bug）: CLI执行器仅接收当前消息，不包含引用内容
    """
    
    def test_quoted_card_to_cli_executor_receives_combined_message(self):
        """
        Property 1: Fault Condition - CLI Executors Receive Combined Messages
        测试用例: 引用卡片消息并发送给CLI执行器
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
        
        期望行为: CLI执行器接收完整的组合消息（包含引用内容和当前消息）
        当前行为（bug）: CLI执行器仅接收当前消息，不包含引用内容
        
        这个测试在未修复的代码上应该失败，证明bug存在。
        """
        # 准备测试数据
        quoted_card_content = "Error: File not found"
        current_message_text = "explain this"
        parent_id = "parent_msg_123"
        
        # 期望的组合消息（使用单行格式和 >>> 分隔符，避免 CLI headless 模式的多行问题）
        expected_combined_message = f"引用消息：[卡片消息]\n{quoted_card_content} >>> 当前消息：{current_message_text}"
        
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
        mock_config.response_language = None  # 不添加语言指令
        
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
             patch('feishu_bot.feishu_bot.GeminiCLIExecutor') as mock_gemini_cli_class:
            
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
            
            # 设置CLI执行器mock - 在创建bot之前
            mock_gemini_cli = Mock()
            mock_gemini_cli.execute.side_effect = mock_cli_execute
            mock_gemini_cli.get_provider_name.return_value = "gemini-cli"
            mock_gemini_cli.verify_directory.return_value = True
            mock_gemini_cli._verify_directory_exists.return_value = True
            mock_gemini_cli.is_available.return_value = True  # 确保执行器可用
            mock_gemini_cli_class.return_value = mock_gemini_cli
            
            # 创建机器人实例
            bot = FeishuBot(mock_config)
            
            # 构造消息接收事件
            event_data = Mock(spec=P2ImMessageReceiveV1)
            event_data.event = Mock()
            event_data.event.message = Mock()
            event_data.event.message.message_id = "msg_test_123"
            event_data.event.message.chat_id = "chat_test_123"
            event_data.event.message.chat_type = "p2p"
            event_data.event.message.message_type = "text"
            event_data.event.message.content = json.dumps({"text": f"@gemini-cli {current_message_text}"})
            event_data.event.message.parent_id = parent_id  # 引用消息
            event_data.event.sender = Mock()
            event_data.event.sender.sender_id = Mock()
            event_data.event.sender.sender_id.user_id = "user_test_123"
            
            # 调用消息处理方法
            print(f"\n[TEST] Calling _handle_message_receive...")
            bot._handle_message_receive(event_data)
            
            # 验证CLI执行器被调用
            print(f"\n[TEST] Verifying CLI executor was called...")
            assert mock_gemini_cli.execute.called, "CLI executor should be called"
            
            # 验证传递给CLI执行器的消息
            print(f"\n[VERIFICATION]")
            print(f"Expected combined message:")
            print(f"  {expected_combined_message}")
            print(f"\nActual captured user_prompt:")
            print(f"  {captured_user_prompt}")
            
            # 关键断言: CLI执行器应该接收到完整的组合消息
            assert captured_user_prompt is not None, "CLI executor should receive a message"
            
            # 验证包含引用内容标记
            assert "引用消息" in captured_user_prompt, \
                f"CLI executor should receive quoted content marker. Got: {captured_user_prompt[:200]}"
            
            # 验证包含引用的卡片内容
            assert quoted_card_content in captured_user_prompt, \
                f"CLI executor should receive quoted card content '{quoted_card_content}'. Got: {captured_user_prompt[:200]}"
            
            # 验证包含当前消息标记
            assert "当前消息" in captured_user_prompt, \
                f"CLI executor should receive current message marker. Got: {captured_user_prompt[:200]}"
            
            # 验证包含当前消息文本
            assert current_message_text in captured_user_prompt, \
                f"CLI executor should receive current message '{current_message_text}'. Got: {captured_user_prompt[:200]}"
            
            # 验证完整的组合消息格式
            assert captured_user_prompt == expected_combined_message, \
                f"CLI executor should receive the exact combined message.\nExpected: {expected_combined_message}\nGot: {captured_user_prompt}"
            
            print(f"\n✅ Test passed! CLI executor received the complete combined message.")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
