# 飞书AI机器人 (Feishu AI Bot)

一个智能的飞书机器人，集成了多个AI能力（Claude Code CLI、Gemini CLI等），支持通过API和CLI两种方式调用AI服务。

## 功能特性

- 🤖 **多AI支持**: 支持Claude、Gemini、OpenAI等多个AI服务
- 🔀 **智能路由**: 自动根据用户命令和消息内容选择最合适的AI服务
- 💬 **消息处理**: 接收和回复飞书消息，支持文本、引用等多种消息类型
- 🔄 **消息去重**: 使用deque实现高效的消息去重机制
- 🛠️ **代码操作**: 通过Claude Code CLI执行代码查看、修改等操作
- ⚡ **快速响应**: API层提供快速响应，CLI层提供深度代码操作

## 架构设计

```
用户消息 → 飞书平台 → 机器人 → 命令解析器 → 智能路由器
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                              AI API层              AI CLI层
                          (快速响应)            (代码操作)
                                    ↓                   ↓
                              执行器注册表
                                    ↓
                              返回结果 → 用户
```

详细架构设计见：`.kiro/specs/feishu-ai-bot/design.md`

## 快速开始

### 环境要求

- Python 3.8+
- 飞书机器人账号和凭证
- Claude Code CLI（可选）
- Gemini CLI（可选）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. 复制环境变量模板文件：

```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

2. 编辑 `.env` 文件，填入你的配置：

```bash
# 飞书机器人凭证（必需）
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here

# 测试配置（可选，用于自动化测试）
FEISHU_CHAT_ID=your_chat_id_here
FEISHU_USER_ID=your_user_id_here

# 目标项目目录（可选，用于Claude Code CLI）
TARGET_PROJECT_DIR=E:\IdeaProjects\your-project
```

3. 验证配置：

```bash
python config.py
```

### 运行机器人

```bash
python lark_bot.py
```

## 测试

### 自动化测试

```bash
# 完整自动化测试
python test_bot_message.py

# 发送单条测试消息
python send_test_message.py <chat_id> "测试消息"

# 查看聊天历史
python check_chat_history.py
```

详细测试指南见：`.kiro/specs/feishu-ai-bot/testing-guide.md`

## 项目结构

```
.
├── lark_bot.py              # 主机器人程序
├── test_bot_message.py      # 自动化测试工具
├── send_test_message.py     # 消息发送工具
├── check_chat_history.py    # 聊天历史查看工具
├── bot_send_to_user.py      # 获取chat_id工具
├── get_chat_id.py           # chat_id获取工具
├── README_TEST.md           # 测试文档
├── QUICK_TEST.md            # 快速测试指南
├── 测试总结.md              # 测试总结
└── .kiro/
    ├── specs/
    │   └── feishu-ai-bot/
    │       ├── requirements.md    # 需求文档
    │       ├── design.md          # 设计文档
    │       ├── tasks.md           # 任务列表
    │       └── testing-guide.md   # 测试指南
    └── steering/
        └── feishu-bot-testing.md  # 测试配置
```

## 开发计划

当前进度：基础功能已完成，AI API层待实现

- [x] 消息接收和回复
- [x] 消息去重机制
- [x] Claude Code CLI集成
- [x] 自动化测试工具
- [ ] 命令解析器
- [ ] 智能路由器
- [ ] AI API层（Claude API、Gemini API、OpenAI API）
- [ ] 执行器注册表
- [ ] 单元测试和属性测试

详细任务列表见：`.kiro/specs/feishu-ai-bot/tasks.md`

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 注意事项

⚠️ **重要**: 
- 请勿将机器人凭证（APP_ID、APP_SECRET）提交到公开仓库
- 建议使用环境变量或配置文件管理敏感信息
- 定期更新依赖包以确保安全性
