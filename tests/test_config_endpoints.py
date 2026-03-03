"""
配置查询 API 端点单元测试
测试 GET /api/configs 端点的功能
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


class TestGetConfigsEndpoint:
    """GET /api/configs 端点单元测试类
    
    测试需求：
    - 2.1: Frontend 应显示所有会话配置的列表视图
    - 2.3: Frontend 应支持按 session_type 筛选配置
    - 2.4: Frontend 应支持按 session_id 搜索配置
    - 2.5: Frontend 应支持按更新时间排序配置列表
    - 6.1: Backend API 应提供 GET /api/configs 端点返回所有会话配置列表
    """
    
    def test_get_empty_configs_list(self, client, auth_token):
        """测试空配置列表 - 需求 2.6"""
        response = client.get('/api/configs', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data'] == []
    
    def test_get_configs_list(self, client, auth_token, app):
        """测试获取配置列表 - 需求 2.1, 6.1"""
        _, config_manager = app
        
        # 创建测试配置
        config_manager.configs['user_001'] = SessionConfig(
            session_id='user_001',
            session_type='user',
            target_project_dir='/path/to/project1',
            response_language='中文',
            default_provider='claude',
            default_layer='api',
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T10:00:00',
            updated_by='admin',
            updated_at='2024-01-01T10:00:00',
            update_count=1
        )
        
        config_manager.configs['group_001'] = SessionConfig(
            session_id='group_001',
            session_type='group',
            target_project_dir='/path/to/project2',
            response_language='English',
            default_provider='gemini',
            default_layer='cli',
            default_cli_provider='claude',
            created_by='admin',
            created_at='2024-01-01T11:00:00',
            updated_by='admin',
            updated_at='2024-01-01T11:00:00',
            update_count=2
        )
        
        response = client.get('/api/configs', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        
        # 验证配置结构
        config = data['data'][0]
        assert 'session_id' in config
        assert 'session_type' in config
        assert 'config' in config
        assert 'metadata' in config
    
    def test_filter_by_session_type(self, client, auth_token, app):
        """测试按 session_type 筛选 - 需求 2.3"""
        _, config_manager = app
        
        # 创建不同类型的配置
        config_manager.configs['user_001'] = SessionConfig(
            session_id='user_001',
            session_type='user',
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T10:00:00',
            updated_by='admin',
            updated_at='2024-01-01T10:00:00',
            update_count=1
        )
        
        config_manager.configs['group_001'] = SessionConfig(
            session_id='group_001',
            session_type='group',
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T11:00:00',
            updated_by='admin',
            updated_at='2024-01-01T11:00:00',
            update_count=1
        )
        
        # 筛选用户配置
        response = client.get('/api/configs?session_type=user', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['session_type'] == 'user'
        
        # 筛选群组配置
        response = client.get('/api/configs?session_type=group', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['session_type'] == 'group'
    
    def test_search_by_session_id(self, client, auth_token, app):
        """测试按 session_id 搜索 - 需求 2.4"""
        _, config_manager = app
        
        # 创建测试配置
        config_manager.configs['user_alice'] = SessionConfig(
            session_id='user_alice',
            session_type='user',
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T10:00:00',
            updated_by='admin',
            updated_at='2024-01-01T10:00:00',
            update_count=1
        )
        
        config_manager.configs['user_bob'] = SessionConfig(
            session_id='user_bob',
            session_type='user',
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T11:00:00',
            updated_by='admin',
            updated_at='2024-01-01T11:00:00',
            update_count=1
        )
        
        # 搜索包含 "alice" 的配置
        response = client.get('/api/configs?search=alice', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert 'alice' in data['data'][0]['session_id'].lower()
    
    def test_sort_by_updated_at(self, client, auth_token, app):
        """测试按更新时间排序 - 需求 2.5"""
        _, config_manager = app
        
        # 创建不同更新时间的配置
        config_manager.configs['user_001'] = SessionConfig(
            session_id='user_001',
            session_type='user',
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T10:00:00',
            updated_by='admin',
            updated_at='2024-01-01T10:00:00',
            update_count=1
        )
        
        config_manager.configs['user_002'] = SessionConfig(
            session_id='user_002',
            session_type='user',
            target_project_dir=None,
            response_language=None,
            default_provider=None,
            default_layer=None,
            default_cli_provider=None,
            created_by='admin',
            created_at='2024-01-01T12:00:00',
            updated_by='admin',
            updated_at='2024-01-01T12:00:00',
            update_count=1
        )
        
        # 默认降序排序（最新的在前）
        response = client.get('/api/configs', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        # 验证降序排序
        assert data['data'][0]['metadata']['updated_at'] >= data['data'][1]['metadata']['updated_at']
        
        # 升序排序
        response = client.get('/api/configs?order=asc', headers={
            'Authorization': f'Bearer {auth_token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # 验证升序排序
        assert data['data'][0]['metadata']['updated_at'] <= data['data'][1]['metadata']['updated_at']
    
    def test_unauthorized_access(self, client):
        """测试未授权访问 - 需求 7.4"""
        response = client.get('/api/configs')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False