"""
配置管理模块
支持从环境变量和配置文件加载配置
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class BotConfig:
    """机器人配置数据类"""
    
    # 飞书应用配置
    app_id: str
    app_secret: str
    
    # AI CLI 配置
    target_directory: str  # 通用目标目录（兼容旧配置）
    claude_cli_target_dir: Optional[str] = None  # Claude CLI 专用目录
    gemini_cli_target_dir: Optional[str] = None  # Gemini CLI 专用目录
    ai_timeout: int = 600
    
    # 缓存配置
    cache_size: int = 1000
    
    # SSL 配置
    ssl_cert_file: str = ""
    
    # 会话管理配置
    session_storage_path: str = "./data/sessions.json"
    max_session_messages: int = 50
    session_timeout: int = 86400  # 24小时
    
    # AI API 配置
    claude_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-4o"
    
    # 默认设置
    default_provider: str = "claude"
    default_layer: str = "api"
    
    # 日志配置
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "BotConfig":
        """从环境变量和配置文件加载配置
        
        Args:
            env_file: .env 文件路径，默认为当前目录下的 .env
            
        Returns:
            BotConfig 实例
        """
        # 加载 .env 文件
        if env_file is None:
            env_file = Path.cwd() / ".env"
        else:
            env_file = Path(env_file)
        
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass  # python-dotenv 未安装，直接使用环境变量
        
        # 从环境变量读取配置
        return cls(
            # 飞书应用配置
            app_id=os.getenv("FEISHU_APP_ID", ""),
            app_secret=os.getenv("FEISHU_APP_SECRET", ""),
            
            # AI CLI 配置
            target_directory=os.getenv("TARGET_PROJECT_DIR", ""),
            ai_timeout=int(os.getenv("AI_TIMEOUT", "600")),
            
            # 缓存配置
            cache_size=int(os.getenv("CACHE_SIZE", "1000")),
            
            # SSL 配置
            ssl_cert_file=os.getenv("SSL_CERT_FILE", ""),
            
            # 会话管理配置
            session_storage_path=os.getenv("SESSION_STORAGE_PATH", "./data/sessions.json"),
            max_session_messages=int(os.getenv("MAX_SESSION_MESSAGES", "50")),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "86400")),
            
            # AI API 配置
            claude_api_key=os.getenv("CLAUDE_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            
            # 默认设置
            default_provider=os.getenv("DEFAULT_PROVIDER", "claude"),
            default_layer=os.getenv("DEFAULT_LAYER", "api"),
            
            # 日志配置
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    def validate(self) -> None:
        """验证配置的有效性
        
        Raises:
            ValueError: 如果必需的配置项缺失或无效
        """
        errors = []
        
        # 验证必需字段
        if not self.app_id:
            errors.append("FEISHU_APP_ID 未配置")
        if not self.app_secret:
            errors.append("FEISHU_APP_SECRET 未配置")
        
        # 验证默认提供商
        valid_providers = ["claude", "gemini", "openai"]
        if self.default_provider not in valid_providers:
            errors.append(f"DEFAULT_PROVIDER 必须是以下之一: {', '.join(valid_providers)}")
        
        # 验证默认执行层
        valid_layers = ["api", "cli"]
        if self.default_layer not in valid_layers:
            errors.append(f"DEFAULT_LAYER 必须是以下之一: {', '.join(valid_layers)}")
        
        # 验证数值范围
        if self.ai_timeout <= 0:
            errors.append("AI_TIMEOUT 必须大于 0")
        if self.cache_size <= 0:
            errors.append("CACHE_SIZE 必须大于 0")
        if self.max_session_messages <= 0:
            errors.append("MAX_SESSION_MESSAGES 必须大于 0")
        if self.session_timeout <= 0:
            errors.append("SESSION_TIMEOUT 必须大于 0")
        
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL 必须是以下之一: {', '.join(valid_log_levels)}")
        
        if errors:
            raise ValueError(
                "配置验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
            )
    
    def has_api_key(self, provider: str) -> bool:
        """检查指定提供商的 API 密钥是否已配置
        
        Args:
            provider: AI 提供商名称 (claude, gemini, openai)
            
        Returns:
            True 如果 API 密钥已配置
        """
        if provider == "claude":
            return bool(self.claude_api_key)
        elif provider == "gemini":
            return bool(self.gemini_api_key)
        elif provider == "openai":
            return bool(self.openai_api_key)
        return False
    
    def print_status(self) -> None:
        """打印配置状态（用于调试，隐藏敏感信息）"""
        print("\n" + "=" * 60)
        print("配置状态")
        print("=" * 60)
        print(f"APP_ID: {'✅ 已配置' if self.app_id else '❌ 未配置'}")
        print(f"APP_SECRET: {'✅ 已配置' if self.app_secret else '❌ 未配置'}")
        print(f"TARGET_PROJECT_DIR: {'✅ 已配置' if self.target_directory else '⚠️ 未配置'}")
        print(f"CLAUDE_API_KEY: {'✅ 已配置' if self.claude_api_key else '⚠️ 未配置'}")
        print(f"GEMINI_API_KEY: {'✅ 已配置' if self.gemini_api_key else '⚠️ 未配置'}")
        print(f"OPENAI_API_KEY: {'✅ 已配置' if self.openai_api_key else '⚠️ 未配置'}")
        print(f"DEFAULT_PROVIDER: {self.default_provider}")
        print(f"DEFAULT_LAYER: {self.default_layer}")
        print(f"LOG_LEVEL: {self.log_level}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # 测试配置加载
    try:
        config = BotConfig.from_env()
        config.validate()
        config.print_status()
        print("✅ 配置验证通过")
    except ValueError as e:
        print(f"❌ 配置验证失败:\n{e}")
