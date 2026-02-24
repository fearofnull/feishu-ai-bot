# 配置说明文档

本文档详细说明飞书AI机器人的所有配置项。

## 配置文件

配置通过 `.env` 文件管理。首次使用时：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

然后编辑 `.env` 文件填入你的配置。

## 用户如何选择不同的 AI 和 CLI

### 通过命令前缀选择

用户可以在消息前加上命令前缀来指定使用哪个 AI 和执行层：

#### API 层（快速对话）
- `@claude` 或 `@claude-api` → Claude API
- `@gemini` 或 `@gemini-api` → Gemini API  
- `@openai` 或 `@gpt` → OpenAI API

#### CLI 层（代码操作）
- `@claude-cli` 或 `@code` → Claude Code CLI
- `@gemini-cli` → Gemini CLI

### 使用示例

```
# 使用 Claude API 快速对话
@claude 帮我解释一下什么是依赖注入

# 使用 Claude Code CLI 分析代码
@code 分析一下这个项目的架构

# 使用 Gemini CLI 查看代码
@gemini-cli 查看 src/main.py 文件的内容

# 使用 OpenAI API
@gpt 写一个快速排序算法
```

### 智能路由

如果用户不指定前缀，机器人会根据消息内容智能选择：
- 包含代码操作关键词（如"查看代码"、"修改文件"）→ 自动使用 CLI 层
- 普通对话 → 使用 DEFAULT_PROVIDER 和 DEFAULT_LAYER 配置

### CLI 目录配置

不同的 CLI 可以配置不同的目标目录：

```bash
# 场景 1: 两个 CLI 使用同一个项目
TARGET_PROJECT_DIR=E:\IdeaProjects\my-project

# 场景 2: 两个 CLI 使用不同项目
CLAUDE_CLI_TARGET_DIR=E:\IdeaProjects\project-a
GEMINI_CLI_TARGET_DIR=E:\IdeaProjects\project-b

# 场景 3: 混合配置（Claude 专用，Gemini 使用通用）
TARGET_PROJECT_DIR=E:\IdeaProjects\default-project
CLAUDE_CLI_TARGET_DIR=E:\IdeaProjects\special-project
# GEMINI_CLI_TARGET_DIR 未配置，将使用 TARGET_PROJECT_DIR
```

---

## 配置项详解

### 1. 飞书应用配置（必需）

