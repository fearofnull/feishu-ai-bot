# 飞书AI机器人 (Feishu AI Bot)

一个智能的飞书机器人，集成了多个AI能力（Claude、Gemini、OpenAI等），支持通过API和CLI两种方式调用AI服务，提供智能路由、会话管理和可扩展的架构。

## 功能特性

- 🤖 **多AI支持**: 支持Claude、Gemini、OpenAI等多个AI服务
- 🔀 **智能路由**: 自动根据用户命令和消息内容选择最合适的AI服务（API层或CLI层）
- 💬 **消息处理**: 接收和回复飞书消息，支持文本、引用等多种消息类型
- 🔄 **消息去重**: 使用deque实现高效的消息去重机制
- 🛠️ **代码操作**: 通过Claude Code CLI和Gemini CLI执行代码查看、修改等操作
- ⚡ **快速响应**: API层提供快速响应，CLI层提供深度代码操作
- 💾 **会话管理**: 支持上下文连续对话，自动管理会话历史和轮换
- 🔌 **可扩展架构**: 轻松添加新的AI Agent和命令前缀
- 🔒 **安全保护**: 敏感信息保护，会话数据本地存储
- 🧪 **完整测试**: 包含单元测试、属性测试和集成测试

## 架构设计

系统采用分层架构，核心是智能路由器，根据用户指令和消息内容选择API层或CLI层：

```
用户消息 → 飞书平台 → 机器人 → 命令解析器 → 智能路由器
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                              AI API层              AI CLI层
                          (快速响应)            (代码操作)
                            ↓                       ↓
                    Claude API              Claude Code CLI
                    Gemini API              Gemini CLI
                    OpenAI API
                                    ↓
                              执行器注册表
                                    ↓
                              返回结果 → 用户
```

### 智能路由功能

系统提供两种路由方式。**详细说明请参考：[智能路由详解](docs/SMART_ROUTING_EXPLAINED.md)**

#### 1. 显式指定（推荐用于明确需求）

使用命令前缀明确指定AI服务和执行层：

**API层前缀**：
- `@claude` 或 `@claude-api` → Claude API
- `@gemini` 或 `@gemini-api` → Gemini API
- `@openai` 或 `@gpt` → OpenAI API

**CLI层前缀**：
- `@code` 或 `@claude-cli` → Claude Code CLI
- `@gemini-cli` → Gemini CLI

示例：
```
@机器人 @claude 解释量子计算        # 使用Claude API
@机器人 @code 分析项目架构          # 使用Claude Code CLI
```

#### 2. 智能判断（自动选择最佳方式）

当用户未指定前缀时，系统会根据消息内容自动选择：

**会话命令优先**（不经过AI）：
- `/help` 或 `帮助` → 显示帮助信息
- `/new` 或 `新会话` → 创建新会话
- `/session` 或 `会话信息` → 查看会话信息
- `/history` 或 `历史记录` → 查看对话历史

**自动选择CLI层**（检测到以下关键词）：
- 代码相关：`查看代码`、`view code`、`分析代码`、`analyze code`
- 文件操作：`修改文件`、`modify file`、`读取文件`、`read file`
- 命令执行：`执行命令`、`execute command`、`运行脚本`、`run script`
- 项目分析：`分析项目`、`analyze project`、`项目结构`、`project structure`
- 代码库：`代码库`、`codebase`

**自动选择API层**（默认）：
- 一般问答（如"你是谁"）
- 概念解释（如"什么是Python装饰器"）
- 代码生成（不需要查看现有代码）
- 翻译、写作等不需要访问代码库的任务

