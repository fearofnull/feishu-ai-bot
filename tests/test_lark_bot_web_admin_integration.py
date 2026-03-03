"""
Integration tests for Web Admin Interface startup in lark_bot.py

Tests the integration of Web Admin Interface with the main bot application.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from threading import Thread
import time


class TestWebAdminIntegration(unittest.TestCase):
    """Test Web Admin Interface integration with lark_bot.py"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original environment variables
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('lark_bot.FeishuBot')
    @patch('feishu_bot.web_admin.server.WebAdminServer')
    def test_web_admin_starts_when_enabled(self, mock_web_server_class, mock_bot_class):
        """Test that Web Admin Interface starts when ENABLE_WEB_ADMIN=true"""
        # Set up environment
        os.environ['ENABLE_WEB_ADMIN'] = 'true'
        os.environ['WEB_ADMIN_PASSWORD'] = 'test_password'
        os.environ['JWT_SECRET_KEY'] = 'test_secret'
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot with config_manager
        mock_bot = Mock()
        mock_bot.config_manager = Mock()
        
        # Create mock web server instance
        mock_web_server = Mock()
        mock_web_server_class.return_value = mock_web_server
        
        # Call start_web_admin
        result = start_web_admin(mock_bot)
        
        # Verify WebAdminServer was created with correct parameters
        mock_web_server_class.assert_called_once()
        call_kwargs = mock_web_server_class.call_args[1]
        
        self.assertEqual(call_kwargs['config_manager'], mock_bot.config_manager)
        self.assertEqual(call_kwargs['host'], '0.0.0.0')
        self.assertEqual(call_kwargs['port'], 5000)
        self.assertEqual(call_kwargs['admin_password'], 'test_password')
        self.assertEqual(call_kwargs['jwt_secret_key'], 'test_secret')
        
        # Verify result is the web server instance
        self.assertEqual(result, mock_web_server)
    
    @patch('lark_bot.FeishuBot')
    def test_web_admin_not_started_when_disabled(self, mock_bot_class):
        """Test that Web Admin Interface does not start when ENABLE_WEB_ADMIN=false"""
        # Set up environment
        os.environ['ENABLE_WEB_ADMIN'] = 'false'
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot
        mock_bot = Mock()
        
        # Call start_web_admin
        result = start_web_admin(mock_bot)
        
        # Verify result is None
        self.assertIsNone(result)
    
    @patch('lark_bot.FeishuBot')
    def test_web_admin_not_started_when_not_set(self, mock_bot_class):
        """Test that Web Admin Interface does not start when ENABLE_WEB_ADMIN is not set"""
        # Ensure ENABLE_WEB_ADMIN is not set
        if 'ENABLE_WEB_ADMIN' in os.environ:
            del os.environ['ENABLE_WEB_ADMIN']
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot
        mock_bot = Mock()
        
        # Call start_web_admin
        result = start_web_admin(mock_bot)
        
        # Verify result is None
        self.assertIsNone(result)
    
    @patch('lark_bot.FeishuBot')
    @patch('feishu_bot.web_admin.server.WebAdminServer')
    def test_web_admin_uses_custom_port(self, mock_web_server_class, mock_bot_class):
        """Test that Web Admin Interface uses custom port from environment"""
        # Set up environment with custom port
        os.environ['ENABLE_WEB_ADMIN'] = 'true'
        os.environ['WEB_ADMIN_PORT'] = '8080'
        os.environ['WEB_ADMIN_HOST'] = '127.0.0.1'
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot
        mock_bot = Mock()
        mock_bot.config_manager = Mock()
        
        # Create mock web server instance
        mock_web_server = Mock()
        mock_web_server_class.return_value = mock_web_server
        
        # Call start_web_admin
        result = start_web_admin(mock_bot)
        
        # Verify WebAdminServer was created with custom port and host
        call_kwargs = mock_web_server_class.call_args[1]
        self.assertEqual(call_kwargs['host'], '127.0.0.1')
        self.assertEqual(call_kwargs['port'], 8080)
    
    def test_web_admin_handles_import_error(self):
        """Test that Web Admin Interface handles import errors gracefully"""
        # Set up environment
        os.environ['ENABLE_WEB_ADMIN'] = 'true'
        
        # Mock the import to fail
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            # Import after setting environment
            from lark_bot import start_web_admin
            
            # Create mock bot
            mock_bot = Mock()
            
            # Call start_web_admin - should not raise exception
            result = start_web_admin(mock_bot)
            
            # Verify result is None (graceful failure)
            self.assertIsNone(result)
    
    @patch('lark_bot.FeishuBot')
    @patch('feishu_bot.web_admin.server.WebAdminServer')
    def test_web_admin_handles_startup_error(self, mock_web_server_class, mock_bot_class):
        """Test that Web Admin Interface handles startup errors gracefully"""
        # Set up environment
        os.environ['ENABLE_WEB_ADMIN'] = 'true'
        
        # Make WebAdminServer initialization fail
        mock_web_server_class.side_effect = Exception("Startup failed")
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot
        mock_bot = Mock()
        mock_bot.config_manager = Mock()
        
        # Call start_web_admin - should not raise exception
        result = start_web_admin(mock_bot)
        
        # Verify result is None (graceful failure)
        self.assertIsNone(result)
    
    @patch('lark_bot.FeishuBot')
    @patch('feishu_bot.web_admin.server.WebAdminServer')
    def test_web_admin_warns_on_missing_password(self, mock_web_server_class, mock_bot_class):
        """Test that Web Admin Interface warns when password is not set"""
        # Set up environment without password
        os.environ['ENABLE_WEB_ADMIN'] = 'true'
        if 'WEB_ADMIN_PASSWORD' in os.environ:
            del os.environ['WEB_ADMIN_PASSWORD']
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot
        mock_bot = Mock()
        mock_bot.config_manager = Mock()
        
        # Create mock web server instance
        mock_web_server = Mock()
        mock_web_server_class.return_value = mock_web_server
        
        # Call start_web_admin with logging capture
        with self.assertLogs('lark_bot', level='WARNING') as log:
            result = start_web_admin(mock_bot)
            
            # Verify warning was logged
            self.assertTrue(
                any('WEB_ADMIN_PASSWORD not set' in message for message in log.output)
            )
    
    @patch('lark_bot.FeishuBot')
    @patch('feishu_bot.web_admin.server.WebAdminServer')
    def test_web_admin_warns_on_missing_jwt_secret(self, mock_web_server_class, mock_bot_class):
        """Test that Web Admin Interface warns when JWT secret is not set"""
        # Set up environment without JWT secret
        os.environ['ENABLE_WEB_ADMIN'] = 'true'
        if 'JWT_SECRET_KEY' in os.environ:
            del os.environ['JWT_SECRET_KEY']
        
        # Import after setting environment
        from lark_bot import start_web_admin
        
        # Create mock bot
        mock_bot = Mock()
        mock_bot.config_manager = Mock()
        
        # Create mock web server instance
        mock_web_server = Mock()
        mock_web_server_class.return_value = mock_web_server
        
        # Call start_web_admin with logging capture
        with self.assertLogs('lark_bot', level='WARNING') as log:
            result = start_web_admin(mock_bot)
            
            # Verify warning was logged
            self.assertTrue(
                any('JWT_SECRET_KEY not set' in message for message in log.output)
            )


if __name__ == '__main__':
    unittest.main()
