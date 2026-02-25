# 智能路由详解

## 概述

智能路由器负责决定用户消息应该由哪个AI服务处理。本文档详细说明路由逻辑和决策过程。

## 路由流程

```
用户消息
    ↓
1. 消息去重
    ↓
2. 消息解析
    ↓
3. 命令解析（提取前缀）
    ↓
4. 会话命令检查 ← 【第一道拦截】
    ├─ 是会话命令 → 直接处理（/help, /new, /session, /history）
    └─ 不是会话命令 → 继续
    ↓
5. 智能路由 ← 【第二道决策】
    ├─ 有显式前缀？
    │   ├─ 是 → 使用指定的 provider + layer
    │   └─ 否 → 继续智能判断
    ├─ 检测CLI关键词？
    │   ├─ 是 → 使用 CLI 层
    │   └─ 否 → 使用 API 层（默认）
    └─ 选择执行器
    ↓
6. AI执行
    ├─ API层：快速响应（Claude API, Gemini API, OpenAI API）
    └─ CLI层：代码操作（Claude Code CLI, Gemini CLI）
    ↓
7. 返回结果
```

## 路由规则详解

### 规则1：会话命令优先

**会话命令**直接处理，不经过AI：
- `/help` 或 `帮助` → 显示帮助信息
- `/new` 或 `新会话` → 创建新会话
- `/session` 或 `会话信息` → 查看会话信息
- `/history` 或 `历史记录` → 查看对话历史

**示例**：
```
用户: /help
处理: 直接返回帮助信息（不调用AI）
```

### 规则2：显式前缀优先

如果用户使用了命令前缀，直接使用指定的服务：

**API层前缀**：
- `@claude` 或 `@claude-api` → Claude API
- `@gemini` 或 `@gemini-api` → Gemini API
- `@openai` 或 `@gpt` → OpenAI API

**CLI层前缀**：
- `@code` 或 `@claude-cli` → Claude Code CLI
- `@gemini-cli` → Gemini CLI

**示例**：
```
用户: @claude 你是谁
处理: 使用 Claude API（显式指定）

用户: @code 查看项目结构
处理: 使用 Claude Code CLI（显式指定）
```

### 规则3：智能判断（无前缀时）

当用户没有使用前缀时，系统会智能判断：

#### 3.1 检测CLI关键词

如果消息包含以下关键词，使用**CLI层**：

**代码相关**：
- 查看代码、view code
- 分析代码、analyze code
- 代码库、codebase

**文件操作**：
- 修改文件、modify file
- 读取文件、read file
- 写入文件、write file
- 创建文件、create file

**命令执行**：
- 执行命令、execute command
- 运行脚本、run script

**项目分析**：
- 分析项目、analyze project
- 项目结构、project structure

**示例**：
```
用户: 查看代码库的结构
检测: 包含"查看代码"和"代码库"关键词
路由: CLI层（Claude Code CLI）
原因: 需要访问本地代码库
```

#### 3.2 默认使用API层

如果消息**不包含**CLI关键词，使用**API层**（默认）：

**示例**：
```
用户: 你是谁
检测: 无CLI关键词
路由: API层（Claude API）
原因: 简单问答，不需要访问代码库

用户: 什么是Python装饰器？
检测: 无CLI关键词
路由: API层（Claude API）
原因: 概念解释，不需要访问代码库

用户: 帮我写一段代码
检测: 无CLI关键词
路由: API层（Claude API）
原因: 代码生成，不需要访问本地代码库
```

## 为什么"你是谁"会路由到Claude？

这是**正确的行为**！原因：

1. **不是会话命令**：`你是谁` 不是 `/help`、`/new` 等会话命令
2. **需要AI回答**：这是一个需要AI回答的问题
3. **无CLI关键词**：消息中没有"查看代码"、"修改文件"等关键词
4. **使用默认层**：根据配置，默认使用 API 层
5. **选择Claude API**：根据配置，默认提供商是 Claude

**完整流程**：
```
用户消息: "你是谁"
    ↓
会话命令检查: 否（不是 /help 等命令）
    ↓
命令前缀检查: 否（没有 @claude 等前缀）
    ↓
CLI关键词检查: 否（没有"查看代码"等关键词）
    ↓
使用默认配置: provider=claude, layer=api
    ↓
路由结果: Claude API ✅
    ↓
AI回答: "我是飞书AI机器人..."
```

## API层 vs CLI层

### API层（快速响应）

**特点**：
- ✅ 响应快速（秒级）
- ✅ 成本较低
- ❌ 无法访问本地代码
- ❌ 无法执行文件操作

**适用场景**：
- 一般问答
- 概念解释
- 代码生成（不需要查看现有代码）
- 翻译、写作
- 数据分析建议

**示例**：
```
✅ 你是谁
✅ 什么是Python装饰器？
✅ 帮我写一个快速排序算法
✅ 翻译这段文字
✅ 解释一下这个错误信息
```

### CLI层（代码操作）

