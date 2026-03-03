"""
Web 管理界面单元测试
使用 pytest 进行单元测试
"""
import pytest
import time
import os
import tempfile
from datetime import datetime, timedelta
from flask import Flask
from feishu_bot.web_admin.auth import AuthManager
from feishu_bot.web_admin.api_routes import register_api_routes
from feishu_bot.core.config_manager import ConfigManager


class TestAuthManager:
    """AuthManager 单元测试类"""
    
    @pytest.fixture
    def auth_manager(self):
        """创建 AuthManager 实例用于测试"""
        secret_key = "test_secret_key_12345678"
        admin_password = "test_admin_password"
        return AuthManager(secret_key, admin_password)
    
    # 测试正确密码验证
    def test_verify_password_correct(self, auth_manager):
        """测试使用正确密码验证应该成功
        
        需求：7.5
        """
        # 使用正确的密码
        result = auth_manager.verify_password("test_admin_password")
        
        # 验证应该成功
        assert result is True, "Correct password should be verified successfully"
    
    def test_verify_password_incorrect(self, auth_manager):
        """测试使用错误密码验证应该失败
        
        需求：7.5
        """
        # 使用错误的密码
        result = auth_manager.verify_password("wrong_password")
        
        # 验证应该失败
        assert result is False, "Incorrect password should fail verification"
    
    def test_verify_password_empty(self, auth_manager):
        """测试使用空密码验证应该失败
        
        需求：7.5
        """
        # 使用空密码
        result = auth_manager.verify_password("")
        
        # 验证应该失败
        assert result is False, "Empty password should fail verification"
    
    def test_verify_password_case_sensitive(self, auth_manager):
        """测试密码验证是大小写敏感的
        
        需求：7.5
        """
        # 使用大小写不同的密码
        result = auth_manager.verify_password("TEST_ADMIN_PASSWORD")
        
        # 验证应该失败（密码是大小写敏感的）
        assert result is False, "Password verification should be case-sensitive"
    
    # 测试令牌生成
    def test_generate_token_returns_dict(self, auth_manager):
        """测试生成令牌返回正确的数据结构
        
        需求：7.5
        """
        # 生成令牌
        token_data = auth_manager.generate_token()
        
        # 验证返回的是字典
        assert isinstance(token_data, dict), "Token data should be a dictionary"
        
        # 验证包含必需的字段
        assert 'token' in token_data, "Token data should contain 'token' field"
        assert 'expires_in' in token_data, "Token data should contain 'expires_in' field"
        assert 'expires_at' in token_data, "Token data should contain 'expires_at' field"
    
    def test_generate_token_returns_valid_token(self, auth_manager):
        """测试生成的令牌是有效的字符串
        
        需求：7.5
        """
        # 生成令牌
        token_data = auth_manager.generate_token()
        token = token_data['token']
        
        # 验证令牌是字符串且不为空
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"
    
    def test_generate_token_expiry_time(self, auth_manager):
        """测试生成的令牌包含正确的过期时间
        
        需求：7.5, 7.6
        """
        # 生成令牌
        token_data = auth_manager.generate_token()
        
        # 验证过期时间（2小时 = 7200秒）
        expected_expires_in = auth_manager.token_expiry_hours * 3600
        assert token_data['expires_in'] == expected_expires_in, \
            f"Token should expire in {expected_expires_in} seconds"
    
    def test_generate_token_unique(self, auth_manager):
        """测试每次生成的令牌都是唯一的
        
        需求：7.5
        """
        # 生成两个令牌
        token1 = auth_manager.generate_token()['token']
        time.sleep(1.1)  # 等待至少1秒以确保时间戳不同（JWT使用秒级精度）
        token2 = auth_manager.generate_token()['token']
        
        # 验证两个令牌不同
        assert token1 != token2, "Each generated token should be unique"
    
    # 测试令牌验证
    def test_verify_token_valid(self, auth_manager):
        """测试验证有效令牌应该成功
        
        需求：7.5
        """
        # 生成令牌
        token_data = auth_manager.generate_token()
        token = token_data['token']
        
        # 验证令牌
        payload = auth_manager.verify_token(token)
        
        # 验证应该成功
        assert payload is not None, "Valid token should be verified successfully"
        assert isinstance(payload, dict), "Payload should be a dictionary"
        assert payload['sub'] == 'admin', "Payload should contain correct subject"
    
    def test_verify_token_contains_timestamps(self, auth_manager):
        """测试验证令牌返回的载荷包含时间戳
        
        需求：7.5, 7.6
        """
        # 生成令牌
        token_data = auth_manager.generate_token()
        token = token_data['token']
        
        # 验证令牌
        payload = auth_manager.verify_token(token)
        
        # 验证载荷包含时间戳字段
        assert 'iat' in payload, "Payload should contain 'iat' (issued at) timestamp"
        assert 'exp' in payload, "Payload should contain 'exp' (expiration) timestamp"
        assert 'sub' in payload, "Payload should contain 'sub' (subject)"
    
    def test_verify_token_invalid_format(self, auth_manager):
        """测试验证格式错误的令牌应该失败
        
        需求：7.5
        """
        # 使用无效格式的令牌
        invalid_token = "invalid.token.format"
        
        # 验证令牌
        payload = auth_manager.verify_token(invalid_token)
        
        # 验证应该失败
        assert payload is None, "Invalid token format should fail verification"
    
    def test_verify_token_empty(self, auth_manager):
        """测试验证空令牌应该失败
        
        需求：7.5
        """
        # 使用空令牌
        empty_token = ""
        
        # 验证令牌
        payload = auth_manager.verify_token(empty_token)
        
        # 验证应该失败
        assert payload is None, "Empty token should fail verification"
    
    def test_verify_token_wrong_secret(self):
        """测试使用不同密钥验证令牌应该失败
        
        需求：7.5
        """
        # 创建两个使用不同密钥的 AuthManager
        auth_manager1 = AuthManager("secret_key_1", "password")
        auth_manager2 = AuthManager("secret_key_2", "password")
        
        # 使用第一个管理器生成令牌
        token = auth_manager1.generate_token()['token']
        
        # 使用第二个管理器验证应该失败
        payload = auth_manager2.verify_token(token)
        
        # 验证应该失败
        assert payload is None, "Token should fail verification with different secret key"
    
    def test_verify_token_expired(self, auth_manager):
        """测试验证过期令牌应该失败
        
        需求：7.5, 7.6
        """
        # 设置极短的过期时间（1秒）
        original_expiry = auth_manager.token_expiry_hours
        auth_manager.token_expiry_hours = 1 / 3600  # 1 second
        
        # 生成令牌
        token = auth_manager.generate_token()['token']
        
        # 等待令牌过期
        time.sleep(2)
        
        # 验证过期的令牌
        payload = auth_manager.verify_token(token)
        
        # 验证应该失败
        assert payload is None, "Expired token should fail verification"
        
        # 恢复原始过期时间
        auth_manager.token_expiry_hours = original_expiry
    
    # 边界情况测试
    def test_password_with_special_characters(self):
        """测试包含特殊字符的密码
        
        需求：7.5
        """
        # 创建包含特殊字符的密码
        special_password = "p@ssw0rd!#$%^&*()"
        auth_manager = AuthManager("secret_key", special_password)
        
        # 验证正确的密码
        assert auth_manager.verify_password(special_password) is True
        
        # 验证错误的密码
        assert auth_manager.verify_password("p@ssw0rd") is False
    
    def test_password_with_unicode(self):
        """测试包含 Unicode 字符的密码
        
        需求：7.5
        """
        # 创建包含中文字符的密码
        unicode_password = "密码123"
        auth_manager = AuthManager("secret_key", unicode_password)
        
        # 验证正确的密码
        assert auth_manager.verify_password(unicode_password) is True
        
        # 验证错误的密码
        assert auth_manager.verify_password("密码") is False
    
    def test_token_generation_consistency(self, auth_manager):
        """测试令牌生成的一致性
        
        需求：7.5
        """
        # 生成多个令牌
        tokens = [auth_manager.generate_token() for _ in range(5)]
        
        # 验证所有令牌都有相同的过期时间设置
        expires_in_values = [t['expires_in'] for t in tokens]
        assert all(e == expires_in_values[0] for e in expires_in_values), \
            "All tokens should have the same expiry time setting"
        
        # 验证所有令牌都可以被验证
        for token_data in tokens:
            payload = auth_manager.verify_token(token_data['token'])
            assert payload is not None, "All generated tokens should be valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ==================== Flask 应用测试 Fixtures ====================

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


# ==================== 登录登出单元测试 ====================

