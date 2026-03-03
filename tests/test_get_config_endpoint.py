"""
测试 GET /api/configs/:session_id 端点
验证需求：3.1, 3.2, 3.3, 6.2
"""
import pytest
import os
import tempfile
from flask import Flask
from feishu_bot.web_admin.auth import AuthManager
from feishu_bot.web_admin.api_routes import register_api_routes
from feishu_bot.core.config_manager import ConfigManager
from feishu_bot.models import SessionConfig


@pytest.fixture
def app():
    """创建测试用的 Flask 应用"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # 创建临时配置文件
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, 'test_configs.json')
    
    # 创建 ConfigManager 和 AuthManager
    config_manager = ConfigManager(storage_path=config_file)
    auth_manager = AuthManager(
        secret_key="test_secret_key_12345678",
        admin_password="test_admin_password"
    )
    
    # 注册 API 路由
    register_api_routes(app, config_manager, auth_manager)
    
    yield app, config_manager
    
    # 清理临时文件
    if os.path.exists(config_file):
        os.remove(config_file)
    os.rmdir(temp_dir)


@pytest.fixture
def client(app):
    """创建测试客户端"""
    flask_app, _ = app
    return flask_app.test_client()


@pytest.fixture
def auth_token(client):
    """获取认证令牌"""
    response = client.post('/api/auth/login', json={
        'password': 'test_admin_password'
    })
    return response.get_json()['data']['token']


class TestGetConfigEndpoint:
    """测试 GET /api/configs/:session_id 端点"""
    
    def test_get_existing_config_returns_200(self, client, app, auth_token):
        """测试获取存在的配置返回 200 和完整配置数据
        
        需求：3.1, 3.2, 3.3, 6.2
        """
        _, config_manager = app
        
        # 创建一个测试配置
        session_id = "test_user_001"
        test_config = SessionConfig(
            session_id=session_id,
            session_type="user",
            target_project_dir="/test/project",
            response_language="中文",
            default_provider="claude",
            default_layer="api",
            default_cli_provider="gemini",
            created_by="admin",
            created_at="2024-01-01T00:00:00",
            updated_by="admin",
            updated_at="2024-01-01T12:00:00",
            update_count=5
        )
        config_manager.configs[session_id] = test_config
        
        # 发送 GET 请求
        response = client.get(
            f'/api/configs/{session_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # 验证响应状态码
        assert response.status_code == 200, \
            "Getting existing config should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        
        # 验证配置数据完整性
        config_data = data['data']
        assert config_data['session_id'] == session_id, \
            "Response should contain correct session_id"
        assert config_data['session_type'] == "user", \
            "Response should contain session_type"
        
        # 验证配置字段（需求 3.2）
        config_fields = config_data['config']
        assert config_fields['target_project_dir'] == "/test/project", \
            "Response should contain target_project_dir"
        assert config_fields['response_language'] == "中文", \
            "Response should contain response_language"
        assert config_fields['default_provider'] == "claude", \
            "Response should contain default_provider"
        assert config_fields['default_layer'] == "api", \
            "Response should contain default_layer"
        assert config_fields['default_cli_provider'] == "gemini", \
            "Response should contain default_cli_provider"
        
        # 验证元数据字段（需求 3.3）
        metadata = config_data['metadata']
        assert metadata['created_by'] == "admin", \
            "Response should contain created_by metadata"
        assert metadata['created_at'] == "2024-01-01T00:00:00", \
            "Response should contain created_at metadata"
        assert metadata['updated_by'] == "admin", \
            "Response should contain updated_by metadata"
        assert metadata['updated_at'] == "2024-01-01T12:00:00", \
            "Response should contain updated_at metadata"
        assert metadata['update_count'] == 5, \
            "Response should contain update_count metadata"
    
    def test_get_nonexistent_config_returns_404(self, client, auth_token):
        """测试获取不存在的配置返回 404
        
        需求：6.2
        """
        # 发送 GET 请求获取不存在的配置
        response = client.get(
            '/api/configs/nonexistent_session_id',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # 验证响应状态码为 404
        assert response.status_code == 404, \
            "Getting nonexistent config should return 404 Not Found"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'NOT_FOUND', \
            "Error code should be NOT_FOUND"
        assert 'message' in data['error'], \
            "Error should contain user-friendly message"
    
    def test_get_config_without_auth_returns_401(self, client, app):
        """测试未认证访问配置返回 401
        
        需求：6.2
        """
        _, config_manager = app
        
        # 创建一个测试配置
        session_id = "test_user_002"
        test_config = SessionConfig(
            session_id=session_id,
            session_type="user",
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by="admin",
            created_at="2024-01-01T00:00:00",
            updated_by="admin",
            updated_at="2024-01-01T00:00:00",
            update_count=0
        )
        config_manager.configs[session_id] = test_config
        
        # 发送 GET 请求，不提供认证令牌
        response = client.get(f'/api/configs/{session_id}')
        
        # 验证响应状态码为 401
        assert response.status_code == 401, \
            "Getting config without auth should return 401 Unauthorized"
    
    def test_get_config_with_null_fields(self, client, app, auth_token):
        """测试获取包含 null 字段的配置
        
        需求：3.2, 3.3
        """
        _, config_manager = app
        
        # 创建一个字段为 None 的测试配置
        session_id = "test_user_003"
        test_config = SessionConfig(
            session_id=session_id,
            session_type="group",
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by="admin",
            created_at="2024-01-01T00:00:00",
            updated_by=None,
            updated_at="2024-01-01T00:00:00",
            update_count=0
        )
        config_manager.configs[session_id] = test_config
        
        # 发送 GET 请求
        response = client.get(
            f'/api/configs/{session_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # 验证响应状态码
        assert response.status_code == 200, \
            "Getting config with null fields should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        config_fields = data['data']['config']
        
        # 验证 null 字段正确返回
        assert config_fields['target_project_dir'] is None, \
            "Null target_project_dir should be returned as null"
        assert config_fields['response_language'] is None, \
            "Null response_language should be returned as null"
        assert config_fields['default_provider'] is None, \
            "Null default_provider should be returned as null"
        assert config_fields['default_layer'] is None, \
            "Null default_layer should be returned as null"
        assert config_fields['default_cli_provider'] is None, \
            "Null default_cli_provider should be returned as null"
    
    def test_get_config_response_format(self, client, app, auth_token):
        """测试响应格式符合 API 规范
        
        需求：6.2
        """
        _, config_manager = app
        
        # 创建一个测试配置
        session_id = "test_user_004"
        test_config = SessionConfig(
            session_id=session_id,
            session_type="user",
            target_project_dir="/test",
            response_language="English",
            default_provider="openai",
            default_layer="cli",
            default_cli_provider=None,
            created_by="admin",
            created_at="2024-01-01T00:00:00",
            updated_by="admin",
            updated_at="2024-01-01T00:00:00",
            update_count=1
        )
        config_manager.configs[session_id] = test_config
        
        # 发送 GET 请求
        response = client.get(
            f'/api/configs/{session_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # 验证响应格式
        data = response.get_json()
        
        # 验证顶层结构
        assert 'success' in data, \
            "Response should contain 'success' field"
        assert 'data' in data, \
            "Response should contain 'data' field"
        
        # 验证数据结构
        config_data = data['data']
        assert 'session_id' in config_data, \
            "Config data should contain 'session_id'"
        assert 'session_type' in config_data, \
            "Config data should contain 'session_type'"
        assert 'config' in config_data, \
            "Config data should contain 'config' object"
        assert 'metadata' in config_data, \
            "Config data should contain 'metadata' object"
        
        # 验证 config 对象包含所有字段
        config_fields = config_data['config']
        required_config_fields = [
            'target_project_dir',
            'response_language',
            'default_provider',
            'default_layer',
            'default_cli_provider'
        ]
        for field in required_config_fields:
            assert field in config_fields, \
                f"Config should contain '{field}' field"
        
        # 验证 metadata 对象包含所有字段
        metadata = config_data['metadata']
        required_metadata_fields = [
            'created_by',
            'created_at',
            'updated_by',
            'updated_at',
            'update_count'
        ]
        for field in required_metadata_fields:
            assert field in metadata, \
                f"Metadata should contain '{field}' field"
    
    def test_get_config_with_special_characters(self, client, app, auth_token):
        """测试获取包含特殊字符的配置
        
        需求：3.2
        """
        _, config_manager = app
        
        # 创建包含特殊字符的测试配置
        session_id = "test_user_005"
        test_config = SessionConfig(
            session_id=session_id,
            session_type="user",
            target_project_dir="/path/with spaces/and-特殊字符",
            response_language="中文/English",
            default_provider="claude",
            default_layer="api",
            default_cli_provider=None,
            created_by="admin",
            created_at="2024-01-01T00:00:00",
            updated_by="admin",
            updated_at="2024-01-01T00:00:00",
            update_count=0
        )
        config_manager.configs[session_id] = test_config
        
        # 发送 GET 请求
        response = client.get(
            f'/api/configs/{session_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # 验证响应状态码
        assert response.status_code == 200, \
            "Getting config with special characters should return 200 OK"
        
        # 验证特殊字符正确返回
        data = response.get_json()
        config_fields = data['data']['config']
        assert config_fields['target_project_dir'] == "/path/with spaces/and-特殊字符", \
            "Special characters in path should be preserved"
        assert config_fields['response_language'] == "中文/English", \
            "Special characters in language should be preserved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
