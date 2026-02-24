# Implementation Plan: Feishu AI Bot

## Overview

本实现计划将飞书 AI 机器人重构为模块化、可扩展的架构，支持多个 AI 提供商和执行方式，并改进配置管理、错误处理、会话管理和测试覆盖。

核心架构变更：
- **智能路由层**：新增命令解析器和智能路由器，根据用户指令和消息内容自动选择 API 层或 CLI 层
- **AI API 层**：新增 AI API 执行器（Claude API、Gemini API、OpenAI API），提供快速响应
- **AI CLI 层**：现有的 CLI 执行器（Claude Code CLI、Gemini CLI），提供深度代码能力
- **会话管理**：支持上下文连续对话，用户可以通过命令开启新会话、查看会话信息和历史记录
- **持久化会话**：会话数据持久化存储，支持机器人重启后恢复对话上下文

核心优势：
- 更快的响应速度（API 调用比 CLI 启动快）
- 更低的成本（简单问题用 API，复杂任务用 CLI）
- 更灵活的选择（用户可以指定使用哪个模型和执行方式）
- 更好的用户体验（根据任务类型自动选择最合适的方式）

## Tasks

- [x] 1. 设置项目结构和配置管理
  - 创建 `feishu_bot/` 包目录结构
  - 实现 `BotConfig` 数据类，支持从环境变量和配置文件加载
  - 添加 AI API 配置字段（claude_api_key, gemini_api_key, openai_api_key）
  - 添加默认设置字段（default_provider, default_layer）
  - 创建 `.env.example` 文件，列出所有必需的配置项
  - 实现配置验证逻辑（检查必需字段）
  - _Requirements: 8.1, 8.2, 8.3, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8_

- [x] 1.1 编写配置管理单元测试
  - 测试从环境变量加载配置
  - 测试配置验证（缺少必需字段）
  - 测试默认值设置
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 2. 实现消息去重缓存
  - [x] 2.1 创建 `DeduplicationCache` 类
    - 使用 `collections.deque` 实现 FIFO 队列
    - 实现 `is_processed(message_id)` 方法
    - 实现 `mark_processed(message_id)` 方法
    - 设置 `maxlen=1000` 自动移除最早条目
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.2 编写消息去重属性测试
    - **Property 4: 消息去重缓存一致性**
    - **Validates: Requirements 2.1, 2.3**

  - [x] 2.3 编写缓存容量属性测试
    - **Property 6: 缓存容量限制**
    - **Validates: Requirements 2.4, 2.5**

- [x] 3. 实现消息处理器
  - [x] 3.1 创建 `MessageHandler` 类
    - 实现 `parse_message_content(message)` 方法，提取文本内容
    - 处理非文本消息，返回友好错误提示
    - 实现 `get_quoted_message(parent_id)` 方法，调用飞书 API 获取引用消息
    - 支持引用文本消息和卡片消息（interactive）
    - 实现 `combine_messages(quoted, current)` 方法，组合消息
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 3.2 编写文本消息提取属性测试
    - **Property 1: 文本消息内容提取**
    - **Validates: Requirements 1.1**

  - [x] 3.3 编写引用消息组合属性测试
    - **Property 2: 引用消息内容组合**
    - **Validates: Requirements 1.2, 1.4**

  - [x] 3.4 编写非文本消息错误处理属性测试
    - **Property 3: 非文本消息错误处理**
    - **Validates: Requirements 1.3**

