# Requirements Document

## Introduction

飞书 AI 机器人是一个集成系统，允许飞书用户通过消息与本地 AI 智能体（Claude Code 或 Gemini CLI）交互。机器人接收飞书消息，在指定的代码仓库目录中执行各种任务，并将 AI 的执行结果返回给用户。支持的 AI 智能体包括 Claude Code 和 Gemini CLI，它们都能够执行代码分析、文件操作、问题解答、代码生成、调试协助等多种任务。该系统旨在提高开发团队的协作效率，使团队成员能够通过飞书直接与 AI 助手交互，获取代码相关的帮助和自动化支持。

## Glossary

- **Feishu_Bot**: 飞书机器人系统，负责接收和响应飞书消息
- **Claude_Code**: Claude Code AI 智能体，能够执行代码分析、文件操作、问题解答、代码生成等多种任务
- **Message_Handler**: 消息处理器，负责解析和处理接收到的飞书消息
- **Deduplication_Cache**: 消息去重缓存，防止重复处理相同消息
- **Target_Directory**: 目标代码仓库目录，Claude 执行操作的工作目录
- **Quoted_Message**: 引用消息，用户在飞书中引用的上一条消息
- **Session**: 会话，表示用户与 AI Agent 的一次连续对话上下文
- **Session_Manager**: 会话管理器，负责创建、存储和管理用户会话
- **Conversation_History**: 对话历史，存储会话中的所有消息和响应
- **Command_Parser**: 命令解析器，负责解析用户消息中的 AI 提供商指令
- **Smart_Router**: 智能路由器，根据用户指令和消息内容决定使用 API 层还是 CLI 层
- **AI_API_Layer**: AI API 层，直接调用 AI 模型 API（Claude API、Gemini API、OpenAI API）
- **AI_CLI_Layer**: AI CLI 层，调用本地 AI CLI 工具（Claude Code CLI、Gemini CLI）
- **Execution_Layer**: 执行层，指 API 层或 CLI 层

## Requirements

### Requirement 1: 消息接收与解析

**User Story:** 作为飞书用户，我希望机器人能够接收并正确解析我发送的消息，以便我能够与 AI 智能体进行交互。

#### Acceptance Criteria

1. WHEN a user sends a text message to Feishu_Bot, THEN THE Message_Handler SHALL extract the text content from the message
2. WHEN a user sends a quoted message (reply to another message), THEN THE Message_Handler SHALL retrieve both the quoted message content and the current message content
3. WHEN a user sends a non-text message type, THEN THE Feishu_Bot SHALL return an error message indicating only text messages are supported
4. WHEN retrieving a quoted message, THEN THE Message_Handler SHALL combine the quoted content and current content in a readable format
5. WHEN message parsing fails, THEN THE Feishu_Bot SHALL return a descriptive error message to the user

### Requirement 2: 消息去重机制

**User Story:** 作为系统管理员，我希望机器人能够防止重复处理相同的消息，以避免资源浪费和重复响应。

#### Acceptance Criteria

1. WHEN a message is received, THEN THE Deduplication_Cache SHALL check if the message ID already exists in the cache
2. WHEN a message ID is found in the cache, THEN THE Feishu_Bot SHALL skip processing and log the duplicate detection
3. WHEN a new message is processed, THEN THE Deduplication_Cache SHALL add the message ID to the cache
4. WHILE the cache size exceeds 1000 entries, THEN THE Deduplication_Cache SHALL automatically remove the oldest entries
5. THE Deduplication_Cache SHALL maintain message IDs in insertion order

### Requirement 3: AI 智能体执行

**User Story:** 作为飞书用户，我希望机器人能够调用 AI 智能体（Claude Code 或 Gemini CLI）执行各种任务并回答我的问题，以便我获得 AI 助手的帮助。

#### Acceptance Criteria

