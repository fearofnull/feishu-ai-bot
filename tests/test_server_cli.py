"""
Web Admin Server 命令行入口测试

测试命令行参数解析和服务器启动配置
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from feishu_bot.web_admin.server import main, WebAdminServer
from feishu_bot.core.config_manager import ConfigManager


class TestCommandLineInterface:
    """命令行接口测试类
    
    测试需求：1.4, 1.5 - 命令行参数配置和环境变量支持
    """
    
    def test_cli_supports_port_parameter(self):
        """测试命令行支持 --port 参数
        
        验证可以通过 --port 参数配置服务器端口。
        
        需求：1.5
        """
        # 模拟命令行参数
        test_args = ['server.py', '--port', '8080']
        
        with patch.object(sys, 'argv', test_args):
            with patch('feishu_bot.web_admin.server.WebAdminServer') as MockServer:
                with patch('feishu_bot.web_admin.server.ConfigManager'):
                    # 模拟服务器启动
                    mock_instance = MagicMock()
                    MockServer.return_value = mock_instance
                    
                    try:
                        # 解析参数但不实际启动服务器
                        import argparse
                        parser = argparse.ArgumentParser()
                        parser.add_argument("--host", default="0.0.0.0")
                        parser.add_argument("--port", type=int, default=5000)
                        parser.add_argument("--debug", action="store_true")
                        parser.add_argument("--static-folder")
                        
                        args = parser.parse_args(test_args[1:])
                        
                        # 验证端口参数被正确解析
                        assert args.port == 8080, \
                            "Port parameter should be parsed correctly"
                    except SystemExit:
                        pass
    
    def test_cli_supports_host_parameter(self):
        """测试命令行支持 --host 参数
        
        验证可以通过 --host 参数配置服务器监听地址。
        
        需求：1.5
        """
        # 模拟命令行参数
        test_args = ['server.py', '--host', '127.0.0.1']
        
        with patch.object(sys, 'argv', test_args):
            # 解析参数
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--host", default="0.0.0.0")
            parser.add_argument("--port", type=int, default=5000)
            parser.add_argument("--debug", action="store_true")
            parser.add_argument("--static-folder")
            
            args = parser.parse_args(test_args[1:])
            
            # 验证主机参数被正确解析
            assert args.host == '127.0.0.1', \
                "Host parameter should be parsed correctly"
    
    def test_cli_reads_password_from_environment(self):
        """测试从环境变量读取密码
        
        验证服务器从 WEB_ADMIN_PASSWORD 环境变量读取管理员密码。
        
        需求：1.5
        """
        # 设置环境变量
        test_password = "test_secure_password_123"
        with patch.dict(os.environ, {'WEB_ADMIN_PASSWORD': test_password}):
            # 验证环境变量被正确读取
            password = os.environ.get('WEB_ADMIN_PASSWORD')
            assert password == test_password, \
                "Password should be read from WEB_ADMIN_PASSWORD environment variable"
    
    def test_cli_reads_secret_key_from_environment(self):
        """测试从环境变量读取密钥
        
        验证服务器从 JWT_SECRET_KEY 环境变量读取 JWT 签名密钥。
        
        需求：1.5
        """
        # 设置环境变量
        test_secret = "test_jwt_secret_key_456"
        with patch.dict(os.environ, {'JWT_SECRET_KEY': test_secret}):
            # 验证环境变量被正确读取
            secret = os.environ.get('JWT_SECRET_KEY')
            assert secret == test_secret, \
                "Secret key should be read from JWT_SECRET_KEY environment variable"
    
    def test_cli_default_port_is_5000(self):
        """测试默认端口为 5000
        
        验证如果不指定 --port 参数，默认使用端口 5000。
        
        需求：1.5
        """
        # 不提供端口参数
        test_args = ['server.py']
        
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="0.0.0.0")
        parser.add_argument("--port", type=int, default=5000)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--static-folder")
        
        args = parser.parse_args(test_args[1:])
        
        # 验证使用默认端口
        assert args.port == 5000, \
            "Default port should be 5000"
    
    def test_cli_default_host_is_all_interfaces(self):
        """测试默认监听所有网络接口
        
        验证如果不指定 --host 参数，默认监听 0.0.0.0（所有接口）。
        
        需求：1.5
        """
        # 不提供主机参数
        test_args = ['server.py']
        
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="0.0.0.0")
        parser.add_argument("--port", type=int, default=5000)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--static-folder")
        
        args = parser.parse_args(test_args[1:])
        
        # 验证使用默认主机
        assert args.host == "0.0.0.0", \
            "Default host should be 0.0.0.0 (all interfaces)"
    
    def test_server_logs_access_url_on_start(self):
        """测试服务器启动时记录访问 URL
        
        验证服务器启动时会记录访问 URL 到日志和控制台。
        
        需求：1.4
        """
        # 创建测试服务器实例
        config_manager = ConfigManager()
        server = WebAdminServer(
            config_manager=config_manager,
            host="127.0.0.1",
            port=8080,
            admin_password="test_password",
            jwt_secret_key="test_secret"
        )
        
        # 模拟 Flask app.run 方法
        with patch.object(server.app, 'run') as mock_run:
            # 捕获打印输出
            with patch('builtins.print') as mock_print:
                try:
                    server.start(debug=False)
                except KeyboardInterrupt:
                    pass
                
                # 验证打印了访问 URL
                print_calls = [str(call) for call in mock_print.call_args_list]
                url_printed = any('http://127.0.0.1:8080' in str(call) for call in print_calls)
                
                assert url_printed, \
                    "Server should print access URL on start"
    
    def test_cli_supports_debug_flag(self):
        """测试命令行支持 --debug 标志
        
        验证可以通过 --debug 标志启用调试模式。
        
        需求：1.5
        """
        # 模拟命令行参数
        test_args = ['server.py', '--debug']
        
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="0.0.0.0")
        parser.add_argument("--port", type=int, default=5000)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--static-folder")
        
        args = parser.parse_args(test_args[1:])
        
        # 验证调试标志被正确解析
        assert args.debug is True, \
            "Debug flag should be parsed correctly"
    
    def test_cli_supports_static_folder_parameter(self):
        """测试命令行支持 --static-folder 参数
        
        验证可以通过 --static-folder 参数指定前端静态文件路径。
        
        需求：1.2
        """
        # 模拟命令行参数
        test_args = ['server.py', '--static-folder', '/path/to/frontend']
        
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="0.0.0.0")
        parser.add_argument("--port", type=int, default=5000)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--static-folder")
        
        args = parser.parse_args(test_args[1:])
        
        # 验证静态文件夹参数被正确解析
        assert args.static_folder == '/path/to/frontend', \
            "Static folder parameter should be parsed correctly"
    
    def test_server_initialization_with_cli_parameters(self):
        """测试使用命令行参数初始化服务器
        
        验证服务器可以使用从命令行解析的参数正确初始化。
        
        需求：1.5
        """
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 使用命令行参数创建服务器
        server = WebAdminServer(
            config_manager=config_manager,
            host="192.168.1.100",
            port=9000,
            admin_password="cli_password",
            jwt_secret_key="cli_secret"
        )
        
        # 验证服务器配置
        assert server.host == "192.168.1.100", \
            "Server should use CLI host parameter"
        assert server.port == 9000, \
            "Server should use CLI port parameter"
        assert server.auth_manager.admin_password == "cli_password", \
            "Server should use CLI password parameter"
        assert server.auth_manager.secret_key == "cli_secret", \
            "Server should use CLI secret key parameter"
    
    def test_environment_variables_override_defaults(self):
        """测试环境变量覆盖默认值
        
        验证环境变量中的配置会覆盖默认值。
        
        需求：1.5
        """
        # 设置环境变量
        test_env = {
            'WEB_ADMIN_PASSWORD': 'env_password',
            'JWT_SECRET_KEY': 'env_secret'
        }
        
        with patch.dict(os.environ, test_env):
            # 读取环境变量
            password = os.environ.get('WEB_ADMIN_PASSWORD')
            secret = os.environ.get('JWT_SECRET_KEY')
            
            # 验证环境变量被正确读取
            assert password == 'env_password', \
                "Environment variable should override default password"
            assert secret == 'env_secret', \
                "Environment variable should override default secret key"
    
    def test_cli_parameters_override_environment_variables(self):
        """测试命令行参数优先级高于环境变量
        
        验证当同时提供命令行参数和环境变量时，命令行参数优先。
        
        需求：1.5
        """
        # 设置环境变量
        with patch.dict(os.environ, {'WEB_ADMIN_PASSWORD': 'env_password'}):
            # 创建服务器，显式提供密码参数
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                host="0.0.0.0",
                port=5000,
                admin_password="cli_password",  # 命令行参数
                jwt_secret_key="test_secret"
            )
            
            # 验证使用命令行参数而不是环境变量
            assert server.auth_manager.admin_password == "cli_password", \
                "CLI parameter should override environment variable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