- [x] 4. 实现会话管理器
  - [x] 4.1 创建 `Session` 和 `Message` 数据类
    - 实现 `Session` 数据类（session_id, user_id, created_at, last_active, messages）
    - 实现 `Message` 数据类（role, content, timestamp）
    - 实现 `Session.is_expired(timeout)` 方法
    - 实现 `Session.should_rotate(max_messages)` 方法
    - _Requirements: 10.5, 10.6_

  - [x] 4.2 创建 `SessionManager` 类
    - 实现 `__init__(storage_path, max_messages, session_timeout)` 方法
    - 实现 `get_or_create_session(user_id)` 方法
    - 实现 `add_message(user_id, role, content)` 方法
    - 实现 `get_conversation_history(user_id, max_messages)` 方法
    - 实现 `create_new_session(user_id)` 方法，归档旧会话
    - 实现 `get_session_info(user_id)` 方法
    - 实现 `format_history_for_ai(user_id)` 方法
    - 实现 `cleanup_expired_sessions()` 方法
    - 实现 `save_sessions()` 和 `load_sessions()` 方法（JSON 持久化）
    - 使用 `filelock` 库实现文件锁，避免并发写入冲突
    - 归档会话文件名格式：`{user_id}_{session_id}_{timestamp}.json`
    - 支持命令识别：`/new`, `新会话`, `/session`, `会话信息`, `/history`, `历史记录`
    - 定期清理过期会话（可配置清理间隔，默认每小时）
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.7, 10.8, 10.9, 10.10_

  - [x] 4.3 编写会话创建和检索属性测试
    - **Property 21: 会话创建和检索**
    - **Validates: Requirements 10.1, 10.2**

  - [x] 4.4 编写会话消息追加属性测试
    - **Property 22: 会话消息追加**
    - **Validates: Requirements 10.2**

  - [x] 4.5 编写新会话命令处理属性测试
    - **Property 23: 新会话命令处理**
    - **Validates: Requirements 10.3**

  - [x] 4.6 编写会话自动轮换属性测试
    - **Property 25: 会话自动轮换**
    - **Validates: Requirements 10.5**

  - [x] 4.7 编写会话过期检测属性测试
    - **Property 26: 会话过期检测**
    - **Validates: Requirements 10.6**

  - [x] 4.8 编写会话信息查询属性测试
    - **Property 27: 会话信息查询**
    - **Validates: Requirements 10.7**

  - [x] 4.9 编写会话持久化属性测试
    - **Property 28: 会话持久化**
    - **Validates: Requirements 10.8**

  - [x] 4.10 编写多用户会话隔离属性测试
    - **Property 29: 多用户会话隔离**
    - **Validates: Requirements 10.9**

  - [x] 4.11 编写对话历史格式化属性测试
    - **Property 30: 对话历史格式化**
    - **Validates: Requirements 10.10**

  - [x] 4.12 编写会话管理单元测试
    - 测试会话存储文件损坏处理
    - 测试会话加载失败处理
    - 测试会话保存失败处理
    - 测试归档会话功能
    - _Requirements: 10.3_

- [x] 5. 实现命令解析器
  - [x] 5.1 创建 `ParsedCommand` 数据类
    - 实现数据类（provider, execution_layer, message, explicit）
    - _Requirements: 11.6_

  - [x] 5.2 创建 `CommandParser` 类
    - 实现 `parse_command(message)` 方法，返回 ParsedCommand
    - 实现 `extract_provider_prefix(message)` 方法，提取 AI 提供商前缀
    - 支持的前缀：@claude-api, @claude, @gemini-api, @gemini, @openai, @gpt, @claude-cli, @code, @gemini-cli
    - 实现 `detect_cli_keywords(message)` 方法，检测 CLI 关键词
    - 支持中英文关键词：查看代码/view code, 修改文件/modify file, 执行命令/execute command, 分析项目/analyze project, 代码库/codebase 等
    - 支持大小写不敏感的前缀匹配
    - 去除前缀后返回实际消息内容
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [x] 5.3 编写命令前缀解析属性测试
    - **Property 36: 命令前缀解析**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.7, 11.8**

  - [x] 5.4 编写 CLI 关键词检测属性测试
    - **Property 37: CLI 关键词检测**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7**

  - [x] 5.5 编写命令解析单元测试
    - 测试各种前缀组合
    - 测试大小写不敏感
    - 测试前缀去除
    - 测试 CLI 关键词检测（中英文）
    - _Requirements: 11.8, 12.7_

