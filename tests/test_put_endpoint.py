"""
测试 PUT /api/configs/:session_id 端点
验证任务 5.1 的实现
"""
import pytest
import os
import tempfile
from flask import Flask
from feishu_bot.web_admin.auth import AuthManager
from feishu_bot.web_admin.api_routes import register_api_routes
from feishu_bot.core.config_manager import ConfigManager


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
    
    yield app
    
    # 清理临时文件
    if os.path.exists(config_file):
        os.remove(config_file)
    os.rmdir(temp_dir)


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """获取认证令牌"""
    response = client.post('/api/auth/login', json={
        'password': 'test_admin_password'
    })
    return response.get_json()['data']['token']


class TestPutConfigEndpoint:
    """测试 PUT /api/configs/:session_id 端点
    
    任务 5.1: 实现 PUT /api/configs/:session_id 端点
    - 接收配置更新数据
    - 验证配置值有效性（provider、layer 枚举值）
    - 调用 ConfigManager.set_config() 保存配置
    - 更新元数据（updated_at、update_count）
    - 返回更新后的配置
    - 需求：4.1, 4.7, 4.8, 4.10, 6.3
    """
    
    def test_create_new_config(self, client, auth_token):
        """测试创建新配置
        
        验证可以通过 PUT 端点创建新的会话配置。
        需求：4.1, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_new'
        
        # 创建新配置
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'target_project_dir': '/test/project',
                                 'response_language': 'zh-CN',
                                 'default_provider': 'claude',
                                 'default_layer': 'api',
                                 'default_cli_provider': 'gemini'
                             },
                             headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Creating new config should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        assert 'message' in data, \
            "Response should contain success message"
        
        # 验证返回的配置数据
        config = data['data']
        assert config['session_id'] == session_id, \
            "Returned config should have correct session_id"
        assert config['config']['target_project_dir'] == '/test/project', \
            "Returned config should have correct target_project_dir"
        assert config['config']['response_language'] == 'zh-CN', \
            "Returned config should have correct response_language"
        assert config['config']['default_provider'] == 'claude', \
            "Returned config should have correct default_provider"
        assert config['config']['default_layer'] == 'api', \
            "Returned config should have correct default_layer"
        assert config['config']['default_cli_provider'] == 'gemini', \
            "Returned config should have correct default_cli_provider"
    
    def test_update_existing_config(self, client, auth_token):
        """测试更新现有配置
        
        验证可以通过 PUT 端点更新现有的会话配置。
        需求：4.1, 4.10, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_update'
        
        # 创建初始配置
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude'
                  },
                  headers=headers)
        
        # 更新配置
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'default_provider': 'gemini',
                                 'default_layer': 'cli'
                             },
                             headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Updating existing config should return 200 OK"
        
        # 验证配置已更新
        data = response.get_json()
        config = data['data']
        assert config['config']['default_provider'] == 'gemini', \
            "Provider should be updated to gemini"
        assert config['config']['default_layer'] == 'cli', \
            "Layer should be updated to cli"
    
    def test_validate_invalid_provider(self, client, auth_token):
        """测试验证无效的 provider 值
        
        验证当提供无效的 provider 值时，端点返回 400 错误。
        需求：4.7, 4.8
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_invalid_provider'
        
        # 尝试设置无效的 provider
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'invalid_provider'
                             },
                             headers=headers)
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Invalid provider should return 400 Bad Request"
        
        # 验证错误响应
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_PROVIDER', \
            "Error code should be INVALID_PROVIDER"
        assert 'field' in data['error'], \
            "Error should specify the invalid field"
        assert data['error']['field'] == 'default_provider', \
            "Error field should be default_provider"
    
    def test_validate_invalid_layer(self, client, auth_token):
        """测试验证无效的 layer 值
        
        验证当提供无效的 layer 值时，端点返回 400 错误。
        需求：4.7, 4.8
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_invalid_layer'
        
        # 尝试设置无效的 layer
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_layer': 'invalid_layer'
                             },
                             headers=headers)
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Invalid layer should return 400 Bad Request"
        
        # 验证错误响应
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_LAYER', \
            "Error code should be INVALID_LAYER"
        assert data['error']['field'] == 'default_layer', \
            "Error field should be default_layer"
    
    def test_validate_invalid_cli_provider(self, client, auth_token):
        """测试验证无效的 CLI provider 值
        
        验证当提供无效的 CLI provider 值时，端点返回 400 错误。
        需求：4.7, 4.8
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_invalid_cli_provider'
        
        # 尝试设置无效的 CLI provider
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_cli_provider': 'invalid_cli_provider'
                             },
                             headers=headers)
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Invalid CLI provider should return 400 Bad Request"
        
        # 验证错误响应
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert data['error']['code'] == 'INVALID_PROVIDER', \
            "Error code should be INVALID_PROVIDER"
    
    def test_metadata_updated(self, client, auth_token):
        """测试元数据自动更新
        
        验证配置更新时，updated_at 和 update_count 自动更新。
        需求：4.10
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_metadata'
        
        # 创建初始配置
        response1 = client.put(f'/api/configs/{session_id}', 
                              json={
                                  'session_type': 'user',
                                  'default_provider': 'claude'
                              },
                              headers=headers)
        
        data1 = response1.get_json()
        initial_update_count = data1['data']['metadata']['update_count']
        initial_updated_at = data1['data']['metadata']['updated_at']
        
        # 等待一小段时间确保时间戳不同
        import time
        time.sleep(0.1)
        
        # 更新配置
        response2 = client.put(f'/api/configs/{session_id}', 
                              json={
                                  'default_provider': 'gemini'
                              },
                              headers=headers)
        
        data2 = response2.get_json()
        updated_update_count = data2['data']['metadata']['update_count']
        updated_updated_at = data2['data']['metadata']['updated_at']
        
        # 验证 update_count 递增
        assert updated_update_count == initial_update_count + 1, \
            "update_count should increment by 1"
        
        # 验证 updated_at 更新
        assert updated_updated_at > initial_updated_at, \
            "updated_at should be updated to a later timestamp"
    
    def test_valid_provider_values(self, client, auth_token):
        """测试所有有效的 provider 值
        
        验证所有有效的 provider 值（claude, gemini, openai）都被接受。
        需求：4.7
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        valid_providers = ['claude', 'gemini', 'openai']
        
        for provider in valid_providers:
            session_id = f'test_session_{provider}'
            response = client.put(f'/api/configs/{session_id}', 
                                 json={
                                     'session_type': 'user',
                                     'default_provider': provider
                                 },
                                 headers=headers)
            
            # 验证响应状态码为 200 OK
            assert response.status_code == 200, \
                f"Valid provider '{provider}' should be accepted"
            
            # 验证配置已保存
            data = response.get_json()
            assert data['data']['config']['default_provider'] == provider, \
                f"Provider should be set to '{provider}'"
    
    def test_valid_layer_values(self, client, auth_token):
        """测试所有有效的 layer 值
        
        验证所有有效的 layer 值（api, cli）都被接受。
        需求：4.7
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        valid_layers = ['api', 'cli']
        
        for layer in valid_layers:
            session_id = f'test_session_layer_{layer}'
            response = client.put(f'/api/configs/{session_id}', 
                                 json={
                                     'session_type': 'user',
                                     'default_layer': layer
                                 },
                                 headers=headers)
            
            # 验证响应状态码为 200 OK
            assert response.status_code == 200, \
                f"Valid layer '{layer}' should be accepted"
            
            # 验证配置已保存
            data = response.get_json()
            assert data['data']['config']['default_layer'] == layer, \
                f"Layer should be set to '{layer}'"
    
    def test_partial_update(self, client, auth_token):
        """测试部分字段更新
        
        验证可以只更新部分字段，其他字段保持不变。
        需求：4.1, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'test_session_partial'
        
        # 创建完整配置
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'target_project_dir': '/original/path',
                      'default_provider': 'claude',
                      'default_layer': 'api'
                  },
                  headers=headers)
        
        # 只更新 provider
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'default_provider': 'gemini'
                             },
                             headers=headers)
        
        # 验证只有 provider 被更新，其他字段保持不变
        data = response.get_json()
        config = data['data']['config']
        assert config['default_provider'] == 'gemini', \
            "Provider should be updated"
        assert config['target_project_dir'] == '/original/path', \
            "target_project_dir should remain unchanged"
        assert config['default_layer'] == 'api', \
            "Layer should remain unchanged"
    
    def test_unauthorized_access(self, client):
        """测试未授权访问
        
        验证没有认证令牌时无法访问 PUT 端点。
        需求：7.4
        """
        session_id = 'test_session_unauth'
        
        # 尝试不带令牌访问
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'claude'
                             })
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "PUT without auth should return 401 Unauthorized"
        
        # 验证错误响应
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
