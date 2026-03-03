"""
Export/Import Property Tests for Web Admin Interface
Property 11, 12, 13 tests for configuration export and import functionality
"""
import pytest
import os
import json
import tempfile
from hypothesis import given, strategies as st, settings
from flask import Flask
from feishu_bot.web_admin.auth import AuthManager
from feishu_bot.web_admin.api_routes import register_api_routes
from feishu_bot.core.config_manager import ConfigManager
from io import BytesIO


# ==================== Helper Functions ====================

def create_test_app(secret_key: str, admin_password: str):
    """Create a test Flask app with authentication
    
    Args:
        secret_key: Secret key for JWT signing
        admin_password: Admin password for login
        
    Returns:
        Tuple of (app, client, auth_manager, config_manager, temp_dir)
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Create temporary config file
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, 'test_configs.json')
    
    # Create managers
    config_manager = ConfigManager(storage_path=config_file)
    auth_manager = AuthManager(secret_key=secret_key, admin_password=admin_password)
    
    # Register routes
    register_api_routes(app, config_manager, auth_manager)
    
    # Create test client
    client = app.test_client()
    
    return app, client, auth_manager, config_manager, temp_dir


def cleanup_test_app(config_manager, temp_dir):
    """Clean up test app resources
    
    Args:
        config_manager: ConfigManager instance
        temp_dir: Temporary directory path
    """
    try:
        # Clean up config file
        if os.path.exists(config_manager.storage_path):
            os.remove(config_manager.storage_path)
        # Remove backup files
        backup_pattern = f"{config_manager.storage_path}.backup_"
        if os.path.exists(os.path.dirname(config_manager.storage_path)):
            for file in os.listdir(os.path.dirname(config_manager.storage_path)):
                if file.startswith(os.path.basename(config_manager.storage_path) + '.backup_'):
                    os.remove(os.path.join(os.path.dirname(config_manager.storage_path), file))
        # Remove temp directory
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    except Exception:
        pass  # Ignore cleanup errors


# ==================== Property 11: 导出导入往返一致性 ====================

# Feature: web-admin-interface, Property 11: 导出导入往返一致性
# **Validates: Requirements 11.1, 11.2, 11.3**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32),
    # Generate a list of configs to export/import
    configs=st.lists(
        st.fixed_dictionaries({
            'session_id': st.text(min_size=1, max_size=50, alphabet=st.characters(
                min_codepoint=ord('a'), max_codepoint=ord('z')
            ) | st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) | st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) | st.just('_') | st.just('-')),
            'session_type': st.sampled_from(['user', 'group']),
            'provider': st.sampled_from(['claude', 'gemini', 'openai']),
            'layer': st.sampled_from(['api', 'cli']),
            'language': st.one_of(st.none(), st.sampled_from(['中文', 'English', '日本語']))
        }),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x['session_id']
    )
)
def test_export_import_roundtrip_consistency(
    secret_key, admin_password, configs
):
    """
    Property 11: 导出导入往返一致性
    
    对于任意配置集合，导出为 JSON 文件后再导入，应该得到相同的配置集合
    （session_id、配置值、元数据都相同）。
    
    **Validates: Requirements 11.1, 11.2, 11.3**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login to get token
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create test configurations
        original_configs = {}
        for config in configs:
            config_data = {
                'session_type': config['session_type'],
                'default_provider': config['provider'],
                'default_layer': config['layer']
            }
            if config['language']:
                config_data['response_language'] = config['language']
            
            response = client.put(
                f'/api/configs/{config["session_id"]}',
                json=config_data,
                headers=headers
            )
            assert response.status_code == 200
            
            # Store original config for comparison
            get_response = client.get(
                f'/api/configs/{config["session_id"]}',
                headers=headers
            )
            assert get_response.status_code == 200
            original_configs[config['session_id']] = get_response.get_json()['data']
        
        # Export configurations
        export_response = client.post('/api/configs/export', headers=headers)
        assert export_response.status_code == 200, \
            "Export should succeed"
        
        # Get exported data
        exported_data = export_response.data
        
        # Clear all configurations
        for session_id in original_configs.keys():
            client.delete(f'/api/configs/{session_id}', headers=headers)
        
        # Verify configs are deleted
        list_response = client.get('/api/configs', headers=headers)
        remaining_configs = [c for c in list_response.get_json()['data'] 
                           if c['session_id'] in original_configs.keys()]
        assert len(remaining_configs) == 0, \
            "All test configs should be deleted before import"
        
        # Import configurations
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(exported_data), 'test_export.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        assert import_response.status_code == 200, \
            f"Import should succeed, got {import_response.status_code}"
        
        import_data = import_response.get_json()
        assert import_data['success'] is True, \
            "Import should be successful"
        assert import_data['data']['imported_count'] == len(configs), \
            f"Should import {len(configs)} configs"
        
        # Verify imported configurations match original
        for session_id, original_config in original_configs.items():
            get_response = client.get(
                f'/api/configs/{session_id}',
                headers=headers
            )
            assert get_response.status_code == 200, \
                f"Config {session_id} should exist after import"
            
            imported_config = get_response.get_json()['data']
            
            # Verify session_id and session_type match
            assert imported_config['session_id'] == original_config['session_id'], \
                "Session ID should match after roundtrip"
            assert imported_config['session_type'] == original_config['session_type'], \
                "Session type should match after roundtrip"
            
            # Verify config values match
            assert imported_config['config']['default_provider'] == \
                   original_config['config']['default_provider'], \
                "Provider should match after roundtrip"
            assert imported_config['config']['default_layer'] == \
                   original_config['config']['default_layer'], \
                "Layer should match after roundtrip"
            assert imported_config['config']['response_language'] == \
                   original_config['config']['response_language'], \
                "Language should match after roundtrip"
            
            # Verify metadata is preserved
            assert imported_config['metadata']['created_by'] == \
                   original_config['metadata']['created_by'], \
                "Created by should match after roundtrip"
            assert imported_config['metadata']['created_at'] == \
                   original_config['metadata']['created_at'], \
                "Created at should match after roundtrip"
            assert imported_config['metadata']['update_count'] == \
                   original_config['metadata']['update_count'], \
                "Update count should match after roundtrip"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)