1. WHEN executing Claude_Code, THEN THE Feishu_Bot SHALL verify the Target_Directory exists before execution
2. WHEN the Target_Directory does not exist, THEN THE Feishu_Bot SHALL return an error message indicating the directory is not found
3. WHEN executing Claude_Code, THEN THE Feishu_Bot SHALL use the `--add-dir` flag to specify the Target_Directory for context
4. WHEN executing Claude_Code, THEN THE Feishu_Bot SHALL use the `-p` or `--prompt` flag to pass the user's question
5. WHEN executing Claude_Code, THEN THE Feishu_Bot SHALL set the working directory to Target_Directory
6. WHEN executing Claude_Code, THEN THE Feishu_Bot SHALL use UTF-8 encoding to capture output
7. WHEN Claude_Code execution exceeds 600 seconds, THEN THE Feishu_Bot SHALL terminate the process and return a timeout error
8. WHEN Claude_Code is not found in the system PATH, THEN THE Feishu_Bot SHALL return an error message indicating Claude Code is not installed
9. WHEN Claude_Code execution completes, THEN THE Feishu_Bot SHALL capture both stdout and stderr output
10. THE Feishu_Bot SHALL use `claude.cmd` on Windows systems and `claude` on Unix-like systems

### Requirement 4: 临时配置管理

**User Story:** 作为系统管理员，我希望机器人使用临时目录存储 Claude Code 配置，以避免权限问题和配置冲突。

#### Acceptance Criteria

1. WHEN executing Claude_Code, THEN THE Feishu_Bot SHALL create a temporary directory with prefix "claude_"
2. WHEN the temporary directory is created, THEN THE Feishu_Bot SHALL set the CLAUDE_CONFIG_DIR environment variable to point to it
3. WHEN Claude_Code execution completes (success or failure), THEN THE Feishu_Bot SHALL delete the temporary directory
4. IF temporary directory cleanup fails, THEN THE Feishu_Bot SHALL log the error but continue processing

### Requirement 5: 响应消息格式化

**User Story:** 作为飞书用户，我希望机器人返回的消息格式清晰，包含我的原始问题和 AI 的回答，以便我理解上下文。

#### Acceptance Criteria

1. WHEN sending a response, THEN THE Feishu_Bot SHALL include the original user message in the response
2. WHEN Claude_Code execution completes, THEN THE Feishu_Bot SHALL include Claude's output in the response
3. WHEN errors occur, THEN THE Feishu_Bot SHALL include descriptive error messages in the response
4. THE Feishu_Bot SHALL format the response message with clear section separators

### Requirement 6: 消息发送策略

**User Story:** 作为飞书用户，我希望机器人能够根据聊天类型选择合适的回复方式，以符合飞书的使用习惯。

#### Acceptance Criteria

1. WHEN the message is from a private chat (p2p), THEN THE Feishu_Bot SHALL send a new message to the chat
2. WHEN the message is from a group chat, THEN THE Feishu_Bot SHALL reply to the original message
3. WHEN sending a message fails, THEN THE Feishu_Bot SHALL raise an exception with error code, message, and log ID
4. THE Feishu_Bot SHALL use the Feishu OpenAPI to send all messages

### Requirement 7: 错误处理与日志

**User Story:** 作为系统管理员，我希望系统能够记录详细的错误信息和操作日志，以便排查问题和监控系统运行状态。

#### Acceptance Criteria

1. WHEN any operation fails, THEN THE Feishu_Bot SHALL log the error message with context information
2. WHEN processing a duplicate message, THEN THE Feishu_Bot SHALL log the message ID and skip reason
3. WHEN Claude_Code executes, THEN THE Feishu_Bot SHALL log the execution result
4. WHEN retrieving quoted messages, THEN THE Message_Handler SHALL log the retrieval process and results

### Requirement 8: SSL 证书配置

**User Story:** 作为系统管理员，我希望系统能够正确配置 SSL 证书，以确保与飞书 API 的安全通信。

#### Acceptance Criteria

