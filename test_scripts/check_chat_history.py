"""
查看聊天历史
"""
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
CHAT_ID = FEISHU_CHAT_ID

if not CHAT_ID:
    print("❌ 错误: 未配置 FEISHU_CHAT_ID")
    print("请在 .env 文件中设置 FEISHU_CHAT_ID")
    exit(1)

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

request = (
    ListMessageRequest.builder()
    .container_id_type("chat")
    .container_id(CHAT_ID)
    .page_size(10)
    .build()
)

response = client.im.v1.message.list(request)

if response.success():
    messages = response.data.items if response.data.items else []
    print(f"\n获取到 {len(messages)} 条最新消息：\n")
    
    for i, msg in enumerate(messages, 1):
        sender_type = msg.sender.sender_type
        msg_content = ""
        
        if msg.msg_type == "text":
            try:
                msg_content = json.loads(msg.body.content)["text"]
            except:
                msg_content = msg.body.content
        
        print(f"{i}. [{sender_type}] {msg_content[:200]}")
        print()
else:
    print(f"获取失败: {response.msg}")
