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

2. 编辑 `.env` 文件，填入你的配置。详细配置说明见 [配置文档](docs/CONFIGURATION.md)

3. 验证配置：

```bash
python config.py
```

### 运行机器人

```bash
python lark_bot.py
```

### 开始使用

在飞书群聊中 @机器人 并发送消息即可开始对话。详细使用方法见 [用户指南](docs/USER_GUIDE.md)

**快速示例**：
```
@机器人 @claude 你好，介绍一下自己

@机器人 @code 分析一下这个项目的架构

@机器人 /session
```

## 测试

项目包含两套测试体系，详见 `docs/TESTING_STRUCTURE.md`

### 自动化测试（tests/）

```bash
# 运行所有测试
pytest tests/

# 运行属性测试
pytest tests/ -k property

# 查看测试覆盖率
pytest tests/ --cov=feishu_bot
```

### 手动测试工具（test_scripts/）

```bash
# 运行集成测试
python test_scripts/run_integration_test.py

# 发送测试消息
python test_scripts/test_bot_message.py

# 查看聊天历史
python test_scripts/check_chat_history.py
```

### 测试文档
- `docs/TESTING_STRUCTURE.md` - 测试结构说明
- `docs/INTEGRATION_TESTING_GUIDE.md` - 集成测试指南
- `docs/INTEGRATION_TEST_RESULTS.md` - 最新测试结果

## 文档

- **用户指南**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - 如何使用机器人
- **配置指南**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - 详细配置说明
- **测试指南**: [docs/INTEGRATION_TESTING_GUIDE.md](docs/INTEGRATION_TESTING_GUIDE.md) - 集成测试
- **架构设计**: `.kiro/specs/feishu-ai-bot/design.md` - 系统架构
- **需求文档**: `.kiro/specs/feishu-ai-bot/requirements.md` - 功能需求
- **任务列表**: `.kiro/specs/feishu-ai-bot/tasks.md` - 开发任务

## 项目结构

```
.
├── lark_bot.py              # 主机器人程序
├── config.py                # 配置管理
├── requirements.txt         # Python依赖
├── README.md                # 项目说明
├── SECURITY.md              # 安全说明
├── .env                     # 环境变量（不提交到Git）
├── .env.example             # 环境变量模板
│
├── feishu_bot/              # 机器人核心代码
│   ├── config.py            # 配置类
│   ├── feishu_bot.py        # 主应用类
│   ├── message_handler.py   # 消息处理器
│   ├── command_parser.py    # 命令解析器
│   ├── smart_router.py      # 智能路由器
│   ├── session_manager.py   # 会话管理器
│   ├── *_executor.py        # 各种AI执行器
│   └── ...                  # 其他模块
│
├── tests/                   # 单元测试和属性测试
│   ├── test_*.py            # 测试文件
│   └── ...
│
├── test_scripts/            # 集成测试脚本
│   ├── run_integration_test.py
│   ├── test_bot_message.py
│   └── ...                  # 其他测试脚本
│
├── docs/                    # 项目文档
│   ├── INTEGRATION_TEST_RESULTS.md
│   ├── INTEGRATION_TESTING_GUIDE.md
│   ├── QUICK_START_INTEGRATION_TEST.md
│   └── ...                  # 其他文档
│
├── data/                    # 数据存储
│   ├── sessions/            # 会话数据
│   └── executor_sessions.json
│
└── .kiro/                   # Kiro配置和规格
    ├── specs/
    │   └── feishu-ai-bot/
    │       ├── requirements.md    # 需求文档
    │       ├── design.md          # 设计文档
    │       └── tasks.md           # 任务列表
    └── steering/
        └── feishu-bot-testing.md  # 测试配置
```

## 开发计划

当前进度：✅ 核心功能已完成并通过集成测试

### 已完成 ✅
- [x] 消息接收和回复
- [x] 消息去重机制
- [x] 命令解析器
- [x] 智能路由器
- [x] AI API层（Claude API、Gemini API、OpenAI API）
- [x] AI CLI层（Claude Code CLI、Gemini CLI）
- [x] 执行器注册表
- [x] 会话管理（上下文、历史记录）
- [x] 集成测试（10项测试全部通过）

### 进行中 🚧
- [ ] 单元测试完善
- [ ] 属性测试完善
- [ ] 性能优化

### 计划中 📋
- [ ] 更多AI提供商支持
- [ ] Web管理界面
- [ ] 监控和日志分析
- [ ] 生产环境部署

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