- [x] 6. 实现智能路由器和执行器注册表
  - [x] 6.1 创建 `ExecutorMetadata` 数据类
    - 实现数据类（name, provider, layer, version, description, capabilities, command_prefixes, priority, config_required）
    - _Requirements: 13.7_

  - [x] 6.2 创建 `ExecutorRegistry` 类
    - 实现 `__init__()` 方法，初始化执行器字典和元数据字典
    - 实现 `register_api_executor(provider, executor, metadata)` 方法
    - 实现 `register_cli_executor(provider, executor, metadata)` 方法
    - 实现 `get_executor(provider, layer)` 方法，返回执行器或抛出 ExecutorNotAvailableError
    - 实现 `list_available_executors(layer)` 方法，列出所有可用执行器
    - 实现 `get_executor_metadata(provider, layer)` 方法
    - 实现 `is_executor_available(provider, layer)` 方法
    - 缓存执行器可用性状态，避免重复检查
    - 支持从配置文件加载执行器注册信息
    - _Requirements: 13.7, 16.1, 16.2, 16.3, 16.5_

  - [x] 6.3 创建 `SmartRouter` 类
    - 实现 `__init__(executor_registry, default_provider, default_layer)` 方法
    - 实现 `route(parsed_command)` 方法，返回合适的执行器
    - 实现 `get_executor(provider, layer)` 方法，通过 ExecutorRegistry 获取指定执行器
    - 实现显式指定优先逻辑（explicit=true 时直接使用指定执行器）
    - 实现智能判断逻辑（检测 CLI 关键词，选择执行层）
    - 实现降级策略（API→CLI 或 CLI→API）
    - 记录降级日志
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

  - [x] 6.4 编写执行器注册表单元测试
    - 测试执行器注册
    - 测试执行器获取
    - 测试执行器可用性检查
    - 测试元数据管理
    - _Requirements: 13.7, 16.5_

  - [x] 6.5 编写智能路由显式指定属性测试
    - **Property 38: 智能路由显式指定优先**
    - **Validates: Requirements 13.1**

  - [x] 6.6 编写智能路由降级策略属性测试
    - **Property 39: 智能路由降级策略**
    - **Validates: Requirements 13.4, 13.5, 13.6**

  - [x] 6.7 编写路由层选择一致性属性测试
    - **Property 46: 路由层选择一致性**
    - **Validates: Requirements 13.2, 13.3**

  - [x] 6.8 编写智能路由单元测试
    - 测试显式指定路由
    - 测试智能判断路由
    - 测试降级策略
    - 测试所有执行器不可用的情况
    - 测试默认提供商和层配置
    - _Requirements: 13.7, 13.8_

- [x] 7. 实现 AI API 执行器
  - [x] 7.1 创建 `AIAPIExecutor` 抽象基类
    - 定义抽象方法：`execute()`, `get_provider_name()`, `format_messages()`
    - 实现共享的初始化逻辑（api_key, model, timeout）
    - _Requirements: 14.1, 14.2, 14.3_

  - [x] 7.2 实现 `ClaudeAPIExecutor` 类
    - 实现 `__init__(api_key, model, timeout)` 方法，默认模型 claude-3-5-sonnet-20241022
    - 实现 `get_provider_name()` 方法，返回 "claude-api"
    - 实现 `format_messages(user_prompt, conversation_history)` 方法，格式化为 Claude API 消息格式
    - 实现 `execute(user_prompt, conversation_history, additional_params)` 方法
    - 使用 anthropic Python SDK 调用 Claude API
    - 支持对话历史上下文
    - 支持可选参数（temperature, max_tokens, system）
    - 处理 API 错误（APIError）
    - 处理超时错误
    - 返回 ExecutionResult
    - _Requirements: 14.1, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 15.1, 15.2, 15.5, 15.6_

  - [x] 7.3 实现 `GeminiAPIExecutor` 类
    - 实现 `__init__(api_key, model, timeout)` 方法，默认模型 gemini-2.0-flash-exp
    - 实现 `get_provider_name()` 方法，返回 "gemini-api"
    - 实现 `format_messages(user_prompt, conversation_history)` 方法，格式化为 Gemini API 消息格式（assistant→model）
    - 实现 `execute(user_prompt, conversation_history, additional_params)` 方法
    - 使用 google-generativeai Python SDK 调用 Gemini API
    - 支持对话历史上下文（使用 chat 模式）
    - 支持可选参数（temperature, max_output_tokens）
    - 处理 API 错误
    - 处理超时错误
    - 返回 ExecutionResult
    - _Requirements: 14.2, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 15.1, 15.3, 15.5, 15.6_

  - [x] 7.4 实现 `OpenAIAPIExecutor` 类
    - 实现 `__init__(api_key, model, timeout)` 方法，默认模型 gpt-4o
    - 实现 `get_provider_name()` 方法，返回 "openai-api"
    - 实现 `format_messages(user_prompt, conversation_history)` 方法，格式化为 OpenAI API 消息格式
    - 实现 `execute(user_prompt, conversation_history, additional_params)` 方法
    - 使用 openai Python SDK 调用 OpenAI API
    - 支持对话历史上下文
    - 支持可选参数（temperature, max_tokens）
    - 处理 API 错误（APIError）
    - 处理超时错误
    - 返回 ExecutionResult
    - _Requirements: 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 15.1, 15.4, 15.5, 15.6_

  - [x] 7.5 编写 Claude API 消息格式化属性测试
    - **Property 40: Claude API 消息格式化**
    - **Validates: Requirements 15.2**

  - [x] 7.6 编写 Gemini API 消息格式化属性测试
    - **Property 41: Gemini API 消息格式化**
    - **Validates: Requirements 15.3**

  - [x] 7.7 编写 OpenAI API 消息格式化属性测试
    - **Property 42: OpenAI API 消息格式化**
    - **Validates: Requirements 15.4**

  - [x] 7.8 编写 API 执行成功响应属性测试
    - **Property 43: API 执行成功响应**
    - **Validates: Requirements 14.7**

  - [x] 7.9 编写 API 执行错误处理属性测试
    - **Property 44: API 执行错误处理**
    - **Validates: Requirements 14.4, 14.5, 14.6**

  - [x] 7.10 编写 API 对话历史上下文属性测试
    - **Property 45: API 对话历史上下文**
    - **Validates: Requirements 14.8, 15.1, 15.6**

  - [x] 7.11 编写 API 执行器单元测试
    - 测试 API 密钥缺失错误
    - 测试超时处理
    - 测试 API 错误处理（配额超限、模型不可用等）
    - 测试对话历史格式化
    - 测试可选参数传递
    - _Requirements: 14.4, 14.5, 14.6, 14.10_