# Feature: web-admin-interface, Property 11: 导出导入往返一致性
# **Validates: Requirements 11.1, 11.2, 11.3**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32)
)
def test_export_import_empty_configs(secret_key, admin_password):
    """
    Property 11: 导出导入往返一致性 - 空配置集
    
    对于空的配置集合，导出后再导入应该保持为空。
    
    **Validates: Requirements 11.1, 11.2, 11.3**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Export empty configs
        export_response = client.post('/api/configs/export', headers=headers)
        assert export_response.status_code == 200
        
        exported_data = export_response.data
        
        # Import empty configs
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(exported_data), 'empty_export.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        assert import_response.status_code == 200
        
        import_data = import_response.get_json()
        assert import_data['data']['imported_count'] == 0, \
            "Should import 0 configs from empty export"
        
        # Verify no configs exist
        list_response = client.get('/api/configs', headers=headers)
        assert len(list_response.get_json()['data']) == 0, \
            "Should have no configs after importing empty export"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)


# ==================== Property 12: 导入验证拒绝无效格式 ====================

# Feature: web-admin-interface, Property 12: 导入验证拒绝无效格式
# **Validates: Requirements 11.4, 11.5**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32),
    invalid_json=st.text(min_size=1, max_size=100).filter(
        lambda x: not x.strip().startswith('{') and not x.strip().startswith('[')
    )
)
def test_import_rejects_invalid_json_format(
    secret_key, admin_password, invalid_json
):
    """
    Property 12: 导入验证拒绝无效格式 - 无效 JSON
    
    对于任意无效的 JSON 文件（格式错误），导入操作应该失败并返回错误，
    不应该创建任何配置。
    
    **Validates: Requirements 11.4, 11.5**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get initial config count
        list_response = client.get('/api/configs', headers=headers)
        initial_count = len(list_response.get_json()['data'])
        
        # Try to import invalid JSON
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(invalid_json.encode('utf-8')), 'invalid.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Verify import failed
        assert import_response.status_code == 400, \
            "Import should fail with 400 for invalid JSON"
        
        response_data = import_response.get_json()
        assert response_data['success'] is False, \
            "Response should indicate failure"
        assert 'error' in response_data, \
            "Response should contain error field"
        assert 'INVALID_JSON' in response_data['error']['code'] or \
               'INVALID_FORMAT' in response_data['error']['code'], \
            "Error code should indicate JSON format error"
        
        # Verify no configs were created
        list_response = client.get('/api/configs', headers=headers)
        final_count = len(list_response.get_json()['data'])
        assert final_count == initial_count, \
            "No configs should be created from invalid JSON"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)



