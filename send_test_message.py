"""
简单的测试消息发送工具
使用方法：python send_test_message.py <chat_id> <message>
"""
import sys
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = ''

# 从配置文件加载配置
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID, validate_config

# 验证配置
try:
    validate_config()
except ValueError as e:
    print(f"❌ 配置加载失败: {e}")
    exit(1)

APP_ID = FEISHU_APP_ID
APP_SECRET = FEISHU_APP_SECRET

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

def send_message(chat_id: str, message: str):
    """发送消息到指定聊天"""
    content = json.dumps({"text": message})
    
    request = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(content)
            .build()
        )
        .build()
    )
    
    response = client.im.v1.message.create(request)
    
    if response.success():
        print(f"✅ 消息发送成功")
        print(f"   Message ID: {response.data.message_id}")
        return True
    else:
        print(f"❌ 消息发送失败: {response.msg} (code: {response.code})")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 如果没有提供参数，尝试使用配置文件中的 chat_id
        if FEISHU_CHAT_ID:
            chat_id = FEISHU_CHAT_ID
            message = sys.argv[1] if len(sys.argv) > 1 else "测试消息：这是一条自动化测试消息"
            print(f"使用配置文件中的 chat_id: {chat_id}")
        else:
            print("使用方法：")
            print("  python send_test_message.py <chat_id> [message]")
            print()
            print("或者在 .env 文件中配置 FEISHU_CHAT_ID，然后：")
            print("  python send_test_message.py [message]")
            print()
            print("示例：")
            print("  python send_test_message.py oc_xxxxx \"测试消息\"")
            print()
            print("如何获取 chat_id：")
            print("  1. 先手动给机器人发一条消息")
            print("  2. 在机器人日志中查看 chat_id")
            sys.exit(1)
    else:
        chat_id = sys.argv[1]
        message = sys.argv[2] if len(sys.argv) > 2 else "测试消息：这是一条自动化测试消息"
    
    print(f"\n发送消息到: {chat_id}")
    print(f"消息内容: {message}\n")
    
    send_message(chat_id, message)
