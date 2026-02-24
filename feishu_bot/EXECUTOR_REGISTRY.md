# ExecutorRegistry 执行器注册表

## 概述

`ExecutorRegistry` 是飞书 AI 机器人的核心组件，负责管理所有 AI 执行器的注册、发现和获取。它提供了统一的接口来管理 API 层和 CLI 层的执行器，支持执行器元数据管理、可用性检查和配置文件加载。

## 核心功能

### 1. 执行器注册

支持注册两种类型的执行器：

- **API 执行器**：直接调用 AI 模型 API（Claude API、Gemini API、OpenAI API）
- **CLI 执行器**：调用本地 AI CLI 工具（Claude Code CLI、Gemini CLI）

```python
from feishu_bot.executor_registry import ExecutorRegistry
from feishu_bot.models import ExecutorMetadata

# 创建注册表
registry = ExecutorRegistry()

# 注册 API 执行器
claude_api_executor = ClaudeAPIExecutor(api_key="...")
metadata = ExecutorMetadata(
    name="Claude API",
    provider="claude",
    layer="api",
    version="1.0.0",
    description="Claude API executor",
    capabilities=["chat", "code_generation"],
    command_prefixes=["@claude", "@claude-api"],
    priority=1,
    config_required=["api_key"]
)
registry.register_api_executor("claude", claude_api_executor, metadata)

# 注册 CLI 执行器
claude_cli_executor = ClaudeCodeCLIExecutor(target_dir="/path/to/repo")
registry.register_cli_executor("claude", claude_cli_executor)
```

### 2. 执行器获取

通过提供商名称和执行层获取执行器：

```python
# 获取 Claude API 执行器
try:
    executor = registry.get_executor("claude", "api")
    result = executor.execute("Hello, Claude!")
except ExecutorNotAvailableError as e:
    print(f"Executor not available: {e.reason}")
```

### 3. 可用性检查

检查执行器是否可用，支持缓存以提高性能：

```python
# 检查单个执行器
if registry.is_executor_available("claude", "api"):
    print("Claude API is available")

# 列出所有可用执行器
available = registry.list_available_executors()
print(f"Available executors: {available}")

# 按层过滤
api_executors = registry.list_available_executors(layer="api")
cli_executors = registry.list_available_executors(layer="cli")
```

### 4. 元数据管理

存储和检索执行器的元数据信息：

```python
# 获取执行器元数据
metadata = registry.get_executor_metadata("claude", "api")
if metadata:
    print(f"Name: {metadata.name}")
    print(f"Capabilities: {metadata.capabilities}")
    print(f"Command prefixes: {metadata.command_prefixes}")
    print(f"Priority: {metadata.priority}")
```

### 5. 配置文件加载

支持从 JSON 配置文件加载执行器元数据：

```python
# 从配置文件创建注册表
registry = ExecutorRegistry(config_path="executor_config.json")
```

配置文件格式示例（`executor_config.json`）：

```json
{
  "executors": [
    {
      "provider": "claude",
      "layer": "api",
      "name": "Claude API",
      "version": "1.0.0",
      "description": "Anthropic Claude API executor",
      "capabilities": ["chat", "code_generation"],
      "command_prefixes": ["@claude", "@claude-api"],
      "priority": 1,
      "config_required": ["claude_api_key"]
    }
  ]
}
```

## 可用性缓存

为了提高性能，`ExecutorRegistry` 会缓存执行器的可用性状态，避免重复检查。

```python
# 清除缓存以强制重新检查
registry.clear_availability_cache()
```

## 异常处理

### ExecutorNotAvailableError

当执行器不可用时抛出此异常：

```python
try:
    executor = registry.get_executor("claude", "api")
except ExecutorNotAvailableError as e:
    print(f"Provider: {e.provider}")
    print(f"Layer: {e.layer}")
    print(f"Reason: {e.reason}")
```

常见的不可用原因：
- 执行器未注册
- API 密钥未配置或无效
- CLI 工具未安装
- 目标目录不存在或无法访问

## 扩展性设计

### 添加新的 AI Agent

系统采用插件式架构，支持轻松添加新的 AI Agent：

1. **实现 AIExecutor 接口**：

```python
from feishu_bot.executor_registry import AIExecutor
from feishu_bot.models import ExecutionResult

class QwenCodeCLIExecutor(AIExecutor):
    def execute(self, user_prompt, conversation_history=None, additional_params=None):
        # 实现 Qwen Code 特定的执行逻辑
        pass
    
    def is_available(self):
        # 检查 Qwen Code CLI 是否可用
        pass
    
    def get_provider_name(self):
        return "qwen-code"
```

2. **注册到系统**：

```python
qwen_executor = QwenCodeCLIExecutor(target_dir="/path/to/repo")
qwen_metadata = ExecutorMetadata(
    name="Qwen Code CLI",
    provider="qwen-code",
    layer="cli",
    version="1.0.0",
    description="Qwen Code AI Agent",
    capabilities=["code_analysis", "code_generation"],
    command_prefixes=["@qwen", "@qwen-code"],
    priority=3,
    config_required=["target_directory"]
)
registry.register_cli_executor("qwen-code", qwen_executor, qwen_metadata)
```

3. **更新命令解析器**（如果需要新的命令前缀）：

```python
command_parser.add_prefix_mapping("@qwen", "qwen-code", "cli")
```

## 最佳实践

1. **始终提供元数据**：注册执行器时提供完整的元数据，便于管理和调试
2. **使用配置文件**：对于生产环境，使用配置文件管理执行器元数据
3. **定期清除缓存**：在配置更改后清除可用性缓存
4. **处理异常**：始终捕获 `ExecutorNotAvailableError` 并提供友好的错误提示
5. **优先级设置**：为执行器设置合理的优先级，用于降级策略

## 相关文档

- [设计文档](../.kiro/specs/feishu-ai-bot/design.md) - 完整的系统设计
- [需求文档](../.kiro/specs/feishu-ai-bot/requirements.md) - 功能需求
- [任务列表](../.kiro/specs/feishu-ai-bot/tasks.md) - 实现任务

## 测试

运行单元测试：

```bash
# 测试基本功能
python -m pytest tests/test_executor_registry.py -v

# 测试配置加载
python -m pytest tests/test_executor_registry_config.py -v

# 运行所有测试
python -m pytest tests/test_executor_registry*.py -v
```

## 需求映射

此实现满足以下需求：

- **Requirement 13.7**: 执行器注册表管理
- **Requirement 16.1**: API 执行器可用性检查
- **Requirement 16.2**: CLI 执行器可用性检查
- **Requirement 16.3**: 执行器不可用异常
- **Requirement 16.5**: 可用性状态缓存