# Feature: web-admin-interface, Property 12: 导入验证拒绝无效格式
# **Validates: Requirements 11.4, 11.5**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32)
)
def test_import_rejects_missing_configs_field(secret_key, admin_password):
    """
    Property 12: 导入验证拒绝无效格式 - 缺少 configs 字段
    
    对于任意缺少必需字段（configs）的 JSON 文件，导入操作应该失败并返回错误。
    
    **Validates: Requirements 11.4, 11.5**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create JSON without 'configs' field
        invalid_data = json.dumps({
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0'
            # Missing 'configs' field
        })
        
        # Try to import
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(invalid_data.encode('utf-8')), 'missing_configs.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Verify import failed
        assert import_response.status_code == 400, \
            "Import should fail with 400 for missing configs field"
        
        response_data = import_response.get_json()
        assert response_data['success'] is False
        assert 'MISSING_CONFIGS' in response_data['error']['code'], \
            "Error code should indicate missing configs field"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)



# Feature: web-admin-interface, Property 12: 导入验证拒绝无效格式
# **Validates: Requirements 11.4, 11.5**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32),
    session_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        min_codepoint=ord('a'), max_codepoint=ord('z')
    ) | st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) | st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) | st.just('_') | st.just('-'))
)
def test_import_rejects_missing_required_config_fields(
    secret_key, admin_password, session_id
):
    """
    Property 12: 导入验证拒绝无效格式 - 缺少必需配置字段
    
    对于任意缺少必需配置字段的 JSON 文件，导入操作应该失败并返回错误。
    
    **Validates: Requirements 11.4, 11.5**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create JSON with incomplete config (missing required fields)
        invalid_data = json.dumps({
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': session_id,
                    'session_type': 'user'
                    # Missing 'config' and 'metadata' fields
                }
            ]
        })
        
        # Try to import
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(invalid_data.encode('utf-8')), 'incomplete.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Verify import failed
        assert import_response.status_code == 400, \
            "Import should fail with 400 for missing required fields"
        
        response_data = import_response.get_json()
        assert response_data['success'] is False
        assert 'MISSING_REQUIRED_FIELDS' in response_data['error']['code'] or \
               'MISSING_CONFIG_FIELDS' in response_data['error']['code'] or \
               'MISSING_METADATA_FIELDS' in response_data['error']['code'], \
            "Error code should indicate missing required fields"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)


# Feature: web-admin-interface, Property 12: 导入验证拒绝无效格式
# **Validates: Requirements 11.4, 11.5**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32),
    session_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        min_codepoint=ord('a'), max_codepoint=ord('z')
    ) | st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) | st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) | st.just('_') | st.just('-')),
    invalid_provider=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ['claude', 'gemini', 'openai']
    )
)
def test_import_rejects_invalid_provider_values(
    secret_key, admin_password, session_id, invalid_provider
):
    """
    Property 12: 导入验证拒绝无效格式 - 无效 provider 值
    
    对于任意包含无效 provider 值的 JSON 文件，导入操作应该失败并返回错误。
    
    **Validates: Requirements 11.4, 11.5**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create JSON with invalid provider
        invalid_data = json.dumps({
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': session_id,
                    'session_type': 'user',
                    'config': {
                        'target_project_dir': None,
                        'response_language': None,
                        'default_provider': invalid_provider,  # Invalid provider
                        'default_layer': 'api',
                        'default_cli_provider': None
                    },
                    'metadata': {
                        'created_by': 'admin',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'admin',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 0
                    }
                }
            ]
        })
        
        # Try to import
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(invalid_data.encode('utf-8')), 'invalid_provider.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Verify import failed
        assert import_response.status_code == 400, \
            "Import should fail with 400 for invalid provider"
        
        response_data = import_response.get_json()
        assert response_data['success'] is False
        assert 'INVALID_PROVIDER' in response_data['error']['code'], \
            "Error code should indicate invalid provider"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)


# ==================== Property 13: 导入前备份 ====================

# Feature: web-admin-interface, Property 13: 导入前备份
# **Validates: Requirements 11.6**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32),
    # Generate configs to create before import
    existing_configs=st.lists(
        st.fixed_dictionaries({
            'session_id': st.text(min_size=1, max_size=50, alphabet=st.characters(
                min_codepoint=ord('a'), max_codepoint=ord('z')
            ) | st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) | st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) | st.just('_') | st.just('-')),
            'provider': st.sampled_from(['claude', 'gemini', 'openai'])
        }),
        min_size=1,
        max_size=5,
        unique_by=lambda x: x['session_id']
    ),
    # Generate configs to import
    import_configs=st.lists(
        st.fixed_dictionaries({
            'session_id': st.text(min_size=1, max_size=50, alphabet=st.characters(
                min_codepoint=ord('a'), max_codepoint=ord('z')
            ) | st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) | st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) | st.just('_') | st.just('-')),
            'provider': st.sampled_from(['claude', 'gemini', 'openai'])
        }),
        min_size=1,
        max_size=5,
        unique_by=lambda x: x['session_id']
    )
)
def test_import_creates_backup_before_modifying(
    secret_key, admin_password, existing_configs, import_configs
):
    """
    Property 13: 导入前备份
    
    对于任意导入操作，执行前应该创建当前配置的备份文件，
    备份文件应该包含所有现有配置。
    
    **Validates: Requirements 11.6**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create existing configurations
        for config in existing_configs:
            client.put(
                f'/api/configs/{config["session_id"]}',
                json={
                    'session_type': 'user',
                    'default_provider': config['provider']
                },
                headers=headers
            )
        
        # Get list of backup files before import
        storage_dir = os.path.dirname(config_manager.storage_path)
        storage_basename = os.path.basename(config_manager.storage_path)
        
        def get_backup_files():
            if not os.path.exists(storage_dir):
                return []
            return [f for f in os.listdir(storage_dir) 
                   if f.startswith(storage_basename + '.backup_')]
        
        backup_files_before = get_backup_files()
        
        # Create import data
        import_data = {
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': []
        }
        
        for config in import_configs:
            import_data['configs'].append({
                'session_id': config['session_id'],
                'session_type': 'user',
                'config': {
                    'target_project_dir': None,
                    'response_language': None,
                    'default_provider': config['provider'],
                    'default_layer': 'api',
                    'default_cli_provider': None
                },
                'metadata': {
                    'created_by': 'admin',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_by': 'admin',
                    'updated_at': '2024-01-01T00:00:00Z',
                    'update_count': 0
                }
            })
        
        import_json = json.dumps(import_data)
        
        # Perform import
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(import_json.encode('utf-8')), 'import.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        assert import_response.status_code == 200, \
            "Import should succeed"
        
        # Get list of backup files after import
        backup_files_after = get_backup_files()
        
        # Verify a new backup file was created
        new_backup_files = set(backup_files_after) - set(backup_files_before)
        assert len(new_backup_files) >= 1, \
            "At least one backup file should be created before import"
        
        # Verify backup file contains the existing configs
        if new_backup_files:
            newest_backup = sorted(new_backup_files)[-1]
            backup_path = os.path.join(storage_dir, newest_backup)
            
            assert os.path.exists(backup_path), \
                "Backup file should exist"
            
            # Read backup file
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Verify backup contains existing configs
            # Backup file format: {"configs": {session_id: config_dict, ...}}
            if 'configs' in backup_data:
                backup_session_ids = set(backup_data['configs'].keys())
            else:
                # Old format: {session_id: config_dict, ...}
                backup_session_ids = set(backup_data.keys())
            
            existing_session_ids = {c['session_id'] for c in existing_configs}
            
            assert existing_session_ids.issubset(backup_session_ids), \
                "Backup should contain all existing configs"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)


