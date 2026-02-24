"""
机器人主动给用户发消息，并获取 chat_id
"""
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = ''

# 从配置文件加载配置
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_USER_ID, validate_config

# 验证配置
try:
    validate_config()
except ValueError as e:
    print(f"❌ 配置加载失败: {e}")
    exit(1)

# 机器人凭证
APP_ID = FEISHU_APP_ID
APP_SECRET = FEISHU_APP_SECRET

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


def send_message_to_user_by_user_id(user_id: str, message: str):
    """
    通过 user_id 给用户发送消息
    
    Args:
        user_id: 用户 user_id
        message: 消息内容
    """
    content = json.dumps({"text": message})
    
    request = (
        CreateMessageRequest.builder()
        .receive_id_type("user_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(user_id)
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
        print(f"   Chat ID: {response.data.chat_id}")
        print(f"\n{'='*60}")
        print(f"✅ 成功获取 chat_id: {response.data.chat_id}")
        print(f"{'='*60}")
        return response.data.chat_id
    else:
        print(f"❌ 消息发送失败: {response.msg} (code: {response.code})")
        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("机器人主动发消息获取 chat_id")
    print("="*60 + "\n")
    
    # 从配置文件读取 user_id，如果没有则提示输入
    YOUR_USER_ID = FEISHU_USER_ID
    
    if not YOUR_USER_ID:
        YOUR_USER_ID = input("请输入你的 user_id: ").strip()
        if not YOUR_USER_ID:
            print("❌ 错误: 未提供 user_id")
            print("请在 .env 文件中设置 FEISHU_USER_ID 或通过命令行输入")
            exit(1)
    
    print(f"正在给用户 {YOUR_USER_ID} 发送消息...\n")
    
    message = "你好！这是「自动回复机器人」发送的测试消息，用于获取 chat_id。现在你可以回复我了！"
    chat_id = send_message_to_user_by_user_id(YOUR_USER_ID, message)
    
    if chat_id:
        print(f"\n请将此 chat_id 添加到 .env 文件中：")
        print(f"  FEISHU_CHAT_ID={chat_id}")
        print(f"\n现在你可以使用这个 chat_id 进行自动化测试：")
        print(f"  python send_test_message.py {chat_id} \"测试消息\"")
        print()
