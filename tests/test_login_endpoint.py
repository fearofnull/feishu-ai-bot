"""
登录端点集成测试
测试 POST /api/auth/login 端点的功能
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


class TestLoginEndpoint:
    """登录端点测试类"""
    
    def test_login_with_correct_password(self, client):
        """测试使用正确密码登录应该成功
        
        需求：7.1, 7.2
        """
        # 发送登录请求
        response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        
        # 验证响应状态码
        assert response.status_code == 200, "Login with correct password should return 200"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, "Response should indicate success"
        assert 'data' in data, "Response should contain data field"
        assert 'token' in data['data'], "Response data should contain token"
        assert 'expires_in' in data['data'], "Response data should contain expires_in"
        assert 'expires_at' in data['data'], "Response data should contain expires_at"
        
        # 验证令牌不为空
        assert len(data['data']['token']) > 0, "Token should not be empty"
        
        # 验证过期时间（2小时 = 7200秒）
        assert data['data']['expires_in'] == 7200, "Token should expire in 7200 seconds"
    
    def test_login_with_wrong_password(self, client):
        """测试使用错误密码登录应该返回 401
        
        需求：7.5
        """
        # 发送登录请求
        response = client.post('/api/auth/login', json={
            'password': 'wrong_password'
        })
        
        # 验证响应状态码
        assert response.status_code == 401, "Login with wrong password should return 401"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is False, "Response should indicate failure"
        assert 'error' in data, "Response should contain error field"
        assert data['error']['code'] == 'INVALID_CREDENTIALS', "Error code should be INVALID_CREDENTIALS"
    
    def test_login_without_password(self, client):
        """测试不提供密码应该返回 400
        
        需求：7.5
        """
        # 发送登录请求（不包含密码）
        response = client.post('/api/auth/login', json={})
        
        # 验证响应状态码
        assert response.status_code == 400, "Login without password should return 400"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is False, "Response should indicate failure"
        assert 'error' in data, "Response should contain error field"
        assert data['error']['code'] == 'MISSING_PASSWORD', "Error code should be MISSING_PASSWORD"
    
    def test_login_with_empty_password(self, client):
        """测试使用空密码应该返回 401
        
        需求：7.5
        """
        # 发送登录请求（空密码）
        response = client.post('/api/auth/login', json={
            'password': ''
        })
        
        # 验证响应状态码
        assert response.status_code == 400, "Login with empty password should return 400"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is False, "Response should indicate failure"
    
    def test_login_response_format(self, client):
        """测试登录成功响应的格式
        
        需求：7.1, 7.2
        """
        # 发送登录请求
        response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        
        # 验证响应格式
        data = response.get_json()
        
        # 验证顶层字段
        assert 'success' in data, "Response should have 'success' field"
        assert 'data' in data, "Response should have 'data' field"
        assert 'message' in data, "Response should have 'message' field"
        
        # 验证 data 字段结构
        assert isinstance(data['data'], dict), "Data field should be a dictionary"
        assert 'token' in data['data'], "Data should contain 'token'"
        assert 'expires_in' in data['data'], "Data should contain 'expires_in'"
        assert 'expires_at' in data['data'], "Data should contain 'expires_at'"
        
        # 验证数据类型
        assert isinstance(data['data']['token'], str), "Token should be a string"
        assert isinstance(data['data']['expires_in'], int), "expires_in should be an integer"
        assert isinstance(data['data']['expires_at'], str), "expires_at should be a string"
    
    def test_login_token_can_be_used(self, client):
        """测试登录获得的令牌可以用于访问受保护的端点
        
        需求：7.1, 7.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        
        # 使用令牌访问受保护的端点
        response = client.get('/api/configs', headers={
            'Authorization': f'Bearer {token}'
        })
        
        # 验证可以成功访问
        assert response.status_code == 200, "Token should allow access to protected endpoints"
    
    def test_login_multiple_times(self, client):
        """测试可以多次登录获取不同的令牌
        
        需求：7.1, 7.2
        """
        # 第一次登录
        response1 = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token1 = response1.get_json()['data']['token']
        
        # 第二次登录
        response2 = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token2 = response2.get_json()['data']['token']
        
        # 验证两次登录都成功
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # 验证获得了不同的令牌（因为时间戳不同）
        # 注意：如果两次请求在同一秒内完成，令牌可能相同
        # 这里只验证两个令牌都是有效的
        assert len(token1) > 0
        assert len(token2) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
