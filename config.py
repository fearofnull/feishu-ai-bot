"""
配置管理模块
从环境变量加载配置信息
"""
import os
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 查找 .env 文件
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载配置文件: {env_path}")
    else:
        print(f"⚠️ 未找到 .env 文件: {env_path}")
        print("请复制 .env.example 为 .env 并填入配置")
except ImportError:
    print("⚠️ 未安装 python-dotenv，请运行: pip install python-dotenv")
    print("将尝试直接从环境变量读取配置")

# 飞书机器人配置
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')

# 测试配置
FEISHU_CHAT_ID = os.getenv('FEISHU_CHAT_ID')
FEISHU_USER_ID = os.getenv('FEISHU_USER_ID')

# 目标项目目录
TARGET_PROJECT_DIR = os.getenv('TARGET_PROJECT_DIR', '')

# 验证必需配置
def validate_config():
    """验证必需的配置项是否存在"""
    missing = []
    
    if not FEISHU_APP_ID:
        missing.append('FEISHU_APP_ID')
    if not FEISHU_APP_SECRET:
        missing.append('FEISHU_APP_SECRET')
    
    if missing:
        raise ValueError(
            f"缺少必需的配置项: {', '.join(missing)}\n"
            f"请在 .env 文件中设置这些配置项"
        )
    
    return True

# 打印配置状态（隐藏敏感信息）
def print_config_status():
    """打印配置状态（用于调试）"""
    print("\n" + "="*60)
    print("配置状态")
    print("="*60)
    print(f"APP_ID: {'✅ 已配置' if FEISHU_APP_ID else '❌ 未配置'}")
    print(f"APP_SECRET: {'✅ 已配置' if FEISHU_APP_SECRET else '❌ 未配置'}")
    print(f"CHAT_ID: {'✅ 已配置' if FEISHU_CHAT_ID else '⚠️ 未配置（测试时需要）'}")
    print(f"USER_ID: {'✅ 已配置' if FEISHU_USER_ID else '⚠️ 未配置（测试时需要）'}")
    print(f"TARGET_PROJECT_DIR: {'✅ 已配置' if TARGET_PROJECT_DIR else '⚠️ 未配置（Claude CLI需要）'}")
    print("="*60 + "\n")

if __name__ == "__main__":
    # 测试配置加载
    try:
        validate_config()
        print_config_status()
        print("✅ 配置验证通过")
    except ValueError as e:
        print(f"❌ 配置验证失败: {e}")
