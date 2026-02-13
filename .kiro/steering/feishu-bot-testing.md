---
inclusion: auto
---

# 飞书机器人自动化测试关键信息

## 测试配置（自动化测试必需）

### 机器人凭证
```python
APP_ID = 'cli_a9f47e209db8dcc5'
APP_SECRET = 'nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT'
```

### 测试环境
- **测试chat_id**: `oc_585f29d10679c7a0b5c3bf0d34adba90`
- **用户user_id**: `155529283`
- **机器人名称**: 自动回复机器人

## 自动化测试方法

### 方法1: 完整自动化测试
```bash
python test_bot_message.py
```
- 自动发送消息
- 等待10秒
- 验证机器人回复
- 输出测试结果

### 方法2: 手动验证
```bash
# 发送消息
python send_test_message.py oc_585f29d10679c7a0b5c3bf0d34adba90 "测试消息"

# 查看结果
python check_chat_history.py
```

## 测试验证标准

**成功标准**:
- 聊天历史中有 `sender_type == "app"` 的消息
- 机器人回复包含用户发送的内容
- 无异常错误

**失败原因**:
1. 机器人未运行（lark_bot.py）
2. WebSocket连接断开
3. 权限配置问题
4. 代码逻辑错误

## 重要提醒

在实现新功能或修改代码后，**必须**：
1. 重启机器人：`python lark_bot.py`
2. 运行测试：`python test_bot_message.py`
3. 验证结果：检查是否有 `✅ 测试通过`

详细测试指南见：`.kiro/specs/feishu-ai-bot/testing-guide.md`
