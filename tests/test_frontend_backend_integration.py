"""
前后端集成测试 - API 契约和错误处理
测试前端和后端之间的 API 契约，确保数据格式一致性和错误处理正确性

验证需求：6.1, 6.2, 6.3, 6.4, 6.5
"""
import pytest
import json
import tempfile
import os
from datetime import datetime
from flask import Flask
from feishu_bot.web_admin.auth import AuthManager
from feishu_bot.web_admin.api_routes import register_api_routes
from feishu_bot.core.config_manager import ConfigManager


# ==================== Fixtures ====================

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
    try:
        if os.path.exists(config_file):
            os.remove(config_file)
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(temp_dir)
    except Exception:
        pass


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


# ==================== API 契约测试 ====================

class TestAPIContract:
    """测试 API 契约 - 确保前后端数据格式一致
    
    验证需求：6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    def test_login_response_contract(self, client):
        """测试登录响应契约
        
        前端期望的响应格式：
        {
            "success": true,
            "data": {
                "token": "string",
                "expires_in": number,
                "expires_at": "ISO8601 string"
            },
            "message": "string"
        }
        
        验证需求：7.1, 7.2
        """
        response = client.post('/api/auth/login', json={
            'password': 'test_admin_password'
        })
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证顶层结构
        assert 'success' in data
        assert 'data' in data
        assert 'message' in data
        
        assert data['success'] is True
        assert isinstance(data['message'], str)
        
        # 验证 data 对象结构
        token_data = data['data']
        assert 'token' in token_data
        assert 'expires_in' in token_data
        assert 'expires_at' in token_data
        
        # 验证数据类型
        assert isinstance(token_data['token'], str)
        assert isinstance(token_data['expires_in'], int)
        assert isinstance(token_data['expires_at'], str)
        
        # 验证令牌不为空
        assert len(token_data['token']) > 0
        
        # 验证过期时间合理（2小时 = 7200秒）
        assert token_data['expires_in'] == 7200
        
        # 验证 expires_at 是有效的 ISO8601 格式
        try:
            datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("expires_at should be valid ISO8601 format")

    
    def test_config_list_response_contract(self, client, auth_token):
        """测试配置列表响应契约
        
        前端期望的响应格式：
        {
            "success": true,
            "data": [
                {
                    "session_id": "string",
                    "session_type": "user" | "group",
                    "config": {...},
                    "metadata": {...}
                }
            ],
            "message": "string"
        }
        
        验证需求：6.1, 2.1, 2.2
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 创建测试配置
        client.put(
            '/api/configs/contract_test_001',
            json={
                'session_type': 'user',
                'default_provider': 'claude',
                'default_layer': 'api'
            },
            headers=headers
        )
        
        # 获取配置列表
        response = client.get('/api/configs', headers=headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证顶层结构
        assert 'success' in data
        assert 'data' in data
        
        assert data['success'] is True
        assert isinstance(data['data'], list)
        
        # 验证配置对象结构
        configs = data['data']
        assert len(configs) > 0
        
        for config in configs:
            # 验证必需字段存在
            assert 'session_id' in config
            assert 'session_type' in config
            assert 'config' in config
            assert 'metadata' in config
            
            # 验证数据类型
            assert isinstance(config['session_id'], str)
            assert isinstance(config['session_type'], str)
            assert isinstance(config['config'], dict)
            assert isinstance(config['metadata'], dict)
            
            # 验证 config 对象包含所有配置字段
            config_obj = config['config']
            assert 'target_project_dir' in config_obj
            assert 'response_language' in config_obj
            assert 'default_provider' in config_obj
            assert 'default_layer' in config_obj
            assert 'default_cli_provider' in config_obj
            
            # 验证 metadata 对象包含所有元数据字段
            metadata = config['metadata']
            assert 'created_by' in metadata
            assert 'created_at' in metadata
            assert 'updated_by' in metadata
            assert 'updated_at' in metadata
            assert 'update_count' in metadata
            
            # 验证元数据类型
            assert isinstance(metadata['update_count'], int)
            assert isinstance(metadata['created_at'], str)
            assert isinstance(metadata['updated_at'], str)
        
        # 清理
        client.delete('/api/configs/contract_test_001', headers=headers)

    
    def test_single_config_response_contract(self, client, auth_token):
        """测试单个配置响应契约
        
        前端期望的响应格式：
        {
            "success": true,
            "data": {
                "session_id": "string",
                "session_type": "user" | "group",
                "config": {...},
                "metadata": {...}
            },
            "message": "string"
        }
        
        验证需求：6.2, 3.1, 3.2, 3.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'contract_test_single'
        
        # 创建测试配置
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'target_project_dir': '/test/project',
                'response_language': 'zh-CN',
                'default_provider': 'claude',
                'default_layer': 'api',
                'default_cli_provider': 'gemini'
            },
            headers=headers
        )
        
        # 获取单个配置
        response = client.get(f'/api/configs/{session_id}', headers=headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证顶层结构
        assert 'success' in data
        assert 'data' in data
        
        assert data['success'] is True
        
        # 验证配置对象
        config = data['data']
        assert config['session_id'] == session_id
        assert config['session_type'] == 'user'
        
        # 验证 config 字段
        config_obj = config['config']
        assert config_obj['target_project_dir'] == '/test/project'
        assert config_obj['response_language'] == 'zh-CN'
        assert config_obj['default_provider'] == 'claude'
        assert config_obj['default_layer'] == 'api'
        assert config_obj['default_cli_provider'] == 'gemini'
        
        # 验证 metadata 字段
        metadata = config['metadata']
        assert 'created_by' in metadata
        assert 'created_at' in metadata
        assert 'updated_by' in metadata
        assert 'updated_at' in metadata
        assert 'update_count' in metadata
        assert metadata['update_count'] >= 1
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)

    
    def test_effective_config_response_contract(self, client, auth_token):
        """测试有效配置响应契约
        
        前端期望的响应格式：
        {
            "success": true,
            "data": {
                "effective_config": {
                    "target_project_dir": "string",
                    "response_language": "string",
                    "default_provider": "string",
                    "default_layer": "string",
                    "default_cli_provider": "string" | null
                }
            },
            "message": "string"
        }
        
        验证需求：6.5, 3.5
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'contract_test_effective'
        
        # 创建测试配置
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'default_provider': 'claude'
            },
            headers=headers
        )
        
        # 获取有效配置
        response = client.get(f'/api/configs/{session_id}/effective', headers=headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证顶层结构
        assert 'success' in data
        assert 'data' in data
        
        assert data['success'] is True
        
        # 验证有效配置对象
        effective_data = data['data']
        assert 'effective_config' in effective_data
        
        effective_config = effective_data['effective_config']
        
        # 验证所有必需字段存在
        assert 'target_project_dir' in effective_config
        assert 'response_language' in effective_config
        assert 'default_provider' in effective_config
        assert 'default_layer' in effective_config
        assert 'default_cli_provider' in effective_config
        
        # 验证会话配置的值被使用
        assert effective_config['default_provider'] == 'claude'
        
        # 验证其他字段存在（可能为 None 或使用全局配置）
        assert 'default_layer' in effective_config
        assert 'response_language' in effective_config
        assert 'target_project_dir' in effective_config
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)

    
    def test_update_config_request_contract(self, client, auth_token):
        """测试更新配置请求契约
        
        前端发送的请求格式：
        {
            "session_type": "user" | "group",
            "target_project_dir": "string" | null,
            "response_language": "string" | null,
            "default_provider": "claude" | "gemini" | "openai",
            "default_layer": "api" | "cli",
            "default_cli_provider": "claude" | "gemini" | "openai" | null
        }
        
        验证需求：6.3, 4.1, 4.7
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'contract_test_update'
        
        # 测试完整的更新请求
        update_data = {
            'session_type': 'user',
            'target_project_dir': '/new/project',
            'response_language': 'en-US',
            'default_provider': 'gemini',
            'default_layer': 'cli',
            'default_cli_provider': 'openai'
        }
        
        response = client.put(
            f'/api/configs/{session_id}',
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        
        # 验证配置已更新
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        config = get_response.get_json()['data']
        
        assert config['config']['target_project_dir'] == '/new/project'
        assert config['config']['response_language'] == 'en-US'
        assert config['config']['default_provider'] == 'gemini'
        assert config['config']['default_layer'] == 'cli'
        assert config['config']['default_cli_provider'] == 'openai'
        
        # 测试部分更新请求
        partial_update = {
            'default_provider': 'claude'
        }
        
        response2 = client.put(
            f'/api/configs/{session_id}',
            json=partial_update,
            headers=headers
        )
        
        assert response2.status_code == 200
        
        # 验证只有指定字段被更新
        get_response2 = client.get(f'/api/configs/{session_id}', headers=headers)
        config2 = get_response2.get_json()['data']
        
        assert config2['config']['default_provider'] == 'claude'
        assert config2['config']['target_project_dir'] == '/new/project'  # 未改变
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)

    
    def test_delete_config_response_contract(self, client, auth_token):
        """测试删除配置响应契约
        
        前端期望的响应格式：
        {
            "success": true,
            "data": null,
            "message": "string"
        }
        
        验证需求：6.4, 5.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'contract_test_delete'
        
        # 创建测试配置
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'default_provider': 'claude'
            },
            headers=headers
        )
        
        # 删除配置
        response = client.delete(f'/api/configs/{session_id}', headers=headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证响应结构
        assert 'success' in data
        assert 'message' in data
        
        assert data['success'] is True
        assert isinstance(data['message'], str)
        
        # 验证配置已删除
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert get_response.status_code == 404


# ==================== 错误处理测试 ====================

class TestErrorHandling:
    """测试错误处理 - 确保前端能正确处理后端错误
    
    验证需求：6.7, 10.1, 10.2, 10.3
    """
    
    def test_authentication_error_format(self, client):
        """测试认证错误格式
        
        前端期望的错误格式：
        {
            "success": false,
            "data": null,
            "message": "string",
            "error": {
                "code": "string",
                "message": "string"
            }
        }
        
        验证需求：7.5, 10.1
        """
        # 测试未认证访问
        response = client.get('/api/configs')
        
        assert response.status_code == 401
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证错误响应结构
        assert 'success' in data
        assert 'error' in data
        
        assert data['success'] is False
        
        # 验证错误对象
        error = data['error']
        assert 'code' in error
        assert 'message' in error
        
        assert isinstance(error['code'], str)
        assert isinstance(error['message'], str)
        assert len(error['message']) > 0

    
    def test_validation_error_format(self, client, auth_token):
        """测试验证错误格式
        
        前端期望能够识别字段级别的验证错误。
        
        验证需求：4.8, 10.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 测试无效的 provider
        response = client.put(
            '/api/configs/error_test',
            json={
                'session_type': 'user',
                'default_provider': 'invalid_provider'
            },
            headers=headers
        )
        
        assert response.status_code == 400
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证错误响应结构
        assert data['success'] is False
        assert 'error' in data
        
        error = data['error']
        assert 'code' in error
        assert 'message' in error
        
        # 验证错误消息提到了问题字段
        error_message = error['message'].lower()
        assert 'provider' in error_message or 'invalid' in error_message
        
        # 如果有 field 字段，验证它指向正确的字段
        if 'field' in error:
            assert error['field'] in ['default_provider', 'provider']
    
    def test_not_found_error_format(self, client, auth_token):
        """测试资源不存在错误格式
        
        验证需求：6.2, 10.1
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 访问不存在的配置
        response = client.get('/api/configs/nonexistent_config', headers=headers)
        
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # 验证错误响应结构
        assert data['success'] is False
        assert 'error' in data
        
        error = data['error']
        assert 'code' in error
        assert 'message' in error
        
        # 验证错误消息是用户友好的
        assert len(error['message']) > 0
        assert 'not found' in error['message'].lower() or '不存在' in error['message']
    
    def test_invalid_json_error_format(self, client, auth_token):
        """测试无效 JSON 错误格式
        
        验证需求：11.5, 10.1
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 创建无效的 JSON 文件
        invalid_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        invalid_file.write("{ invalid json")
        invalid_file.close()
        
        try:
            with open(invalid_file.name, 'rb') as f:
                response = client.post(
                    '/api/configs/import',
                    data={'file': (f, 'invalid.json')},
                    headers=headers,
                    content_type='multipart/form-data'
                )
            
            assert response.status_code == 400
            assert response.content_type == 'application/json'
            
            data = response.get_json()
            
            # 验证错误响应结构
            assert data['success'] is False
            assert 'error' in data
            
            error = data['error']
            assert 'code' in error
            assert 'message' in error
            
            # 验证错误消息提到了 JSON 问题
            error_message = error['message'].lower()
            assert 'json' in error_message or 'format' in error_message or '格式' in error_message
            
        finally:
            os.unlink(invalid_file.name)



# ==================== 数据一致性测试 ====================

class TestDataConsistency:
    """测试前后端数据一致性
    
    验证需求：6.1, 6.2, 6.3, 6.4
    """
    
    def test_null_value_handling(self, client, auth_token):
        """测试 null 值的处理
        
        验证前端发送 null 值和后端返回 null 值的一致性。
        
        验证需求：4.1, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'null_test'
        
        # 创建配置，某些字段为 null
        create_data = {
            'session_type': 'user',
            'target_project_dir': None,
            'response_language': None,
            'default_provider': 'claude',
            'default_layer': 'api',
            'default_cli_provider': None
        }
        
        response = client.put(
            f'/api/configs/{session_id}',
            json=create_data,
            headers=headers
        )
        
        assert response.status_code == 200
        
        # 读取配置并验证 null 值被正确保存
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        config = get_response.get_json()['data']
        
        assert config['config']['target_project_dir'] is None
        assert config['config']['response_language'] is None
        assert config['config']['default_cli_provider'] is None
        
        # 验证非 null 值正确保存
        assert config['config']['default_provider'] == 'claude'
        assert config['config']['default_layer'] == 'api'
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)
    
    def test_timestamp_format_consistency(self, client, auth_token):
        """测试时间戳格式一致性
        
        验证所有时间戳都使用 ISO8601 格式。
        
        验证需求：3.3, 6.2
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'timestamp_test'
        
        # 创建配置
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'default_provider': 'claude'
            },
            headers=headers
        )
        
        # 获取配置
        response = client.get(f'/api/configs/{session_id}', headers=headers)
        config = response.get_json()['data']
        
        metadata = config['metadata']
        
        # 验证时间戳格式
        for timestamp_field in ['created_at', 'updated_at']:
            timestamp = metadata[timestamp_field]
            
            # 验证是字符串
            assert isinstance(timestamp, str)
            
            # 验证可以解析为 datetime
            try:
                # 处理可能的 'Z' 后缀
                if timestamp.endswith('Z'):
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    datetime.fromisoformat(timestamp)
            except ValueError:
                pytest.fail(f"{timestamp_field} should be valid ISO8601 format: {timestamp}")
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)

    
    def test_enum_value_consistency(self, client, auth_token):
        """测试枚举值一致性
        
        验证前后端对枚举值的处理一致。
        
        验证需求：4.4, 4.5, 4.6, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 测试所有有效的 provider 值
        valid_providers = ['claude', 'gemini', 'openai']
        
        for provider in valid_providers:
            session_id = f'enum_test_{provider}'
            
            response = client.put(
                f'/api/configs/{session_id}',
                json={
                    'session_type': 'user',
                    'default_provider': provider
                },
                headers=headers
            )
            
            assert response.status_code == 200, \
                f"Provider '{provider}' should be accepted"
            
            # 验证值被正确保存
            get_response = client.get(f'/api/configs/{session_id}', headers=headers)
            config = get_response.get_json()['data']
            assert config['config']['default_provider'] == provider
            
            # 清理
            client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # 测试所有有效的 layer 值
        valid_layers = ['api', 'cli']
        
        for layer in valid_layers:
            session_id = f'enum_test_layer_{layer}'
            
            response = client.put(
                f'/api/configs/{session_id}',
                json={
                    'session_type': 'user',
                    'default_layer': layer
                },
                headers=headers
            )
            
            assert response.status_code == 200, \
                f"Layer '{layer}' should be accepted"
            
            # 验证值被正确保存
            get_response = client.get(f'/api/configs/{session_id}', headers=headers)
            config = get_response.get_json()['data']
            assert config['config']['default_layer'] == layer
            
            # 清理
            client.delete(f'/api/configs/{session_id}', headers=headers)
    
    def test_list_filtering_consistency(self, client, auth_token):
        """测试列表筛选的一致性
        
        验证前端筛选参数和后端筛选逻辑一致。
        
        验证需求：2.3, 2.4, 6.1
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 创建测试数据
        test_configs = [
            {'session_id': 'filter_user_001', 'session_type': 'user'},
            {'session_id': 'filter_user_002', 'session_type': 'user'},
            {'session_id': 'filter_group_001', 'session_type': 'group'},
        ]
        
        for config in test_configs:
            client.put(
                f'/api/configs/{config["session_id"]}',
                json={
                    'session_type': config['session_type'],
                    'default_provider': 'claude'
                },
                headers=headers
            )
        
        # 测试按 session_type 筛选
        user_response = client.get('/api/configs?session_type=user', headers=headers)
        user_configs = user_response.get_json()['data']
        
        # 验证所有返回的配置都是 user 类型
        for config in user_configs:
            if config['session_id'].startswith('filter_'):
                assert config['session_type'] == 'user'
        
        # 测试按 session_id 搜索
        search_response = client.get('/api/configs?search=filter_user', headers=headers)
        search_results = search_response.get_json()['data']
        
        # 验证搜索结果包含匹配的配置
        search_ids = [c['session_id'] for c in search_results]
        assert 'filter_user_001' in search_ids or 'filter_user_002' in search_ids
        
        # 清理
        for config in test_configs:
            client.delete(f'/api/configs/{config["session_id"]}', headers=headers)


# ==================== 边界情况测试 ====================

class TestEdgeCases:
    """测试边界情况
    
    验证需求：10.1, 10.2, 10.3
    """
    
    def test_empty_string_vs_null(self, client, auth_token):
        """测试空字符串和 null 的区别
        
        验证前端发送空字符串和 null 的处理一致性。
        
        验证需求：4.1, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 测试空字符串
        session_id1 = 'empty_string_test'
        response1 = client.put(
            f'/api/configs/{session_id1}',
            json={
                'session_type': 'user',
                'target_project_dir': '',  # 空字符串
                'default_provider': 'claude'
            },
            headers=headers
        )
        
        # 空字符串应该被接受（或转换为 null）
        assert response1.status_code == 200
        
        get_response1 = client.get(f'/api/configs/{session_id1}', headers=headers)
        config1 = get_response1.get_json()['data']
        
        # 验证空字符串被保存（或转换为 null）
        target_dir = config1['config']['target_project_dir']
        assert target_dir == '' or target_dir is None
        
        # 清理
        client.delete(f'/api/configs/{session_id1}', headers=headers)

    
    def test_unicode_character_handling(self, client, auth_token):
        """测试 Unicode 字符处理
        
        验证前后端正确处理 Unicode 字符（中文、emoji 等）。
        
        验证需求：4.1, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'unicode_test'
        
        # 包含各种 Unicode 字符的配置
        unicode_data = {
            'session_type': 'user',
            'target_project_dir': '/项目/路径/测试',
            'response_language': '中文简体',
            'default_provider': 'claude'
        }
        
        response = client.put(
            f'/api/configs/{session_id}',
            json=unicode_data,
            headers=headers
        )
        
        assert response.status_code == 200
        
        # 验证 Unicode 字符被正确保存和返回
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        config = get_response.get_json()['data']
        
        assert config['config']['target_project_dir'] == '/项目/路径/测试'
        assert config['config']['response_language'] == '中文简体'
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)
    
    def test_very_long_string_handling(self, client, auth_token):
        """测试超长字符串处理
        
        验证系统对超长字符串的处理。
        
        验证需求：4.1, 10.1
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'long_string_test'
        
        # 创建一个很长的路径
        long_path = '/very/long/path/' + 'a' * 500
        
        response = client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'target_project_dir': long_path,
                'default_provider': 'claude'
            },
            headers=headers
        )
        
        # 系统应该接受或拒绝（取决于实现）
        if response.status_code == 200:
            # 如果接受，验证数据被正确保存
            get_response = client.get(f'/api/configs/{session_id}', headers=headers)
            config = get_response.get_json()['data']
            assert config['config']['target_project_dir'] == long_path
            
            # 清理
            client.delete(f'/api/configs/{session_id}', headers=headers)
        else:
            # 如果拒绝，应该返回适当的错误
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data


