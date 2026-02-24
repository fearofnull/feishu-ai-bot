"""
WebSocket 事件路由属性测试

Property 20: WebSocket 事件路由
For any 通过 WebSocket 接收的消息事件，Event_Handler 应该调用注册的消息接收处理器，
并传递完整的事件数据。

Validates: Requirements 9.3
"""
import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch, MagicMock
from feishu_bot.event_handler import EventHandler
from feishu_bot.websocket_client import WebSocketClient
import lark_oapi as lark


# 生成测试数据的策略
@st.composite
def message_event_data(draw):
    """生成消息事件数据"""
    return {
        'message_id': draw(st.text(min_size=1, max_size=50)),
        'chat_id': draw(st.text(min_size=1, max_size=50)),
        'chat_type': draw(st.sampled_from(['p2p', 'group'])),
        'message_type': draw(st.sampled_from(['text', 'image', 'file'])),
        'content': draw(st.text(min_size=1, max_size=200)),
        'sender_id': draw(st.text(min_size=1, max_size=50)),
        'create_time': draw(st.integers(min_value=1000000000, max_value=9999999999))
    }


class TestWebSocketEventRoutingProperties:
    """WebSocket 事件路由属性测试类"""
    
    @given(event_data=message_event_data())
    def test_property_20_event_handler_routes_to_registered_handler(self, event_data):
        """
        Property 20: WebSocket 事件路由
        
        For any 通过 WebSocket 接收的消息事件，Event_Handler 应该调用注册的
        消息接收处理器，并传递完整的事件数据。
        
        Validates: Requirements 9.3
        """
        # 创建 mock 消息处理器
        mock_message_handler = Mock()
        
        # 创建事件处理器并注册消息处理器
        event_handler = EventHandler()
        event_handler.register_message_receive_handler(mock_message_handler)
        
        # 创建 mock 事件对象
        mock_event = Mock()
        mock_event.event.message.message_id = event_data['message_id']
        mock_event.event.message.chat_id = event_data['chat_id']
        mock_event.event.message.chat_type = event_data['chat_type']
        mock_event.event.message.message_type = event_data['message_type']
        mock_event.event.message.content = event_data['content']
        mock_event.event.message.sender_id = event_data['sender_id']
        mock_event.event.message.create_time = event_data['create_time']
        
        # 模拟事件分发器构建
        with patch('feishu_bot.event_handler.lark.EventDispatcherHandler') as mock_dispatcher_class:
            mock_builder = MagicMock()
            mock_dispatcher_class.builder.return_value = mock_builder
            mock_builder.register_p2_im_message_receive_v1.return_value = mock_builder
            mock_builder.build.return_value = Mock()
            
            # 构建事件分发器
            event_handler.build()
            
            # 验证消息处理器被正确注册
            mock_builder.register_p2_im_message_receive_v1.assert_called_once_with(mock_message_handler)
            
            # 模拟调用注册的处理器
            registered_handler = mock_builder.register_p2_im_message_receive_v1.call_args[0][0]
            registered_handler(mock_event)
            
            # 验证消息处理器被调用，并传递了完整的事件数据
            mock_message_handler.assert_called_once_with(mock_event)
    
    @given(
        app_id=st.text(min_size=1, max_size=50),
        app_secret=st.text(min_size=1, max_size=50)
    )
    def test_property_20_websocket_client_registers_event_handler(self, app_id, app_secret):
        """
        Property 20: WebSocket 客户端注册事件处理器
        
        For any WebSocket 客户端初始化，应该正确注册事件处理器到飞书 SDK
        
        Validates: Requirements 9.2, 9.3
        """
        # 创建 mock 事件处理器
        mock_event_handler = Mock(spec=EventHandler)
        mock_dispatcher = Mock()
        mock_event_handler.build.return_value = mock_dispatcher
        
        with patch('feishu_bot.websocket_client.lark.ws.Client') as mock_ws_client_class:
            mock_ws_instance = Mock()
            mock_ws_client_class.return_value = mock_ws_instance
            
            # 创建 WebSocket 客户端
            client = WebSocketClient(
                app_id=app_id,
                app_secret=app_secret,
                event_handler=mock_event_handler
            )
            
            # 验证事件处理器被构建
            mock_event_handler.build.assert_called_once()
            
            # 验证 WebSocket 客户端使用了构建的事件分发器
            mock_ws_client_class.assert_called_once()
            call_args = mock_ws_client_class.call_args[0]
            call_kwargs = mock_ws_client_class.call_args[1]
            
            # app_id 和 app_secret 作为位置参数传递
            assert call_args[0] == app_id
            assert call_args[1] == app_secret
            assert call_kwargs['event_handler'] is mock_dispatcher
    
    @given(event_data=message_event_data())
    def test_property_20_handler_receives_complete_event_data(self, event_data):
        """
        Property 20: 处理器接收完整事件数据
        
        For any 消息事件，注册的处理器应该接收到包含所有必要字段的完整事件数据
        
        Validates: Requirements 9.3
        """
        # 创建一个捕获事件数据的处理器
        captured_events = []
        
        def capturing_handler(event):
            captured_events.append(event)
        
        # 创建事件处理器并注册
        event_handler = EventHandler()
        event_handler.register_message_receive_handler(capturing_handler)
        
        # 创建 mock 事件
        mock_event = Mock()
        mock_event.event.message.message_id = event_data['message_id']
        mock_event.event.message.chat_id = event_data['chat_id']
        mock_event.event.message.chat_type = event_data['chat_type']
        mock_event.event.message.message_type = event_data['message_type']
        mock_event.event.message.content = event_data['content']
        mock_event.event.message.sender_id = event_data['sender_id']
        mock_event.event.message.create_time = event_data['create_time']
        
        # 模拟事件分发
        with patch('feishu_bot.event_handler.lark.EventDispatcherHandler') as mock_dispatcher_class:
            mock_builder = MagicMock()
            mock_dispatcher_class.builder.return_value = mock_builder
            mock_builder.register_p2_im_message_receive_v1.return_value = mock_builder
            mock_builder.build.return_value = Mock()
            
            event_handler.build()
            
            # 获取注册的处理器并调用
            registered_handler = mock_builder.register_p2_im_message_receive_v1.call_args[0][0]
            registered_handler(mock_event)
            
            # 验证事件被捕获
            assert len(captured_events) == 1
            captured_event = captured_events[0]
            
            # 验证所有字段都被传递
            assert captured_event.event.message.message_id == event_data['message_id']
            assert captured_event.event.message.chat_id == event_data['chat_id']
            assert captured_event.event.message.chat_type == event_data['chat_type']
            assert captured_event.event.message.message_type == event_data['message_type']
            assert captured_event.event.message.content == event_data['content']
            assert captured_event.event.message.sender_id == event_data['sender_id']
            assert captured_event.event.message.create_time == event_data['create_time']
