"""
OpenAI API 集成测试
测试机器人使用 OpenAI API 回复消息
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

# 创建客户端
client = lark.Client.builder().app_id(FEISHU_APP_ID).app_secret(FEISHU_APP_SECRET).build()


def send_message_to_chat(chat_id: str, message: str) -> dict:
    """发送消息到指定群聊"""
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
        }
    else:
        return {
            "success": False,
            "code": response.code,
            "msg": response.msg,
        }


def get_chat_history(chat_id: str, page_size: int = 10) -> dict:
    """获取聊天历史"""
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


def test_openai_api():
    """测试 OpenAI API 回复"""
    print("\n" + "="*60)
    print("OpenAI API 集成测试")
    print("="*60 + "\n")
    
    chat_id = FEISHU_CHAT_ID
    if not chat_id:
        print("❌ 错误: 未配置 FEISHU_CHAT_ID")
        exit(1)
    
    # 测试消息 - 明确指定使用 OpenAI
    test_message = "@openai 你好，请用一句话介绍你自己"
    
    print(f"[步骤 1] 发送测试消息: {test_message}")
    result = send_message_to_chat(chat_id, test_message)
    
    if not result["success"]:
        print(f"❌ 发送消息失败: {result['msg']}")
        return
    
    print(f"✅ 消息发送成功 (Message ID: {result['message_id']})")
    
    # 等待机器人处理
    wait_seconds = 15
    print(f"\n[步骤 2] 等待 {wait_seconds} 秒，让机器人处理...")
    time.sleep(wait_seconds)
    
    # 获取聊天历史
    print(f"\n[步骤 3] 检查机器人回复...")
    history = get_chat_history(chat_id, page_size=5)
    
    if not history["success"]:
        print(f"❌ 获取聊天历史失败: {history['msg']}")
        return
    
    messages = history["messages"]
    print(f"   获取到 {len(messages)} 条消息\n")
    
    # 分析消息
    bot_replied = False
    bot_message = ""
    
    for msg in messages:
        sender_type = msg.sender.sender_type
        
        if msg.msg_type == "text":
            try:
                content = json.loads(msg.body.content)["text"]
            except:
                content = msg.body.content
            
            print(f"   [{sender_type}] {content[:100]}...")
            
            if sender_type == "app":
                bot_replied = True
                bot_message = content
    
    # 输出结果
    print("\n" + "="*60)
    if bot_replied:
        print("✅ 测试通过：OpenAI API 成功回复")
        print(f"\n机器人回复:\n{bot_message}")
    else:
        print("❌ 测试失败：机器人没有回复")
        print("\n请检查:")
        print("1. lark_bot.py 是否正在运行")
        print("2. OPENAI_API_KEY 是否配置正确")
        print("3. OPENAI_BASE_URL 是否配置正确（如果使用）")
        print("4. 查看机器人日志中的错误信息")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_openai_api()