1. WHEN the Feishu_Bot starts, THEN THE system SHALL set SSL_CERT_FILE environment variable to the certifi certificate bundle path
2. WHEN the Feishu_Bot starts, THEN THE system SHALL clear the SSL_CERT_DIR environment variable
3. THE Feishu_Bot SHALL use the configured SSL certificates for all HTTPS requests to Feishu API

### Requirement 9: 长连接事件监听

**User Story:** 作为系统管理员，我希望机器人能够通过长连接实时接收飞书消息，以提供即时响应。

#### Acceptance Criteria

1. WHEN the Feishu_Bot starts, THEN THE system SHALL establish a WebSocket connection to Feishu
2. WHEN the WebSocket connection is established, THEN THE Feishu_Bot SHALL register the message receive event handler
3. WHEN a message event is received through WebSocket, THEN THE Feishu_Bot SHALL invoke the registered event handler
4. THE Feishu_Bot SHALL maintain the WebSocket connection continuously during runtime
5. WHEN the WebSocket connection fails, THEN THE Feishu_Bot SHALL log the error with DEBUG level logging enabled

### Requirement 10: 会话管理

**User Story:** 作为飞书用户，我希望机器人能够记住我之前的对话内容，以便进行连续的上下文对话，并且我可以随时开启新的会话。

#### Acceptance Criteria

1. WHEN a user sends the first message, THEN THE Session_Manager SHALL create a new Session for that user
2. WHEN a user sends subsequent messages, THEN THE Session_Manager SHALL retrieve the existing Session and append the new message to Conversation_History
3. WHEN a user sends a command to start a new session (e.g., "/new" or "新会话"), THEN THE Session_Manager SHALL create a new Session and archive the old one
4. WHEN executing Claude_Code with an active Session, THEN THE Feishu_Bot SHALL include the Conversation_History in the context
5. WHEN a Session exceeds a maximum message count (e.g., 50 messages), THEN THE Session_Manager SHALL automatically create a new Session
6. WHEN a Session is inactive for a specified duration (e.g., 24 hours), THEN THE Session_Manager SHALL expire the Session
7. WHEN a user sends a command to view session info (e.g., "/session" or "会话信息"), THEN THE Feishu_Bot SHALL return the current session ID, message count, and creation time
8. THE Session_Manager SHALL store sessions persistently to survive bot restarts
9. THE Session_Manager SHALL support multiple concurrent sessions for different users
10. WHEN including Conversation_History in AI context, THEN THE Feishu_Bot SHALL format it as a readable conversation thread
11. WHERE the AI provider supports native session management (e.g., Claude Code CLI, Gemini CLI), THEN THE Feishu_Bot SHALL use the AI's native session feature instead of manually passing conversation history
12. WHEN using Claude Code CLI with native session support, THEN THE Feishu_Bot SHALL maintain a mapping between user IDs and Claude session IDs
13. WHEN using Gemini CLI with native session support, THEN THE Feishu_Bot SHALL maintain a mapping between user IDs and Gemini session IDs
14. WHEN a user sends a "/new" command, THEN THE Feishu_Bot SHALL clear both the bot session and the AI CLI session (for both Claude Code and Gemini CLI)


### Requirement 11: 命令解析与 AI 提供商识别

**User Story:** 作为飞书用户，我希望能够通过命令前缀指定使用哪个 AI 提供商和执行方式，以便我根据任务类型选择最合适的 AI。

#### Acceptance Criteria

1. WHEN a user sends a message with "@claude-api" or "@claude" prefix, THEN THE Command_Parser SHALL extract "claude" as provider and "api" as execution layer
2. WHEN a user sends a message with "@gemini-api" or "@gemini" prefix, THEN THE Command_Parser SHALL extract "gemini" as provider and "api" as execution layer
3. WHEN a user sends a message with "@openai" or "@gpt" prefix, THEN THE Command_Parser SHALL extract "openai" as provider and "api" as execution layer
4. WHEN a user sends a message with "@claude-cli" or "@code" prefix, THEN THE Command_Parser SHALL extract "claude" as provider and "cli" as execution layer
5. WHEN a user sends a message with "@gemini-cli" prefix, THEN THE Command_Parser SHALL extract "gemini" as provider and "cli" as execution layer
6. WHEN a user sends a message without any AI provider prefix, THEN THE Command_Parser SHALL mark the command as not explicit (explicit=false)
7. WHEN extracting provider prefix, THEN THE Command_Parser SHALL remove the prefix from the message content
8. THE Command_Parser SHALL support case-insensitive prefix matching

