# 飞书AI机器人自动化测试指南

## 关键测试信息（重要！）

### 机器人配置
```python
APP_ID = 'cli_a9f47e209db8dcc5'
APP_SECRET = 'nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT'
```

### 测试环境
- **机器人名称**: 自动回复机器人
- **用户user_id**: 155529283
- **测试chat_id**: oc_585f29d10679c7a0b5c3bf0d34adba90
- **目标项目目录**: E:\IdeaProjects\xp-ass-part

### 已开通权限
- im:chat
- im:chat:create
- im:chat:create_by_user
- contact:user.employee_id:readonly

## 自动化测试工具

### 1. test_bot_message.py - 完整自动化测试
**功能**: 发送消息 → 等待处理 → 验证回复

**使用方法**:
```bash
python test_bot_message.py
```

**测试流程**:
1. 发送测试消息到指定chat_id
2. 等待10秒让机器人处理
3. 获取聊天历史
4. 检查是否有机器人回复（sender_type == "app"）
5. 输出测试结果

**关键代码**:
```python
CHAT_ID = "oc_585f29d10679c7a0b5c3bf0d34adba90"
TEST_MESSAGE = "自动化测试：请回复这条消息"
test_bot_response(CHAT_ID, TEST_MESSAGE, wait_seconds=10)
```

### 2. send_test_message.py - 快速发送消息
**功能**: 向机器人发送单条测试消息

**使用方法**:
```bash
python send_test_message.py <chat_id> "消息内容"
```

**示例**:
```bash
python send_test_message.py oc_585f29d10679c7a0b5c3bf0d34adba90 "测试消息"
```

### 3. check_chat_history.py - 查看聊天记录
**功能**: 获取最近10条消息，验证机器人响应

**使用方法**:
```bash
python check_chat_history.py
```

**输出格式**:
```
1. [user] 用户消息内容
2. [app] 机器人回复内容
```

### 4. bot_send_to_user.py - 获取chat_id
**功能**: 机器人主动发送消息给用户，用于获取chat_id

**使用方法**:
```bash
python bot_send_to_user.py
```

## 测试流程

### 完整测试流程
```bash
# 1. 启动机器人
python lark_bot.py

# 2. 运行自动化测试（在另一个终端）
python test_bot_message.py

# 3. 查看测试结果
# 测试脚本会自动输出：✅ 测试通过 或 ❌ 测试失败
```

### 快速验证流程
```bash
# 1. 发送测试消息
python send_test_message.py oc_585f29d10679c7a0b5c3bf0d34adba90 "测试"

# 2. 等待几秒

# 3. 查看聊天历史
python check_chat_history.py
```

## 测试验证点

### 基础功能测试
- [ ] 机器人能接收消息
- [ ] 机器人能回复消息
- [ ] 消息去重正常工作
- [ ] 消息内容正确解析

### Claude Code CLI集成测试
- [ ] Claude命令能正常执行
- [ ] 能正确传递用户输入
- [ ] 能捕获Claude输出
- [ ] 错误处理正常

### AI API层测试（待实现）
- [ ] 命令解析器工作正常
- [ ] 智能路由器正确分发
- [ ] API执行器正常调用
- [ ] CLI执行器正常调用

## 常见问题排查

### 问题1: 机器人没有回复
**排查步骤**:
1. 检查机器人是否在运行：`python lark_bot.py`
2. 查看机器人日志输出
3. 检查WebSocket连接状态
4. 验证权限配置

### 问题2: Claude命令执行失败
**排查步骤**:
1. 检查Claude CLI是否安装：`claude.cmd --version`
2. 验证目标目录是否存在
3. 检查命令格式是否正确（使用stdin而非-p参数）
4. 查看错误日志

### 问题3: 获取不到chat_id
**解决方案**:
```bash
# 方法1: 使用bot_send_to_user.py
python bot_send_to_user.py

# 方法2: 手动发消息后查看日志
# 在飞书客户端给机器人发消息，然后在lark_bot.py日志中查看chat_id
```

## 测试数据结构

### 消息发送请求
```python
{
    "receive_id": "oc_585f29d10679c7a0b5c3bf0d34adba90",
    "msg_type": "text",
    "content": '{"text": "消息内容"}'
}
```

### 消息接收事件
```python
{
    "message_id": "om_xxx",
    "chat_id": "oc_xxx",
    "chat_type": "p2p",
    "message_type": "text",
    "content": '{"text": "消息内容"}'
}
```

### 聊天历史响应
```python
{
    "items": [
        {
            "message_id": "om_xxx",
            "sender": {"sender_type": "user" | "app"},
            "msg_type": "text",
            "body": {"content": '{"text": "消息内容"}'}
        }
    ]
}
```

## 性能测试

### 响应时间测试
```python
import time

start = time.time()
send_message_to_chat(chat_id, "测试消息")
time.sleep(5)  # 等待处理
history = get_chat_history(chat_id)
end = time.time()

print(f"总响应时间: {end - start}秒")
```

### 并发测试
```python
import concurrent.futures

def send_test(i):
    return send_message_to_chat(chat_id, f"并发测试{i}")

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_test, i) for i in range(10)]
    results = [f.result() for f in futures]
```

## 集成到CI/CD

### GitHub Actions示例
```yaml
name: Feishu Bot Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install lark-oapi certifi
      - name: Run tests
        run: |
          python test_bot_message.py
```

## 重要提醒

1. **chat_id是关键**: 所有测试都需要正确的chat_id
2. **机器人必须运行**: 测试前确保lark_bot.py在运行
3. **等待时间**: 给机器人足够的处理时间（建议10秒）
4. **权限检查**: 确保所有必需权限已开通
5. **环境变量**: 使用certifi处理SSL证书

## 下一步测试计划

1. **单元测试**: 使用pytest测试各个组件
2. **属性测试**: 使用Hypothesis测试47个correctness properties
3. **集成测试**: 测试完整的消息流程
4. **性能测试**: 测试响应时间和并发处理
5. **错误测试**: 测试各种异常情况的处理