# ==================== 并发和性能测试 ====================

class TestConcurrencyAndPerformance:
    """测试并发请求和性能相关场景
    
    验证需求：6.1, 6.2, 6.3, 6.4
    """
    
    def test_concurrent_config_updates(self, client, auth_token):
        """测试并发更新同一配置
        
        验证系统能正确处理并发更新请求。
        
        验证需求：6.3, 4.10
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'concurrent_test'
        
        # 创建初始配置
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'default_provider': 'claude',
                'default_layer': 'api'
            },
            headers=headers
        )
        
        # 模拟并发更新（顺序执行，但验证最终一致性）
        response1 = client.put(
            f'/api/configs/{session_id}',
            json={'default_provider': 'gemini'},
            headers=headers
        )
        
        response2 = client.put(
            f'/api/configs/{session_id}',
            json={'default_layer': 'cli'},
            headers=headers
        )
        
        # 两个请求都应该成功
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # 验证最终状态一致
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        config = get_response.get_json()['data']
        
        # 验证 update_count 正确递增
        assert config['metadata']['update_count'] >= 2
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)
    
    def test_multiple_sessions_isolation(self, client, auth_token):
        """测试多个会话配置的隔离性
        
        验证不同会话的配置互不影响。
        
        验证需求：6.1, 6.2, 6.3
        """
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 创建多个不同的配置
        configs = [
            {'session_id': 'isolation_test_1', 'provider': 'claude'},
            {'session_id': 'isolation_test_2', 'provider': 'gemini'},
            {'session_id': 'isolation_test_3', 'provider': 'openai'},
        ]
        
        for config in configs:
            client.put(
                f'/api/configs/{config["session_id"]}',
                json={
                    'session_type': 'user',
                    'default_provider': config['provider']
                },
                headers=headers
            )
        
        # 验证每个配置都保持独立
        for config in configs:
            response = client.get(
                f'/api/configs/{config["session_id"]}',
                headers=headers
            )
            data = response.get_json()['data']
            assert data['config']['default_provider'] == config['provider']
        
        # 更新一个配置不应影响其他配置
        client.put(
            '/api/configs/isolation_test_1',
            json={'default_layer': 'cli'},
            headers=headers
        )
        
        # 验证其他配置未受影响
        response2 = client.get('/api/configs/isolation_test_2', headers=headers)
        config2 = response2.get_json()['data']
        assert 'default_layer' not in config2['config'] or config2['config']['default_layer'] is None
        
        # 清理
        for config in configs:
            client.delete(f'/api/configs/{config["session_id"]}', headers=headers)


# ==================== API 响应时间测试 ====================

class TestAPIResponseTime:
    """测试 API 响应时间
    
    验证需求：6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    def test_config_list_response_time(self, client, auth_token):
        """测试配置列表响应时间
        
        验证 API 响应时间在合理范围内。
        
        验证需求：6.1
        """
        import time
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 创建一些测试配置
        for i in range(10):
            client.put(
                f'/api/configs/perf_test_{i}',
                json={
                    'session_type': 'user',
                    'default_provider': 'claude'
                },
                headers=headers
            )
        
        # 测量响应时间
        start_time = time.time()
        response = client.get('/api/configs', headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 验证响应成功
        assert response.status_code == 200
        
        # 验证响应时间合理（应该在 1 秒内）
        assert response_time < 1.0, f"Response time {response_time}s exceeds 1 second"
        
        # 清理
        for i in range(10):
            client.delete(f'/api/configs/perf_test_{i}', headers=headers)
    
    def test_single_config_response_time(self, client, auth_token):
        """测试单个配置查询响应时间
        
        验证需求：6.2
        """
        import time
        
        headers = {'Authorization': f'Bearer {auth_token}'}
        session_id = 'perf_single_test'
        
        # 创建测试配置
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'default_provider': 'claude'
            },
            headers=headers
        )
        
        # 测量响应时间
        start_time = time.time()
        response = client.get(f'/api/configs/{session_id}', headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 验证响应成功
        assert response.status_code == 200
        
        # 验证响应时间合理（应该在 0.5 秒内）
        assert response_time < 0.5, f"Response time {response_time}s exceeds 0.5 second"
        
        # 清理
        client.delete(f'/api/configs/{session_id}', headers=headers)


# ==================== 完整工作流测试 ====================

class TestCompleteWorkflow:
    """测试完整的用户工作流
    
    验证需求：6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    def test_complete_config_management_workflow(self, client, auth_token):
        """测试完整的配置管理工作流
        
        模拟用户从登录到管理配置的完整流程。
        
        验证需求：7.1, 6.1, 6.2, 6.3, 6.5, 6.4
        """
        # 1. 登录（已通过 auth_token fixture 完成）
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # 2. 查看配置列表（应该为空或包含之前的测试数据）
        list_response = client.get('/api/configs', headers=headers)
        assert list_response.status_code == 200
        initial_count = len(list_response.get_json()['data'])
        
        # 3. 创建新配置
        session_id = 'workflow_test'
        create_response = client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'target_project_dir': '/test/project',
                'response_language': 'zh-CN',
                'default_provider': 'claude',
                'default_layer': 'api'
            },
            headers=headers
        )
        assert create_response.status_code == 200
        
        # 4. 验证配置列表增加了一个
        list_response2 = client.get('/api/configs', headers=headers)
        assert len(list_response2.get_json()['data']) == initial_count + 1
        
        # 5. 查看配置详情
        detail_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert detail_response.status_code == 200
        config = detail_response.get_json()['data']
        assert config['config']['default_provider'] == 'claude'
        
        # 6. 查看有效配置
        effective_response = client.get(
            f'/api/configs/{session_id}/effective',
            headers=headers
        )
        assert effective_response.status_code == 200
        effective_config = effective_response.get_json()['data']['effective_config']
        assert effective_config['default_provider'] == 'claude'
        
        # 7. 更新配置
        update_response = client.put(
            f'/api/configs/{session_id}',
            json={'default_provider': 'gemini'},
            headers=headers
        )
        assert update_response.status_code == 200
        
        # 8. 验证更新生效
        detail_response2 = client.get(f'/api/configs/{session_id}', headers=headers)
        config2 = detail_response2.get_json()['data']
        assert config2['config']['default_provider'] == 'gemini'
        assert config2['metadata']['update_count'] == 2
        
        # 9. 删除配置
        delete_response = client.delete(f'/api/configs/{session_id}', headers=headers)
        assert delete_response.status_code == 200
        
        # 10. 验证配置已删除
        detail_response3 = client.get(f'/api/configs/{session_id}', headers=headers)
        assert detail_response3.status_code == 404
        
        # 11. 验证配置列表恢复原数量
        list_response3 = client.get('/api/configs', headers=headers)
        assert len(list_response3.get_json()['data']) == initial_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