### Requirement 12: CLI 关键词智能检测

**User Story:** 作为飞书用户，我希望系统能够自动识别我的消息是否需要访问代码库，以便自动选择合适的执行方式。

#### Acceptance Criteria

1. WHEN a message contains code-related keywords (e.g., "查看代码", "view code", "分析代码", "analyze code"), THEN THE Command_Parser SHALL detect it as requiring CLI layer
2. WHEN a message contains file operation keywords (e.g., "修改文件", "modify file", "读取文件", "read file"), THEN THE Command_Parser SHALL detect it as requiring CLI layer
3. WHEN a message contains command execution keywords (e.g., "执行命令", "execute command", "运行脚本", "run script"), THEN THE Command_Parser SHALL detect it as requiring CLI layer
4. WHEN a message contains project analysis keywords (e.g., "分析项目", "analyze project", "项目结构", "project structure"), THEN THE Command_Parser SHALL detect it as requiring CLI layer
5. WHEN a message contains codebase keywords (e.g., "代码库", "codebase"), THEN THE Command_Parser SHALL detect it as requiring CLI layer
6. WHEN a message does not contain any CLI keywords, THEN THE Command_Parser SHALL return false for CLI detection
7. THE Command_Parser SHALL support both Chinese and English keywords

### Requirement 13: 智能路由决策

**User Story:** 作为系统管理员，我希望系统能够根据用户指令和消息内容智能选择 API 层或 CLI 层，以提供最佳的响应速度和功能支持。

#### Acceptance Criteria

1. WHEN a user explicitly specifies an AI provider and execution layer, THEN THE Smart_Router SHALL use the specified executor without intelligent judgment
2. WHEN a user does not specify execution layer and the message contains CLI keywords, THEN THE Smart_Router SHALL route to CLI layer
3. WHEN a user does not specify execution layer and the message does not contain CLI keywords, THEN THE Smart_Router SHALL route to the default layer (API layer)
4. WHEN the specified executor is not available, THEN THE Smart_Router SHALL attempt to fallback to another layer (API→CLI or CLI→API)
5. WHEN fallback fails (all executors unavailable), THEN THE Smart_Router SHALL return an error message indicating no available executor
6. WHEN fallback occurs, THEN THE Smart_Router SHALL log the fallback action with provider, original layer, and fallback layer
7. THE Smart_Router SHALL support configurable default provider (default: claude)
8. THE Smart_Router SHALL support configurable default layer (default: api)

### Requirement 14: AI API 执行

**User Story:** 作为飞书用户，我希望机器人能够调用 AI API（Claude API、Gemini API、OpenAI API）快速回答一般问题，以获得更快的响应速度。

#### Acceptance Criteria

1. WHEN executing Claude API, THEN THE Claude_API_Executor SHALL use the Anthropic API endpoint
2. WHEN executing Gemini API, THEN THE Gemini_API_Executor SHALL use the Google AI API endpoint
3. WHEN executing OpenAI API, THEN THE OpenAI_API_Executor SHALL use the OpenAI API endpoint
4. WHEN an API key is not configured, THEN THE AI_API_Executor SHALL return an error message indicating missing API key
5. WHEN an API request times out (exceeds 60 seconds), THEN THE AI_API_Executor SHALL return a timeout error
6. WHEN an API returns an error (e.g., quota exceeded, model unavailable), THEN THE AI_API_Executor SHALL capture the error and return a descriptive error message
7. WHEN an API call succeeds, THEN THE AI_API_Executor SHALL extract the response content and return it in ExecutionResult
8. THE AI_API_Executor SHALL support passing conversation history as context
9. THE AI_API_Executor SHALL format conversation history according to each API's message format requirements
10. THE AI_API_Executor SHALL support configurable model selection (e.g., claude-3-5-sonnet, gpt-4o, gemini-2.0-flash)