- [~] 8. 实现执行器可用性检查
  - [x] 8.1 创建 `ExecutorNotAvailableError` 异常类
    - 实现自定义异常类，包含 provider, layer, reason 字段
    - _Requirements: 16.3_

  - [~] 8.2 在 API 执行器中添加可用性检查
    - 实现 `is_available()` 方法，检查 API 密钥是否配置
    - 在初始化时检查可用性
    - _Requirements: 16.1, 16.3_

  - [~] 8.3 在 CLI 执行器中添加可用性检查
    - 实现 `is_available()` 方法，检查 CLI 工具是否安装和目标目录是否存在
    - 在初始化时检查可用性
    - _Requirements: 16.2, 16.3_

  - [~] 8.4 实现执行器可用性缓存
    - 缓存执行器可用性状态，避免重复检查
    - _Requirements: 16.5_

  - [~] 8.5 编写执行器可用性检查单元测试
    - 测试 API 密钥缺失检查
    - 测试 CLI 工具未安装检查
    - 测试目标目录不存在检查
    - 测试可用性缓存
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [~] 9. Checkpoint - 确保智能路由和 API 执行器测试通过
  - 确保所有测试通过，如有问题请询问用户

- [~] 10. 临时配置管理器
  - [~] 10.1 创建 `TempConfigManager` 类
    - 实现 `create_temp_dir()` 方法，使用 `tempfile.mkdtemp(prefix="claude_")`
    - 实现 `cleanup(temp_dir)` 方法，删除临时目录
    - 实现上下文管理器协议（`__enter__` 和 `__exit__`）
    - 在 `__enter__` 中设置 `CLAUDE_CONFIG_DIR` 环境变量
    - 在 `__exit__` 中清理临时目录（即使发生异常）
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [~] 10.2 编写临时目录生命周期属性测试
    - **Property 10: 临时目录生命周期**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [~] 10.3 编写临时目录清理单元测试
    - 测试正常清理
    - 测试异常情况下的清理
    - 测试清理失败的日志记录
    - _Requirements: 4.4_

