"""
测试 /help 命令
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feishu_bot.session_manager import SessionManager


def test_help_command():
    """测试帮助命令"""
    print("=" * 60)
    print("测试 /help 命令")
    print("=" * 60)
    
    # 创建会话管理器
    sm = SessionManager(storage_path="./test_data/sessions.json")
    
    # 测试不同的帮助命令格式
    test_commands = ["/help", "帮助", "help", "/HELP", "Help"]
    
    for cmd in test_commands:
        print(f"\n测试命令: {cmd}")
        print("-" * 60)
        
        # 检查是否为会话命令
        is_cmd = sm.is_session_command(cmd)
        print(f"是否为会话命令: {is_cmd}")
        
        if is_cmd:
            # 处理命令
            response = sm.handle_session_command("test_user", cmd)
            print(f"\n响应:\n{response}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_help_command()
