"""
飞书机器人消息测试工具
用于自动化测试机器人是否能正常接收和回复消息
"""
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import time
import os
import certifi

# 使用certifi提供的证书bundle
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

# 机器人凭证
APP_ID = FEISHU_APP_ID
APP_SECRET = FEISHU_APP_SECRET

# 创建客户端
client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


def list_bot_chats():
    """
    列出机器人所在的所有群聊
    
    Returns:
        list: 群聊列表
    """
    print("\n正在获取机器人所在的群聊列表...")
    
    request = ListChatRequest.builder().page_size(20).build()
    response = client.im.v1.chat.list(request)
    
    if response.success():
        chats = response.data.items if response.data.items else []
        print(f"找到 {len(chats)} 个群聊：\n")
        
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat.name}")
            print(f"   Chat ID: {chat.chat_id}")
            print(f"   类型: {chat.chat_mode}")
            print()
        
        return chats
    else:
        print(f"获取群聊列表失败: {response.msg}")
        return []


def send_message_to_user(user_open_id: str, message: str) -> dict:
    """
    发送消息给指定用户
    
    Args:
        user_open_id: 用户的 open_id
        message: 要发送的消息内容
        
    Returns:
        dict: 包含发送结果的字典
    """
    content = json.dumps({"text": message})
    
    request = (
        CreateMessageRequest.builder()
        .receive_id_type("open_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(user_open_id)
            .msg_type("text")
            .content(content)
            .build()
        )
        .build()
    )
    
    response = client.im.v1.message.create(request)
    
    if response.success():
        return {
            "success": True,
            "message_id": response.data.message_id,
            "chat_id": response.data.chat_id,
            "create_time": response.data.create_time
        }
    else:
        return {
            "success": False,
            "code": response.code,
            "msg": response.msg,
            "log_id": response.get_log_id()
        }


def get_chat_history(chat_id: str, page_size: int = 10) -> dict:
    """
    获取聊天历史，用于验证机器人是否回复
    
    Args:
        chat_id: 聊天 ID
        page_size: 获取消息数量
        
    Returns:
        dict: 聊天历史
    """
    request = (
        ListMessageRequest.builder()
        .container_id_type("chat")
        .container_id(chat_id)
        .page_size(page_size)
        .build()
    )
    
    response = client.im.v1.message.list(request)
    
    if response.success():
        return {
            "success": True,
            "messages": response.data.items if response.data.items else []
        }
    else:
        return {
            "success": False,
            "code": response.code,
            "msg": response.msg
        }


def send_message_to_chat(chat_id: str, message: str) -> dict:
    """
    发送消息到指定群聊
    
    Args:
        chat_id: 群聊 ID
        message: 要发送的消息内容
        
    Returns:
        dict: 包含发送结果的字典
    """
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
        return {
            "success": True,
            "message_id": response.data.message_id,
            "chat_id": response.data.chat_id,
            "create_time": response.data.create_time
        }
    else:
        return {
            "success": False,
            "code": response.code,
            "msg": response.msg,
            "log_id": response.get_log_id()
        }


def test_bot_response(chat_id: str, test_message: str, wait_seconds: int = 5):
    """
    测试机器人是否能正常接收和回复消息
    
    Args:
        chat_id: 群聊 ID（可以是单聊或群聊）
        test_message: 测试消息内容
        wait_seconds: 等待机器人回复的时间（秒）
    """
    print(f"\n{'='*60}")
    print(f"开始测试机器人消息接收和回复功能")
    print(f"{'='*60}\n")
    
    # 1. 发送测试消息
    print(f"[步骤 1] 发送测试消息: {test_message}")
    result = send_message_to_chat(chat_id, test_message)
    
    if not result["success"]:
        print(f"❌ 发送消息失败: {result['msg']} (code: {result['code']})")
        return
    
    print(f"✅ 消息发送成功")
    print(f"   - Message ID: {result['message_id']}")
    print(f"   - Chat ID: {result['chat_id']}")
    
    chat_id = result["chat_id"]
    
    # 2. 等待机器人处理
    print(f"\n[步骤 2] 等待 {wait_seconds} 秒，让机器人处理消息...")
    time.sleep(wait_seconds)
    
    # 3. 获取聊天历史，检查机器人是否回复
    print(f"\n[步骤 3] 获取聊天历史，检查机器人回复...")
    history = get_chat_history(chat_id, page_size=5)
    
    if not history["success"]:
        print(f"❌ 获取聊天历史失败: {history['msg']}")
        return
    
    messages = history["messages"]
    print(f"   - 获取到 {len(messages)} 条消息")
    
    # 4. 分析消息
    bot_replied = False
    for msg in messages:
        sender_type = msg.sender.sender_type
        msg_content = ""
        
        if msg.msg_type == "text":
            try:
                msg_content = json.loads(msg.body.content)["text"]
            except:
                msg_content = msg.body.content
        
        print(f"\n   消息:")
        print(f"   - 发送者类型: {sender_type}")
        print(f"   - 消息类型: {msg.msg_type}")
        print(f"   - 内容: {msg_content[:100]}..." if len(msg_content) > 100 else f"   - 内容: {msg_content}")
        
        if sender_type == "app":
            bot_replied = True
    
    # 5. 输出测试结果
    print(f"\n{'='*60}")
    if bot_replied:
        print("✅ 测试通过：机器人成功接收并回复了消息")
    else:
        print("❌ 测试失败：机器人没有回复消息")
        print("\n可能的原因：")
        print("1. 机器人程序 (lark_bot.py) 没有运行")
        print("2. WebSocket 连接有问题")
        print("3. 消息处理逻辑有错误")
        print("4. Claude Code CLI 配置有问题")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("飞书机器人自动化测试工具")
    print("="*60)
    
    # 使用配置文件中的 chat_id
    CHAT_ID = FEISHU_CHAT_ID
    if not CHAT_ID:
        print("❌ 错误: 未配置 FEISHU_CHAT_ID")
        print("请在 .env 文件中设置 FEISHU_CHAT_ID")
        exit(1)
    
    TEST_MESSAGE = "自动化测试：请回复这条消息"
    
    # 运行测试
    test_bot_response(CHAT_ID, TEST_MESSAGE, wait_seconds=10)