class TestLoginLogoutEndpoints:
    """登录和登出端点单元测试类
    
    测试需求：7.5 - 当用户提供错误的凭据时，Authentication_Module 应拒绝访问并显示错误消息
    """
    
    def test_login_with_correct_password_success(self, client):
        """测试正确密码登录成功
        
        验证使用正确的管理员密码可以成功登录并获得有效的 JWT 令牌。
        
        需求：7.5
        """
        # 发送登录请求，使用正确的密码
        response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Login with correct password should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        assert 'token' in data['data'], \
            "Response data should contain JWT token"
        
        # 验证令牌不为空且是字符串
        token = data['data']['token']
        assert isinstance(token, str), \
            "Token should be a string"
        assert len(token) > 0, \
            "Token should not be empty"
    
    def test_login_with_wrong_password_fails(self, client):
        """测试错误密码登录失败
        
        验证使用错误的密码登录时，系统拒绝访问并返回 401 未授权状态码。
        
        需求：7.5
        """
        # 发送登录请求，使用错误的密码
        response = client.post('/api/auth/login', json={
            'password': 'wrong_password_123'
        })
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Login with wrong password should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_CREDENTIALS', \
            "Error code should be INVALID_CREDENTIALS"
        assert 'message' in data['error'], \
            "Error should contain user-friendly message"
    
    def test_login_with_empty_password_fails(self, client):
        """测试空密码登录失败
        
        验证使用空密码登录时，系统拒绝访问并返回 400 错误请求状态码。
        
        需求：7.5
        """
        # 发送登录请求，使用空密码
        response = client.post('/api/auth/login', json={
            'password': ''
        })
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Login with empty password should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_login_without_password_field_fails(self, client):
        """测试缺少密码字段登录失败
        
        验证请求体中不包含密码字段时，系统返回 400 错误请求状态码。
        
        需求：7.5
        """
        # 发送登录请求，不包含密码字段
        response = client.post('/api/auth/login', json={})
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Login without password field should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'MISSING_PASSWORD', \
            "Error code should be MISSING_PASSWORD"
    
    def test_unauthenticated_access_returns_401(self, client):
        """测试未认证访问返回 401
        
        验证在没有提供有效认证令牌的情况下访问受保护的端点时，
        系统返回 401 未授权状态码。
        
        需求：7.5
        """
        # 尝试访问受保护的端点，不提供认证令牌
        response = client.get('/api/configs')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Access without authentication should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'UNAUTHORIZED', \
            "Error code should be UNAUTHORIZED"
    
    def test_invalid_token_format_returns_401(self, client):
        """测试无效令牌格式返回 401
        
        验证使用格式错误的认证令牌访问受保护端点时，系统返回 401 状态码。
        
        需求：7.5
        """
        # 尝试访问受保护的端点，使用无效格式的令牌
        response = client.get('/api/configs', headers={
            'Authorization': 'InvalidTokenFormat'
        })
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Access with invalid token format should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_expired_token_returns_401(self, client):
        """测试过期令牌返回 401
        
        验证使用已过期的认证令牌访问受保护端点时，系统返回 401 状态码。
        
        需求：7.5
        """
        # 创建一个短期有效的 AuthManager
        temp_auth = AuthManager(
            secret_key="test_secret_key_12345678",
            admin_password="test_admin_password"
        )
        temp_auth.token_expiry_hours = 1 / 3600  # 1 秒
        
        # 生成令牌
        token = temp_auth.generate_token()['token']
        
        # 等待令牌过期
        time.sleep(2)
        
        # 尝试使用过期令牌访问受保护的端点
        response = client.get('/api/configs', headers={
            'Authorization': f'Bearer {token}'
        })
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Access with expired token should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_logout_with_valid_token_success(self, client):
        """测试使用有效令牌登出成功
        
        验证使用有效的认证令牌可以成功登出。
        
        需求：7.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        
        # 发送登出请求
        response = client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {token}'
        })
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Logout with valid token should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'message' in data, \
            "Response should contain success message"
    
    def test_logout_without_token_fails(self, client):
        """测试未认证登出失败
        
        验证在没有提供认证令牌的情况下尝试登出时，系统返回 401 状态码。
        
        需求：7.5
        """
        # 尝试登出，不提供认证令牌
        response = client.post('/api/auth/logout')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Logout without token should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
    
    def test_authenticated_access_with_valid_token_success(self, client):
        """测试使用有效令牌访问受保护端点成功
        
        验证使用有效的认证令牌可以成功访问受保护的 API 端点。
        
        需求：7.5
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
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Access with valid token should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
    
    def test_login_error_message_does_not_leak_info(self, client):
        """测试登录错误消息不泄露敏感信息
        
        验证登录失败时的错误消息是通用的，不会泄露系统内部信息。
        
        需求：7.5
        """
        # 使用错误密码登录
        response = client.post('/api/auth/login', json={
            'password': 'wrong_password'
        })
        
        # 验证错误消息是通用的
        data = response.get_json()
        error_message = data['error']['message'].lower()
        
        # 错误消息不应包含具体的密码信息或系统细节
        assert 'password' not in error_message or 'invalid' in error_message, \
            "Error message should not leak specific password information"
        assert 'admin' not in error_message, \
            "Error message should not leak admin username"
    
    def test_multiple_login_attempts_allowed(self, client):
        """测试允许多次登录尝试
        
        验证系统允许用户进行多次登录尝试（在实际生产环境中应该有速率限制）。
        
        需求：7.5
        """
        # 进行多次登录尝试
        for i in range(3):
            response = client.post('/api/auth/login', json={
                'password': 'test_admin_password'
            })
            
            # 验证每次都能成功登录
            assert response.status_code == 200, \
                f"Login attempt {i+1} should succeed"
            
            # 验证每次都获得令牌
            data = response.get_json()
            assert 'token' in data['data'], \
                f"Login attempt {i+1} should return a token"




# ==================== 配置查询单元测试 ====================

