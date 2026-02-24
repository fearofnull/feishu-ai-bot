"""
检查最新消息
"""
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = ''

from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID

client = lark.Client.builder().app_id(FEISHU_APP_ID).app_secret(FEISHU_APP_SECRET).build()

def get_latest_messages(chat_id: str, count: int = 10):
    """获取最新消息"""
    request = (
        ListMessageRequest.builder()
        .container_id_type("chat")
        .container_id(chat_id)
        .page_size(count)
        .build()
    )
    
    response = client.im.v1.message.list(request)
    
    if response.success():
        messages = response.data.items if response.data.items else []
        print(f"\n最新 {len(messages)} 条消息:\n")
        
        for i, msg in enumerate(messages, 1):
            sender_type = msg.sender.sender_type
            
            if msg.msg_type == "text":
                try:
                    content = json.loads(msg.body.content)["text"]
                except:
                    content = msg.body.content
            else:
                content = f"[{msg.msg_type}]"
            
            print(f"{i}. [{sender_type}] {content}")
            print(f"   Message ID: {msg.message_id}")
            print(f"   Create Time: {msg.create_time}")
            print()
    else:
        print(f"获取消息失败: {response.msg}")

if __name__ == "__main__":
    get_latest_messages(FEISHU_CHAT_ID, 10)