**降级策略**（自动容错）：
- 当指定的AI服务不可用时（如API密钥未配置），系统会自动降级到其他可用服务
- 降级顺序：同provider另一层 → 其他provider同一层 → 其他provider另一层
- 示例：claude/api不可用 → 尝试claude/cli → 尝试openai/api → 尝试gemini/api
- 详细说明见：[智能路由详解 - 降级策略](docs/SMART_ROUTING_EXPLAINED.md#降级策略fallback)

### AI API层 vs AI CLI层

| 特性 | AI API层 | AI CLI层 |
|------|---------|---------|
| **响应速度** | 快速（秒级） | 较慢（需要启动CLI工具） |
| **成本** | 较低（按token计费） | 较高（CLI工具可能有额外开销） |
| **代码访问** | 无法访问本地代码 | 可以访问和操作本地代码 |
| **适用场景** | 一般问答、概念解释、翻译、写作 | 代码分析、文件操作、项目查看 |
| **上下文管理** | 手动传递对话历史 | 使用原生会话管理 |
| **支持的AI** | Claude API、Gemini API、OpenAI API | Claude Code CLI、Gemini CLI |

**选择建议**：
- 简单问答、概念解释 → 使用API层（`@claude`、`@gemini`、`@openai`）
- 代码分析、文件操作 → 使用CLI层（`@code`、`@gemini-cli`）
- 不确定时 → 让系统智能判断（不使用前缀）

### 会话管理

系统采用双层会话管理架构：

#### 1. 飞书机器人会话层

**功能**：
- 管理用户与机器人的交互历史
- 提供会话信息查询和历史记录查看
- 支持会话轮换和过期管理

**会话命令**：
- `/help` 或 `帮助`：查看所有可用命令和使用说明
- `/session` 或 `会话信息`：查看当前会话ID、消息数、创建时间
- `/history` 或 `历史记录`：查看对话历史
- `/new` 或 `新会话`：开启新会话（清除历史）

**自动管理**：
- 单个会话最大消息数：50条（可配置）
- 会话超时时间：24小时（可配置）
- 超过限制后自动创建新会话

#### 2. AI CLI原生会话层

**功能**：
- 利用AI CLI工具的原生会话管理能力
- 让AI自己维护上下文，无需手动传递历史
- 提高效率和上下文理解质量

**支持的CLI**：
- Claude Code CLI：使用`--session`参数
- Gemini CLI：使用`--session`参数

**会话映射**：
- 系统为每个飞书用户维护一个AI CLI会话ID
- 会话映射持久化存储，重启后自动恢复
- 使用`/new`命令时同时清除两层会话

#### 会话管理架构说明

**API层对话历史**：
- 对于API层（Claude API、Gemini API、OpenAI API），系统会将飞书机器人会话中的对话历史格式化后传递给API
- 每次API调用都包含完整的对话历史，确保上下文连续性

**CLI层原生会话**：
- 对于CLI层（Claude Code CLI、Gemini CLI），系统使用AI工具的原生会话管理
- 飞书机器人会话仅用于显示历史记录和会话信息
- AI CLI会话用于实际的AI上下文管理，由AI工具自动维护

**优势**：
- 对于API层：完全控制对话历史，灵活管理上下文
- 对于CLI层：利用AI原生能力，获得更好的上下文理解
- 统一的会话管理接口，用户体验一致

详细架构设计见项目文档

## 快速开始

有两种部署方式可选：

### 方式1：Docker 部署（推荐，适合生产环境）

#### 环境要求
- Docker 20.10+
- Docker Compose 2.0+（可选）
- 至少 1GB 内存

#### 部署步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd feishu-ai-bot
```

2. **配置环境变量**
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

填入必需配置：
- `FEISHU_APP_ID`: 飞书应用ID
- `FEISHU_APP_SECRET`: 飞书应用密钥
- 至少一个AI API密钥

3. **启动服务**

使用 Docker Compose（推荐）：
```bash
docker-compose up -d
```

或使用部署脚本：
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh start
```

或使用 Docker 命令：
```bash
docker build -t feishu-ai-bot .
docker run -d \
  --name feishu-ai-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  feishu-ai-bot
```

4. **查看日志**
```bash
# 使用 Docker Compose
docker-compose logs -f

# 使用部署脚本
./scripts/deploy.sh logs

# 使用 Docker 命令
docker logs -f feishu-ai-bot
```

5. **管理服务**
```bash
# 停止服务
./scripts/deploy.sh stop

# 重启服务
./scripts/deploy.sh restart

# 查看状态
./scripts/deploy.sh status

# 更新服务
./scripts/deploy.sh update
```

详细部署文档见 [部署指南](docs/deployment/DEPLOYMENT.md)。

### 方式2：本地运行（适合开发测试）

#### 环境要求

- Python 3.8+
- 飞书机器人账号和凭证
- 至少一个AI服务的API密钥（Claude API、Gemini API或OpenAI API）
- Claude Code CLI（可选，用于代码操作）
- Gemini CLI（可选，用于代码操作）

#### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd feishu-ai-bot
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**

复制环境变量模板文件：
```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

编辑 `.env` 文件，填入你的配置：

**必需配置**：
- `FEISHU_APP_ID`: 飞书应用ID（在[飞书开放平台](https://open.feishu.cn/)获取）
- `FEISHU_APP_SECRET`: 飞书应用密钥

**AI服务配置**（至少配置一个）：
- `CLAUDE_API_KEY`: Claude API密钥（[获取地址](https://console.anthropic.com/)）
- `GEMINI_API_KEY`: Gemini API密钥（[获取地址](https://aistudio.google.com/app/apikey)）
- `OPENAI_API_KEY`: OpenAI API密钥（[获取地址](https://platform.openai.com/api-keys)）

**CLI工具配置**（可选，用于代码操作）：
- `TARGET_PROJECT_DIR`: 目标项目目录路径
- 安装[Claude Code CLI](https://code.claude.com/docs/)或[Gemini CLI](https://geminicli.com/docs/)

**会话管理配置**（可选）：
- `SESSION_STORAGE_PATH`: 会话存储路径（默认：`./data/sessions.json`）
- `MAX_SESSION_MESSAGES`: 单个会话最大消息数（默认：50）
- `SESSION_TIMEOUT`: 会话超时时间（默认：86400秒，24小时）

**默认设置**（可选）：
- `DEFAULT_PROVIDER`: 默认AI提供商（可选值：`claude`、`gemini`、`openai`，默认：`claude`）
  - 主要用于API层的默认提供商
- `DEFAULT_LAYER`: 默认执行层（可选值：`api`、`cli`，默认：`api`）
- `DEFAULT_CLI_PROVIDER`: CLI层专用默认提供商（可选，默认使用`DEFAULT_PROVIDER`）
  - 当AI判断需要CLI层时，使用此提供商
  - 适用场景：API层和CLI层想使用不同的提供商
  - 示例：`DEFAULT_PROVIDER=openai`（API层用OpenAI），`DEFAULT_CLI_PROVIDER=gemini`（CLI层用Gemini）

**智能路由配置**（可选）：
- `USE_AI_INTENT_CLASSIFICATION`: 是否使用AI进行意图分类（可选值：`true`、`false`，默认：`true`）
  - 启用后使用AI判断用户意图，比关键词检测更准确
  - 详细说明见 [AI意图分类文档](docs/AI_INTENT_CLASSIFICATION.md)

**语言配置**（可选）：
- `RESPONSE_LANGUAGE`: AI回复语言（默认：空，由AI自动判断）
  - 支持的语言代码：
    - `zh-CN`: 中文（简体）
    - `zh-TW`: 中文（繁體）
    - `en-US`: English
    - `ja-JP`: 日本語
    - `ko-KR`: 한국어
    - `fr-FR`: Français
    - `de-DE`: Deutsch
    - `es-ES`: Español
  - 设置后，AI会被要求使用指定语言回复
  - 留空则由AI根据用户输入自动判断使用什么语言

详细配置说明见 [配置文档](docs/CONFIGURATION.md) 或 `.env.example` 文件。

4. **验证配置**
```bash
python scripts/verify_config.py
```

#### 运行机器人

```bash
python lark_bot.py
```

### 使用示例

在飞书群聊中 @机器人 并发送消息即可开始对话。

#### 基本对话
```
@机器人 你好，介绍一下自己
@机器人 什么是Python装饰器？
```

#### 使用命令前缀指定AI服务

**API层（快速响应）**：
```
@机器人 @claude 解释一下量子计算
@机器人 @gemini 翻译这段文字
@机器人 @openai 写一首诗
```

**CLI层（代码操作）**：
```
@机器人 @code 分析这个项目的架构
@机器人 @claude-cli 查看src/main.py文件
@机器人 @gemini-cli 修改README.md文件
```

#### 会话管理命令
```
@机器人 /help           # 查看所有可用命令
@机器人 /session        # 查看当前会话信息
@机器人 /history        # 查看对话历史
@机器人 /new            # 开启新会话
```

#### 智能路由（自动选择）

系统会根据消息内容自动选择合适的执行方式：

**自动使用CLI层**（包含代码相关关键词）：
```
@机器人 查看代码库的结构
@机器人 分析项目中的错误
@机器人 修改配置文件
```

**自动使用API层**（一般问答）：
```
@机器人 解释一下这个概念
@机器人 帮我写一段代码
@机器人 翻译这段文字
```

详细使用方法见 [用户指南](docs/USER_GUIDE.md)

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

## 可扩展性

系统采用插件式架构，支持轻松添加新的AI Agent和命令前缀。

### 如何添加新的AI Agent

#### 1. 添加API执行器

创建新的API执行器类，继承`AIAPIExecutor`：

```python
# feishu_bot/qwen_api_executor.py
from feishu_bot.ai_api_executor import AIAPIExecutor
from feishu_bot.models import ExecutionResult

class QwenAPIExecutor(AIAPIExecutor):
    def __init__(self, api_key: str, model: str = "qwen-plus", timeout: int = 60):
        super().__init__(api_key, model, timeout)
        # 初始化Qwen API客户端
        
    def get_provider_name(self) -> str:
        return "qwen-api"
    
    def format_messages(self, user_prompt: str, conversation_history=None):
        # 格式化为Qwen API消息格式
        pass
    
    def execute(self, user_prompt: str, conversation_history=None, additional_params=None) -> ExecutionResult:
        # 调用Qwen API
        pass
```

#### 2. 添加CLI执行器

创建新的CLI执行器类，继承`AICLIExecutor`：

```python
# feishu_bot/qwen_cli_executor.py
from feishu_bot.ai_cli_executor import AICLIExecutor
from feishu_bot.models import ExecutionResult

class QwenCodeCLIExecutor(AICLIExecutor):
    def __init__(self, target_dir: str, timeout: int = 600):
        super().__init__(target_dir, timeout)
        
    def get_command_name(self) -> str:
        return "qwen-code"  # CLI命令名称
    
    def build_command_args(self, user_prompt: str, additional_params=None):
        # 构建Qwen Code CLI命令参数
        args = [self.get_command_name()]
        args.extend(["--cwd", self.target_dir])
        args.extend(["--prompt", user_prompt])
        return args
    
    def verify_directory(self) -> bool:
        # 验证目标目录
        return os.path.exists(self.target_dir)
    
    def execute(self, user_prompt: str, additional_params=None) -> ExecutionResult:
        # 执行Qwen Code CLI命令
        pass
```

#### 3. 注册到执行器注册表

在`lark_bot.py`或配置文件中注册新的执行器：

```python
from feishu_bot.executor_registry import ExecutorRegistry, ExecutorMetadata
from feishu_bot.qwen_api_executor import QwenAPIExecutor
from feishu_bot.qwen_cli_executor import QwenCodeCLIExecutor

# 创建执行器注册表
registry = ExecutorRegistry()

# 注册Qwen API执行器
if config.qwen_api_key:
    qwen_api = QwenAPIExecutor(
        api_key=config.qwen_api_key,
        model="qwen-plus"
    )
    qwen_api_metadata = ExecutorMetadata(
        name="Qwen API",
        provider="qwen",
        layer="api",
        version="1.0.0",
        description="Qwen AI API for general Q&A",
        capabilities=["general_qa", "translation", "writing"],
        command_prefixes=["@qwen", "@qwen-api"],
        priority=3,
        config_required=["qwen_api_key"]
    )
    registry.register_api_executor("qwen", qwen_api, qwen_api_metadata)

# 注册Qwen CLI执行器
if config.target_directory:
    qwen_cli = QwenCodeCLIExecutor(
        target_dir=config.target_directory,
        timeout=config.ai_timeout
    )
    qwen_cli_metadata = ExecutorMetadata(
        name="Qwen Code CLI",
        provider="qwen",
        layer="cli",
        version="1.0.0",
        description="Qwen Code CLI for code analysis",
        capabilities=["code_analysis", "file_operations"],
        command_prefixes=["@qwen-code", "@qwen-cli"],
        priority=3,
        config_required=["target_directory"]
    )
    registry.register_cli_executor("qwen", qwen_cli, qwen_cli_metadata)
```

### 如何添加新的命令前缀

在`feishu_bot/command_parser.py`中添加新的前缀映射：

```python
class CommandParser:
    def __init__(self):
        self.prefix_map = {
            # 现有前缀
            "@claude": ("claude", "api"),
            "@claude-api": ("claude", "api"),
            "@claude-cli": ("claude", "cli"),
            "@code": ("claude", "cli"),
            "@gemini": ("gemini", "api"),
            "@gemini-api": ("gemini", "api"),
            "@gemini-cli": ("gemini", "cli"),
            "@openai": ("openai", "api"),
            "@gpt": ("openai", "api"),
            
            # 新增Qwen前缀
            "@qwen": ("qwen", "api"),
            "@qwen-api": ("qwen", "api"),
            "@qwen-code": ("qwen", "cli"),
            "@qwen-cli": ("qwen", "cli"),
        }
```

### 集成示例：Qwen Code

完整的Qwen Code集成示例：

1. **安装Qwen Code CLI**（假设存在）
```bash
pip install qwen-code-cli
```

2. **配置环境变量**（`.env`）
```bash
# Qwen API配置
QWEN_API_KEY=your_qwen_api_key_here

# Qwen Code CLI配置
TARGET_PROJECT_DIR=/path/to/your/project
```

3. **创建执行器**（参考上面的代码示例）

4. **使用新的AI Agent**
```
@机器人 @qwen 解释一下机器学习
@机器人 @qwen-code 分析这个项目的代码质量
```

### 扩展点总结

系统提供以下扩展点：

1. **AI API执行器**：实现`AIAPIExecutor`接口
2. **AI CLI执行器**：实现`AICLIExecutor`接口
3. **命令前缀**：在`CommandParser`中添加映射
4. **执行器元数据**：定义能力、优先级、配置要求
5. **配置管理**：在`BotConfig`中添加新的配置项

**未来扩展方向**：
- 支持更多AI提供商：Cohere、Mistral、Anthropic等
- 支持更多CLI工具：Cursor AI、Codeium、Tabnine等
- 支持混合执行：同时调用多个Agent并合并结果
- 支持Agent链：一个Agent的输出作为另一个Agent的输入

## 文档

- **用户指南**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - 如何使用机器人
- **配置指南**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - 详细配置说明
- **测试指南**: [docs/INTEGRATION_TESTING_GUIDE.md](docs/INTEGRATION_TESTING_GUIDE.md) - 集成测试
- **快速测试**: [docs/QUICK_START_INTEGRATION_TEST.md](docs/QUICK_START_INTEGRATION_TEST.md) - 5分钟快速测试
- **测试结构**: [docs/TESTING_STRUCTURE.md](docs/TESTING_STRUCTURE.md) - 测试体系说明
- **文档目录**: [docs/README.md](docs/README.md) - 所有文档索引

## 参考文档

### AI API文档
- **Claude API**: https://docs.anthropic.com/en/api/messages
- **Gemini API**: https://ai.google.dev/api/python/google/generativeai
- **OpenAI API**: https://platform.openai.com/docs/api-reference/chat

### AI CLI文档
- **Claude Code CLI**: 
  - 中文文档：https://code.claude.com/docs/zh-CN/cli-reference
  - 英文文档：https://code.claude.com/docs/
- **Gemini CLI**:
  - 会话管理：https://geminicli.com/docs/cli/session-management/
  - Headless模式：https://geminicli.com/docs/cli/headless/

### 飞书开放平台
- **飞书API Explorer**: https://open.feishu.cn/api-explorer
- **飞书Python SDK**: https://open.feishu.cn/document/server-side-sdk/python--sdk

## 故障排查指南

### 常见问题

#### 1. 机器人无法启动

**问题**：运行`python lark_bot.py`时报错

**可能原因**：
- 缺少必需的环境变量
- Python依赖未安装
- 飞书应用凭证无效

**解决方法**：
```bash
# 1. 检查环境变量
python config.py

# 2. 重新安装依赖
pip install -r requirements.txt --upgrade

# 3. 验证飞书凭证
# 登录飞书开放平台检查APP_ID和APP_SECRET是否正确
```

#### 2. 机器人收不到消息

**问题**：在飞书中@机器人，但没有响应

**可能原因**：
- WebSocket连接未建立
- 机器人未添加到群聊
- 事件订阅未配置

**解决方法**：
```bash
# 1. 检查日志中的WebSocket连接状态
# 查看是否有"WebSocket connected"日志

# 2. 确认机器人已添加到群聊
# 在飞书群聊中查看成员列表

# 3. 检查飞书开放平台的事件订阅配置
# 确保订阅了"接收消息"事件（im.message.receive_v1）
```

#### 3. AI执行失败

**问题**：机器人返回"执行失败"错误

**可能原因**：
- API密钥无效或过期
- CLI工具未安装
- 目标目录不存在
- 网络连接问题

**解决方法**：
```bash
# 1. 验证API密钥
# 检查.env文件中的API密钥是否正确

# 2. 检查CLI工具安装
claude --version  # 检查Claude Code CLI
gemini --version  # 检查Gemini CLI

# 3. 验证目标目录
# 确保TARGET_PROJECT_DIR指向的目录存在

# 4. 测试网络连接
curl https://api.anthropic.com/v1/messages  # 测试Claude API
curl https://generativelanguage.googleapis.com  # 测试Gemini API
```

#### 4. 会话管理问题

**问题**：会话历史丢失或会话无法创建

**可能原因**：
- 会话存储文件损坏
- 磁盘空间不足
- 文件权限问题

**解决方法**：
```bash
# 1. 检查会话存储文件
ls -la data/sessions.json

# 2. 检查磁盘空间
df -h

# 3. 修复文件权限
chmod 644 data/sessions.json

# 4. 备份并重置会话
cp data/sessions.json data/sessions.json.backup
echo '{"sessions": {}}' > data/sessions.json
```

#### 5. 智能路由不工作

**问题**：系统没有正确选择API层或CLI层

**可能原因**：
- 命令前缀拼写错误
- CLI关键词检测失败
- 执行器不可用

**解决方法**：
```bash
# 1. 检查命令前缀
# 确保使用正确的前缀：@claude, @code, @gemini等

# 2. 查看日志中的路由决策
# 日志会显示"Routing to API layer"或"Routing to CLI layer"

# 3. 检查执行器可用性
# 日志会显示哪些执行器已注册和可用

# 4. 尝试显式指定执行层
@机器人 @claude-api 测试API层
@机器人 @claude-cli 测试CLI层
```

### 日志调试

启用DEBUG日志以获取更详细的信息：

```bash
# 在.env文件中设置
LOG_LEVEL=DEBUG

# 或在命令行中设置
export LOG_LEVEL=DEBUG  # Linux/Mac
set LOG_LEVEL=DEBUG     # Windows

python lark_bot.py
```

DEBUG日志会显示：
- WebSocket连接状态
- 消息解析详情
- 命令路由决策
- API请求和响应
- CLI命令执行详情

### 性能优化

如果遇到性能问题：

1. **减少会话历史长度**
```bash
# 在.env中设置
MAX_SESSION_MESSAGES=20  # 默认50
```

2. **调整超时时间**
```bash
# 在.env中设置
AI_TIMEOUT=300  # 默认600秒
```

3. **使用API层而非CLI层**
```bash
# API层响应更快
@机器人 @claude 你的问题
```

4. **定期清理会话**
```bash
# 手动清理过期会话
python -c "from feishu_bot.session_manager import SessionManager; sm = SessionManager(); sm.cleanup_expired_sessions()"
```

### 获取帮助

如果以上方法无法解决问题：

1. **查看日志文件**：检查详细的错误信息
2. **查看文档**：阅读相关的设计文档和需求文档
3. **提交Issue**：在GitHub上提交问题，附上日志和配置信息
4. **联系开发者**：通过邮件或其他方式联系项目维护者

**提交Issue时请包含**：
- 错误信息和日志
- 配置文件（隐藏敏感信息）
- 复现步骤
- 系统环境（Python版本、操作系统等）

## 项目结构

```
.
├── lark_bot.py              # 主机器人程序
├── config.py                # 配置管理
├── requirements.txt         # Python依赖
├── README.md                # 项目说明
├── .env                     # 环境变量（不提交到Git）
├── .env.example             # 环境变量模板
├── .gitignore               # Git忽略文件配置
│
├── feishu_bot/              # 机器人核心代码
│   ├── config.py            # 配置类
│   ├── feishu_bot.py        # 主应用类
│   ├── message_handler.py   # 消息处理器
│   ├── command_parser.py    # 命令解析器
│   ├── smart_router.py      # 智能路由器
│   ├── session_manager.py   # 会话管理器
│   ├── executor_registry.py # 执行器注册表
│   ├── *_api_executor.py    # API执行器（Claude、Gemini、OpenAI）
│   ├── *_cli_executor.py    # CLI执行器（Claude Code、Gemini）
│   ├── cache.py             # 缓存管理
│   ├── ssl_config.py        # SSL配置
│   ├── websocket_client.py  # WebSocket客户端
│   └── ...                  # 其他模块
│
├── tests/                   # 单元测试和属性测试
│   ├── test_*.py            # 单元测试文件
│   ├── test_*_properties.py # 属性测试文件
│   └── ...
│
├── test_scripts/            # 集成测试和手动测试脚本
│   ├── run_integration_test.py      # 集成测试主程序
│   ├── test_bot_message.py          # 自动化消息测试
│   ├── send_test_message.py         # 发送测试消息
│   ├── check_chat_history.py        # 查看聊天历史
│   └── ...                          # 其他测试脚本
│
├── docs/                    # 项目文档
│   ├── README.md                        # 文档目录
│   ├── USER_GUIDE.md                    # 用户指南
│   ├── CONFIGURATION.md                 # 配置指南
│   ├── INTEGRATION_TESTING_GUIDE.md     # 集成测试指南
│   ├── QUICK_START_INTEGRATION_TEST.md  # 快速测试指南
│   └── TESTING_STRUCTURE.md             # 测试结构说明
│
├── data/                    # 数据存储（不提交到Git）
│   ├── sessions.json        # 会话数据
│   ├── executor_sessions.json  # 执行器会话映射
│   └── archived_sessions/   # 归档会话
│
└── test_data/               # 测试数据
    ├── sessions.json        # 测试会话数据
    └── archived_sessions/   # 测试归档会话
```

**注意**：
- `data/` 文件夹包含用户会话数据，已添加到 `.gitignore`，不会提交到Git
- `.env` 文件包含敏感配置信息，已添加到 `.gitignore`，不会提交到Git
- 使用 `.env.example` 作为环境变量配置模板

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

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 注意事项

⚠️ **安全提醒**: 
- **请勿将敏感信息提交到公开仓库**
  - `.env` 文件包含API密钥和凭证，已添加到 `.gitignore`
  - `data/` 文件夹包含用户会话数据，已添加到 `.gitignore`
- **使用环境变量管理敏感信息**
  - 使用 `.env.example` 作为配置模板
  - 复制为 `.env` 并填入真实凭证
- **定期更新依赖包以确保安全性**
  ```bash
  pip install -r requirements.txt --upgrade
  ```
- **定期轮换API密钥**
  - 建议每3-6个月更换一次API密钥
  - 如发现密钥泄露，立即在对应平台重置

## 数据隐私

本项目重视用户数据隐私和安全：

### 本地存储
- **会话数据**：存储在本地 `data/` 文件夹，不会上传到Git仓库
- **会话内容**：包含用户对话历史，仅用于维护上下文
- **自动清理**：会话超过24小时自动过期并归档

### 数据保护措施
- `data/` 文件夹已添加到 `.gitignore`，防止意外提交
- 会话数据仅存储在本地，不会发送到第三方（除AI服务商）
- 支持手动清理会话：使用 `/new` 命令创建新会话

### AI服务商数据处理
- **Claude API**：根据Anthropic隐私政策处理
- **Gemini API**：根据Google隐私政策处理
- **OpenAI API**：根据OpenAI隐私政策处理

建议定期清理本地会话数据：
```bash
# 备份会话数据
cp -r data/ data_backup/

# 清理过期会话
python -c "from feishu_bot.session_manager import SessionManager; sm = SessionManager(); sm.cleanup_expired_sessions()"
```
