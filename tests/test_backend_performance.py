"""
Tests for backend performance optimizations

This module tests the caching, JSON optimization, and compression features.
"""

import pytest
import time
import gzip
from io import BytesIO

from feishu_bot.web_admin.cache import SimpleCache, cached
from feishu_bot.web_admin.json_utils import dumps, loads
from feishu_bot.web_admin.compression import compress_json, decompress_json


class TestSimpleCache:
    """Test SimpleCache functionality"""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = SimpleCache(default_ttl=60)
        
        # Set value
        cache.set('key1', 'value1')
        
        # Get value
        assert cache.get('key1') == 'value1'
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = SimpleCache(default_ttl=60)
        
        # Get non-existent key
        assert cache.get('nonexistent') is None
    
    def test_cache_expiration(self):
        """Test cache entry expiration"""
        cache = SimpleCache(default_ttl=1)
        
        # Set value with 1 second TTL
        cache.set('key1', 'value1', ttl=1)
        
        # Should exist immediately
        assert cache.get('key1') == 'value1'
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get('key1') is None
    
    def test_cache_delete(self):
        """Test cache deletion"""
        cache = SimpleCache(default_ttl=60)
        
        # Set and delete
        cache.set('key1', 'value1')
        cache.delete('key1')
        
        # Should not exist
        assert cache.get('key1') is None
    
    def test_cache_clear(self):
        """Test clearing all cache entries"""
        cache = SimpleCache(default_ttl=60)
        
        # Set multiple values
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        # Clear cache
        cache.clear()
        
        # All should be gone
        assert cache.get('key1') is None
        assert cache.get('key2') is None
    
    def test_cache_invalidate_pattern(self):
        """Test pattern-based cache invalidation"""
        cache = SimpleCache(default_ttl=60)
        
        # Set multiple values
        cache.set('user:123', 'data1')
        cache.set('user:456', 'data2')
        cache.set('config:789', 'data3')
        
        # Invalidate user keys
        count = cache.invalidate_pattern('user:')
        
        # Should invalidate 2 keys
        assert count == 2
        assert cache.get('user:123') is None
        assert cache.get('user:456') is None
        assert cache.get('config:789') == 'data3'
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = SimpleCache(default_ttl=60)
        
        # Set value
        cache.set('key1', 'value1')
        
        # Hit
        cache.get('key1')
        
        # Miss
        cache.get('key2')
        
        # Get stats
        stats = cache.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1
        assert stats['total_requests'] == 2
    
    def test_cached_decorator(self):
        """Test cached decorator"""
        cache = SimpleCache(default_ttl=60)
        call_count = 0
        
        @cached(cache, key_func=lambda x: f"func:{x}", ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
        
        # Different argument - should execute function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2


class TestJSONUtils:
    """Test JSON optimization utilities"""
    
    def test_dumps_and_loads(self):
        """Test JSON serialization and deserialization"""
        data = {
            'key1': 'value1',
            'key2': 123,
            'key3': [1, 2, 3],
            'key4': {'nested': 'value'}
        }
        
        # Serialize
        json_str = dumps(data)
        
        # Deserialize
        result = loads(json_str)
        
        assert result == data
    
    def test_dumps_with_unicode(self):
        """Test JSON serialization with Unicode characters"""
        data = {
            'chinese': '你好世界',
            'emoji': '😀🎉',
            'mixed': 'Hello 世界'
        }
        
        # Serialize
        json_str = dumps(data)
        
        # Deserialize
        result = loads(json_str)
        
        assert result == data
    
    def test_dumps_with_indent(self):
        """Test JSON serialization with indentation"""
        data = {'key': 'value'}
        
        # Serialize with indent
        json_str = dumps(data, indent=2)
        
        # Should contain newlines (pretty printed)
        assert '\n' in json_str or '  ' in json_str


class TestCompression:
    """Test compression utilities"""
    
    def test_compress_and_decompress_json(self):
        """Test JSON compression and decompression"""
        data = {
            'key1': 'value1' * 100,  # Repeat to make it compressible
            'key2': 'value2' * 100,
            'key3': [1, 2, 3] * 50
        }
        
        # Compress
        compressed = compress_json(data)
        
        # Should be bytes
        assert isinstance(compressed, bytes)
        
        # Decompress
        result = decompress_json(compressed)
        
        # Should match original
        assert result == data
    
    def test_compression_reduces_size(self):
        """Test that compression actually reduces size"""
        import json
        
        # Create large repetitive data
        data = {
            'data': 'x' * 1000,
            'list': [{'id': i, 'value': 'test' * 10} for i in range(100)]
        }
        
        # Original size
        original_size = len(json.dumps(data).encode('utf-8'))
        
        # Compressed size
        compressed = compress_json(data)
        compressed_size = len(compressed)
        
        # Compressed should be smaller
        assert compressed_size < original_size
        
        # Calculate compression ratio
        ratio = (1 - compressed_size / original_size) * 100
        print(f"Compression ratio: {ratio:.1f}%")
        
        # Should achieve at least 50% compression on repetitive data
        assert ratio > 50


class TestConfigManagerCaching:
    """Test ConfigManager caching functionality"""
    
    def test_effective_config_caching(self):
        """Test that effective config is cached"""
        from feishu_bot.core.config_manager import ConfigManager
        from feishu_bot.models import SessionConfig
        
        # Create config manager
        config_manager = ConfigManager(storage_path="./data/test_configs.json")
        
        # Create a session config
        session_id = "test_user_123"
        config_manager.configs[session_id] = SessionConfig(
            session_id=session_id,
            session_type="user",
            target_project_dir="/test/path",
            response_language="中文",
            default_provider="claude",
            default_layer="api",
            default_cli_provider=None,
            created_by="test",
            created_at="2024-01-01T00:00:00",
            updated_by="test",
            updated_at="2024-01-01T00:00:00",
            update_count=1
        )
        
        # First call - should compute and cache
        config1 = config_manager.get_effective_config(session_id, "user")
        
        # Second call - should use cache
        config2 = config_manager.get_effective_config(session_id, "user")
        
        # Should return same values
        assert config1 == config2
        assert config1['target_project_dir'] == "/test/path"
        assert config1['response_language'] == "中文"
        
        # Cache should have entry
        cache_key = f"{session_id}:user"
        assert cache_key in config_manager._effective_config_cache
    
    def test_cache_invalidation_on_update(self):
        """Test that cache is invalidated when config is updated"""
        from feishu_bot.core.config_manager import ConfigManager
        
        # Create config manager
        config_manager = ConfigManager(storage_path="./data/test_configs.json")
        
        session_id = "test_user_456"
        
        # Set initial config
        config_manager.set_config(
            session_id=session_id,
            session_type="user",
            config_key="default_provider",
            config_value="claude",
            user_id="test"
        )
        
        # Get effective config (should cache)
        config1 = config_manager.get_effective_config(session_id, "user")
        assert config1['default_provider'] == "claude"
        
        # Update config
        config_manager.set_config(
            session_id=session_id,
            session_type="user",
            config_key="default_provider",
            config_value="gemini",
            user_id="test"
        )
        
        # Get effective config again (should use new value, not cache)
        config2 = config_manager.get_effective_config(session_id, "user")
        assert config2['default_provider'] == "gemini"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