**特点**：
- ✅ 可以访问本地代码库
- ✅ 可以执行文件操作
- ✅ 可以运行命令
- ❌ 响应较慢（需要启动CLI工具）
- ❌ 成本较高

**适用场景**：
- 代码分析（需要查看现有代码）
- 文件操作（读取、修改、创建文件）
- 项目结构分析
- 代码重构建议（基于现有代码）

**示例**：
```
✅ 查看代码库的结构
✅ 分析这个项目的架构
✅ 修改 config.py 文件
✅ 读取 README.md 的内容
✅ 执行测试命令
```

## 如何控制路由？

### 方法1：使用显式前缀（推荐）

明确指定使用哪个服务：

```
@claude 你是谁              # 强制使用 Claude API
@code 查看项目结构          # 强制使用 Claude Code CLI
@gemini 解释这个概念        # 强制使用 Gemini API
@gemini-cli 分析代码        # 强制使用 Gemini CLI
```

### 方法2：使用CLI关键词（传统方式）

在消息中包含CLI关键词，自动路由到CLI层：

```
查看代码库的结构            # 自动路由到 CLI 层
分析项目的代码质量          # 自动路由到 CLI 层
```

**注意**：关键词检测可能不够准确。例如"如何设计一个代码审查流程？"包含"代码"关键词，但实际上是讨论流程设计，不需要CLI层。

### 方法2.5：使用AI意图分类（推荐）🆕

启用AI意图分类功能，让AI判断是否需要CLI层，比关键词检测更准确：

```bash
# 在 .env 文件中启用
USE_AI_INTENT_CLASSIFICATION=true
```

**优势**：
- ✅ 理解用户真实意图，不被关键词误导
- ✅ 可以处理各种表达方式
- ✅ 能区分"讨论代码"和"操作代码"

**详细说明**：参见 [AI_INTENT_CLASSIFICATION.md](AI_INTENT_CLASSIFICATION.md)

### 方法3：修改默认配置

在 `.env` 文件中修改默认设置：

```bash
# 默认AI提供商（claude, gemini, openai）
# 主要用于API层
DEFAULT_PROVIDER=claude

# 默认执行层（api, cli）
DEFAULT_LAYER=api

# CLI层专用默认提供商（可选）🆕
# 当AI判断需要CLI层时，使用此提供商
# 如果不设置，系统会自动检测第一个可用的CLI执行器
DEFAULT_CLI_PROVIDER=gemini
```

**使用场景**：
- API层和CLI层想使用不同的提供商
- 例如：API层用OpenAI（快速便宜），CLI层用Gemini（代码能力强）

**示例配置**：
```bash
DEFAULT_PROVIDER=openai          # API层默认用OpenAI
DEFAULT_CLI_PROVIDER=gemini      # CLI层默认用Gemini
```

**路由示例**：
```
用户: "你是谁"
判断: 不需要CLI → 使用API层
提供商: openai (DEFAULT_PROVIDER)
结果: openai/api ✅

用户: "查看代码库结构"
判断: 需要CLI → 使用CLI层
提供商: gemini (DEFAULT_CLI_PROVIDER)
结果: gemini/cli ✅
```

**自动检测CLI提供商**（当未设置DEFAULT_CLI_PROVIDER时）：

如果不设置 `DEFAULT_CLI_PROVIDER`，系统会自动检测第一个可用的CLI执行器：

```bash
# 不设置DEFAULT_CLI_PROVIDER
DEFAULT_PROVIDER=openai
# DEFAULT_CLI_PROVIDER 留空或不设置
```

**自动检测优先级**：
1. Claude Code CLI（如果已配置）
2. Gemini CLI（如果已配置）

**示例**：
```
配置:
  DEFAULT_PROVIDER=openai
  DEFAULT_CLI_PROVIDER=未设置
  已配置: openai/api, gemini/cli

用户: "查看代码库结构"
判断: 需要CLI → 使用CLI层
自动检测: gemini/cli 可用 ✅
结果: gemini/cli
```

**重要说明**：
- ⚠️ API层和CLI层是**完全不同的工具**
- ⚠️ `openai/api` 存在，但 `openai/cli` **不存在**（OpenAI没有CLI工具）
- ⚠️ 不能简单地用 `DEFAULT_PROVIDER` 替代 `DEFAULT_CLI_PROVIDER`
- ✅ 如果未设置 `DEFAULT_CLI_PROVIDER`，系统会自动检测可用的CLI执行器

## 降级策略（Fallback）

当指定的AI服务不可用时（例如API密钥未配置），系统会自动降级到其他可用的服务。

### 降级顺序

系统采用**3层降级策略**：

```
原始选择: claude/api (不可用)
    ↓
策略1: 同provider的另一层
    → claude/cli (尝试)
    ↓ (失败)
策略2: 其他provider的同一层
    → gemini/api (尝试)
    → openai/api (尝试)
    ↓ (失败)
策略3: 其他provider的另一层
    → gemini/cli (尝试)
    → openai/cli (尝试)
    ↓ (失败)
所有策略都失败 → 返回错误
```

### 降级示例

**场景1：只配置了OpenAI**