- [~] 11. 实现 AI CLI 执行器接口和实现
  - [x] 11.1 创建 `AICLIExecutor` 抽象基类
    - 定义抽象方法：`execute()`, `verify_directory()`, `get_command_name()`, `build_command_args()`
    - 实现共享的初始化逻辑（target_dir, timeout）
    - _Requirements: 3.1, 3.2_

  - [x] 11.2 实现 `ClaudeCodeCLIExecutor` 类
    - 实现 `get_command_name()`，根据操作系统返回 `claude.cmd` 或 `claude`
    - 实现 `__init__()`，支持 `use_native_session` 参数和 `session_storage_path` 参数
    - 实现 `get_or_create_claude_session(user_id)` 方法，管理 Claude Code 会话
    - 实现 `build_command_args()`，构建 Claude CLI 命令参数
    - 支持 `--add-dir`, `-p/--prompt`, `--session` 等参数
    - 支持额外参数（`--json`, `--model`, `--max-tokens` 等）
    - 实现 `verify_directory()`，检查目标目录是否存在
    - 实现 `execute()`，执行命令并捕获输出
    - 实现 `update_session_id(user_id, session_id)` 方法，更新会话映射
    - 实现 `clear_session(user_id)` 方法，清除用户的 Claude Code 会话
    - 实现 `save_session_mappings()` 和 `load_session_mappings()` 方法（JSON 持久化）
    - 使用 `filelock` 库实现文件锁，避免并发写入冲突
    - 会话映射存储路径：`./data/executor_sessions.json`
    - 使用 UTF-8 编码处理输出
    - 设置超时时间（默认 600 秒）
    - 捕获 stdout 和 stderr
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 10.11, 10.12, 10.14_

  - [x] 11.3 实现 `GeminiCLIExecutor` 类
    - 实现 `get_command_name()`，返回 `gemini`
    - 实现 `__init__()`，支持 `use_native_session` 参数和 `session_storage_path` 参数
    - 实现 `get_or_create_gemini_session(user_id)` 方法，管理 Gemini CLI 会话
    - 实现 `build_command_args()`，构建 Gemini CLI 命令参数
    - 支持 `--cwd`, `--prompt`, `--session` 等参数
    - 支持额外参数（`--json`, `--model`, `--temperature` 等）
    - 实现 `verify_directory()`，检查目标目录是否存在
    - 实现 `execute()`，执行命令并捕获输出
    - 实现 `update_session_id(user_id, session_id)` 方法，更新会话映射
    - 实现 `clear_session(user_id)` 方法，清除用户的 Gemini CLI 会话
    - 实现 `save_session_mappings()` 和 `load_session_mappings()` 方法（JSON 持久化）
    - 使用 `filelock` 库实现文件锁，避免并发写入冲突
    - 会话映射存储路径：`./data/executor_sessions.json`（与 Claude 共享）
    - 使用 UTF-8 编码处理输出
    - 设置超时时间（默认 600 秒）
    - 捕获 stdout 和 stderr
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 10.11, 10.12, 10.13_

  - [~] 11.4 删除 `AIExecutorFactory` 类（已被智能路由器替代）
    - 移除旧的工厂模式代码
    - 更新相关引用
    - _Requirements: N/A_

  - [~] 11.5 编写目录验证属性测试
    - **Property 7: 目录验证**
    - **Validates: Requirements 3.1**

  - [~] 11.6 编写 Claude CLI 命令构造属性测试
    - **Property 8: Claude 命令构造完整性**
    - **Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.10**

  - [~] 11.7 编写 Gemini CLI 命令构造属性测试
    - **Property 9: Gemini 命令构造完整性**
    - **Validates: Requirements 3.3, 3.4, 3.5, 3.6**

  - [~] 11.8 编写命令输出捕获属性测试
    - **Property 11: 命令输出捕获**
    - **Validates: Requirements 3.9**

  - [x] 11.9 编写 AI CLI 执行器单元测试
    - 测试命令超时处理
    - 测试 AI CLI 未安装错误
    - 测试 UTF-8 编码处理
    - 测试额外参数传递
    - _Requirements: 3.7, 3.8_

  - [~] 11.10 编写 Claude Code CLI 原生会话属性测试
    - **Property 31: Claude Code CLI 原生会话使用**
    - **Property 33: Claude Code CLI 会话映射**
    - **Validates: Requirements 10.11, 10.12**

  - [~] 11.11 编写 Gemini CLI 原生会话属性测试
    - **Property 32: Gemini CLI 原生会话使用**
    - **Property 34: Gemini CLI 会话映射**
    - **Validates: Requirements 10.11, 10.13**

  - [~] 11.12 编写双层会话清除属性测试
    - **Property 35: 双层会话清除**
    - **Validates: Requirements 10.3, 10.14**

- [~] 12. Checkpoint - 确保核心组件测试通过
  - 确保所有测试通过，如有问题请询问用户