#### FEISHU_APP_ID
- **类型**: 字符串
- **必需**: 是
- **说明**: 飞书应用的唯一标识符
- **获取方式**: 
  1. 访问 [飞书开放平台](https://open.feishu.cn/)
  2. 进入你的应用
  3. 在"凭证与基础信息"页面找到 App ID
- **示例**: `cli_a1b2c3d4e5f6g7h8`

#### FEISHU_APP_SECRET
- **类型**: 字符串
- **必需**: 是
- **说明**: 飞书应用的密钥，用于身份验证
- **获取方式**: 在 App ID 同一页面找到 App Secret
- **示例**: `abcdefghijklmnopqrstuvwxyz123456`
- **安全提示**: 
  - ⚠️ 切勿将此密钥提交到公开仓库
  - ⚠️ 定期更换密钥以提高安全性

---

### 2. AI CLI 配置

#### CLAUDE_CLI_TARGET_DIR
- **类型**: 字符串（文件路径）
- **必需**: 否（使用 Claude CLI 时需要）
- **默认值**: 空（使用 TARGET_PROJECT_DIR）
- **说明**: Claude Code CLI 执行代码操作的目标项目目录
- **使用场景**: 
  - 当用户使用 `@claude-cli` 或 `@code` 命令时
  - 当智能路由选择 Claude CLI 层时
- **示例**: 
  - Windows: `E:\IdeaProjects\my-project`
  - Linux/Mac: `/home/user/projects/my-project`
- **注意**: 
  - 如果未配置，将使用 TARGET_PROJECT_DIR
  - 路径必须存在且可访问
  - 建议使用绝对路径

#### GEMINI_CLI_TARGET_DIR
- **类型**: 字符串（文件路径）
- **必需**: 否（使用 Gemini CLI 时需要）
- **默认值**: 空（使用 TARGET_PROJECT_DIR）
- **说明**: Gemini CLI 执行代码操作的目标项目目录
- **使用场景**: 
  - 当用户使用 `@gemini-cli` 命令时
  - 当智能路由选择 Gemini CLI 层时
- **示例**: 
  - Windows: `E:\IdeaProjects\another-project`
  - Linux/Mac: `/home/user/projects/another-project`
- **注意**: 
  - 如果未配置，将使用 TARGET_PROJECT_DIR
  - 可以与 Claude CLI 使用不同的项目目录

#### TARGET_PROJECT_DIR
- **类型**: 字符串（文件路径）
- **必需**: 否（使用 CLI 层时需要）
- **默认值**: 空
- **说明**: 通用目标项目目录，当 CLAUDE_CLI_TARGET_DIR 或 GEMINI_CLI_TARGET_DIR 未配置时使用
- **使用场景**: 
  - 作为所有 CLI 的默认目录
  - 兼容旧版本配置
- **示例**: 
  - Windows: `E:\IdeaProjects\my-project`
  - Linux/Mac: `/home/user/projects/my-project`
- **配置建议**:
  - 如果两个 CLI 使用同一个项目：只配置 TARGET_PROJECT_DIR
  - 如果两个 CLI 使用不同项目：分别配置 CLAUDE_CLI_TARGET_DIR 和 GEMINI_CLI_TARGET_DIR

#### AI_TIMEOUT
- **类型**: 整数（秒）
- **必需**: 否
- **默认值**: 600（10分钟）
- **说明**: CLI 执行器等待 AI 响应的最长时间
- **建议值**: 
  - 简单查询: 300（5分钟）
  - 复杂代码操作: 600-1200（10-20分钟）
- **注意**: 超时后会返回错误，但不会中断 AI 进程

---

### 3. AI API 配置

至少需要配置一个 AI 提供商的 API 密钥。

#### CLAUDE_API_KEY
- **类型**: 字符串
- **必需**: 否（但推荐配置）
- **说明**: Anthropic Claude API 密钥
- **获取方式**: 
  1. 访问 [Anthropic Console](https://console.anthropic.com/)
  2. 创建 API Key
- **使用场景**: 
  - 用户使用 `@claude` 或 `@api` 命令
  - DEFAULT_PROVIDER 设置为 `claude` 时
- **支持的模型**: Claude 3.5 Sonnet, Claude 3 Opus 等

#### GEMINI_API_KEY
- **类型**: 字符串
- **必需**: 否
- **说明**: Google Gemini API 密钥
- **获取方式**: 
  1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
  2. 创建 API Key
- **使用场景**: 用户使用 `@gemini` 命令
- **支持的模型**: Gemini 1.5 Pro, Gemini 1.5 Flash 等

#### OPENAI_API_KEY
- **类型**: 字符串
- **必需**: 否
- **说明**: OpenAI API 密钥或兼容服务的密钥
- **获取方式**: 
  1. OpenAI: 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
  2. ModelScope: 访问 [ModelScope](https://www.modelscope.cn/)
- **使用场景**: 
  - 用户使用 `@openai` 或 `@gpt` 命令
  - DEFAULT_PROVIDER 设置为 `openai` 时

#### OPENAI_BASE_URL
- **类型**: 字符串（URL）
- **必需**: 否
- **默认值**: `https://api.openai.com/v1`
- **说明**: OpenAI API 的基础 URL，用于兼容第三方服务
- **常用值**: 
  - OpenAI 官方: `https://api.openai.com/v1`（默认）
  - ModelScope: `https://api-inference.modelscope.cn/v1`
  - Azure OpenAI: `https://your-resource.openai.azure.com/`
- **使用场景**: 
  - 使用 ModelScope 等国内服务
  - 使用 Azure OpenAI
  - 使用其他兼容 OpenAI API 的服务

#### OPENAI_MODEL
- **类型**: 字符串
- **必需**: 否
- **默认值**: `gpt-4o`
- **说明**: 指定使用的 OpenAI 模型
- **常用值**: 
  - OpenAI: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
  - ModelScope: `qwen-plus`, `qwen-turbo`, `qwen-max`
- **注意**: 模型名称必须与 API 服务支持的模型匹配

---

### 4. 默认设置

#### DEFAULT_PROVIDER
- **类型**: 字符串（枚举）
- **必需**: 否
- **默认值**: `claude`
- **可选值**: `claude`, `gemini`, `openai`
- **说明**: 当用户未指定提供商时使用的默认 AI 服务
- **使用场景**: 
  - 用户直接发送消息（不带 @ 前缀）
  - 智能路由选择提供商时的首选
- **建议**: 选择你配置了 API 密钥的提供商

#### DEFAULT_LAYER
- **类型**: 字符串（枚举）
- **必需**: 否
- **默认值**: `api`
- **可选值**: 
  - `api`: API 层（快速响应，适合对话）
  - `cli`: CLI 层（深度代码能力，适合代码操作）
- **说明**: 当用户未指定执行层时使用的默认执行方式
- **选择建议**: 
  - 主要用于对话: 选择 `api`
  - 主要用于代码操作: 选择 `cli`

---

### 5. 会话管理配置

#### SESSION_STORAGE_PATH
- **类型**: 字符串（文件路径）
- **必需**: 否
- **默认值**: `./data/sessions.json`
- **说明**: 会话数据的存储位置
- **注意**: 
  - 目录会自动创建
  - 建议使用相对路径

#### MAX_SESSION_MESSAGES
- **类型**: 整数
- **必需**: 否
- **默认值**: 50
- **说明**: 单个会话最大消息数，超过后自动创建新会话
- **目的**: 避免上下文过长导致性能下降
- **建议值**: 
  - 短对话场景: 20-30
  - 长对话场景: 50-100
- **注意**: 值越大，上下文越完整，但响应可能越慢

#### SESSION_TIMEOUT
- **类型**: 整数（秒）
- **必需**: 否
- **默认值**: 86400（24小时）
- **说明**: 会话闲置超过此时间后自动过期
- **建议值**: 
  - 频繁使用: 3600-7200（1-2小时）
  - 偶尔使用: 86400（24小时）
  - 长期保留: 604800（7天）

---

### 6. 缓存配置

#### CACHE_SIZE
- **类型**: 整数
- **必需**: 否
- **默认值**: 1000
- **说明**: 消息去重缓存的容量
- **目的**: 防止重复处理相同消息（飞书可能重复推送）
- **建议值**: 
  - 低流量: 500-1000
  - 中流量: 1000-2000
  - 高流量: 2000-5000
- **注意**: 值越大，内存占用越多

---

### 7. SSL 配置

#### SSL_CERT_FILE
- **类型**: 字符串（文件路径）
- **必需**: 否
- **默认值**: 空（使用 certifi 提供的证书）
- **说明**: 自定义 SSL 证书路径
- **使用场景**: 
  - 企业内网环境
  - 使用自签名证书
  - SSL 证书验证问题
- **示例**: `/path/to/custom/cert.pem`
- **注意**: 通常不需要配置

---

### 8. 日志配置

#### LOG_LEVEL
- **类型**: 字符串（枚举）
- **必需**: 否
- **默认值**: `INFO`
- **可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **说明**: 控制日志输出的详细程度
- **级别说明**: 
  - `DEBUG`: 最详细，包含所有调试信息（开发时使用）
  - `INFO`: 一般信息，记录关键操作（生产环境推荐）
  - `WARNING`: 警告信息，可能的问题
  - `ERROR`: 错误信息，需要关注
  - `CRITICAL`: 严重错误，系统可能无法继续运行
- **建议**: 
  - 开发/调试: `DEBUG`
  - 生产环境: `INFO` 或 `WARNING`

---

### 9. 测试配置

仅用于运行测试脚本，生产环境不需要配置。

#### FEISHU_CHAT_ID
- **类型**: 字符串
- **必需**: 否（测试时需要）
- **说明**: 测试用的飞书群聊 ID
- **获取方式**: 运行 `python test_scripts/get_chat_id.py`
- **使用场景**: 运行集成测试脚本

#### FEISHU_USER_ID
- **类型**: 字符串
- **必需**: 否（测试时需要）
- **说明**: 测试用的飞书用户 ID（Open ID）
- **获取方式**: 
  1. 在测试群中发送消息
  2. 查看机器人日志获取 Open ID
- **使用场景**: 运行集成测试脚本

---

## 配置验证

运行以下命令验证配置是否正确：

```bash
python config.py
```

或

```bash
python feishu_bot/config.py
```

输出示例：
```
✅ 已加载配置文件: E:\TraeProjects\lark-bot\.env

============================================================
配置状态
============================================================
APP_ID: ✅ 已配置
APP_SECRET: ✅ 已配置
TARGET_PROJECT_DIR: ✅ 已配置
CLAUDE_API_KEY: ✅ 已配置
GEMINI_API_KEY: ⚠️ 未配置
OPENAI_API_KEY: ✅ 已配置
DEFAULT_PROVIDER: claude
DEFAULT_LAYER: api
LOG_LEVEL: INFO
============================================================

✅ 配置验证通过
```

## 常见配置场景

### 场景 1: 仅使用 Claude API
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
CLAUDE_API_KEY=your_claude_key
DEFAULT_PROVIDER=claude
DEFAULT_LAYER=api
```

### 场景 2: 使用 ModelScope（国内）
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
OPENAI_API_KEY=your_modelscope_key
OPENAI_BASE_URL=https://api-inference.modelscope.cn/v1
OPENAI_MODEL=qwen-plus
DEFAULT_PROVIDER=openai
DEFAULT_LAYER=api
```

### 场景 3: 多 AI 混合使用
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
CLAUDE_API_KEY=your_claude_key
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
DEFAULT_PROVIDER=claude
DEFAULT_LAYER=api
```

### 场景 4: 不同 CLI 使用不同项目
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
CLAUDE_API_KEY=your_claude_key
GEMINI_API_KEY=your_gemini_key
CLAUDE_CLI_TARGET_DIR=E:\IdeaProjects\backend-project
GEMINI_CLI_TARGET_DIR=E:\IdeaProjects\frontend-project
DEFAULT_PROVIDER=claude
DEFAULT_LAYER=api
```

用户可以通过 `@code` 操作后端项目，通过 `@gemini-cli` 操作前端项目。
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
CLAUDE_API_KEY=your_claude_key
TARGET_PROJECT_DIR=E:\IdeaProjects\my-project
DEFAULT_PROVIDER=claude
DEFAULT_LAYER=cli
AI_TIMEOUT=1200
```

### 场景 5: 代码操作为主
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
CLAUDE_API_KEY=your_claude_key
TARGET_PROJECT_DIR=E:\IdeaProjects\my-project
DEFAULT_PROVIDER=claude
DEFAULT_LAYER=cli
AI_TIMEOUT=1200
```

## 命令前缀完整列表

### API 层命令
| 命令前缀 | AI 提供商 | 说明 |
|---------|----------|------|
| `@claude` | Claude API | Anthropic Claude（推荐） |
| `@claude-api` | Claude API | 同上（显式指定 API） |
| `@gemini` | Gemini API | Google Gemini |
| `@gemini-api` | Gemini API | 同上（显式指定 API） |
| `@openai` | OpenAI API | OpenAI GPT |
| `@gpt` | OpenAI API | 同上（简写） |

### CLI 层命令
| 命令前缀 | AI CLI | 说明 | 目标目录配置 |
|---------|--------|------|-------------|
| `@code` | Claude Code CLI | Claude 代码操作（推荐） | CLAUDE_CLI_TARGET_DIR |
| `@claude-cli` | Claude Code CLI | 同上（显式指定） | CLAUDE_CLI_TARGET_DIR |
| `@gemini-cli` | Gemini CLI | Gemini 代码操作 | GEMINI_CLI_TARGET_DIR |

### 使用技巧

1. **快速切换 AI**：在同一会话中可以随时切换不同的 AI
   ```
   @claude 用 Python 写一个快速排序
   @gemini 用 Java 写一个快速排序
   @gpt 用 JavaScript 写一个快速排序
   ```

2. **混合使用 API 和 CLI**：
   ```
   @claude 这个项目应该怎么重构？
   @code 帮我查看一下 src/main.py 的代码
   ```

3. **不同项目的代码操作**：
   ```
   @code 分析后端项目的数据库设计
   @gemini-cli 查看前端项目的组件结构
   ```

---

## 安全建议

1. **保护敏感信息**
   - ✅ 将 `.env` 添加到 `.gitignore`
   - ✅ 不要在代码中硬编码密钥
   - ✅ 定期更换 API 密钥

2. **权限控制**
   - ✅ 限制 `.env` 文件的读取权限
   - ✅ 在生产环境使用环境变量而非文件

3. **日志安全**
   - ✅ 确保日志不包含敏感信息
   - ✅ 定期清理旧日志文件

## 故障排查

### 问题 1: 配置验证失败
**症状**: 运行 `python config.py` 报错
**解决**: 
1. 检查 `.env` 文件是否存在
2. 检查必需配置项是否填写
3. 检查配置值格式是否正确

### 问题 2: AI 无响应
**症状**: 机器人收到消息但不回复
**解决**: 
1. 检查对应 AI 的 API 密钥是否正确
2. 检查 DEFAULT_PROVIDER 是否配置了有效的提供商
3. 查看日志确认错误信息

### 问题 3: CLI 层无法使用
**症状**: 使用 `@code` 命令报错
**解决**: 
1. 检查 TARGET_PROJECT_DIR 是否配置
2. 检查目录路径是否存在
3. 检查是否安装了 Claude Code CLI

## 更多帮助

- 查看 [README.md](../README.md) 了解快速开始
- 查看 [INTEGRATION_TESTING_GUIDE.md](INTEGRATION_TESTING_GUIDE.md) 了解测试配置
- 查看 `.kiro/specs/feishu-ai-bot/design.md` 了解架构设计
