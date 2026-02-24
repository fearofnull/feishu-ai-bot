# 飞书AI机器人集成测试指南

## 概述

本指南将帮助你通过发送飞书消息来测试机器人是否能正常调用AI并回复问题。

## 前提条件

### 1. 环境配置

确保 `.env` 文件已正确配置：

```bash
# 飞书机器人凭证（必需）
FEISHU_APP_ID=cli_a9f47e209db8dcc5
FEISHU_APP_SECRET=nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT

# 测试配置（必需）
FEISHU_CHAT_ID=oc_585f29d10679c7a0b5c3bf0d34adba90
FEISHU_USER_ID=155529283

# 目标项目目录（可选，CLI层需要）
TARGET_PROJECT_DIR=E:\IdeaProjects\xp-ass-part

# AI API密钥（至少配置一个）
CLAUDE_API_KEY=your_claude_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 安装依赖

```bash
pip install lark-oapi certifi python-dotenv
```

### 3. 验证配置

```bash
python config.py
```

应该看到：
```
✅ 已加载配置文件: .env
✅ 配置验证通过
```

## 集成测试方法

### 方法1: 自动化完整测试（推荐）

这是最简单的方法，会自动发送消息、等待回复、验证结果。

```bash
# 1. 启动机器人（在一个终端）
python lark_bot.py

# 2. 运行自动化测试（在另一个终端）
python test_bot_message.py
```

**测试流程**：
1. 发送测试消息到配置的chat_id
2. 等待10秒让机器人处理
3. 获取聊天历史
4. 检查是否有机器人回复（sender_type == "app"）
5. 输出测试结果

**预期输出**：
```
============================================================
开始测试机器人消息接收和回复功能
============================================================

[步骤 1] 发送测试消息: 自动化测试：请回复这条消息
✅ 消息发送成功
   - Message ID: om_xxxxx
   - Chat ID: oc_585f29d10679c7a0b5c3bf0d34adba90

[步骤 2] 等待 10 秒，让机器人处理消息...

[步骤 3] 获取聊天历史，检查机器人回复...
   - 获取到 5 条消息

   消息:
   - 发送者类型: user
   - 消息类型: text
   - 内容: 自动化测试：请回复这条消息

   消息:
   - 发送者类型: app
   - 消息类型: text
   - 内容: [AI的回复内容]

============================================================
✅ 测试通过：机器人成功接收并回复了消息
============================================================
```

### 方法2: 手动测试

#### 步骤1: 启动机器人

```bash
python lark_bot.py
```

你应该看到：
```
Loading configuration...
✅ Configuration loaded successfully
Initializing FeishuBot...
✅ FeishuBot initialized successfully
✅ Scheduler started
Starting FeishuBot...
```

#### 步骤2: 发送测试消息

```bash
# 使用配置文件中的chat_id
python send_test_message.py "你好，请介绍一下你自己"

# 或指定chat_id
python send_test_message.py oc_585f29d10679c7a0b5c3bf0d34adba90 "你好"
```

#### 步骤3: 查看聊天历史

```bash
python check_chat_history.py
```

你应该看到：
```
获取到 10 条最新消息：

1. [user] 你好，请介绍一下你自己

2. [app] 你好！我是飞书AI机器人...
```

### 方法3: 通过飞书客户端测试

1. 在飞书客户端中找到机器人
2. 发送消息："你好"
3. 等待机器人回复
4. 验证回复内容是否正确

## 测试不同的AI提供商

机器人支持多个AI提供商，你可以通过命令前缀指定：

### API层测试（快速响应）

```bash
# 测试Claude API
python send_test_message.py "@claude 什么是Python？"

# 测试Gemini API
python send_test_message.py "@gemini 什么是JavaScript？"

# 测试OpenAI API
python send_test_message.py "@openai 什么是机器学习？"
```

### CLI层测试（代码能力）

```bash
# 测试Claude Code CLI
python send_test_message.py "@code 查看项目结构"

# 测试Gemini CLI
python send_test_message.py "@gemini-cli 分析代码库"
```

### 智能路由测试（自动选择）

不指定前缀时，机器人会根据消息内容自动选择：

```bash
# 一般问答 → 自动使用API层
python send_test_message.py "什么是人工智能？"

# 代码相关 → 自动使用CLI层
python send_test_message.py "查看代码库中的文件"
python send_test_message.py "分析项目结构"
```

## 测试会话管理

### 测试连续对话

```bash
# 第一条消息
python send_test_message.py "我叫张三"

# 等待回复后，发送第二条
python send_test_message.py "我叫什么名字？"

# 机器人应该记住你的名字
```

### 测试会话命令

```bash
# 查看会话信息
python send_test_message.py "/session"

