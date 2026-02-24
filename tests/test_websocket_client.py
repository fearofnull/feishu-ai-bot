"""
WebSocketClient 单元测试

测试 WebSocket 客户端的连接管理功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.websocket_client import WebSocketClient
from feishu_bot.event_handler import EventHandler
import lark_oapi as lark


class TestWebSocketClient:
    """WebSocketClient 单元测试类"""
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_init_success(self, mock_ws_client_class):
        """测试成功初始化"""
        # 创建 mock 事件处理器
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        # 创建 mock WebSocket 客户端
        mock_ws_instance = Mock()
        mock_ws_client_class.return_value = mock_ws_instance
        
        # 初始化 WebSocketClient
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        # 验证
        assert client.app_id == "test_app_id"
        assert client.app_secret == "test_app_secret"
        assert client.event_handler is mock_event_handler
        assert client.log_level == lark.LogLevel.INFO
        assert client._ws_client is mock_ws_instance
        
        # 验证调用
        mock_event_handler.build.assert_called_once()
        mock_ws_client_class.assert_called_once_with(
            "test_app_id",
            "test_app_secret",
            event_handler=mock_dispatcher,
            log_level=lark.LogLevel.INFO
        )
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_init_with_custom_log_level(self, mock_ws_client_class):
        """测试使用自定义日志级别初始化"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        mock_ws_client_class.return_value = Mock()
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler,
            log_level=lark.LogLevel.DEBUG
        )
        
        assert client.log_level == lark.LogLevel.DEBUG
        mock_ws_client_class.assert_called_once_with(
            "test_app_id",
            "test_app_secret",
            event_handler=mock_dispatcher,
            log_level=lark.LogLevel.DEBUG
        )
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_init_failure(self, mock_ws_client_class):
        """测试初始化失败"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        # 模拟 WebSocket 客户端创建失败
        mock_ws_client_class.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            WebSocketClient(
                app_id="test_app_id",
                app_secret="test_app_secret",
                event_handler=mock_event_handler
            )
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_start_success(self, mock_ws_client_class):
        """测试成功启动连接"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        mock_ws_instance = Mock()
        mock_ws_client_class.return_value = mock_ws_instance
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        # 启动连接
        client.start()
        
        # 验证调用
        mock_ws_instance.start.assert_called_once()
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_start_failure(self, mock_ws_client_class):
        """测试启动连接失败"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        mock_ws_instance = Mock()
        mock_ws_instance.start.side_effect = Exception("Connection error")
        mock_ws_client_class.return_value = mock_ws_instance
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        with pytest.raises(Exception, match="Connection error"):
            client.start()
    
    def test_start_without_init(self):
        """测试未初始化时启动连接"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        with patch('feishu_bot.websocket_client.lark.ws.Client') as mock_ws_client_class:
            mock_ws_client_class.return_value = Mock()
            client = WebSocketClient(
                app_id="test_app_id",
                app_secret="test_app_secret",
                event_handler=mock_event_handler
            )
            
            # 手动设置为 None 模拟未初始化
            client._ws_client = None
            
            with pytest.raises(RuntimeError, match="WebSocket client not initialized"):
                client.start()
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_stop_with_stop_method(self, mock_ws_client_class):
        """测试停止连接（客户端有 stop 方法）"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        mock_ws_instance = Mock()
        mock_ws_instance.stop = Mock()  # 添加 stop 方法
        mock_ws_client_class.return_value = mock_ws_instance
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        # 停止连接
        client.stop()
        
        # 验证调用
        mock_ws_instance.stop.assert_called_once()
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_stop_without_stop_method(self, mock_ws_client_class):
        """测试停止连接（客户端没有 stop 方法）"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        mock_ws_instance = Mock(spec=[])  # 没有 stop 方法
        mock_ws_client_class.return_value = mock_ws_instance
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        # 停止连接（不应该抛出异常）
        client.stop()
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_stop_with_error(self, mock_ws_client_class):
        """测试停止连接时发生错误"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        mock_ws_instance = Mock()
        mock_ws_instance.stop = Mock(side_effect=Exception("Stop error"))
        mock_ws_client_class.return_value = mock_ws_instance
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        # 停止连接（不应该抛出异常，只记录日志）
        client.stop()
    
    @patch('feishu_bot.websocket_client.lark.ws.Client')
    def test_stop_when_not_initialized(self, mock_ws_client_class):
        """测试未初始化时停止连接"""
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        mock_ws_client_class.return_value = Mock()
        
        client = WebSocketClient(
            app_id="test_app_id",
            app_secret="test_app_secret",
            event_handler=mock_event_handler
        )
        
        # 手动设置为 None
        client._ws_client = None
        
        # 停止连接（不应该抛出异常）
        client.stop()
