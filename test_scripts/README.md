# 测试脚本目录

本目录包含用于测试飞书AI机器人的各种脚本。

## 脚本说明

### 集成测试脚本
- `run_integration_test.py` - 主集成测试脚本
- `test_bot_message.py` - 机器人消息测试
- `test_openai_api.py` - OpenAI API测试
- `test_openai_direct.py` - OpenAI直接调用测试

### 消息发送脚本
- `bot_send_to_user.py` - 机器人发送消息给用户
- `send_test_message.py` - 发送测试消息

### 消息查询脚本
- `check_chat_history.py` - 查看聊天历史
- `check_latest_messages.py` - 查看最新消息

### 工具脚本
- `get_chat_id.py` - 获取聊天ID

## 使用方法

1. 确保已配置 `.env` 文件
2. 确保机器人正在运行 (`python lark_bot.py`)
3. 运行相应的测试脚本

例如：
```bash
python test_scripts/run_integration_test.py
```

## 注意事项

- 这些脚本仅用于开发和测试
- 不要在生产环境中使用
- 确保有正确的API密钥和权限