# 查看对话历史
python send_test_message.py "/history"

# 创建新会话
python send_test_message.py "/new"
```

## 故障排查

### 问题1: 机器人没有回复

**检查清单**：
1. ✅ 机器人是否在运行？
   ```bash
   # 检查进程
   ps aux | grep lark_bot.py
   ```

2. ✅ WebSocket连接是否正常？
   - 查看机器人日志，应该看到 "Starting FeishuBot..."
   - 没有错误信息

3. ✅ 配置是否正确？
   ```bash
   python config.py
   ```

4. ✅ AI API密钥是否配置？
   - 至少配置一个AI提供商的API密钥
   - 检查 `.env` 文件

### 问题2: 测试脚本报错

**常见错误**：

1. **配置加载失败**
   ```
   ❌ 配置加载失败: 缺少必需的配置项: FEISHU_APP_ID
   ```
   **解决**: 检查 `.env` 文件是否存在且配置正确

2. **SSL证书错误**
   ```
   SSL: CERTIFICATE_VERIFY_FAILED
   ```
   **解决**: 确保安装了 certifi
   ```bash
   pip install certifi
   ```

3. **权限错误**
   ```
   code: 99991663, msg: no permission
   ```
   **解决**: 检查机器人权限配置

### 问题3: 机器人回复错误

**检查AI配置**：

1. **API密钥错误**
   - 机器人会回复："AI 执行失败：API key not configured"
   - 解决：在 `.env` 中配置正确的API密钥

2. **CLI工具未安装**
   - 机器人会回复："Claude Code is not installed"
   - 解决：安装对应的CLI工具

3. **目标目录不存在**
   - 机器人会回复："Target directory not found"
   - 解决：检查 `TARGET_PROJECT_DIR` 配置

## 性能测试

### 测试响应时间

```python
import time
from test_bot_message import send_message_to_chat, get_chat_history

chat_id = "oc_585f29d10679c7a0b5c3bf0d34adba90"

# 记录开始时间
start = time.time()

# 发送消息
send_message_to_chat(chat_id, "测试响应时间")

# 等待回复
time.sleep(5)

# 获取历史
get_chat_history(chat_id)

# 计算总时间
end = time.time()
print(f"总响应时间: {end - start:.2f}秒")
```

### 并发测试

```python
import concurrent.futures
from test_bot_message import send_message_to_chat

chat_id = "oc_585f29d10679c7a0b5c3bf0d34adba90"

def send_test(i):
    return send_message_to_chat(chat_id, f"并发测试消息 {i}")

# 发送10条并发消息
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_test, i) for i in range(10)]
    results = [f.result() for f in futures]

print(f"成功发送: {sum(1 for r in results if r['success'])} 条")
```

## 测试检查清单

### 基础功能测试
- [ ] 机器人能接收消息
- [ ] 机器人能回复消息
- [ ] 消息去重正常工作
- [ ] 消息内容正确解析

### AI提供商测试
- [ ] Claude API 正常工作
- [ ] Gemini API 正常工作
- [ ] OpenAI API 正常工作
- [ ] Claude Code CLI 正常工作
- [ ] Gemini CLI 正常工作

### 智能路由测试
- [ ] 命令前缀正确识别
- [ ] CLI关键词自动检测
- [ ] 降级策略正常工作

### 会话管理测试
- [ ] 连续对话保持上下文
- [ ] /new 命令创建新会话
- [ ] /session 命令显示会话信息
- [ ] /history 命令显示对话历史
- [ ] 会话自动轮换（超过50条消息）
- [ ] 会话自动过期（24小时）

### 错误处理测试
- [ ] API密钥错误处理
- [ ] CLI工具未安装处理
- [ ] 目标目录不存在处理
- [ ] 网络错误处理
- [ ] 超时错误处理

## 下一步

完成集成测试后，你可以：

1. **运行单元测试**
   ```bash
   pytest tests/
   ```

2. **运行属性测试**
   ```bash
   pytest tests/ -k property
   ```

3. **查看测试覆盖率**
   ```bash
   pytest --cov=feishu_bot tests/
   ```

4. **部署到生产环境**
   - 配置生产环境的 `.env`
   - 使用 systemd 或 supervisor 管理进程
   - 配置日志轮转
   - 设置监控告警

## 参考文档

- [飞书开放平台](https://open.feishu.cn/)
- [Claude API文档](https://docs.anthropic.com/en/api/messages)
- [Gemini API文档](https://ai.google.dev/api/python/google/generativeai)
- [OpenAI API文档](https://platform.openai.com/docs/api-reference/chat)
- [测试指南](.kiro/specs/feishu-ai-bot/testing-guide.md)