### Requirement 15: API 对话历史管理

**User Story:** 作为飞书用户，我希望使用 API 层时也能保持对话上下文，以便进行连续的多轮对话。

#### Acceptance Criteria

1. WHEN executing an API call with conversation history, THEN THE AI_API_Executor SHALL include all historical messages in the API request
2. WHEN formatting conversation history for Claude API, THEN THE AI_API_Executor SHALL use "user" and "assistant" roles
3. WHEN formatting conversation history for Gemini API, THEN THE AI_API_Executor SHALL convert "assistant" role to "model" role
4. WHEN formatting conversation history for OpenAI API, THEN THE AI_API_Executor SHALL use "user" and "assistant" roles
5. WHEN the conversation history is empty, THEN THE AI_API_Executor SHALL only send the current user message
6. THE AI_API_Executor SHALL maintain message order consistent with the session's conversation history

### Requirement 16: 执行器可用性检查

**User Story:** 作为系统管理员，我希望系统能够检查执行器是否可用，以便在执行器不可用时提供友好的错误提示或自动降级。

#### Acceptance Criteria

1. WHEN checking API executor availability, THEN THE system SHALL verify the API key is configured
2. WHEN checking CLI executor availability, THEN THE system SHALL verify the CLI tool is installed and the target directory exists
3. WHEN an executor is not available, THEN THE system SHALL raise an ExecutorNotAvailableError
4. WHEN all executors are unavailable, THEN THE system SHALL return an error message listing unavailable executors and reasons
5. THE system SHALL cache executor availability status to avoid repeated checks

### Requirement 17: 配置管理增强

**User Story:** 作为系统管理员，我希望能够配置 AI API 密钥和默认执行策略，以便灵活管理不同的 AI 提供商。

#### Acceptance Criteria

1. THE system SHALL support configuring Claude API key via environment variable or configuration file
2. THE system SHALL support configuring Gemini API key via environment variable or configuration file
3. THE system SHALL support configuring OpenAI API key via environment variable or configuration file
4. THE system SHALL support configuring default AI provider (default: claude)
5. THE system SHALL support configuring default execution layer (default: api)
6. THE system SHALL support configuring API request timeout (default: 60 seconds)
7. WHEN an API key is not configured, THEN THE corresponding API executor SHALL not be initialized
8. THE system SHALL validate configuration on startup and log any missing or invalid configurations


### Requirement 18: 存储层管理

**User Story:** 作为系统管理员，我希望系统能够持久化存储会话数据和执行器会话映射，以便机器人重启后能够恢复对话上下文。

#### Acceptance Criteria

1. WHEN saving session data, THEN THE system SHALL use JSON format for storage
2. WHEN saving session data, THEN THE system SHALL use file locks to prevent concurrent write conflicts
3. WHEN the application starts, THEN THE system SHALL load all session data from storage
4. WHEN a session is updated, THEN THE system SHALL automatically save the session data
5. WHEN archiving old sessions, THEN THE system SHALL save them to the archived_sessions directory with filename format `{user_id}_{session_id}_{timestamp}.json`
6. WHEN saving executor session mappings, THEN THE system SHALL store Claude CLI and Gemini CLI session mappings in the same JSON file
7. WHEN an executor session mapping is updated, THEN THE system SHALL automatically save the mapping
8. THE system SHALL support configurable storage paths for sessions and executor mappings
9. THE system SHALL create storage directories if they do not exist
10. WHEN storage operations fail, THEN THE system SHALL log the error and continue operation (graceful degradation)
11. THE system SHALL support periodic cleanup of expired sessions (configurable interval, default: hourly)
12. THE system SHALL limit single file size to prevent performance issues (recommended < 10MB)
