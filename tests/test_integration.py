"""
集成测试 - 测试完整的消息处理流程
"""
import pytest
import os
import json
from unittest.mock import Mock, MagicMock, patch
from feishu_bot.config import BotConfig
from feishu_bot.feishu_bot import FeishuBot
from feishu_bot.models import ExecutionResult


@pytest.fixture
def test_config():
    """创建测试配置"""
    return BotConfig(
        app_id="test_app_id",
        app_secret="test_app_secret",
        target_directory="./test_dir",
        ai_timeout=60,
        cache_size=100,
        session_storage_path="./test_data/sessions.json",
        max_session_messages=10,
        session_timeout=3600,
        openai_api_key="test_openai_key",
        openai_base_url="https://api-inference.modelscope.cn/v1",
        openai_model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        default_provider="openai",
        default_layer="api"
    )


@pytest.fixture
def mock_lark_client():
    """创建模拟的飞书客户端"""
    client = Mock()
    client.im.v1.message.create = Mock(return_value=Mock(success=lambda: True))
    client.im.v1.message.reply = Mock(return_value=Mock(success=lambda: True))
    client.im.v1.message.get = Mock(return_value=Mock(
        success=lambda: True,
        data=Mock(
            message=Mock(
                message_type="text",
                content=json.dumps({"text": "quoted message"})
            )
        )
    ))
    return client


@pytest.fixture
def mock_message_event():
    """创建模拟的消息事件"""
    event = Mock()
    event.event.message.message_id = "test_message_id"
    event.event.message.chat_id = "test_chat_id"
    event.event.message.chat_type = "p2p"
    event.event.message.message_type = "text"
    event.event.message.content = json.dumps({"text": "测试消息"})
    event.event.message.parent_id = None
    event.event.sender.sender_id.user_id = "test_user_id"
    return event