- [~] 13. 实现响应格式化器
  - [~] 13.1 创建 `ResponseFormatter` 类
    - 实现 `format_response(user_message, ai_output, error)` 方法
    - 成功响应格式：包含原始消息和 AI 输出
    - 错误响应格式：包含原始消息和错误信息
    - 使用清晰的分隔符（"\n\n" 和标题行）
    - 实现 `format_error(error_message)` 方法
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [~] 13.2 编写响应消息完整性属性测试
    - **Property 11: 响应消息完整性**
    - **Validates: Requirements 5.1, 5.2, 5.4**

  - [~] 13.3 编写响应格式化单元测试
    - 测试成功响应格式
    - 测试错误响应格式
    - 测试包含原始消息
    - _Requirements: 5.3_

- [~] 14. 实现消息发送器
  - [~] 14.1 创建 `MessageSender` 类
    - 实现 `send_message(chat_type, chat_id, message_id, content)` 方法
    - 实现 `send_new_message(chat_id, content)` 方法，调用 `im.v1.message.create`
    - 实现 `reply_message(message_id, content)` 方法，调用 `im.v1.message.reply`
    - 根据 chat_type 选择发送策略（p2p 使用新消息，其他使用回复）
    - 处理 API 调用失败，抛出包含 code, msg, log_id 的异常
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [~] 14.2 编写私聊消息发送属性测试
    - **Property 14: 私聊消息发送策略**
    - **Validates: Requirements 6.1**

  - [~] 14.3 编写群聊消息回复属性测试
    - **Property 15: 群聊消息回复策略**
    - **Validates: Requirements 6.2**

  - [~] 14.4 编写消息发送单元测试
    - 测试 API 调用失败处理
    - 测试异常信息包含 code, msg, log_id
    - _Requirements: 6.3_

- [~] 15. 实现日志记录策略
  - [~] 15.1 配置日志系统
    - 设置日志格式（时间戳、级别、模块、消息）
    - 配置日志级别（支持通过环境变量配置）
    - 支持 INFO, WARNING, ERROR, DEBUG 级别
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [~] 15.2 在各组件中添加日志记录
    - MessageHandler: 记录消息解析、引用消息检索
    - DeduplicationCache: 记录重复消息跳过
    - CommandParser: 记录命令解析结果
    - SmartRouter: 记录路由决策和降级
    - AIAPIExecutor: 记录 API 调用结果
    - AICLIExecutor: 记录 CLI 命令执行结果
    - MessageSender: 记录消息发送结果
    - 错误处理: 记录所有错误和上下文信息
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [~] 15.3 编写日志记录属性测试
    - **Property 16: 错误日志记录**
    - **Property 17: 重复消息日志记录**
    - **Property 18: AI 执行日志记录**
    - **Property 19: 引用消息检索日志记录**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

- [x] 16. 实现事件处理器和 WebSocket 客户端
  - [x] 16.1 创建 `EventHandler` 类
    - 实现 `register_message_receive_handler(handler)` 方法
    - 实现 `dispatch_event(event)` 方法
    - 使用 `lark_oapi.EventDispatcherHandler` 作为基础
    - _Requirements: 9.3_

  - [x] 16.2 创建 `WebSocketClient` 类
    - 实现 `__init__(app_id, app_secret, event_handler)` 方法
    - 实现 `start()` 方法，建立 WebSocket 连接
    - 实现 `stop()` 方法，关闭连接
    - 使用 `lark_oapi.ws.Client` 建立长连接
    - 注册消息接收事件处理器
    - 处理连接失败，记录错误日志
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 16.3 编写 WebSocket 事件路由属性测试
    - **Property 20: WebSocket 事件路由**
    - **Validates: Requirements 9.3**

  - [x] 16.4 编写 WebSocket 客户端单元测试
    - 测试连接建立
    - 测试事件处理器注册
    - 测试连接失败处理
    - _Requirements: 9.1, 9.2, 9.5_

- [x] 17. 实现 SSL 证书配置
  - [x] 17.1 创建 SSL 配置函数
    - 实现 `configure_ssl()` 函数
    - 设置 `SSL_CERT_FILE` 环境变量为 certifi 证书路径
    - 清除 `SSL_CERT_DIR` 环境变量
    - 在应用启动时调用
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 17.2 编写 SSL 配置单元测试
    - 测试 SSL_CERT_FILE 设置
    - 测试 SSL_CERT_DIR 清除
    - _Requirements: 8.1, 8.2_

