"""
EventHandler 单元测试

测试事件处理器的注册和构建功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.event_handler import EventHandler


class TestEventHandler:
    """EventHandler 单元测试类"""
    
    def test_init(self):
        """测试初始化"""
        handler = EventHandler()
        assert handler.verification_token == ""
        assert handler.encrypt_key == ""
        assert handler._message_handler is None
        assert handler._dispatcher is None
        
    def test_init_with_params(self):
        """测试带参数初始化"""
        handler = EventHandler(
            verification_token="test_token",
            encrypt_key="test_key"
        )
        assert handler.verification_token == "test_token"
        assert handler.encrypt_key == "test_key"
    
    def test_register_message_receive_handler(self):
        """测试注册消息接收处理器"""
        handler = EventHandler()
        mock_handler = Mock()
        
        handler.register_message_receive_handler(mock_handler)
        
        assert handler._message_handler is mock_handler
    
    @patch('feishu_bot.event_handler.lark.EventDispatcherHandler')
    def test_build_success(self, mock_dispatcher_class):
        """测试成功构建事件分发器"""
        handler = EventHandler()
        mock_handler = Mock()
        handler.register_message_receive_handler(mock_handler)
        
        # 模拟 builder 链式调用
        mock_builder = MagicMock()
        mock_dispatcher_class.builder.return_value = mock_builder
        mock_builder.register_p2_im_message_receive_v1.return_value = mock_builder
        mock_built_dispatcher = Mock()
        mock_builder.build.return_value = mock_built_dispatcher
        
        result = handler.build()
        
        # 验证调用链
        mock_dispatcher_class.builder.assert_called_once_with("", "")
        mock_builder.register_p2_im_message_receive_v1.assert_called_once_with(mock_handler)
        mock_builder.build.assert_called_once()
        
        assert result is mock_built_dispatcher
        assert handler._dispatcher is mock_built_dispatcher
    
    def test_build_without_handler(self):
        """测试未注册处理器时构建失败"""
        handler = EventHandler()
        
        with pytest.raises(ValueError, match="Message handler must be registered"):
            handler.build()
    
    @patch('feishu_bot.event_handler.lark.EventDispatcherHandler')
    def test_build_with_custom_tokens(self, mock_dispatcher_class):
        """测试使用自定义令牌构建"""
        handler = EventHandler(
            verification_token="custom_token",
            encrypt_key="custom_key"
        )
        mock_handler = Mock()
        handler.register_message_receive_handler(mock_handler)
        
        # 模拟 builder 链式调用
        mock_builder = MagicMock()
        mock_dispatcher_class.builder.return_value = mock_builder
        mock_builder.register_p2_im_message_receive_v1.return_value = mock_builder
        mock_builder.build.return_value = Mock()
        
        handler.build()
        
        # 验证使用了自定义令牌
        mock_dispatcher_class.builder.assert_called_once_with("custom_token", "custom_key")
    
    def test_get_dispatcher_before_build(self):
        """测试构建前获取分发器返回 None"""
        handler = EventHandler()
        assert handler.get_dispatcher() is None
    
    @patch('feishu_bot.event_handler.lark.EventDispatcherHandler')
    def test_get_dispatcher_after_build(self, mock_dispatcher_class):
        """测试构建后获取分发器"""
        handler = EventHandler()
        mock_handler = Mock()
        handler.register_message_receive_handler(mock_handler)
        
        # 模拟 builder 链式调用
        mock_builder = MagicMock()
        mock_dispatcher_class.builder.return_value = mock_builder
        mock_builder.register_p2_im_message_receive_v1.return_value = mock_builder
        mock_built_dispatcher = Mock()
        mock_builder.build.return_value = mock_built_dispatcher
        
        handler.build()
        
        assert handler.get_dispatcher() is mock_built_dispatcher