class TestIntegration:
    """集成测试类"""
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_bot_initialization(self, mock_ws_client, mock_lark_client, test_config):
        """测试机器人初始化"""
        # 创建机器人实例
        bot = FeishuBot(test_config)
        
        # 验证核心组件已初始化
        assert bot.config == test_config
        assert bot.dedup_cache is not None
        assert bot.message_handler is not None
        assert bot.session_manager is not None
        assert bot.command_parser is not None
        assert bot.executor_registry is not None
        assert bot.smart_router is not None
        assert bot.response_formatter is not None
        assert bot.message_sender is not None
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_executor_registration(self, mock_ws_client, mock_lark_client, test_config):
        """测试执行器注册"""
        bot = FeishuBot(test_config)
        
        # 验证 OpenAI API 执行器已注册
        assert bot.executor_registry.is_executor_available("openai", "api")
        
        # 获取执行器元数据
        metadata = bot.executor_registry.get_executor_metadata("openai", "api")
        assert metadata.name == "OpenAI API"
        assert metadata.provider == "openai"
        assert metadata.layer == "api"
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_message_deduplication(self, mock_ws_client, mock_lark_client, test_config, mock_message_event):
        """测试消息去重"""
        bot = FeishuBot(test_config)
        bot.client = mock_lark_client()
        
        # 第一次处理消息
        bot._handle_message_receive(mock_message_event)
        
        # 第二次处理相同消息（应该被跳过）
        bot._handle_message_receive(mock_message_event)
        
        # 验证消息已被标记为已处理
        assert bot.dedup_cache.is_processed("test_message_id")
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_session_command_new(self, mock_ws_client, mock_lark_client, test_config):
        """测试 /new 命令"""
        bot = FeishuBot(test_config)
        bot.client = mock_lark_client()
        
        # 创建初始会话
        session1 = bot.session_manager.get_or_create_session("test_user")
        session1_id = session1.session_id
        
        # 处理 /new 命令
        result = bot._handle_session_command(
            "test_user", "/new", "p2p", "test_chat", "test_msg"
        )
        
        assert result is True
        
        # 验证新会话已创建
        session2 = bot.session_manager.get_or_create_session("test_user")
        assert session2.session_id != session1_id
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_session_command_info(self, mock_ws_client, mock_lark_client, test_config):
        """测试 /session 命令"""
        bot = FeishuBot(test_config)
        bot.client = mock_lark_client()
        
        # 创建会话并添加消息
        bot.session_manager.get_or_create_session("test_user")
        bot.session_manager.add_message("test_user", "user", "test message")
        
        # 处理 /session 命令
        result = bot._handle_session_command(
            "test_user", "/session", "p2p", "test_chat", "test_msg"
        )
        
        assert result is True
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_command_parsing_explicit(self, mock_ws_client, mock_lark_client, test_config):
        """测试显式命令解析"""
        bot = FeishuBot(test_config)
        
        # 测试 @openai 前缀
        parsed = bot.command_parser.parse_command("@openai 你好")
        assert parsed.provider == "openai"
        assert parsed.execution_layer == "api"
        assert parsed.message == "你好"
        assert parsed.explicit is True
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_command_parsing_cli_keywords(self, mock_ws_client, mock_lark_client, test_config):
        """测试 CLI 关键词检测"""
        bot = FeishuBot(test_config)
        
        # 测试包含 CLI 关键词的消息
        parsed = bot.command_parser.parse_command("查看代码")
        assert bot.command_parser.detect_cli_keywords(parsed.message) is True
        
        # 测试不包含 CLI 关键词的消息
        parsed = bot.command_parser.parse_command("你好")
        assert bot.command_parser.detect_cli_keywords(parsed.message) is False
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_smart_routing_explicit(self, mock_ws_client, mock_lark_client, test_config):
        """测试智能路由 - 显式指定"""
        bot = FeishuBot(test_config)
        
        # 显式指定 OpenAI API
        parsed = bot.command_parser.parse_command("@openai 你好")
        executor = bot.smart_router.route(parsed)
        
        assert executor.get_provider_name() == "openai-api"
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_response_formatting_success(self, mock_ws_client, mock_lark_client, test_config):
        """测试响应格式化 - 成功"""
        bot = FeishuBot(test_config)
        
        response = bot.response_formatter.format_response(
            "测试消息", "AI 回复内容"
        )
        
        assert "测试消息" in response
        assert "AI 回复内容" in response
        assert "AI 输出" in response
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_response_formatting_error(self, mock_ws_client, mock_lark_client, test_config):
        """测试响应格式化 - 错误"""
        bot = FeishuBot(test_config)
        
        response = bot.response_formatter.format_error(
            "测试消息", "执行失败：超时"
        )
        
        assert "测试消息" in response
        assert "执行失败" in response
        assert "超时" in response
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_message_sending_p2p(self, mock_ws_client, mock_lark_client_class, test_config):
        """测试消息发送 - 私聊"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success = Mock(return_value=True)
        mock_client.im.v1.message.create = Mock(return_value=mock_response)
        mock_lark_client_class.builder.return_value.app_id.return_value.app_secret.return_value.build.return_value = mock_client
        
        bot = FeishuBot(test_config)
        
        # 发送私聊消息
        bot.message_sender.send_message(
            "p2p", "test_chat_id", "test_message_id", "测试内容"
        )
        
        # 验证调用了 create 方法
        assert mock_client.im.v1.message.create.called
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_message_sending_group(self, mock_ws_client, mock_lark_client_class, test_config):
        """测试消息发送 - 群聊"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.success = Mock(return_value=True)
        mock_client.im.v1.message.reply = Mock(return_value=mock_response)
        mock_lark_client_class.builder.return_value.app_id.return_value.app_secret.return_value.build.return_value = mock_client
        
        bot = FeishuBot(test_config)
        
        # 发送群聊消息
        bot.message_sender.send_message(
            "group", "test_chat_id", "test_message_id", "测试内容"
        )
        
        # 验证调用了 reply 方法
        assert mock_client.im.v1.message.reply.called
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_session_history_update(self, mock_ws_client, mock_lark_client, test_config):
        """测试会话历史更新"""
        bot = FeishuBot(test_config)
        
        # 清空初始会话（如果有）
        session = bot.session_manager.get_or_create_session("test_user")
        session.messages.clear()
        
        # 添加消息到会话
        bot.session_manager.add_message("test_user", "user", "用户消息")
        bot.session_manager.add_message("test_user", "assistant", "AI 回复")
        
        # 获取对话历史
        history = bot.session_manager.get_conversation_history("test_user")
        
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "用户消息"
        assert history[1].role == "assistant"
        assert history[1].content == "AI 回复"
    
    @patch('feishu_bot.feishu_bot.LarkClient')
    @patch('feishu_bot.feishu_bot.WebSocketClient')
    def test_session_auto_rotation(self, mock_ws_client, mock_lark_client, test_config):
        """测试会话自动轮换"""
        # 设置最大消息数为 5
        test_config.max_session_messages = 5
        bot = FeishuBot(test_config)
        
        # 创建会话
        session1 = bot.session_manager.get_or_create_session("test_user")
        session1_id = session1.session_id
        
        # 添加 5 条消息
        for i in range(5):
            bot.session_manager.add_message("test_user", "user", f"消息 {i}")
        
        # 再添加一条消息，应该触发轮换
        bot.session_manager.add_message("test_user", "user", "触发轮换")
        
        # 获取当前会话
        session2 = bot.session_manager.get_or_create_session("test_user")
        
        # 验证会话已轮换
        assert session2.session_id != session1_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
