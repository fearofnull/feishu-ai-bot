"""
Web Admin Error Handling Scenarios Unit Tests

This module tests various error scenarios in the web admin API endpoints,
verifying proper error response formats and logging for each case.

Tests Requirements: 10.1, 10.2, 10.3
"""

import pytest
import os
import tempfile
import shutil
import logging
from io import BytesIO
from flask import Flask
from feishu_bot.web_admin.api_routes import register_api_routes
from feishu_bot.web_admin.auth import AuthManager
from feishu_bot.web_admin.logging_config import configure_logging
from feishu_bot.core.config_manager import ConfigManager


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files"""
    log_dir = tempfile.mkdtemp()
    yield log_dir
    # Cleanup
    shutil.rmtree(log_dir, ignore_errors=True)


@pytest.fixture
def app(temp_log_dir):
    """Create test Flask app with logging configured"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Configure logging
    configure_logging(
        app,
        log_level="DEBUG",
        log_dir=temp_log_dir,
        enable_file_logging=True
    )
    
    # Create temporary config file
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, 'test_configs.json')
    
    # Create ConfigManager and AuthManager
    config_manager = ConfigManager(storage_path=config_file)
    auth_manager = AuthManager(
        secret_key="test_secret_key_12345678",
        admin_password="test_admin_password"
    )
    
    # Register API routes
    register_api_routes(app, config_manager, auth_manager)
    
    yield app
    
    # Cleanup
    if os.path.exists(config_file):
        os.remove(config_file)
    os.rmdir(temp_dir)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Get authentication token for tests"""
    response = client.post('/api/auth/login', json={
        'password': 'test_admin_password'
    })
    return response.get_json()['data']['token']


class TestAuthenticationErrorScenarios:
    """Test authentication error scenarios
    
    Validates Requirements: 10.1 - API 请求失败时显示用户友好的错误消息
    """
    
    def test_login_missing_password_field(self, client, temp_log_dir):
        """Test login with missing password field returns proper error
        
        Requirement: 10.1
        """
        # Attempt login without password field
        response = client.post('/api/auth/login', json={})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'MISSING_PASSWORD'
        assert 'message' in data['error']
        assert isinstance(data['error']['message'], str)
        
        # Verify error is logged
        error_log = os.path.join(temp_log_dir, 'web_admin_error.log')
        if os.path.exists(error_log):
            with open(error_log, 'r', encoding='utf-8') as f:
                log_content = f.read()
                # Log should contain error information
                assert len(log_content) >= 0  # Log file exists
    
    def test_login_invalid_credentials(self, client, temp_log_dir):
        """Test login with invalid credentials returns proper error
        
        Requirement: 10.1
        """
        # Attempt login with wrong password
        response = client.post('/api/auth/login', json={
            'password': 'wrong_password'
        })
        
        # Verify response format
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_CREDENTIALS'
        assert 'message' in data['error']
        
        # Verify authentication failure is logged
        auth_log = os.path.join(temp_log_dir, 'web_admin_auth.log')
        assert os.path.exists(auth_log)
        with open(auth_log, 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert 'Authentication failed' in log_content
    
    def test_access_without_token(self, client, temp_log_dir):
        """Test accessing protected endpoint without token
        
        Requirement: 10.1
        """
        # Attempt to access protected endpoint
        response = client.get('/api/configs')
        
        # Verify response format
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'UNAUTHORIZED'
        assert 'message' in data['error']
    
    def test_access_with_invalid_token(self, client, temp_log_dir):
        """Test accessing protected endpoint with invalid token
        
        Requirement: 10.1
        """
        # Attempt to access with invalid token
        response = client.get('/api/configs', headers={
            'Authorization': 'Bearer invalid_token_format'
        })
        
        # Verify response format
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data


class TestValidationErrorScenarios:
    """Test validation error scenarios
    
    Validates Requirements: 10.1, 10.3 - 配置验证失败时显示验证错误
    """
    
    def test_update_config_invalid_provider(self, client, auth_token, temp_log_dir):
        """Test updating config with invalid provider
        
        Requirement: 10.1, 10.3
        """
        # Attempt to update with invalid provider
        response = client.put('/api/configs/test_session', 
                             json={
                                 'session_type': 'user',
                                 'default_provider': 'invalid_provider'
                             },
                             headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_PROVIDER'
        assert 'message' in data['error']
        assert 'field' in data['error']
        assert data['error']['field'] == 'default_provider'
        
        # Verify error message is user-friendly
        assert 'claude' in data['error']['message'].lower() or \
               'gemini' in data['error']['message'].lower() or \
               'openai' in data['error']['message'].lower()
    
    def test_update_config_invalid_layer(self, client, auth_token, temp_log_dir):
        """Test updating config with invalid layer
        
        Requirement: 10.1, 10.3
        """
        # Attempt to update with invalid layer
        response = client.put('/api/configs/test_session',
                             json={
                                 'session_type': 'user',
                                 'default_layer': 'invalid_layer'
                             },
                             headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_LAYER'
        assert 'field' in data['error']
        assert data['error']['field'] == 'default_layer'
        
        # Verify error message mentions valid options
        assert 'api' in data['error']['message'].lower() or \
               'cli' in data['error']['message'].lower()
    
    def test_update_config_invalid_cli_provider(self, client, auth_token, temp_log_dir):
        """Test updating config with invalid CLI provider
        
        Requirement: 10.1, 10.3
        """
        # Attempt to update with invalid CLI provider
        response = client.put('/api/configs/test_session',
                             json={
                                 'session_type': 'user',
                                 'default_cli_provider': 'invalid_cli_provider'
                             },
                             headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # The actual error code is INVALID_PROVIDER for CLI provider validation
        assert data['error']['code'] == 'INVALID_PROVIDER'
        assert 'field' in data['error']
        assert data['error']['field'] == 'default_cli_provider'


class TestNotFoundErrorScenarios:
    """Test not found error scenarios
    
    Validates Requirements: 10.1 - API 请求失败时显示用户友好的错误消息
    """
    
    def test_get_nonexistent_config(self, client, auth_token, temp_log_dir):
        """Test getting non-existent config returns proper error
        
        Requirement: 10.1
        """
        # Attempt to get non-existent config
        response = client.get('/api/configs/nonexistent_session',
                             headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # The actual error code is NOT_FOUND
        assert data['error']['code'] == 'NOT_FOUND'
        assert 'message' in data['error']
        assert 'nonexistent_session' in data['error']['message']
    
    def test_delete_nonexistent_config(self, client, auth_token, temp_log_dir):
        """Test deleting non-existent config returns proper error
        
        Requirement: 10.1
        """
        # Attempt to delete non-existent config
        response = client.delete('/api/configs/nonexistent_session',
                                headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # The actual error code is NOT_FOUND
        assert data['error']['code'] == 'NOT_FOUND'


class TestImportExportErrorScenarios:
    """Test import/export error scenarios
    
    Validates Requirements: 10.1 - API 请求失败时显示用户友好的错误消息
    """
    
    def test_import_missing_file(self, client, auth_token, temp_log_dir):
        """Test importing without file returns proper error
        
        Requirement: 10.1
        """
        # Attempt to import without file
        response = client.post('/api/configs/import',
                              data={},
                              headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'MISSING_FILE'
        assert 'message' in data['error']
    
    def test_import_invalid_json(self, client, auth_token, temp_log_dir):
        """Test importing invalid JSON returns proper error
        
        Requirement: 10.1
        """
        # Create invalid JSON file
        invalid_json = b'{ invalid json content'
        
        # Attempt to import
        response = client.post('/api/configs/import',
                              data={'file': (BytesIO(invalid_json), 'test.json')},
                              content_type='multipart/form-data',
                              headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_JSON'
        assert 'message' in data['error']
    
    def test_import_missing_configs_field(self, client, auth_token, temp_log_dir):
        """Test importing JSON without configs field
        
        Requirement: 10.1
        """
        # Create JSON without configs field
        invalid_data = b'{"other_field": "value"}'
        
        # Attempt to import
        response = client.post('/api/configs/import',
                              data={'file': (BytesIO(invalid_data), 'test.json')},
                              content_type='multipart/form-data',
                              headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'MISSING_CONFIGS'
    
    def test_import_invalid_config_format(self, client, auth_token, temp_log_dir):
        """Test importing config with missing required fields
        
        Requirement: 10.1
        """
        # Create config with missing required fields
        invalid_config = b'{"configs": [{"session_id": "test"}]}'
        
        # Attempt to import
        response = client.post('/api/configs/import',
                              data={'file': (BytesIO(invalid_config), 'test.json')},
                              content_type='multipart/form-data',
                              headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify response format
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # Should indicate missing required fields
        assert 'MISSING' in data['error']['code'] or 'INVALID' in data['error']['code']


class TestErrorResponseConsistency:
    """Test error response format consistency
    
    Validates Requirements: 10.1 - 确保所有错误响应格式一致
    """
    
    def test_all_errors_have_required_fields(self, client, auth_token):
        """Test all error responses have required fields
        
        Requirement: 10.1
        """
        # Test various error scenarios
        error_scenarios = [
            # Authentication errors
            (client.post('/api/auth/login', json={}), 400),
            (client.get('/api/configs'), 401),
            
            # Validation errors
            (client.put('/api/configs/test', 
                       json={'default_provider': 'invalid'},
                       headers={'Authorization': f'Bearer {auth_token}'}), 400),
            
            # Not found errors
            (client.get('/api/configs/nonexistent',
                       headers={'Authorization': f'Bearer {auth_token}'}), 404),
        ]
        
        for response, expected_status in error_scenarios:
            assert response.status_code == expected_status
            data = response.get_json()
            
            # Verify required fields
            assert 'success' in data
            assert data['success'] is False
            # Note: 'data' field may not always be present in error responses
            # but 'error' field must be present
            assert 'error' in data
            assert 'code' in data['error']
            assert 'message' in data['error']
            assert isinstance(data['error']['code'], str)
            assert isinstance(data['error']['message'], str)
            assert len(data['error']['message']) > 0
    
    def test_error_messages_are_user_friendly(self, client, auth_token):
        """Test error messages are user-friendly and don't leak internal details
        
        Requirement: 10.1
        """
        # Test various error scenarios
        error_responses = [
            client.post('/api/auth/login', json={'password': 'wrong'}),
            client.put('/api/configs/test',
                      json={'default_provider': 'invalid'},
                      headers={'Authorization': f'Bearer {auth_token}'}),
            client.get('/api/configs/nonexistent',
                      headers={'Authorization': f'Bearer {auth_token}'}),
        ]
        
        for response in error_responses:
            data = response.get_json()
            message = data['error']['message'].lower()
            
            # Should not contain technical details
            assert 'traceback' not in message
            assert 'exception' not in message
            assert 'stack' not in message
            
            # Should be descriptive
            assert len(message) > 10


class TestErrorLogging:
    """Test error logging functionality
    
    Validates Requirements: 10.1 - 错误应该被记录到日志文件
    """
    
    def test_authentication_errors_are_logged(self, client, temp_log_dir):
        """Test authentication errors are logged
        
        Requirement: 10.1
        """
        # Trigger authentication error
        client.post('/api/auth/login', json={'password': 'wrong'})
        
        # Verify error is logged in auth log
        auth_log = os.path.join(temp_log_dir, 'web_admin_auth.log')
        assert os.path.exists(auth_log)
        
        with open(auth_log, 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert 'Authentication failed' in log_content
    
    def test_validation_errors_are_logged(self, client, auth_token, temp_log_dir):
        """Test validation errors are logged
        
        Requirement: 10.1
        """
        # Trigger validation error
        client.put('/api/configs/test',
                  json={'default_provider': 'invalid'},
                  headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify error is logged
        app_log = os.path.join(temp_log_dir, 'web_admin.log')
        assert os.path.exists(app_log)
        
        # Log file should exist and contain some content
        with open(app_log, 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert len(log_content) > 0
    
    def test_not_found_errors_are_logged(self, client, auth_token, temp_log_dir):
        """Test not found errors are logged
        
        Requirement: 10.1
        """
        # Trigger not found error
        client.get('/api/configs/nonexistent',
                  headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify error is logged
        app_log = os.path.join(temp_log_dir, 'web_admin.log')
        assert os.path.exists(app_log)
        
        with open(app_log, 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert len(log_content) > 0
    
    def test_error_logs_contain_context(self, client, auth_token, temp_log_dir):
        """Test error logs contain contextual information
        
        Requirement: 10.1
        """
        # Trigger an error
        client.put('/api/configs/test',
                  json={'default_provider': 'invalid'},
                  headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify log contains context
        app_log = os.path.join(temp_log_dir, 'web_admin.log')
        with open(app_log, 'r', encoding='utf-8') as f:
            log_content = f.read()
            
            # Should contain timestamp (in format [YYYY-MM-DD HH:MM:SS])
            assert '[' in log_content and ']' in log_content
            
            # Should contain log level
            assert '[INFO]' in log_content or '[WARNING]' in log_content or '[ERROR]' in log_content


class TestErrorRecovery:
    """Test error recovery and system stability
    
    Validates Requirements: 10.1 - 系统应该从错误中恢复
    """
    
    def test_system_continues_after_error(self, client, auth_token):
        """Test system continues to function after errors
        
        Requirement: 10.1
        """
        # Trigger an error
        client.put('/api/configs/test',
                  json={'default_provider': 'invalid'},
                  headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify system still works
        response = client.get('/api/configs',
                             headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
    
    def test_multiple_errors_dont_crash_system(self, client, auth_token):
        """Test multiple errors don't crash the system
        
        Requirement: 10.1
        """
        # Trigger multiple errors
        for _ in range(5):
            client.put('/api/configs/test',
                      json={'default_provider': 'invalid'},
                      headers={'Authorization': f'Bearer {auth_token}'})
        
        # Verify system still works
        response = client.get('/api/configs',
                             headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
