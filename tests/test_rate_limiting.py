"""
Tests for Rate Limiting

This module tests the rate limiting functionality of the web admin interface.
"""

import pytest
import time
from feishu_bot.core.config_manager import ConfigManager
from feishu_bot.web_admin.server import WebAdminServer


@pytest.fixture
def test_server():
    """Create a test server with rate limiting enabled"""
    config_manager = ConfigManager()
    server = WebAdminServer(
        config_manager=config_manager,
        host="127.0.0.1",
        port=5001,
        admin_password="test_password",
        jwt_secret_key="test_secret",
        enable_rate_limiting=True
    )
    return server


@pytest.fixture
def test_client(test_server):
    """Create a test client"""
    test_server.app.config['TESTING'] = True
    with test_server.app.test_client() as client:
        yield client


def test_login_rate_limit(test_client):
    """Test that login endpoint has rate limiting (5 per minute)"""
    # Make 5 login attempts (should all succeed or fail based on password)
    for i in range(5):
        response = test_client.post('/api/auth/login', json={'password': 'wrong'})
        # Should get 401 (wrong password) not 429 (rate limited)
        assert response.status_code == 401
    
    # 6th attempt should be rate limited
    response = test_client.post('/api/auth/login', json={'password': 'wrong'})
    assert response.status_code == 429
    
    data = response.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'RATE_LIMIT_EXCEEDED'


def test_api_rate_limit(test_client):
    """Test that API endpoints have rate limiting (60 per minute)"""
    # First login to get a token
    response = test_client.post('/api/auth/login', json={'password': 'test_password'})
    assert response.status_code == 200
    token = response.get_json()['data']['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Make 60 API requests (should all succeed)
    for i in range(60):
        response = test_client.get('/api/configs', headers=headers)
        assert response.status_code == 200
    
    # 61st request should be rate limited
    response = test_client.get('/api/configs', headers=headers)
    assert response.status_code == 429
    
    data = response.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'RATE_LIMIT_EXCEEDED'


def test_export_import_rate_limit(test_client):
    """Test that export/import endpoints have rate limiting (10 per minute)"""
    # First login to get a token
    response = test_client.post('/api/auth/login', json={'password': 'test_password'})
    assert response.status_code == 200
    token = response.get_json()['data']['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Make 10 export requests (should all succeed)
    for i in range(10):
        response = test_client.post('/api/configs/export', headers=headers)
        assert response.status_code == 200
    
    # 11th request should be rate limited
    response = test_client.post('/api/configs/export', headers=headers)
    assert response.status_code == 429
    
    data = response.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'RATE_LIMIT_EXCEEDED'


def test_rate_limiting_disabled():
    """Test that rate limiting can be disabled"""
    config_manager = ConfigManager()
    server = WebAdminServer(
        config_manager=config_manager,
        host="127.0.0.1",
        port=5002,
        admin_password="test_password",
        jwt_secret_key="test_secret",
        enable_rate_limiting=False
    )
    
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        # Make many login attempts (should not be rate limited)
        for i in range(10):
            response = client.post('/api/auth/login', json={'password': 'wrong'})
            # Should get 401 (wrong password) not 429 (rate limited)
            assert response.status_code == 401


def test_rate_limit_headers(test_client):
    """Test that rate limit headers are included in responses"""
    response = test_client.post('/api/auth/login', json={'password': 'test_password'})
    
    # Check for rate limit headers
    assert 'X-RateLimit-Limit' in response.headers
    assert 'X-RateLimit-Remaining' in response.headers
    assert 'X-RateLimit-Reset' in response.headers
    
    # Verify header values
    limit = int(response.headers['X-RateLimit-Limit'])
    remaining = int(response.headers['X-RateLimit-Remaining'])
    
    assert limit == 5  # Login limit is 5 per minute
    assert remaining < limit  # Should have used one attempt


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