```
配置:
  DEFAULT_PROVIDER=claude
  DEFAULT_LAYER=api
  只有 OPENAI_API_KEY 配置

用户消息: "你是谁"
    ↓
路由决策: claude/api (默认)
    ↓
检查可用性: claude/api 不可用（未配置API密钥）
    ↓
降级策略1: claude/cli 不可用
    ↓
降级策略2: openai/api 可用 ✅
    ↓
最终使用: openai/api
```

**场景2：显式指定不可用的服务**

```
用户消息: "@claude 你是谁"
    ↓
路由决策: claude/api (显式指定)
    ↓
检查可用性: claude/api 不可用
    ↓
降级策略: 自动尝试其他可用服务
    ↓
最终使用: openai/api (降级成功)
```

### 降级日志

系统会在日志中显示降级过程：

```
[ROUTING] ⚠️  Executor claude/api not available: API key not configured
[ROUTING] Fallback strategy 1: claude/api -> claude/cli
[ROUTING] Strategy 1 failed: claude/cli not available
[ROUTING] Fallback strategy 2: claude/api -> openai/api
[ROUTING] ✅ Fallback successful: using openai/api
```

### 配置建议

为了避免频繁降级，建议：

1. **设置正确的默认提供商**：
   ```bash
   # 如果只配置了OpenAI
   DEFAULT_PROVIDER=openai
   ```

2. **配置多个AI服务**（可选）：
   ```bash
   CLAUDE_API_KEY=your_claude_key
   GEMINI_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key
   ```

3. **查看降级日志**：
   ```bash
   LOG_LEVEL=INFO  # 显示降级警告
   ```

## 常见问题

### Q1: 为什么简单问题也要经过AI？

**A**: 因为简单问题也需要AI回答。会话命令（如 `/help`）不需要AI，会直接处理。但"你是谁"、"什么是Python"这类问题需要AI生成回答。

### Q2: 如何让所有问题都使用API层？

**A**: 当前默认配置就是使用API层。只有在消息包含CLI关键词时才会使用CLI层。

### Q3: 如何强制使用CLI层？

**A**: 使用CLI前缀：`@code` 或 `@claude-cli` 或 `@gemini-cli`

### Q4: 智能路由会自动选择最合适的AI吗？

**A**: 智能路由主要决定使用API层还是CLI层。AI提供商的选择基于：
1. 显式前缀（如果有）
2. 默认配置（如果没有前缀）
3. 降级策略（如果首选不可用）

### Q5: 如何查看路由决策过程？

**A**: 在 `.env` 文件中设置 `LOG_LEVEL=DEBUG`，日志会显示详细的路由决策过程。

### Q6: 我只配置了OpenAI，为什么还能正常工作？

**A**: 系统会自动降级。即使默认配置是Claude，当Claude不可用时，系统会自动使用OpenAI。建议将 `DEFAULT_PROVIDER` 设置为 `openai` 以避免不必要的降级。

### Q7: 降级会影响响应速度吗？

**A**: 降级检查非常快速（毫秒级），对用户体验影响极小。但建议配置正确的默认提供商以避免每次都降级。

## 总结

智能路由的核心逻辑：

1. **会话命令** → 直接处理（不经过AI）
2. **显式前缀** → 使用指定的服务
3. **CLI关键词** → 使用CLI层（代码操作）
4. **默认情况** → 使用API层（快速响应）
5. **降级策略** → 自动切换到可用服务

这个设计确保：
- ✅ 简单问题快速响应（API层）
- ✅ 代码操作准确执行（CLI层）
- ✅ 用户可以显式控制（前缀）
- ✅ 系统智能判断（关键词检测）
- ✅ 服务不可用时自动降级（容错机制）

## 执行器名称显示 🆕

为了让用户清楚地知道是哪个AI服务回答了问题，系统会在响应消息中显示执行器名称。

### 显示格式

**成功响应**：
```
【使用 OpenAI API 回答】

我是AI助手，很高兴为您服务...
```

**错误响应**：
```
【使用 Claude Code CLI 回答】

❌ 处理失败 / Error

执行命令失败...
```

### 执行器名称列表

- `OpenAI API` - OpenAI API服务
- `Claude API` - Anthropic Claude API服务
- `Gemini API` - Google Gemini API服务
- `Claude Code CLI` - Claude Code CLI工具
- `Gemini CLI` - Gemini CLI工具

### 示例

**场景1：API层回答**
```
用户: 你是谁
响应: 【使用 OpenAI API 回答】

我是AI助手...
```

**场景2：CLI层回答**
```
用户: 查看代码库结构
响应: 【使用 Claude Code CLI 回答】

项目结构如下：
- src/
  - main.py
  - utils.py
...
```

**场景3：降级后回答**
```
用户: @claude 你是谁
配置: 只有OpenAI可用
响应: 【使用 OpenAI API 回答】

我是AI助手...
```

### 好处

- ✅ 用户清楚知道是哪个AI服务回答的
- ✅ 便于调试和问题排查
- ✅ 了解降级策略是否生效
- ✅ 验证路由决策是否正确
