# 飞书机器人测试指南

## 测试方式

### 方式 1：手动测试（最简单）

1. 确保机器人程序正在运行：
   ```bash
   python lark_bot.py
   ```

2. 在飞书客户端中：
   - 搜索你的机器人（使用机器人名称）
   - 给机器人发送一条消息，例如："你好"
   - 观察机器人是否回复

### 方式 2：使用测试脚本（自动化）

由于飞书 API 的限制（open_id 不能跨应用使用），自动化测试需要以下步骤：

1. **先手动给机器人发一条消息**，建立单聊会话

2. **从机器人日志中获取 chat_id**：
   - 运行 `python lark_bot.py`
   - 给机器人发消息
   - 在日志中找到类似这样的输出：`chat_id: oc_xxxxx`

3. **修改测试脚本**：
   ```python
   # 在 test_bot_message.py 中修改
   CHAT_ID = "oc_xxxxx"  # 替换为你的 chat_id
   ```

4. **运行测试**：
   ```bash
   python test_bot_message.py
   ```

### 方式 3：集成测试（推荐用于 CI/CD）

创建一个测试用户账号，使用该账号的凭证进行自动化测试：

```python
# tests/integration/test_bot_integration.py
import pytest
from lark_oapi import Client
from lark_oapi.api.im.v1 import *

@pytest.fixture
def test_client():
    """测试客户端（使用测试用户凭证）"""
    return Client.builder()\\
        .app_id("test_app_id")\\
        .app_secret("test_app_secret")\\
        .build()

def test_bot_receives_message(test_client):
    """测试机器人接收消息"""
    # 发送测试消息
    # 等待机器人回复
    # 验证回复内容
    pass
```

## 当前测试脚本功能

`test_bot_message.py` 提供以下功能：

1. **发送测试消息**：向指定 chat_id 发送消息
2. **等待机器人回复**：等待指定时间（默认 10 秒）
3. **获取聊天历史**：检查机器人是否回复
4. **输出测试结果**：显示详细的测试过程和结果

## 测试检查项

测试时需要验证：

- ✅ 机器人能接收到消息
- ✅ 消息去重功能正常（重复消息不会被处理两次）
- ✅ 引用消息功能正常
- ✅ Claude Code CLI 执行成功
- ✅ 机器人能正确回复消息
- ✅ 错误处理正常（目录不存在、Claude 命令失败等）

## 常见问题

### Q: 为什么不能直接用 open_id 发消息？
A: 飞书的 open_id 是应用级别的，不能跨应用使用。测试脚本使用的是机器人自己的凭证，所以需要使用 chat_id。

### Q: 如何获取 chat_id？
A: 
1. 手动给机器人发一条消息
2. 在机器人日志中查看
3. 或者使用飞书 API Explorer 查询

### Q: 测试脚本报错 "Bot/User can NOT be out of the chat"
A: 这个 chat_id 已经失效，需要重新获取。先手动给机器人发消息建立新的会话。

### Q: 如何进行完整的自动化测试？
A: 建议使用以下方案：
1. 创建测试专用的飞书应用
2. 使用测试应用的凭证
3. 在 CI/CD 中运行集成测试
4. 使用 pytest + Hypothesis 进行属性测试
