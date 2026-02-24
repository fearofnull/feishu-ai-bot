# 飞书AI机器人集成测试 - 快速开始

## 🚀 5分钟快速测试

### 第1步：确认配置

检查 `.env` 文件是否包含以下配置：

```bash
# 必需配置
FEISHU_APP_ID=cli_a9f47e209db8dcc5
FEISHU_APP_SECRET=nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT
FEISHU_CHAT_ID=oc_585f29d10679c7a0b5c3bf0d34adba90

# AI API密钥（至少配置一个）
CLAUDE_API_KEY=your_key_here
# 或
GEMINI_API_KEY=your_key_here
# 或
OPENAI_API_KEY=your_key_here
```

### 第2步：启动机器人

在一个终端运行：

```bash
python lark_bot.py
```

看到以下输出表示启动成功：
```
✅ Configuration loaded successfully
✅ FeishuBot initialized successfully
✅ Scheduler started
Starting FeishuBot...
```

### 第3步：运行集成测试

在另一个终端运行：

```bash
python run_integration_test.py
```

或者直接运行自动化测试：

```bash
python test_bot_message.py
```

### 第4步：查看结果

如果测试通过，你会看到：

```
============================================================
✅ 测试通过：机器人成功接收并回复了消息
============================================================
```

## 📋 测试内容

集成测试会验证以下功能：

### ✅ 基础功能
- 机器人接收飞书消息
- 机器人解析消息内容
- 机器人调用AI处理
- 机器人回复消息

### ✅ AI集成
- Claude API 调用
- Gemini API 调用
- OpenAI API 调用
- 智能路由选择

### ✅ 会话管理
- 连续对话上下文
- 会话命令处理
- 会话持久化

## 🔍 测试不同场景

### 测试API层（快速响应）

```bash
# 在飞书中发送消息
@claude 什么是Python？
@gemini 什么是JavaScript？
@openai 什么是机器学习？
```

### 测试CLI层（代码能力）

```bash
# 在飞书中发送消息
@code 查看项目结构
@gemini-cli 分析代码库
```

### 测试智能路由

```bash
# 一般问答 → 自动使用API层
什么是人工智能？

# 代码相关 → 自动使用CLI层
查看代码库中的文件
分析项目结构
```

### 测试会话管理

```bash
# 连续对话
我叫张三
我叫什么名字？

# 会话命令
/session    # 查看会话信息
/history    # 查看对话历史
/new        # 创建新会话
```

## 🛠️ 故障排查

### 问题：机器人没有回复

**解决方案**：

1. 检查机器人是否在运行
   ```bash
   # Windows
   tasklist | findstr python
   
   # Linux/Mac
   ps aux | grep lark_bot.py
   ```

2. 检查配置
   ```bash
   python config.py
   ```

3. 查看机器人日志
   - 检查终端输出
   - 查找错误信息

### 问题：API调用失败

**解决方案**：

1. 检查API密钥是否正确
   ```bash
   # 在 .env 中确认
   CLAUDE_API_KEY=sk-ant-...
   ```

2. 检查网络连接
   - 确保能访问AI服务

3. 查看错误消息
   - 机器人会回复具体错误

### 问题：CLI层不工作

**解决方案**：

1. 检查CLI工具是否安装
   ```bash
   claude.cmd --version
   gemini --version
   ```

2. 检查目标目录配置
   ```bash
   # 在 .env 中确认
   TARGET_PROJECT_DIR=E:\IdeaProjects\your-project
   ```

## 📚 更多信息

- 详细测试指南：[INTEGRATION_TESTING_GUIDE.md](INTEGRATION_TESTING_GUIDE.md)
- 项目文档：[.kiro/specs/feishu-ai-bot/](. kiro/specs/feishu-ai-bot/)
- 测试脚本说明：[.kiro/specs/feishu-ai-bot/testing-guide.md](.kiro/specs/feishu-ai-bot/testing-guide.md)

## ✨ 下一步

完成集成测试后，你可以：

1. **运行单元测试**
   ```bash
   pytest tests/
   ```

2. **运行属性测试**
   ```bash
   pytest tests/ -k property
   ```

3. **部署到生产环境**
   - 配置生产环境变量
   - 使用进程管理工具（systemd/supervisor）
   - 配置日志和监控

## 🎯 测试检查清单

- [ ] 机器人能接收消息
- [ ] 机器人能回复消息
- [ ] Claude API 正常工作
- [ ] Gemini API 正常工作
- [ ] OpenAI API 正常工作
- [ ] 智能路由正常工作
- [ ] 会话管理正常工作
- [ ] 错误处理正常工作

---

**需要帮助？** 查看 [INTEGRATION_TESTING_GUIDE.md](INTEGRATION_TESTING_GUIDE.md) 获取详细说明。