# Feature: web-admin-interface, Property 13: 导入前备份
# **Validates: Requirements 11.6**
@settings(max_examples=100)
@given(
    secret_key=st.text(min_size=16, max_size=64),
    admin_password=st.text(min_size=8, max_size=32),
    session_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        min_codepoint=ord('a'), max_codepoint=ord('z')
    ) | st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) | st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) | st.just('_') | st.just('-'))
)
def test_import_backup_preserves_data_on_failure(
    secret_key, admin_password, session_id
):
    """
    Property 13: 导入前备份 - 失败时数据保护
    
    对于任意导入操作，即使导入失败，原有配置应该保持不变，
    因为备份已经创建。
    
    **Validates: Requirements 11.6**
    """
    app, client, auth_manager, config_manager, temp_dir = create_test_app(
        secret_key, admin_password
    )
    
    try:
        # Login
        login_response = client.post('/api/auth/login', json={
            'password': admin_password
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create existing configuration
        original_provider = 'claude'
        client.put(
            f'/api/configs/{session_id}',
            json={
                'session_type': 'user',
                'default_provider': original_provider
            },
            headers=headers
        )
        
        # Get original config
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        original_config = get_response.get_json()['data']
        
        # Try to import invalid data (should fail)
        invalid_import_data = json.dumps({
            'export_timestamp': '2024-01-01T00:00:00Z',
            'export_version': '1.0',
            'configs': [
                {
                    'session_id': 'test_invalid',
                    'session_type': 'user',
                    'config': {
                        'target_project_dir': None,
                        'response_language': None,
                        'default_provider': 'invalid_provider',  # Invalid
                        'default_layer': 'api',
                        'default_cli_provider': None
                    },
                    'metadata': {
                        'created_by': 'admin',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_by': 'admin',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'update_count': 0
                    }
                }
            ]
        })
        
        # Perform import (should fail)
        import_response = client.post(
            '/api/configs/import',
            data={'file': (BytesIO(invalid_import_data.encode('utf-8')), 'invalid.json')},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        assert import_response.status_code == 400, \
            "Import should fail with invalid data"
        
        # Verify original config is unchanged
        get_response = client.get(f'/api/configs/{session_id}', headers=headers)
        assert get_response.status_code == 200, \
            "Original config should still exist"
        
        current_config = get_response.get_json()['data']
        assert current_config['config']['default_provider'] == original_provider, \
            "Original config should be unchanged after failed import"
        
    finally:
        cleanup_test_app(config_manager, temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
