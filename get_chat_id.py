"""
获取与机器人的 chat_id
方法：创建一个与指定用户的单聊，返回 chat_id
"""
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = ''

# 从配置文件加载配置
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, validate_config

# 验证配置
try:
    validate_config()
except ValueError as e:
    print(f"❌ 配置加载失败: {e}")
    exit(1)

APP_ID = FEISHU_APP_ID
APP_SECRET = FEISHU_APP_SECRET

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


def create_p2p_chat_and_get_id(user_id: str, user_id_type: str = "open_id"):
    """
    创建与用户的单聊并获取 chat_id
    
    Args:
        user_id: 用户 ID
        user_id_type: ID 类型（open_id, union_id, user_id）
    
    Returns:
        str: chat_id
    """
    print(f"\n正在创建与用户的单聊...")
    print(f"用户 ID: {user_id}")
    print(f"ID 类型: {user_id_type}\n")
    
    # 创建单聊
    request = (
        CreateChatRequest.builder()
        .user_id_type(user_id_type)
        .request_body(
            CreateChatRequestBody.builder()
            .chat_mode("p2p")  # 单聊模式
            .chat_type("private")  # 私有聊天
            .user_id_list([user_id])  # 用户列表
            .build()
        )
        .build()
    )
    
    response = client.im.v1.chat.create(request)
    
    if response.success():
        chat_id = response.data.chat_id
        print(f"✅ 成功获取 chat_id: {chat_id}")
        return chat_id
    else:
        print(f"❌ 创建单聊失败: {response.msg} (code: {response.code})")
        
        # 如果是因为已存在，尝试通过发送消息获取
        if response.code == 1254044:  # 群组已存在
            print("\n单聊已存在，尝试通过发送消息获取 chat_id...")
            return send_message_and_get_chat_id(user_id, user_id_type)
        
        return None


def send_message_and_get_chat_id(user_id: str, user_id_type: str = "open_id"):
    """
    通过发送消息获取 chat_id
    
    Args:
        user_id: 用户 ID
        user_id_type: ID 类型
    
    Returns:
        str: chat_id
    """
    content = json.dumps({"text": "Hello! 这是一条测试消息，用于获取 chat_id"})
    
    request = (
        CreateMessageRequest.builder()
        .receive_id_type(user_id_type)
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
        chat_id = response.data.chat_id
        print(f"✅ 成功获取 chat_id: {chat_id}")
        return chat_id
    else:
        print(f"❌ 发送消息失败: {response.msg} (code: {response.code})")
        return None


def get_user_info():
    """获取当前用户信息（需要 user access token）"""
    print("\n尝试获取当前用户信息...")
    # 注意：这需要 user_access_token，而不是 tenant_access_token
    # 机器人使用 tenant_access_token，无法直接获取用户信息
    print("提示：机器人使用的是 tenant_access_token，无法直接获取用户信息")
    print("你需要提供你的 open_id\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("获取 chat_id 工具")
    print("="*60)
    
    # 你的 open_id（需要手动提供或从配置读取）
    # 注意：这个 open_id 是特定于某个应用的，不能跨应用使用
    YOUR_OPEN_ID = input("请输入你的 open_id（或直接回车跳过）: ").strip()
    
    if not YOUR_OPEN_ID:
        print("\n提示：你可以通过以下方式获取 open_id：")
        print("1. 在飞书客户端给机器人发一条消息")
        print("2. 启动机器人程序：python lark_bot.py")
        print("3. 在机器人日志中查看 open_id 和 chat_id")
        exit(0)
    
    # 直接尝试发送消息获取 chat_id
    print("\n尝试通过发送消息获取 chat_id...")
    print("-" * 60)
    
    chat_id = send_message_and_get_chat_id(YOUR_OPEN_ID, "open_id")
    
    if chat_id:
        print(f"\n{'='*60}")
        print(f"✅ 成功！你的 chat_id 是: {chat_id}")
        print(f"{'='*60}")
        print("\n请将此 chat_id 添加到 .env 文件中：")
        print(f"  FEISHU_CHAT_ID={chat_id}")
        print("\n现在你可以使用这个 chat_id 进行测试：")
        print(f"  python send_test_message.py {chat_id} \"测试消息\"")
        print()
    else:
        print("\n❌ 无法获取 chat_id")
        print("\n请尝试以下方法：")
        print("1. 在飞书客户端手动给机器人发一条消息")
        print("2. 启动机器人程序：python lark_bot.py")
        print("3. 在机器人日志中查看 chat_id")