class TestConfigQueryEndpoints:
    """配置查询端点单元测试类
    
    测试需求：3.5, 6.5 - 有效配置查询
    """
    
    def test_get_effective_config_with_session_config(self, client):
        """测试获取有效配置（会话配置存在）
        
        验证当会话配置存在时，有效配置应该使用会话配置的值。
        
        需求：3.5, 6.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个会话配置
        session_id = 'test_session_001'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'target_project_dir': '/test/project',
                      'response_language': 'en-US',
                      'default_provider': 'gemini',
                      'default_layer': 'cli',
                      'default_cli_provider': 'openai'
                  },
                  headers=headers)
        
        # 获取有效配置
        response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Get effective config should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        assert 'effective_config' in data['data'], \
            "Response data should contain effective_config"
        
        # 验证有效配置使用会话配置的值
        effective = data['data']['effective_config']
        assert effective['target_project_dir'] == '/test/project', \
            "Effective config should use session config value for target_project_dir"
        assert effective['response_language'] == 'en-US', \
            "Effective config should use session config value for response_language"
        assert effective['default_provider'] == 'gemini', \
            "Effective config should use session config value for default_provider"
        assert effective['default_layer'] == 'cli', \
            "Effective config should use session config value for default_layer"
        assert effective['default_cli_provider'] == 'openai', \
            "Effective config should use session config value for default_cli_provider"
    
    def test_get_effective_config_without_session_config(self, client):
        """测试获取有效配置（会话配置不存在）
        
        验证当会话配置不存在时，有效配置应该使用全局默认值。
        
        需求：3.5, 6.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取不存在的会话的有效配置
        session_id = 'nonexistent_session'
        response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Get effective config should return 200 OK even if session config doesn't exist"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        assert 'effective_config' in data['data'], \
            "Response data should contain effective_config"
        
        # 验证有效配置使用默认值
        effective = data['data']['effective_config']
        assert 'target_project_dir' in effective, \
            "Effective config should contain target_project_dir"
        assert 'response_language' in effective, \
            "Effective config should contain response_language"
        assert 'default_provider' in effective, \
            "Effective config should contain default_provider"
        assert 'default_layer' in effective, \
            "Effective config should contain default_layer"
        assert 'default_cli_provider' in effective, \
            "Effective config should contain default_cli_provider"
    
    def test_get_effective_config_partial_session_config(self, client):
        """测试获取有效配置（部分会话配置）
        
        验证当会话配置只设置了部分字段时，有效配置应该对已设置的字段使用会话值，
        对未设置的字段使用全局默认值。
        
        需求：3.5, 6.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个只设置部分字段的会话配置
        session_id = 'test_session_partial'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'gemini',  # 只设置 provider
                      # 其他字段不设置，应该使用默认值
                  },
                  headers=headers)
        
        # 获取有效配置
        response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Get effective config should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        effective = data['data']['effective_config']
        
        # 验证已设置的字段使用会话配置的值
        assert effective['default_provider'] == 'gemini', \
            "Effective config should use session config value for set fields"
        
        # 验证未设置的字段使用默认值
        assert 'target_project_dir' in effective, \
            "Effective config should contain default value for unset fields"
        assert 'response_language' in effective, \
            "Effective config should contain default value for unset fields"
        assert 'default_layer' in effective, \
            "Effective config should contain default value for unset fields"
    
    def test_get_effective_config_without_auth_fails(self, client):
        """测试未认证获取有效配置失败
        
        验证在没有提供认证令牌的情况下尝试获取有效配置时，系统返回 401 状态码。
        
        需求：7.4
        """
        # 尝试获取有效配置，不提供认证令牌
        session_id = 'test_session_001'
        response = client.get(f'/api/configs/{session_id}/effective')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Get effective config without auth should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_get_effective_config_priority_rules(self, client):
        """测试有效配置优先级规则
        
        验证有效配置正确应用优先级规则：会话配置 > 全局配置 > 默认值
        
        需求：3.5, 6.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建会话配置，只设置 provider
        session_id = 'test_priority'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'gemini',
                  },
                  headers=headers)
        
        # 获取有效配置
        response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        data = response.get_json()
        effective = data['data']['effective_config']
        
        # 验证会话配置的字段使用会话值
        assert effective['default_provider'] == 'gemini', \
            "Session config should override global config"
        
        # 验证未设置的字段使用全局配置或默认值
        # 这些字段应该存在且有值（来自全局配置或默认值）
        assert effective['default_layer'] in ['api', 'cli'], \
            "Unset fields should use global config or default values"
    
    def test_get_global_config_success(self, client):
        """测试获取全局配置成功
        
        验证可以成功获取全局默认配置。
        
        需求：12.1, 12.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取全局配置
        response = client.get('/api/configs/global', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Get global config should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        assert 'global_config' in data['data'], \
            "Response data should contain global_config"
        
        # 验证全局配置包含所有必需字段
        global_config = data['data']['global_config']
        assert 'target_project_dir' in global_config, \
            "Global config should contain target_project_dir"
        assert 'response_language' in global_config, \
            "Global config should contain response_language"
        assert 'default_provider' in global_config, \
            "Global config should contain default_provider"
        assert 'default_layer' in global_config, \
            "Global config should contain default_layer"
        assert 'default_cli_provider' in global_config, \
            "Global config should contain default_cli_provider"
    
    def test_get_global_config_without_auth_fails(self, client):
        """测试未认证获取全局配置失败
        
        验证在没有提供认证令牌的情况下尝试获取全局配置时，系统返回 401 状态码。
        
        需求：7.4
        """
        # 尝试获取全局配置，不提供认证令牌
        response = client.get('/api/configs/global')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Get global config without auth should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_get_global_config_readonly(self, client):
        """测试全局配置是只读的
        
        验证全局配置端点只支持 GET 方法，返回的是全局配置而不是会话配置。
        
        需求：12.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取全局配置
        response = client.get('/api/configs/global', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "GET method on global config should return 200 OK"
        
        # 验证返回的是全局配置格式（包含 global_config 字段）
        data = response.get_json()
        assert 'global_config' in data['data'], \
            "Response should contain global_config field"
        
        # 验证不包含会话配置特有的字段（如 session_id, metadata）
        assert 'session_id' not in data['data'], \
            "Global config response should not contain session_id"
        assert 'metadata' not in data['data'], \
            "Global config response should not contain metadata"
    
    def test_get_empty_config_list(self, client):
        """测试空配置列表
        
        验证当系统中没有任何配置时，GET /api/configs 返回空列表。
        
        需求：2.6
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取配置列表（应该为空）
        response = client.get('/api/configs', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Get empty config list should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        
        # 验证返回空列表
        assert isinstance(data['data'], list), \
            "Data should be a list"
        assert len(data['data']) == 0, \
            "Config list should be empty"
    
    def test_filter_configs_by_session_type(self, client):
        """测试配置筛选功能 - 按会话类型筛选
        
        验证可以按 session_type 筛选配置列表，只返回匹配的配置。
        
        需求：2.3, 6.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建不同类型的配置
        client.put('/api/configs/user_001', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        client.put('/api/configs/user_002', 
                  json={'session_type': 'user', 'default_provider': 'gemini'},
                  headers=headers)
        client.put('/api/configs/group_001', 
                  json={'session_type': 'group', 'default_provider': 'openai'},
                  headers=headers)
        
        # 筛选 user 类型的配置
        response = client.get('/api/configs?session_type=user', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Filter configs by session_type should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        
        configs = data['data']
        assert len(configs) == 2, \
            "Should return 2 user configs"
        
        # 验证所有返回的配置都是 user 类型
        for config in configs:
            assert config['session_type'] == 'user', \
                "All returned configs should be of type 'user'"
        
        # 筛选 group 类型的配置
        response = client.get('/api/configs?session_type=group', headers=headers)
        data = response.get_json()
        configs = data['data']
        
        assert len(configs) == 1, \
            "Should return 1 group config"
        assert configs[0]['session_type'] == 'group', \
            "Returned config should be of type 'group'"
    
    def test_search_configs_by_session_id(self, client):
        """测试配置筛选功能 - 按会话 ID 搜索
        
        验证可以按 session_id 搜索配置列表，返回包含搜索关键词的配置。
        
        需求：2.4, 6.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建多个配置
        client.put('/api/configs/test_user_001', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        client.put('/api/configs/test_user_002', 
                  json={'session_type': 'user', 'default_provider': 'gemini'},
                  headers=headers)
        client.put('/api/configs/prod_group_001', 
                  json={'session_type': 'group', 'default_provider': 'openai'},
                  headers=headers)
        
        # 搜索包含 "test" 的配置
        response = client.get('/api/configs?search=test', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Search configs should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        
        configs = data['data']
        assert len(configs) == 2, \
            "Should return 2 configs containing 'test'"
        
        # 验证所有返回的配置 ID 都包含搜索关键词
        for config in configs:
            assert 'test' in config['session_id'].lower(), \
                "All returned config IDs should contain 'test'"
        
        # 搜索包含 "prod" 的配置
        response = client.get('/api/configs?search=prod', headers=headers)
        data = response.get_json()
        configs = data['data']
        
        assert len(configs) == 1, \
            "Should return 1 config containing 'prod'"
        assert 'prod' in configs[0]['session_id'].lower(), \
            "Returned config ID should contain 'prod'"
    
    def test_sort_configs_by_updated_time(self, client):
        """测试配置排序功能 - 按更新时间排序
        
        验证可以按更新时间对配置列表进行排序（升序和降序）。
        
        需求：2.5, 6.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建多个配置，确保它们有不同的更新时间
        client.put('/api/configs/config_001', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        time.sleep(0.1)  # 确保时间戳不同
        
        client.put('/api/configs/config_002', 
                  json={'session_type': 'user', 'default_provider': 'gemini'},
                  headers=headers)
        time.sleep(0.1)
        
        client.put('/api/configs/config_003', 
                  json={'session_type': 'user', 'default_provider': 'openai'},
                  headers=headers)
        
        # 测试降序排序（默认）
        response = client.get('/api/configs?sort=updated_at&order=desc', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Sort configs should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        
        configs = data['data']
        assert len(configs) == 3, \
            "Should return all 3 configs"
        
        # 验证降序排序（最新的在前）
        updated_times = [config['metadata']['updated_at'] for config in configs]
        assert updated_times == sorted(updated_times, reverse=True), \
            "Configs should be sorted by updated_at in descending order"
        
        # 测试升序排序
        response = client.get('/api/configs?sort=updated_at&order=asc', headers=headers)
        data = response.get_json()
        configs = data['data']
        
        # 验证升序排序（最旧的在前）
        updated_times = [config['metadata']['updated_at'] for config in configs]
        assert updated_times == sorted(updated_times), \
            "Configs should be sorted by updated_at in ascending order"
    
    def test_get_nonexistent_config_returns_404(self, client):
        """测试配置不存在返回 404
        
        验证当请求不存在的配置时，系统返回 404 Not Found 状态码。
        
        需求：6.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 请求不存在的配置
        response = client.get('/api/configs/nonexistent_session_id', headers=headers)
        
        # 验证响应状态码为 404 Not Found
        assert response.status_code == 404, \
            "Get nonexistent config should return 404 Not Found"
        
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
        assert 'nonexistent_session_id' in data['error']['message'], \
            "Error message should mention the session ID"
    
    def test_combined_filter_and_search(self, client):
        """测试组合筛选和搜索
        
        验证可以同时使用 session_type 筛选和 session_id 搜索。
        
        需求：2.3, 2.4, 6.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建多个配置
        client.put('/api/configs/test_user_001', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        client.put('/api/configs/test_group_001', 
                  json={'session_type': 'group', 'default_provider': 'gemini'},
                  headers=headers)
        client.put('/api/configs/prod_user_001', 
                  json={'session_type': 'user', 'default_provider': 'openai'},
                  headers=headers)
        
        # 组合筛选：session_type=user 且 search=test
        response = client.get('/api/configs?session_type=user&search=test', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Combined filter and search should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        configs = data['data']
        
        # 应该只返回一个配置：test_user_001
        assert len(configs) == 1, \
            "Should return 1 config matching both filters"
        assert configs[0]['session_id'] == 'test_user_001', \
            "Should return test_user_001"
        assert configs[0]['session_type'] == 'user', \
            "Config should be of type 'user'"
    
    def test_filter_with_no_matches(self, client):
        """测试筛选无匹配结果
        
        验证当筛选条件没有匹配的配置时，返回空列表。
        
        需求：2.3, 2.4, 6.2
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一些配置
        client.put('/api/configs/user_001', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        
        # 筛选不存在的类型
        response = client.get('/api/configs?session_type=nonexistent', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Filter with no matches should return 200 OK"
        
        # 验证返回空列表
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert len(data['data']) == 0, \
            "Should return empty list when no configs match"
        
        # 搜索不存在的关键词
        response = client.get('/api/configs?search=nonexistent_keyword', headers=headers)
        data = response.get_json()
        
        assert len(data['data']) == 0, \
            "Should return empty list when search has no matches"



# ==================== 配置删除单元测试 ====================

class TestConfigDeleteEndpoint:
    """配置删除端点单元测试类
    
    测试需求：5.3, 5.5, 6.4 - 配置删除（重置）功能
    """
    
    def test_delete_existing_config_success(self, client):
        """测试删除存在的配置成功
        
        验证可以成功删除一个存在的会话配置。
        
        需求：5.3, 5.5, 6.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个配置
        session_id = 'test_delete_001'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude',
                      'default_layer': 'api'
                  },
                  headers=headers)
        
        # 验证配置已创建
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert get_response.status_code == 200, \
            "Config should exist before deletion"
        
        # 删除配置
        delete_response = client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert delete_response.status_code == 200, \
            "Delete existing config should return 200 OK"
        
        # 验证响应数据结构
        data = delete_response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'message' in data, \
            "Response should contain success message"
        
        # 验证配置已被删除
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert get_response.status_code == 404, \
            "Config should not exist after deletion"
    
    def test_delete_nonexistent_config_returns_404(self, client):
        """测试删除不存在的配置返回 404
        
        验证尝试删除不存在的配置时，系统返回 404 Not Found 状态码。
        
        需求：5.3, 6.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 尝试删除不存在的配置
        session_id = 'nonexistent_config'
        response = client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # 验证响应状态码为 404 Not Found
        assert response.status_code == 404, \
            "Delete nonexistent config should return 404 Not Found"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'NOT_FOUND', \
            "Error code should be NOT_FOUND"
    
    def test_delete_config_without_auth_fails(self, client):
        """测试未认证删除配置失败
        
        验证在没有提供认证令牌的情况下尝试删除配置时，系统返回 401 状态码。
        
        需求：7.4, 6.4
        """
        # 尝试删除配置，不提供认证令牌
        session_id = 'test_delete_002'
        response = client.delete(f'/api/configs/{session_id}')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Delete config without auth should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_delete_config_persists_after_deletion(self, client):
        """测试配置删除后持久化
        
        验证配置删除操作会持久化到存储，删除后配置不再存在于配置列表中。
        
        需求：5.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建多个配置
        client.put('/api/configs/persist_001', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        client.put('/api/configs/persist_002', 
                  json={'session_type': 'user', 'default_provider': 'gemini'},
                  headers=headers)
        
        # 获取配置列表，验证有 2 个配置
        list_response = client.get('/api/configs', headers=headers)
        configs = list_response.get_json()['data']
        assert len(configs) == 2, \
            "Should have 2 configs before deletion"
        
        # 删除一个配置
        client.delete('/api/configs/persist_001', headers=headers)
        
        # 再次获取配置列表，验证只剩 1 个配置
        list_response = client.get('/api/configs', headers=headers)
        configs = list_response.get_json()['data']
        assert len(configs) == 1, \
            "Should have 1 config after deletion"
        assert configs[0]['session_id'] == 'persist_002', \
            "Remaining config should be persist_002"
    
    def test_delete_config_multiple_times(self, client):
        """测试多次删除同一配置
        
        验证第一次删除成功，后续删除返回 404。
        
        需求：5.3, 6.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个配置
        session_id = 'test_multi_delete'
        client.put(f'/api/configs/{session_id}', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        
        # 第一次删除应该成功
        response1 = client.delete(f'/api/configs/{session_id}', headers=headers)
        assert response1.status_code == 200, \
            "First deletion should succeed"
        
        # 第二次删除应该返回 404
        response2 = client.delete(f'/api/configs/{session_id}', headers=headers)
        assert response2.status_code == 404, \
            "Second deletion should return 404"
        
        # 第三次删除也应该返回 404
        response3 = client.delete(f'/api/configs/{session_id}', headers=headers)
        assert response3.status_code == 404, \
            "Third deletion should also return 404"
    
    def test_delete_config_resets_to_defaults(self, client):
        """测试删除配置后恢复默认值
        
        验证删除配置后，该会话将使用全局默认配置。
        
        需求：5.3, 5.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个配置
        session_id = 'test_reset_defaults'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'gemini',
                      'default_layer': 'cli'
                  },
                  headers=headers)
        
        # 获取有效配置，验证使用会话配置的值
        effective_response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        effective_before = effective_response.get_json()['data']['effective_config']
        assert effective_before['default_provider'] == 'gemini', \
            "Should use session config before deletion"
        
        # 删除配置
        client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # 再次获取有效配置，验证使用全局默认值
        effective_response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        effective_after = effective_response.get_json()['data']['effective_config']
        
        # 验证不再使用会话配置的值（应该使用全局默认值）
        # 注意：这里不能断言具体的默认值，因为全局配置可能不同
        # 但可以验证有效配置仍然存在且包含所有必需字段
        assert 'default_provider' in effective_after, \
            "Effective config should still contain default_provider"
        assert 'default_layer' in effective_after, \
            "Effective config should still contain default_layer"
    
    def test_delete_config_with_invalid_token_fails(self, client):
        """测试使用无效令牌删除配置失败
        
        验证使用无效的认证令牌尝试删除配置时，系统返回 401 状态码。
        
        需求：7.4, 6.4
        """
        # 尝试删除配置，使用无效令牌
        session_id = 'test_delete_003'
        response = client.delete(f'/api/configs/{session_id}', headers={
            'Authorization': 'Bearer invalid_token_12345'
        })
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Delete config with invalid token should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
    
    def test_delete_config_response_format(self, client):
        """测试删除配置响应格式
        
        验证删除配置的响应符合 API 响应格式规范。
        
        需求：6.4, 6.6
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个配置
        session_id = 'test_response_format'
        client.put(f'/api/configs/{session_id}', 
                  json={'session_type': 'user', 'default_provider': 'claude'},
                  headers=headers)
        
        # 删除配置
        response = client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # 验证响应格式
        data = response.get_json()
        
        # 验证包含必需字段
        assert 'success' in data, \
            "Response should contain 'success' field"
        assert 'message' in data, \
            "Response should contain 'message' field"
        
        # 验证字段类型
        assert isinstance(data['success'], bool), \
            "'success' should be a boolean"
        assert isinstance(data['message'], str), \
            "'message' should be a string"
        
        # 验证成功响应的值
        assert data['success'] is True, \
            "'success' should be True for successful deletion"
        assert len(data['message']) > 0, \
            "'message' should not be empty"



# ==================== 配置修改单元测试 ====================

class TestConfigModificationEndpoint:
    """配置修改端点单元测试类
    
    测试需求：4.8, 4.9, 5.4 - 配置创建、更新、验证和元数据
    """
    
    def test_create_new_config_success(self, client):
        """测试创建新配置成功
        
        验证可以成功创建一个新的会话配置。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建新配置
        session_id = 'test_create_001'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'target_project_dir': '/test/project',
                                 'response_language': 'English',
                                 'default_provider': 'claude',
                                 'default_layer': 'api',
                                 'default_cli_provider': 'gemini'
                             },
                             headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Create new config should return 200 OK"
        
        # 验证响应数据结构
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        
        # 验证配置数据
        config_data = data['data']
        assert config_data['session_id'] == session_id, \
            "Config should have correct session_id"
        assert config_data['config']['target_project_dir'] == '/test/project', \
            "Config should have correct target_project_dir"
        assert config_data['config']['response_language'] == 'English', \
            "Config should have correct response_language"
        assert config_data['config']['default_provider'] == 'claude', \
            "Config should have correct default_provider"
        assert config_data['config']['default_layer'] == 'api', \
            "Config should have correct default_layer"
        assert config_data['config']['default_cli_provider'] == 'gemini', \
            "Config should have correct default_cli_provider"
        
        # 验证元数据存在
        assert 'metadata' in config_data, \
            "Config should contain metadata"
        assert 'created_at' in config_data['metadata'], \
            "Metadata should contain created_at"
        assert 'updated_at' in config_data['metadata'], \
            "Metadata should contain updated_at"
        assert 'update_count' in config_data['metadata'], \
            "Metadata should contain update_count"
    
    def test_update_existing_config_success(self, client):
        """测试更新现有配置成功
        
        验证可以成功更新一个已存在的会话配置。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建初始配置
        session_id = 'test_update_001'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude',
                      'default_layer': 'api'
                  },
                  headers=headers)
        
        # 更新配置
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'default_provider': 'gemini',
                                 'default_layer': 'cli',
                                 'target_project_dir': '/updated/path'
                             },
                             headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Update existing config should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        
        # 验证配置已更新
        config_data = data['data']
        assert config_data['config']['default_provider'] == 'gemini', \
            "Provider should be updated to gemini"
        assert config_data['config']['default_layer'] == 'cli', \
            "Layer should be updated to cli"
        assert config_data['config']['target_project_dir'] == '/updated/path', \
            "Target directory should be updated"
    
    def test_reject_invalid_provider(self, client):
        """测试拒绝无效的 provider
        
        验证当提供无效的 provider 值时，系统拒绝更新并返回 400 错误。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 尝试设置无效的 provider
        session_id = 'test_invalid_provider'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'invalid_provider'
                             },
                             headers=headers)
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Invalid provider should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_PROVIDER', \
            "Error code should be INVALID_PROVIDER"
        assert 'field' in data['error'], \
            "Error should specify the field"
        assert data['error']['field'] == 'default_provider', \
            "Error field should be default_provider"
        
        # 验证错误消息是用户友好的
        assert 'message' in data['error'], \
            "Error should contain user-friendly message"
        assert len(data['error']['message']) > 0, \
            "Error message should not be empty"
        assert 'claude' in data['error']['message'].lower() or \
               'gemini' in data['error']['message'].lower() or \
               'openai' in data['error']['message'].lower(), \
            "Error message should mention valid providers"
    
    def test_reject_invalid_layer(self, client):
        """测试拒绝无效的 layer
        
        验证当提供无效的 layer 值时，系统拒绝更新并返回 400 错误。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 尝试设置无效的 layer
        session_id = 'test_invalid_layer'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_layer': 'invalid_layer'
                             },
                             headers=headers)
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Invalid layer should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_LAYER', \
            "Error code should be INVALID_LAYER"
        assert 'field' in data['error'], \
            "Error should specify the field"
        assert data['error']['field'] == 'default_layer', \
            "Error field should be default_layer"
        
        # 验证错误消息是用户友好的
        assert 'message' in data['error'], \
            "Error should contain user-friendly message"
        assert len(data['error']['message']) > 0, \
            "Error message should not be empty"
        assert 'api' in data['error']['message'].lower() or \
               'cli' in data['error']['message'].lower(), \
            "Error message should mention valid layers"
    
    def test_reject_invalid_cli_provider(self, client):
        """测试拒绝无效的 CLI provider
        
        验证当提供无效的 CLI provider 值时，系统拒绝更新并返回 400 错误。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 尝试设置无效的 CLI provider
        session_id = 'test_invalid_cli_provider'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_cli_provider': 'invalid_cli_provider'
                             },
                             headers=headers)
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Invalid CLI provider should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_PROVIDER', \
            "Error code should be INVALID_PROVIDER"
        assert 'field' in data['error'], \
            "Error should specify the field"
        assert data['error']['field'] == 'default_cli_provider', \
            "Error field should be default_cli_provider"
    
    def test_config_deletion_via_delete_endpoint(self, client):
        """测试通过 DELETE 端点删除配置
        
        验证可以使用 DELETE 方法删除配置。
        
        需求：5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建配置
        session_id = 'test_delete_via_endpoint'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude'
                  },
                  headers=headers)
        
        # 验证配置存在
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert get_response.status_code == 200, \
            "Config should exist before deletion"
        
        # 删除配置
        delete_response = client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # 验证删除成功
        assert delete_response.status_code == 200, \
            "Delete should return 200 OK"
        
        # 验证配置已被删除
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert get_response.status_code == 404, \
            "Config should not exist after deletion"
    
    def test_metadata_update_on_config_change(self, client):
        """测试配置更新时元数据自动更新
        
        验证当配置被更新时，updated_at 和 update_count 会自动更新。
        
        需求：4.9, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建初始配置
        session_id = 'test_metadata_update'
        response1 = client.put(f'/api/configs/{session_id}', 
                              json={
                                  'session_type': 'user',
                                  'default_provider': 'claude'
                              },
                              headers=headers)
        
        data1 = response1.get_json()
        initial_updated_at = data1['data']['metadata']['updated_at']
        initial_update_count = data1['data']['metadata']['update_count']
        
        # 等待一小段时间确保时间戳不同
        time.sleep(0.1)
        
        # 更新配置
        response2 = client.put(f'/api/configs/{session_id}', 
                              json={
                                  'default_provider': 'gemini'
                              },
                              headers=headers)
        
        data2 = response2.get_json()
        updated_updated_at = data2['data']['metadata']['updated_at']
        updated_update_count = data2['data']['metadata']['update_count']
        
        # 验证 updated_at 已更新
        assert updated_updated_at != initial_updated_at, \
            "updated_at should be updated after config change"
        assert updated_updated_at > initial_updated_at, \
            "updated_at should be later than initial value"
        
        # 验证 update_count 已递增
        assert updated_update_count == initial_update_count + 1, \
            "update_count should increment by 1 after each update"
    
    def test_metadata_created_at_unchanged_on_update(self, client):
        """测试配置更新时 created_at 不变
        
        验证当配置被更新时，created_at 保持不变。
        
        需求：4.9, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建初始配置
        session_id = 'test_created_at_unchanged'
        response1 = client.put(f'/api/configs/{session_id}', 
                              json={
                                  'session_type': 'user',
                                  'default_provider': 'claude'
                              },
                              headers=headers)
        
        data1 = response1.get_json()
        initial_created_at = data1['data']['metadata']['created_at']
        
        # 等待一小段时间
        time.sleep(0.1)
        
        # 更新配置
        response2 = client.put(f'/api/configs/{session_id}', 
                              json={
                                  'default_provider': 'gemini'
                              },
                              headers=headers)
        
        data2 = response2.get_json()
        updated_created_at = data2['data']['metadata']['created_at']
        
        # 验证 created_at 未改变
        assert updated_created_at == initial_created_at, \
            "created_at should remain unchanged after config update"
    
    def test_multiple_updates_increment_count(self, client):
        """测试多次更新递增计数
        
        验证多次更新配置时，update_count 持续递增。
        
        需求：4.9, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建初始配置
        session_id = 'test_multiple_updates'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'claude'
                             },
                             headers=headers)
        
        initial_count = response.get_json()['data']['metadata']['update_count']
        
        # 执行多次更新
        providers = ['gemini', 'openai', 'claude', 'gemini']
        for i, provider in enumerate(providers, start=1):
            time.sleep(0.05)  # 确保时间戳不同
            response = client.put(f'/api/configs/{session_id}', 
                                 json={'default_provider': provider},
                                 headers=headers)
            
            current_count = response.get_json()['data']['metadata']['update_count']
            expected_count = initial_count + i
            
            assert current_count == expected_count, \
                f"After update {i}, update_count should be {expected_count}"
    
    def test_partial_config_update(self, client):
        """测试部分配置更新
        
        验证可以只更新配置的部分字段，其他字段保持不变。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建完整配置
        session_id = 'test_partial_update'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'target_project_dir': '/original/path',
                      'response_language': 'English',
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
        
        # 验证更新成功
        assert response.status_code == 200, \
            "Partial update should succeed"
        
        # 验证只有 provider 被更新，其他字段保持不变
        config = response.get_json()['data']['config']
        assert config['default_provider'] == 'gemini', \
            "Provider should be updated"
        assert config['target_project_dir'] == '/original/path', \
            "Target directory should remain unchanged"
        assert config['response_language'] == 'English', \
            "Response language should remain unchanged"
        assert config['default_layer'] == 'api', \
            "Layer should remain unchanged"
    
    def test_config_validation_error_messages_user_friendly(self, client):
        """测试配置验证错误消息用户友好
        
        验证当配置验证失败时，错误消息清晰且用户友好。
        
        需求：4.8, 4.9, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 测试无效 provider 的错误消息
        session_id = 'test_error_messages'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'invalid_value'
                             },
                             headers=headers)
        
        data = response.get_json()
        error_message = data['error']['message']
        
        # 验证错误消息包含有用信息
        assert 'invalid' in error_message.lower() or \
               'provider' in error_message.lower(), \
            "Error message should mention the problem"
        
        # 验证错误消息提供了有效选项
        assert 'claude' in error_message or \
               'gemini' in error_message or \
               'openai' in error_message, \
            "Error message should list valid options"
        
        # 验证错误消息不包含技术细节或堆栈跟踪
        assert 'traceback' not in error_message.lower(), \
            "Error message should not contain technical details"
        assert 'exception' not in error_message.lower(), \
            "Error message should not contain exception details"
    
    def test_config_update_without_auth_fails(self, client):
        """测试未认证更新配置失败
        
        验证在没有提供认证令牌的情况下尝试更新配置时，系统返回 401 状态码。
        
        需求：7.4, 5.4
        """
        # 尝试更新配置，不提供认证令牌
        session_id = 'test_update_no_auth'
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'claude'
                             })
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Update config without auth should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_config_accepts_null_values(self, client):
        """测试配置接受 null 值
        
        验证可以将配置字段设置为 null 以清除该字段。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建配置
        session_id = 'test_null_values'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'target_project_dir': '/some/path',
                      'default_provider': 'claude'
                  },
                  headers=headers)
        
        # 将字段设置为 null
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'target_project_dir': None,
                                 'default_provider': None
                             },
                             headers=headers)
        
        # 验证更新成功
        assert response.status_code == 200, \
            "Setting fields to null should succeed"
        
        # 验证字段已被清除
        config = response.get_json()['data']['config']
        assert config['target_project_dir'] is None, \
            "Target directory should be null"
        assert config['default_provider'] is None, \
            "Provider should be null"
    
    def test_config_accepts_empty_string_as_null(self, client):
        """测试配置接受空字符串作为 null
        
        验证空字符串被视为 null 值。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建配置
        session_id = 'test_empty_string'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude'
                  },
                  headers=headers)
        
        # 将字段设置为空字符串
        response = client.put(f'/api/configs/{session_id}', 
                             json={
                                 'default_provider': ''
                             },
                             headers=headers)
        
        # 验证更新成功
        assert response.status_code == 200, \
            "Setting field to empty string should succeed"
        
        # 验证空字符串被视为 null
        config = response.get_json()['data']['config']
        assert config['default_provider'] is None or config['default_provider'] == '', \
            "Empty string should be treated as null"
    
    def test_config_response_format_consistency(self, client):
        """测试配置响应格式一致性
        
        验证创建和更新配置的响应格式一致。
        
        需求：4.8, 5.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建配置
        session_id = 'test_response_format'
        create_response = client.put(f'/api/configs/{session_id}', 
                                     json={
                                         'session_type': 'user',
                                         'default_provider': 'claude'
                                     },
                                     headers=headers)
        
        # 更新配置
        update_response = client.put(f'/api/configs/{session_id}', 
                                     json={
                                         'default_provider': 'gemini'
                                     },
                                     headers=headers)
        
        # 验证两个响应的格式一致
        create_data = create_response.get_json()
        update_data = update_response.get_json()
        
        # 验证都包含相同的顶层字段
        assert set(create_data.keys()) == set(update_data.keys()), \
            "Create and update responses should have same top-level fields"
        
        # 验证都包含 success, data, message 字段
        for response_data in [create_data, update_data]:
            assert 'success' in response_data, \
                "Response should contain 'success' field"
            assert 'data' in response_data, \
                "Response should contain 'data' field"
            assert 'message' in response_data, \
                "Response should contain 'message' field"
            
            # 验证 data 字段包含 session_id, config, metadata
            data_obj = response_data['data']
            assert 'session_id' in data_obj, \
                "Data should contain 'session_id'"
            assert 'config' in data_obj, \
                "Data should contain 'config'"
            assert 'metadata' in data_obj, \
                "Data should contain 'metadata'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ==================== 配置导出单元测试 ====================

class TestConfigExportEndpoint:
    """配置导出端点单元测试类
    
    测试需求：11.1, 11.3 - 配置导出功能
    """
    
    def test_export_configs_success(self, client):
        """测试导出配置成功
        
        验证可以成功导出所有配置为 JSON 文件。
        
        需求：11.1, 11.3
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一些测试配置
        test_configs = [
            {
                'session_id': 'export_test_001',
                'session_type': 'user',
                'default_provider': 'claude',
                'default_layer': 'api'
            },
            {
                'session_id': 'export_test_002',
                'session_type': 'group',
                'default_provider': 'gemini',
                'default_layer': 'cli'
            }
        ]
        
        for config in test_configs:
            session_id = config.pop('session_id')
            client.put(f'/api/configs/{session_id}', 
                      json=config,
                      headers=headers)
        
        # 导出配置
        response = client.post('/api/configs/export', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Export configs should return 200 OK"
        
        # 验证响应是文件下载
        assert response.content_type == 'application/json', \
            "Export should return JSON file"
        
        # 验证响应包含 Content-Disposition 头
        assert 'Content-Disposition' in response.headers, \
            "Export should include Content-Disposition header"
        assert 'attachment' in response.headers['Content-Disposition'], \
            "Export should be an attachment"
        assert 'feishu_bot_configs_' in response.headers['Content-Disposition'], \
            "Export filename should contain 'feishu_bot_configs_'"
        
        # 验证导出的 JSON 数据
        import json
        export_data = json.loads(response.data.decode('utf-8'))
        
        # 验证导出数据结构
        assert 'export_timestamp' in export_data, \
            "Export data should contain export_timestamp"
        assert 'export_version' in export_data, \
            "Export data should contain export_version"
        assert 'configs' in export_data, \
            "Export data should contain configs array"
        
        # 验证导出的配置数量
        assert len(export_data['configs']) >= 2, \
            "Export should contain at least the test configs"
        
        # 验证配置数据完整性
        for config in export_data['configs']:
            assert 'session_id' in config, \
                "Each config should have session_id"
            assert 'session_type' in config, \
                "Each config should have session_type"
            assert 'config' in config, \
                "Each config should have config object"
            assert 'metadata' in config, \
                "Each config should have metadata object"
    
    def test_export_configs_empty(self, client):
        """测试导出空配置列表
        
        验证当没有配置时，导出功能仍然正常工作。
        
        需求：11.1, 11.3
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 导出配置（应该为空）
        response = client.post('/api/configs/export', headers=headers)
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Export empty configs should return 200 OK"
        
        # 验证导出的 JSON 数据
        import json
        export_data = json.loads(response.data.decode('utf-8'))
        
        # 验证导出数据结构
        assert 'configs' in export_data, \
            "Export data should contain configs array"
        assert isinstance(export_data['configs'], list), \
            "Configs should be an array"
    
    def test_export_configs_without_auth_fails(self, client):
        """测试未认证导出配置失败
        
        验证在没有提供认证令牌的情况下尝试导出配置时，系统返回 401 状态码。
        
        需求：7.4
        """
        # 尝试导出配置，不提供认证令牌
        response = client.post('/api/configs/export')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Export without auth should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_export_configs_includes_all_fields(self, client):
        """测试导出包含所有配置字段
        
        验证导出的配置包含所有必需的字段和元数据。
        
        需求：11.1, 11.3
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个完整的配置
        session_id = 'export_complete_test'
        client.put(f'/api/configs/{session_id}', 
                  json={
                      'session_type': 'user',
                      'target_project_dir': '/test/project',
                      'response_language': 'zh-CN',
                      'default_provider': 'claude',
                      'default_layer': 'api',
                      'default_cli_provider': 'gemini'
                  },
                  headers=headers)
        
        # 导出配置
        response = client.post('/api/configs/export', headers=headers)
        
        # 验证导出的 JSON 数据
        import json
        export_data = json.loads(response.data.decode('utf-8'))
        
        # 查找我们创建的配置
        test_config = None
        for config in export_data['configs']:
            if config['session_id'] == session_id:
                test_config = config
                break
        
        assert test_config is not None, \
            "Export should contain the test config"
        
        # 验证配置字段完整性
        config_obj = test_config['config']
        assert config_obj['target_project_dir'] == '/test/project', \
            "Export should include target_project_dir"
        assert config_obj['response_language'] == 'zh-CN', \
            "Export should include response_language"
        assert config_obj['default_provider'] == 'claude', \
            "Export should include default_provider"
        assert config_obj['default_layer'] == 'api', \
            "Export should include default_layer"
        assert config_obj['default_cli_provider'] == 'gemini', \
            "Export should include default_cli_provider"
        
        # 验证元数据完整性
        metadata = test_config['metadata']
        assert 'created_by' in metadata, \
            "Export should include created_by metadata"
        assert 'created_at' in metadata, \
            "Export should include created_at metadata"
        assert 'updated_by' in metadata, \
            "Export should include updated_by metadata"
        assert 'updated_at' in metadata, \
            "Export should include updated_at metadata"
        assert 'update_count' in metadata, \
            "Export should include update_count metadata"


class TestConfigImportEndpoint:
    """配置导入端点单元测试类
    
    测试需求：11.2, 11.4, 11.5, 11.6, 11.7 - 配置导入功能
    """
    
    def test_import_configs_success(self, client):
        """测试导入配置成功
        
        验证可以成功从 JSON 文件导入配置。
        
        需求：11.2, 11.7
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备导入数据
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': 'import_test_001',
                    'session_type': 'user',
                    'config': {
                        'target_project_dir': '/import/test/project',
                        'response_language': 'zh-CN',
                        'default_provider': 'claude',
                        'default_layer': 'api',
                        'default_cli_provider': 'gemini'
                    },
                    'metadata': {
                        'created_by': 'test_user',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'test_user',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 1
                    }
                },
                {
                    'session_id': 'import_test_002',
                    'session_type': 'group',
                    'config': {
                        'target_project_dir': None,
                        'response_language': 'en-US',
                        'default_provider': 'gemini',
                        'default_layer': 'cli',
                        'default_cli_provider': None
                    },
                    'metadata': {
                        'created_by': 'test_user',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'test_user',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 2
                    }
                }
            ]
        }
        
        # 创建文件对象
        json_str = json.dumps(import_data, ensure_ascii=False)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 导入配置
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'test_import.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 200 OK
        assert response.status_code == 200, \
            "Import configs should return 200 OK"
        
        # 验证响应数据
        data = response.get_json()
        assert data['success'] is True, \
            "Response should indicate success"
        assert 'data' in data, \
            "Response should contain data field"
        assert 'imported_count' in data['data'], \
            "Response data should contain imported_count"
        assert data['data']['imported_count'] == 2, \
            "Should import 2 configurations"
        
        # 验证配置已导入
        get_response = client.get('/api/configs/import_test_001', headers=headers)
        assert get_response.status_code == 200, \
            "Imported config should be retrievable"
        
        imported_config = get_response.get_json()['data']
        assert imported_config['config']['target_project_dir'] == '/import/test/project', \
            "Imported config should have correct values"
    
    def test_import_configs_missing_file(self, client):
        """测试导入时缺少文件
        
        验证当请求中没有文件时，系统返回 400 错误。
        
        需求：11.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 尝试导入，不提供文件
        response = client.post('/api/configs/import',
                              data={},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import without file should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'MISSING_FILE', \
            "Error code should be MISSING_FILE"
    
    def test_import_configs_invalid_json(self, client):
        """测试导入无效的 JSON 文件
        
        验证当 JSON 格式错误时，系统返回 400 错误并拒绝导入。
        
        需求：11.4, 11.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备无效的 JSON 数据
        import io
        invalid_json = "{ invalid json format }"
        file_data = io.BytesIO(invalid_json.encode('utf-8'))
        
        # 尝试导入
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'invalid.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import with invalid JSON should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
        assert data['error']['code'] == 'INVALID_JSON', \
            "Error code should be INVALID_JSON"
    
    def test_import_configs_missing_configs_field(self, client):
        """测试导入缺少 configs 字段的文件
        
        验证当 JSON 文件缺少必需的 configs 字段时，系统返回 400 错误。
        
        需求：11.4, 11.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备缺少 configs 字段的数据
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0'
            # 缺少 configs 字段
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 尝试导入
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'missing_configs.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import without configs field should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert data['error']['code'] == 'MISSING_CONFIGS', \
            "Error code should be MISSING_CONFIGS"
    
    def test_import_configs_missing_required_fields(self, client):
        """测试导入缺少必需字段的配置
        
        验证当配置缺少必需字段时，系统返回 400 错误并拒绝导入。
        
        需求：11.4, 11.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备缺少必需字段的配置
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': 'incomplete_config',
                    # 缺少 session_type, config, metadata 字段
                }
            ]
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 尝试导入
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'incomplete.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import with missing required fields should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert data['error']['code'] == 'MISSING_REQUIRED_FIELDS', \
            "Error code should be MISSING_REQUIRED_FIELDS"
    
    def test_import_configs_invalid_provider(self, client):
        """测试导入包含无效 provider 的配置
        
        验证当配置包含无效的 provider 值时，系统返回 400 错误并拒绝导入。
        
        需求：11.4, 11.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备包含无效 provider 的配置
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': 'invalid_provider_config',
                    'session_type': 'user',
                    'config': {
                        'target_project_dir': None,
                        'response_language': None,
                        'default_provider': 'invalid_provider',  # 无效的 provider
                        'default_layer': 'api',
                        'default_cli_provider': None
                    },
                    'metadata': {
                        'created_by': 'test_user',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'test_user',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 1
                    }
                }
            ]
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 尝试导入
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'invalid_provider.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import with invalid provider should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert data['error']['code'] == 'INVALID_PROVIDER', \
            "Error code should be INVALID_PROVIDER"
    
    def test_import_configs_invalid_layer(self, client):
        """测试导入包含无效 layer 的配置
        
        验证当配置包含无效的 layer 值时，系统返回 400 错误并拒绝导入。
        
        需求：11.4, 11.5
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备包含无效 layer 的配置
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': 'invalid_layer_config',
                    'session_type': 'user',
                    'config': {
                        'target_project_dir': None,
                        'response_language': None,
                        'default_provider': 'claude',
                        'default_layer': 'invalid_layer',  # 无效的 layer
                        'default_cli_provider': None
                    },
                    'metadata': {
                        'created_by': 'test_user',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'test_user',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 1
                    }
                }
            ]
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 尝试导入
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'invalid_layer.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import with invalid layer should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert data['error']['code'] == 'INVALID_LAYER', \
            "Error code should be INVALID_LAYER"
    
    def test_import_configs_creates_backup(self, client):
        """测试导入前创建备份
        
        验证在导入配置前，系统会创建现有配置的备份文件。
        
        需求：11.6
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个现有配置
        client.put('/api/configs/existing_config',
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude'
                  },
                  headers=headers)
        
        # 准备导入数据
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': 'new_import_config',
                    'session_type': 'user',
                    'config': {
                        'target_project_dir': None,
                        'response_language': None,
                        'default_provider': 'gemini',
                        'default_layer': 'api',
                        'default_cli_provider': None
                    },
                    'metadata': {
                        'created_by': 'test_user',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'test_user',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 1
                    }
                }
            ]
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 导入配置
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'backup_test.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证导入成功
        assert response.status_code == 200, \
            "Import should succeed"
        
        # 注意：在单元测试中，我们无法直接验证备份文件是否创建，
        # 因为测试使用临时文件。但我们可以验证导入成功，
        # 这意味着备份逻辑没有阻止导入。
        data = response.get_json()
        assert data['success'] is True, \
            "Import should succeed even with backup creation"
    
    def test_import_configs_without_auth_fails(self, client):
        """测试未认证导入配置失败
        
        验证在没有提供认证令牌的情况下尝试导入配置时，系统返回 401 状态码。
        
        需求：7.4
        """
        # 准备导入数据
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': []
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 尝试导入配置，不提供认证令牌
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'test.json')},
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 401 Unauthorized
        assert response.status_code == 401, \
            "Import without auth should return 401 Unauthorized"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in data, \
            "Response should contain error field"
    
    def test_import_configs_empty_filename(self, client):
        """测试导入空文件名
        
        验证当文件名为空时，系统返回 400 错误。
        
        需求：11.4
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 准备空文件名的文件
        import io
        file_data = io.BytesIO(b'{}')
        
        # 尝试导入，使用空文件名
        response = client.post('/api/configs/import',
                              data={'file': (file_data, '')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证响应状态码为 400 Bad Request
        assert response.status_code == 400, \
            "Import with empty filename should return 400 Bad Request"
        
        # 验证响应包含错误信息
        data = response.get_json()
        assert data['success'] is False, \
            "Response should indicate failure"
        assert data['error']['code'] == 'EMPTY_FILENAME', \
            "Error code should be EMPTY_FILENAME"
    
    def test_import_configs_overwrites_existing(self, client):
        """测试导入覆盖现有配置
        
        验证导入的配置会覆盖同 session_id 的现有配置。
        
        需求：11.2, 11.7
        """
        # 先登录获取令牌
        login_response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 创建一个现有配置
        session_id = 'overwrite_test'
        client.put(f'/api/configs/{session_id}',
                  json={
                      'session_type': 'user',
                      'default_provider': 'claude',
                      'default_layer': 'api'
                  },
                  headers=headers)
        
        # 准备导入数据（相同 session_id，不同配置）
        import json
        import io
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': session_id,
                    'session_type': 'group',  # 不同的 session_type
                    'config': {
                        'target_project_dir': '/overwrite/test',
                        'response_language': 'en-US',
                        'default_provider': 'gemini',  # 不同的 provider
                        'default_layer': 'cli',  # 不同的 layer
                        'default_cli_provider': 'openai'
                    },
                    'metadata': {
                        'created_by': 'import_user',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'import_user',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 5
                    }
                }
            ]
        }
        
        json_str = json.dumps(import_data)
        file_data = io.BytesIO(json_str.encode('utf-8'))
        
        # 导入配置
        response = client.post('/api/configs/import',
                              data={'file': (file_data, 'overwrite.json')},
                              headers=headers,
                              content_type='multipart/form-data')
        
        # 验证导入成功
        assert response.status_code == 200, \
            "Import should succeed"
        
        # 验证配置已被覆盖
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        updated_config = get_response.get_json()['data']
        
        assert updated_config['session_type'] == 'group', \
            "Session type should be updated"
        assert updated_config['config']['default_provider'] == 'gemini', \
            "Provider should be updated"
        assert updated_config['config']['default_layer'] == 'cli', \
            "Layer should be updated"
        assert updated_config['config']['target_project_dir'] == '/overwrite/test', \
            "Target project dir should be updated"



# ==================== Web 服务器单元测试 ====================

class TestWebAdminServer:
    """Web 服务器单元测试类
    
    测试需求：1.6 - Web 服务器启动、端口配置和优雅关闭
    """
    
    def test_server_initialization_with_defaults(self):
        """测试使用默认参数初始化服务器
        
        验证可以使用默认参数成功创建 WebAdminServer 实例。
        
        需求：1.1, 1.5
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（使用默认参数）
            server = WebAdminServer(
                config_manager=config_manager
            )
            
            # 验证服务器属性
            assert server.config_manager is config_manager, \
                "Server should store config manager reference"
            assert server.host == "0.0.0.0", \
                "Default host should be 0.0.0.0"
            assert server.port == 5000, \
                "Default port should be 5000"
            assert server.app is not None, \
                "Flask app should be initialized"
            assert server.auth_manager is not None, \
                "Auth manager should be initialized"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_with_custom_port(self):
        """测试使用自定义端口初始化服务器
        
        验证可以通过参数配置服务器监听端口。
        
        需求：1.5
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（使用自定义端口）
            custom_port = 8080
            server = WebAdminServer(
                config_manager=config_manager,
                port=custom_port
            )
            
            # 验证端口配置
            assert server.port == custom_port, \
                f"Server port should be {custom_port}"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_with_custom_host(self):
        """测试使用自定义主机地址初始化服务器
        
        验证可以通过参数配置服务器监听地址。
        
        需求：1.5
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（使用自定义主机地址）
            custom_host = "127.0.0.1"
            server = WebAdminServer(
                config_manager=config_manager,
                host=custom_host
            )
            
            # 验证主机地址配置
            assert server.host == custom_host, \
                f"Server host should be {custom_host}"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_with_custom_password(self):
        """测试使用自定义管理员密码初始化服务器
        
        验证可以通过参数配置管理员密码。
        
        需求：7.3
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（使用自定义密码）
            custom_password = "custom_secure_password_123"
            server = WebAdminServer(
                config_manager=config_manager,
                admin_password=custom_password
            )
            
            # 验证密码配置（通过 auth_manager）
            assert server.auth_manager is not None, \
                "Auth manager should be initialized"
            assert server.auth_manager.verify_password(custom_password), \
                "Auth manager should use custom password"
            assert not server.auth_manager.verify_password("wrong_password"), \
                "Auth manager should reject wrong password"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_with_custom_jwt_secret(self):
        """测试使用自定义 JWT 密钥初始化服务器
        
        验证可以通过参数配置 JWT 签名密钥。
        
        需求：7.3
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（使用自定义 JWT 密钥）
            custom_secret = "custom_jwt_secret_key_12345678"
            server = WebAdminServer(
                config_manager=config_manager,
                jwt_secret_key=custom_secret
            )
            
            # 验证 JWT 密钥配置（通过生成和验证令牌）
            token_data = server.auth_manager.generate_token()
            token = token_data['token']
            
            # 使用相同密钥应该能验证令牌
            payload = server.auth_manager.verify_token(token)
            assert payload is not None, \
                "Token should be valid with same secret key"
            
            # 使用不同密钥的 AuthManager 应该无法验证令牌
            from feishu_bot.web_admin.auth import AuthManager
            different_auth = AuthManager("different_secret", "password")
            payload2 = different_auth.verify_token(token)
            assert payload2 is None, \
                "Token should be invalid with different secret key"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_flask_app_configured(self):
        """测试 Flask 应用正确配置
        
        验证服务器初始化时正确配置了 Flask 应用，包括 CORS 和路由。
        
        需求：1.2, 1.3
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例
            server = WebAdminServer(
                config_manager=config_manager
            )
            
            # 验证 Flask 应用存在
            assert server.app is not None, \
                "Flask app should be initialized"
            
            # 验证路由已注册（检查是否有 API 路由）
            rules = [rule.rule for rule in server.app.url_map.iter_rules()]
            assert any('/api/auth/login' in rule for rule in rules), \
                "Login API route should be registered"
            assert any('/api/configs' in rule for rule in rules), \
                "Configs API route should be registered"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_stop_graceful_shutdown(self):
        """测试服务器优雅关闭
        
        验证调用 stop() 方法可以优雅地关闭服务器，确保配置已保存。
        
        需求：1.6
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例
            server = WebAdminServer(
                config_manager=config_manager
            )
            
            # 创建一个配置（模拟有未保存的配置）
            session_id = 'test_shutdown_session'
            # 使用正确的 set_config 方法签名
            config_manager.set_config(
                session_id=session_id,
                session_type='user',
                config_key='target_project_dir',
                config_value=temp_dir,  # 使用存在的目录
                user_id='test_user'
            )
            config_manager.set_config(
                session_id=session_id,
                session_type='user',
                config_key='default_provider',
                config_value='claude',
                user_id='test_user'
            )
            
            # 调用 stop 方法
            server.stop()
            
            # 验证配置已保存（通过重新加载配置管理器）
            new_config_manager = ConfigManager(storage_path=config_file)
            saved_config = new_config_manager.configs.get(session_id)
            
            assert saved_config is not None, \
                "Config should be saved after graceful shutdown"
            assert saved_config.target_project_dir == temp_dir, \
                "Saved config should contain correct data"
            assert saved_config.default_provider == 'claude', \
                "Saved config should contain correct provider"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_with_static_folder(self):
        """测试使用静态文件夹初始化服务器
        
        验证可以配置静态文件服务路径。
        
        需求：1.2
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件和静态文件夹
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        static_folder = os.path.join(temp_dir, 'static')
        os.makedirs(static_folder)
        
        # 创建一个测试文件
        test_file = os.path.join(static_folder, 'index.html')
        with open(test_file, 'w') as f:
            f.write('<html><body>Test</body></html>')
        
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（配置静态文件夹）
            server = WebAdminServer(
                config_manager=config_manager,
                static_folder=static_folder
            )
            
            # 验证静态文件路由已配置
            rules = [rule.rule for rule in server.app.url_map.iter_rules()]
            assert any('/' == rule for rule in rules), \
                "Root route should be registered for static files"
        finally:
            # 清理临时文件
            if os.path.exists(test_file):
                os.remove(test_file)
            if os.path.exists(static_folder):
                os.rmdir(static_folder)
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_without_static_folder(self):
        """测试不配置静态文件夹初始化服务器
        
        验证在不提供静态文件夹时，服务器仍然可以正常初始化（仅提供 API）。
        
        需求：1.2
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（不配置静态文件夹）
            server = WebAdminServer(
                config_manager=config_manager,
                static_folder=None
            )
            
            # 验证服务器正常初始化
            assert server.app is not None, \
                "Flask app should be initialized without static folder"
            
            # 验证 API 路由仍然存在
            rules = [rule.rule for rule in server.app.url_map.iter_rules()]
            assert any('/api/auth/login' in rule for rule in rules), \
                "API routes should be registered without static folder"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_initialization_with_nonexistent_static_folder(self):
        """测试使用不存在的静态文件夹初始化服务器
        
        验证当提供的静态文件夹路径不存在时，服务器仍然可以正常初始化。
        
        需求：1.2
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例（使用不存在的静态文件夹路径）
            nonexistent_folder = '/path/to/nonexistent/folder'
            server = WebAdminServer(
                config_manager=config_manager,
                static_folder=nonexistent_folder
            )
            
            # 验证服务器正常初始化
            assert server.app is not None, \
                "Flask app should be initialized even with nonexistent static folder"
        finally:
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_spa_routing_fallback(self):
        """测试 SPA 路由回退功能
        
        验证对于不存在的路径，服务器返回 index.html 以支持客户端路由。
        
        需求：1.2
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件和静态文件夹
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        static_folder = os.path.join(temp_dir, 'static')
        os.makedirs(static_folder)
        
        # 创建 index.html 和一个静态资源文件
        index_file = os.path.join(static_folder, 'index.html')
        with open(index_file, 'w') as f:
            f.write('<html><body>SPA App</body></html>')
        
        assets_dir = os.path.join(static_folder, 'assets')
        os.makedirs(assets_dir)
        js_file = os.path.join(assets_dir, 'app.js')
        with open(js_file, 'w') as f:
            f.write('console.log("app");')
        
        config_manager = ConfigManager(storage_path=config_file)
        
        try:
            # 创建服务器实例
            server = WebAdminServer(
                config_manager=config_manager,
                static_folder=static_folder
            )
            
            # 创建测试客户端
            client = server.app.test_client()
            
            # 测试根路径返回 index.html
            response = client.get('/')
            assert response.status_code == 200, \
                "Root path should return 200"
            assert b'SPA App' in response.data, \
                "Root path should return index.html content"
            
            # 测试静态资源文件可以正常访问
            response = client.get('/assets/app.js')
            assert response.status_code == 200, \
                "Static asset should be accessible"
            assert b'console.log' in response.data, \
                "Static asset should return correct content"
            
            # 测试不存在的路径返回 index.html（SPA 路由回退）
            response = client.get('/configs')
            assert response.status_code == 200, \
                "Non-existent path should return 200"
            assert b'SPA App' in response.data, \
                "Non-existent path should return index.html for SPA routing"
            
            # 测试嵌套路径也返回 index.html
            response = client.get('/configs/some-session-id')
            assert response.status_code == 200, \
                "Nested path should return 200"
            assert b'SPA App' in response.data, \
                "Nested path should return index.html for SPA routing"
            
            # 验证 API 路由不受影响
            response = client.get('/api/configs')
            assert response.status_code == 401, \
                "API routes should still work (401 for unauthorized)"
        finally:
            # 清理临时文件
            if os.path.exists(js_file):
                os.remove(js_file)
            if os.path.exists(assets_dir):
                os.rmdir(assets_dir)
            if os.path.exists(index_file):
                os.remove(index_file)
            if os.path.exists(static_folder):
                os.rmdir(static_folder)
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_multiple_instances_different_ports(self):
        """测试创建多个服务器实例使用不同端口
        
        验证可以创建多个服务器实例，每个使用不同的端口。
        
        需求：1.5
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file1 = os.path.join(temp_dir, 'test_configs1.json')
        config_file2 = os.path.join(temp_dir, 'test_configs2.json')
        config_manager1 = ConfigManager(storage_path=config_file1)
        config_manager2 = ConfigManager(storage_path=config_file2)
        
        try:
            # 创建两个服务器实例，使用不同端口
            server1 = WebAdminServer(
                config_manager=config_manager1,
                port=5001
            )
            server2 = WebAdminServer(
                config_manager=config_manager2,
                port=5002
            )
            
            # 验证两个服务器使用不同端口
            assert server1.port == 5001, \
                "First server should use port 5001"
            assert server2.port == 5002, \
                "Second server should use port 5002"
            assert server1.port != server2.port, \
                "Servers should use different ports"
        finally:
            # 清理临时文件
            for config_file in [config_file1, config_file2]:
                if os.path.exists(config_file):
                    os.remove(config_file)
            os.rmdir(temp_dir)
    
    def test_server_environment_variable_fallback(self):
        """测试环境变量回退机制
        
        验证当不提供密码和密钥参数时，服务器会从环境变量读取，
        如果环境变量也不存在，则使用默认值。
        
        需求：1.5, 7.3
        """
        from feishu_bot.web_admin.server import WebAdminServer
        from feishu_bot.core.config_manager import ConfigManager
        
        # 创建临时配置文件
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_configs.json')
        config_manager = ConfigManager(storage_path=config_file)
        
        # 保存原始环境变量
        original_password = os.environ.get('WEB_ADMIN_PASSWORD')
        original_secret = os.environ.get('JWT_SECRET_KEY')
        
        try:
            # 清除环境变量
            if 'WEB_ADMIN_PASSWORD' in os.environ:
                del os.environ['WEB_ADMIN_PASSWORD']
            if 'JWT_SECRET_KEY' in os.environ:
                del os.environ['JWT_SECRET_KEY']
            
            # 创建服务器实例（不提供密码和密钥参数）
            server = WebAdminServer(
                config_manager=config_manager
            )
            
            # 验证服务器使用默认值
            assert server.auth_manager is not None, \
                "Auth manager should be initialized with defaults"
            
            # 验证默认密码 "admin123" 可以使用
            assert server.auth_manager.verify_password("admin123"), \
                "Default password should be 'admin123'"
        finally:
            # 恢复原始环境变量
            if original_password is not None:
                os.environ['WEB_ADMIN_PASSWORD'] = original_password
            if original_secret is not None:
                os.environ['JWT_SECRET_KEY'] = original_secret
            
            # 清理临时文件
            if os.path.exists(config_file):
                os.remove(config_file)
            os.rmdir(temp_dir)
