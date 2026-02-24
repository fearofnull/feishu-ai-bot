#!/usr/bin/env python
"""
飞书AI机器人集成测试快速启动脚本
"""
import sys
import time
import subprocess
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(step_num, text):
    """打印步骤"""
    print(f"\n[步骤 {step_num}] {text}")
    print("-" * 70)

def check_config():
    """检查配置"""
    print_step(1, "检查配置")
    try:
        from config import validate_config, print_config_status
        validate_config()
        print_config_status()
        print("✅ 配置检查通过")
        return True
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        print("\n请确保：")
        print("1. .env 文件存在")
        print("2. FEISHU_APP_ID 和 FEISHU_APP_SECRET 已配置")
        print("3. FEISHU_CHAT_ID 已配置（用于测试）")
        print("4. 至少配置一个AI API密钥")
        return False

def check_bot_running():
    """检查机器人是否在运行"""
    print_step(2, "检查机器人状态")
    
    # 尝试导入并检查
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'lark_bot.py' in ' '.join(cmdline):
                    print(f"✅ 机器人正在运行 (PID: {proc.info['pid']})")
                    return True
            except:
                pass
    except ImportError:
        print("⚠️ 未安装 psutil，无法自动检测机器人状态")
        print("   请手动确认 lark_bot.py 是否在运行")
        response = input("\n机器人是否在运行？(y/n): ").lower()
        return response == 'y'
    
    print("❌ 机器人未运行")
    print("\n请在另一个终端运行：")
    print("  python lark_bot.py")
    print("\n然后重新运行此测试脚本")
    return False

def run_test():
    """运行集成测试"""
    print_step(3, "运行集成测试")
    
    try:
        from test_bot_message import test_bot_response
        from config import FEISHU_CHAT_ID
        
        if not FEISHU_CHAT_ID:
            print("❌ 未配置 FEISHU_CHAT_ID")
            return False
        
        # 运行测试
        test_message = "集成测试：请回复这条消息"
        test_bot_response(FEISHU_CHAT_ID, test_message, wait_seconds=10)
        return True
        
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_menu():
    """显示菜单"""
    print_header("飞书AI机器人集成测试")
    
    print("请选择测试模式：\n")
    print("1. 完整自动化测试（推荐）")
    print("   - 自动发送消息、等待回复、验证结果")
    print()
    print("2. 快速消息测试")
    print("   - 发送一条测试消息")
    print()
    print("3. 查看聊天历史")
    print("   - 查看最近10条消息")
    print()
    print("4. 测试不同AI提供商")
    print("   - 测试Claude API、Gemini API、OpenAI API")
    print()
    print("5. 测试会话管理")
    print("   - 测试连续对话和会话命令")
    print()
    print("0. 退出")
    print()
    
    choice = input("请输入选项 (0-5): ").strip()
    return choice

def test_quick_message():
    """快速消息测试"""
    print_header("快速消息测试")
    
    from send_test_message import send_message
    from config import FEISHU_CHAT_ID
    
    if not FEISHU_CHAT_ID:
        print("❌ 未配置 FEISHU_CHAT_ID")
        return
    
    message = input("请输入测试消息: ").strip()
    if not message:
        message = "测试消息：这是一条快速测试"
    
    print(f"\n发送消息: {message}")
    send_message(FEISHU_CHAT_ID, message)
    
    print("\n提示：请在飞书客户端查看机器人回复")
    print("或运行: python check_chat_history.py")

def test_chat_history():
    """查看聊天历史"""
    print_header("查看聊天历史")
    
    try:
        subprocess.run([sys.executable, "check_chat_history.py"])
    except Exception as e:
        print(f"❌ 执行失败: {e}")

def test_ai_providers():
    """测试不同AI提供商"""
    print_header("测试AI提供商")
    
    from send_test_message import send_message
    from config import FEISHU_CHAT_ID
    
    if not FEISHU_CHAT_ID:
        print("❌ 未配置 FEISHU_CHAT_ID")
        return
    
    tests = [
        ("Claude API", "@claude 什么是Python？"),
        ("Gemini API", "@gemini 什么是JavaScript？"),
        ("OpenAI API", "@openai 什么是机器学习？"),
        ("智能路由（一般问答）", "什么是人工智能？"),
        ("智能路由（代码相关）", "查看代码库结构"),
    ]
    
    print("将依次测试以下AI提供商：\n")
    for i, (name, msg) in enumerate(tests, 1):
        print(f"{i}. {name}")
        print(f"   消息: {msg}")
    
    print("\n按回车开始测试...")
    input()
    
    for i, (name, msg) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] 测试 {name}")
        print(f"发送: {msg}")
        send_message(FEISHU_CHAT_ID, msg)
        print("等待5秒...")
        time.sleep(5)
    
    print("\n✅ 所有测试消息已发送")
    print("请在飞书客户端查看机器人回复")

def test_session_management():
    """测试会话管理"""
    print_header("测试会话管理")
    
    from send_test_message import send_message
    from config import FEISHU_CHAT_ID
    
    if not FEISHU_CHAT_ID:
        print("❌ 未配置 FEISHU_CHAT_ID")
        return
    
    tests = [
        ("连续对话测试1", "我叫张三"),
        ("连续对话测试2", "我叫什么名字？"),
        ("查看会话信息", "/session"),
        ("查看对话历史", "/history"),
        ("创建新会话", "/new"),
    ]
    
    print("将依次测试以下会话功能：\n")
    for i, (name, msg) in enumerate(tests, 1):
        print(f"{i}. {name}")
        print(f"   命令: {msg}")
    
    print("\n按回车开始测试...")
    input()
    
    for i, (name, msg) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {name}")
        print(f"发送: {msg}")
        send_message(FEISHU_CHAT_ID, msg)
        print("等待3秒...")
        time.sleep(3)
    
    print("\n✅ 所有测试消息已发送")
    print("请在飞书客户端查看机器人回复")

def main():
    """主函数"""
    # 检查配置
    if not check_config():
        return
    
    while True:
        choice = show_menu()
        
        if choice == "0":
            print("\n再见！")
            break
        elif choice == "1":
            # 完整自动化测试
            if check_bot_running():
                run_test()
            input("\n按回车继续...")
        elif choice == "2":
            # 快速消息测试
            test_quick_message()
            input("\n按回车继续...")
        elif choice == "3":
            # 查看聊天历史
            test_chat_history()
            input("\n按回车继续...")
        elif choice == "4":
            # 测试AI提供商
            test_ai_providers()
            input("\n按回车继续...")
        elif choice == "5":
            # 测试会话管理
            test_session_management()
            input("\n按回车继续...")
        else:
            print("\n❌ 无效选项，请重新选择")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
