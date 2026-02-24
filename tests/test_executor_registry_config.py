"""
执行器注册表配置加载测试
"""
import pytest
import json
import tempfile
import os
from feishu_bot.executor_registry import ExecutorRegistry
from feishu_bot.models import ExecutorMetadata


def test_load_from_config_file():
    """测试从配置文件加载执行器元数据"""
    # 创建临时配置文件
    config_data = {
        "executors": [
            {
                "provider": "claude",
                "layer": "api",
                "name": "Claude API",
                "version": "1.0.0",
                "description": "Claude API executor",
                "capabilities": ["chat", "code"],
                "command_prefixes": ["@claude", "@claude-api"],
                "priority": 1,
                "config_required": ["api_key"]
            },
            {
                "provider": "gemini",
                "layer": "cli",
                "name": "Gemini CLI",
                "version": "1.0.0",
                "description": "Gemini CLI executor",
                "capabilities": ["code_analysis"],
                "command_prefixes": ["@gemini-cli"],
                "priority": 2,
                "config_required": ["target_directory"]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        # 创建注册表并加载配置
        registry = ExecutorRegistry(config_path=config_path)
        
        # 验证 Claude API 元数据
        claude_metadata = registry.get_executor_metadata("claude", "api")
        assert claude_metadata is not None
        assert claude_metadata.name == "Claude API"
        assert claude_metadata.provider == "claude"
        assert claude_metadata.layer == "api"
        assert claude_metadata.version == "1.0.0"
        assert "chat" in claude_metadata.capabilities
        assert "@claude" in claude_metadata.command_prefixes
        assert claude_metadata.priority == 1
        assert "api_key" in claude_metadata.config_required
        
        # 验证 Gemini CLI 元数据
        gemini_metadata = registry.get_executor_metadata("gemini", "cli")
        assert gemini_metadata is not None
        assert gemini_metadata.name == "Gemini CLI"
        assert gemini_metadata.provider == "gemini"
        assert gemini_metadata.layer == "cli"
        
    finally:
        # 清理临时文件
        os.unlink(config_path)


def test_load_from_nonexistent_config():
    """测试加载不存在的配置文件"""
    # 不应该抛出异常，只是不加载配置
    registry = ExecutorRegistry(config_path="/nonexistent/path/config.json")
    
    # 注册表应该是空的
    assert len(registry.executor_metadata) == 0


def test_load_from_invalid_config():
    """测试加载无效的配置文件"""
    # 创建无效的配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write("invalid json content {")
        config_path = f.name
    
    try:
        # 不应该抛出异常，只是记录错误
        registry = ExecutorRegistry(config_path=config_path)
        
        # 注册表应该是空的
        assert len(registry.executor_metadata) == 0
        
    finally:
        os.unlink(config_path)


def test_load_config_with_missing_fields():
    """测试加载缺少必需字段的配置"""
    config_data = {
        "executors": [
            {
                "provider": "claude",
                # 缺少 layer 字段
                "name": "Claude API"
            },
            {
                # 缺少 provider 字段
                "layer": "api",
                "name": "Unknown API"
            },
            {
                "provider": "gemini",
                "layer": "api",
                "name": "Gemini API"
                # 其他字段使用默认值
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        registry = ExecutorRegistry(config_path=config_path)
        
        # 只有 gemini 应该被加载（有 provider 和 layer）
        assert registry.get_executor_metadata("claude", "api") is None
        
        gemini_metadata = registry.get_executor_metadata("gemini", "api")
        assert gemini_metadata is not None
        assert gemini_metadata.name == "Gemini API"
        # 验证默认值
        assert gemini_metadata.version == "1.0.0"
        assert gemini_metadata.description == ""
        assert gemini_metadata.capabilities == []
        assert gemini_metadata.priority == 10
        
    finally:
        os.unlink(config_path)
