"""
配置管理器测试
"""
import os
import json
import tempfile
import pytest
from pathlib import Path

from feishu_bot.core.config_manager import ConfigManager
from feishu_bot.models import SessionConfig
from feishu_bot.config import BotConfig


class TestConfigManager:
    """配置管理器测试类"""
    
    @pytest.fixture
    def temp_storage(self):
        """创建临时存储文件"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        lock_path = f"{temp_path}.lock"
        if os.path.exists(lock_path):
            os.unlink(lock_path)
    
    @pytest.fixture
    def global_config(self):
        """创建全局配置"""
        return BotConfig(
            app_id="test_app_id",
            app_secret="test_app_secret",
            target_directory="/default/project",
            default_provider="claude",
            default_layer="api",
            response_language="zh-CN"
        )
    
    @pytest.fixture
    def config_manager(self, temp_storage, global_config):
        """创建配置管理器实例"""
        return ConfigManager(
            storage_path=temp_storage,
            global_config=global_config
        )
    
    def test_get_effective_config_defaults(self, config_manager):
        """测试获取默认配置"""
        effective = config_manager.get_effective_config("user123", "user")
        
        assert effective["target_project_dir"] == "/default/project"
        assert effective["response_language"] == "zh-CN"
        assert effective["default_provider"] == "claude"
        assert effective["default_layer"] == "api"
    
    def test_set_config(self, config_manager):
        """测试设置配置"""
        success, msg = config_manager.set_config(
            session_id="user123",
            session_type="user",
            config_key="target_project_dir",
            config_value="/new/project",
            user_id="user123"
        )
        
        assert success
        assert "✅" in msg
        
        # 验证配置已保存
        effective = config_manager.get_effective_config("user123", "user")
        assert effective["target_project_dir"] == "/new/project"
    
    def test_set_language_config(self, config_manager):
        """测试设置语言配置"""
        success, msg = config_manager.set_config(
            session_id="user123",
            session_type="user",
            config_key="response_language",
            config_value="en-US",
            user_id="user123"
        )
        
        assert success
        
        effective = config_manager.get_effective_config("user123", "user")
        assert effective["response_language"] == "en-US"
    
    def test_set_provider_config(self, config_manager):
        """测试设置提供商配置"""
        success, msg = config_manager.set_config(
            session_id="user123",
            session_type="user",
            config_key="default_provider",
            config_value="gemini",
            user_id="user123"
        )
        
        assert success
        
        effective = config_manager.get_effective_config("user123", "user")
        assert effective["default_provider"] == "gemini"
    
    def test_invalid_provider(self, config_manager):
        """测试无效的提供商"""
        success, msg = config_manager.set_config(
            session_id="user123",
            session_type="user",
            config_key="default_provider",
            config_value="invalid",
            user_id="user123"
        )
        
        assert not success
        assert "❌" in msg
        assert "Invalid provider" in msg or "无效的提供商" in msg
    
    def test_invalid_layer(self, config_manager):
        """测试无效的执行层"""
        success, msg = config_manager.set_config(
            session_id="user123",
            session_type="user",
            config_key="default_layer",
            config_value="invalid",
            user_id="user123"
        )
        
        assert not success
        assert "❌" in msg
    
    def test_temp_params_override(self, config_manager):
        """测试临时参数覆盖"""
        # 设置会话配置
        config_manager.set_config(
            session_id="user123",
            session_type="user",
            config_key="target_project_dir",
            config_value="/session/project",
            user_id="user123"
        )
        
        # 使用临时参数覆盖
        temp_params = {"dir": "/temp/project"}
        effective = config_manager.get_effective_config(
            "user123", "user", temp_params
        )
        
        assert effective["target_project_dir"] == "/temp/project"
        
        # 验证会话配置未被修改
        effective_no_temp = config_manager.get_effective_config("user123", "user")
        assert effective_no_temp["target_project_dir"] == "/session/project"
    
    def test_config_priority(self, config_manager):
        """测试配置优先级"""
        # 全局配置: /default/project (来自 global_config)
        # 会话配置: /session/project
        # 临时参数: /temp/project
        
        # 1. 只有全局配置
        effective = config_manager.get_effective_config("user123", "user")
        assert effective["target_project_dir"] == "/default/project"
        
        # 2. 会话配置覆盖全局配置
        config_manager.set_config(
            "user123", "user", "target_project_dir", "/session/project", "user123"
        )
        effective = config_manager.get_effective_config("user123", "user")
        assert effective["target_project_dir"] == "/session/project"
        
        # 3. 临时参数覆盖会话配置
        temp_params = {"dir": "/temp/project"}
        effective = config_manager.get_effective_config(
            "user123", "user", temp_params
        )
        assert effective["target_project_dir"] == "/temp/project"
    
    def test_reset_config(self, config_manager):
        """测试重置配置"""
        # 设置配置
        config_manager.set_config(
            "user123", "user", "target_project_dir", "/new/project", "user123"
        )
        
        # 重置配置
        success, msg = config_manager.reset_config("user123")
        assert success
        
        # 验证配置已重置
        effective = config_manager.get_effective_config("user123", "user")
        assert effective["target_project_dir"] == "/default/project"
    
    def test_group_config(self, config_manager):
        """测试群组配置"""
        # 用户A设置群组配置
        config_manager.set_config(
            session_id="chat123",
            session_type="group",
            config_key="target_project_dir",
            config_value="/group/project",
            user_id="userA"
        )
        
        # 验证配置已保存
        effective = config_manager.get_effective_config("chat123", "group")
        assert effective["target_project_dir"] == "/group/project"
        
        # 验证元数据
        config = config_manager.configs["chat123"]
        assert config.created_by == "userA"
        assert config.session_type == "group"
    
    def test_config_persistence(self, config_manager, temp_storage):
        """测试配置持久化"""
        # 设置配置
        config_manager.set_config(
            "user123", "user", "target_project_dir", "/persist/project", "user123"
        )
        
        # 创建新的配置管理器实例（模拟重启）
        new_manager = ConfigManager(
            storage_path=temp_storage,
            global_config=config_manager.global_config
        )
        
        # 验证配置已加载
        effective = new_manager.get_effective_config("user123", "user")
        assert effective["target_project_dir"] == "/persist/project"
    
    def test_parse_temp_params(self, config_manager):
        """测试解析临时参数"""
        message = "--dir=/tmp/test --lang=en-US 查看项目结构"
        clean_message, temp_params = config_manager.parse_temp_params(message)
        
        assert clean_message == "查看项目结构"
        assert temp_params["dir"] == "/tmp/test"
        assert temp_params["lang"] == "en-US"
    
    def test_is_config_command(self, config_manager):
        """测试配置命令识别"""
        assert config_manager.is_config_command("/setdir /path")
        assert config_manager.is_config_command("/lang zh-CN")
        assert config_manager.is_config_command("/config")
        assert config_manager.is_config_command("/reset")
        assert not config_manager.is_config_command("普通消息")
    
    def test_handle_config_command_setdir(self, config_manager):
        """测试处理 setdir 命令"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            response = config_manager.handle_config_command(
                session_id="user123",
                session_type="user",
                user_id="user123",
                message=f"/setdir {tmpdir}"
            )
            
            assert response is not None
            assert "✅" in response
    
    def test_handle_config_command_view(self, config_manager):
        """测试查看配置命令"""
        response = config_manager.handle_config_command(
            session_id="user123",
            session_type="user",
            user_id="user123",
            message="/config"
        )
        
        assert response is not None
        assert "当前配置" in response or "Current Config" in response
    
    def test_update_count(self, config_manager):
        """测试更新次数统计"""
        # 第一次设置
        config_manager.set_config(
            "user123", "user", "target_project_dir", "/project1", "user123"
        )
        config = config_manager.configs["user123"]
        assert config.update_count == 1
        
        # 第二次设置
        config_manager.set_config(
            "user123", "user", "target_project_dir", "/project2", "user123"
        )
        assert config.update_count == 2
        
        # 第三次设置（不同的配置项）
        config_manager.set_config(
            "user123", "user", "response_language", "en-US", "user123"
        )
        assert config.update_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