- [x] 18. 集成所有组件并重构主程序
  - [x] 18.1 创建主应用类 `FeishuBot`
    - 初始化所有组件（配置、缓存、处理器、发送器、会话管理器、命令解析器、执行器注册表、智能路由器等）
    - 初始化并注册 AI API 执行器（Claude API、Gemini API、OpenAI API）
    - 初始化并注册 AI CLI 执行器（Claude Code CLI、Gemini CLI）
    - 为每个执行器设置元数据（名称、版本、能力、命令前缀、优先级等）
    - 实现消息接收处理流程：
      1. 消息去重
      2. 消息解析
      3. 命令解析（识别 AI 提供商和执行层）
      4. 会话命令检查（/new, /session, /history）
      5. 智能路由（通过 ExecutorRegistry 选择执行器）
      6. AI 执行（API 或 CLI）
      7. 响应格式化
      8. 消息发送
      9. 会话历史更新
    - 使用统一的会话策略：
      - API 层：传递对话历史给 API
      - CLI 层：使用原生会话（传递 user_id 给 executor）
      - 飞书机器人会话用于显示历史记录和会话信息
    - 处理 `/new` 命令时，清除飞书机器人会话和 AI CLI 会话
    - 实现完整的错误处理流程（包括路由降级）
    - 支持动态添加新 Agent（通过配置文件或 API）
    - _Requirements: 所有需求_

  - [x] 18.2 重构 `lark_bot.py` 主程序
    - 使用新的模块化组件替换原有代码
    - 保持向后兼容（如果需要）
    - 添加命令行参数支持（配置文件路径、日志级别等）
    - 添加会话清理定时任务（清理过期会话）
    - _Requirements: 所有需求_

  - [x] 18.3 编写集成测试
    - 测试完整的消息处理流程
    - 测试命令解析和智能路由流程
    - 测试 API 层执行流程（Claude API、Gemini API、OpenAI API）
    - 测试 CLI 层执行流程（Claude Code CLI、Gemini CLI）
    - 测试路由降级流程
    - 测试会话管理流程（创建、轮换、命令处理）
    - 测试 API 层对话历史传递
    - 测试 CLI 层原生会话使用
    - 测试双层会话清除
    - 测试错误处理流程
    - 测试不同聊天类型的消息发送
    - _Requirements: 所有需求_

- [~] 19. 最终检查点 - 确保所有测试通过
  - 运行所有单元测试和属性测试
  - 验证代码覆盖率
  - 确保所有需求都有对应的测试
  - 如有问题请询问用户

- [~] 20. 创建文档和示例
  - [~] 20.1 更新 README.md
    - 添加安装说明
    - 添加配置说明（包括 AI API 密钥、会话管理配置、默认提供商和层配置）
    - 添加使用示例（包括命令前缀使用、会话命令使用）
    - 添加智能路由功能说明（显式指定 vs 智能判断）
    - 添加 AI API 层和 CLI 层的区别说明
    - 添加会话管理功能说明（/new, /session, /history 命令）
    - 添加会话管理架构说明（API 层对话历史 vs CLI 层原生会话）
    - 添加可扩展性说明：
      - 如何添加新的 AI Agent（实现接口、注册到 ExecutorRegistry）
      - 如何添加新的命令前缀
      - 提供 Qwen Code 等 Agent 的集成示例
    - 添加参考文档链接：
      - Claude API: https://docs.anthropic.com/en/api/messages
      - Gemini API: https://ai.google.dev/api/python/google/generativeai
      - OpenAI API: https://platform.openai.com/docs/api-reference/chat
      - Claude Code CLI: https://code.claude.com/docs/zh-CN/cli-reference, https://code.claude.com/docs/
      - Gemini CLI: https://geminicli.com/docs/cli/session-management/, https://geminicli.com/docs/cli/headless/
      - 飞书 API: https://open.feishu.cn/api-explorer, https://open.feishu.cn/document/server-side-sdk/python--sdk
    - 添加故障排查指南

  - [~] 20.2 创建 `.env.example` 文件
    - 列出所有配置项（包括 AI API 密钥、会话存储路径、最大消息数、超时时间、默认提供商和层）
    - 提供示例值和说明

  - [~] 20.3 添加代码注释和文档字符串
    - 为所有公共类和方法添加文档字符串
    - 添加类型注解
    - 添加使用示例（特别是智能路由、会话管理和双层会话策略相关的）
    - 在代码中添加参考文档链接

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求编号，确保可追溯性
- 检查点任务确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边界情况
- 使用 Python Hypothesis 库进行属性测试，每个测试至少运行 100 次迭代
