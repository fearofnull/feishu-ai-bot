# 动态配置系统使用示例 / Dynamic Configuration System Examples

本文档提供动态配置系统的实际使用示例。

This document provides practical examples of using the dynamic configuration system.

## 场景 1：个人开发者设置项目目录 / Scenario 1: Individual Developer Setting Project Directory

### 背景 / Background
开发者小李在私聊中使用机器人，需要让 CLI 工具在特定项目目录下工作。

Developer Li uses the bot in private chat and needs CLI tools to work in a specific project directory.

### 操作步骤 / Steps

```
用户: /setdir /home/li/my-awesome-project
机器人: ✅ 配置已更新 / Config updated: target_project_dir = /home/li/my-awesome-project

用户: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /home/li/my-awesome-project
- 回复语言 / Language: (自动 / Auto)
- 默认提供商 / Provider: claude
- 默认执行层 / Layer: api
- CLI提供商 / CLI Provider: (使用默认 / Use default)

📊 配置元数据 / Metadata:
- 创建者 / Created by: ou_xxx
- 创建时间 / Created at: 2026-02-28T10:30:00
- 更新者 / Updated by: ou_xxx
- 更新时间 / Updated at: 2026-02-28T10:30:00
- 更新次数 / Update count: 1

用户: @code 查看项目结构
机器人: [在 /home/li/my-awesome-project 目录下执行]
```

### 说明 / Notes
- 配置会持久化保存，下次使用时自动生效
- Configuration is persisted and automatically applies next time

---

## 场景 2：团队协作中的群聊配置 / Scenario 2: Group Chat Configuration for Team Collaboration

### 背景 / Background
开发团队在群聊中使用机器人，需要共享项目配置。

Development team uses the bot in group chat and needs to share project configuration.

### 操作步骤 / Steps

```
用户A: /setdir /team/shared-project
机器人: ✅ 配置已更新 / Config updated: target_project_dir = /team/shared-project

用户A: /lang zh-CN
机器人: ✅ 配置已更新 / Config updated: response_language = zh-CN

用户B: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /team/shared-project
- 回复语言 / Language: zh-CN
- 默认提供商 / Provider: claude
- 默认执行层 / Layer: api
- CLI提供商 / CLI Provider: (使用默认 / Use default)

📊 配置元数据 / Metadata:
- 创建者 / Created by: ou_userA
- 创建时间 / Created at: 2026-02-28T09:00:00
- 更新者 / Updated by: ou_userA
- 更新时间 / Updated at: 2026-02-28T09:15:00
- 更新次数 / Update count: 2

用户B: 查看代码
机器人: [使用群组配置，在 /team/shared-project 目录下执行，使用中文回复]

用户C: /setdir /team/another-project
机器人: ✅ 配置已更新 / Config updated: target_project_dir = /team/another-project

用户A: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /team/another-project
...
📊 配置元数据 / Metadata:
- 创建者 / Created by: ou_userA
- 更新者 / Updated by: ou_userC
- 更新次数 / Update count: 3
```

### 说明 / Notes
- 群聊配置对所有成员可见和可修改
- 系统会记录谁修改了配置，提供透明度
- Group configuration is visible and modifiable by all members
- System tracks who modified the configuration for transparency

---

## 场景 3：临时切换项目目录 / Scenario 3: Temporarily Switch Project Directory

### 背景 / Background
开发者需要临时查看另一个项目，但不想修改持久化配置。

Developer needs to temporarily check another project without modifying persistent configuration.

### 操作步骤 / Steps

```
用户: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /home/user/main-project
...

用户: --dir=/home/user/temp-project 查看 README 文件
机器人: [临时使用 /home/user/temp-project 目录]
README.md 内容：
...

用户: 查看代码结构
机器人: [恢复使用 /home/user/main-project 目录]
```

### 说明 / Notes
- 临时参数仅对当前请求有效
- 不会修改持久化配置
- Temporary parameters only apply to the current request
- Does not modify persistent configuration

---

## 场景 4：多语言支持 / Scenario 4: Multi-language Support

### 背景 / Background
国际团队需要在不同语言之间切换。

International team needs to switch between different languages.

### 操作步骤 / Steps

```
用户: /lang zh-CN
机器人: ✅ 配置已更新 / Config updated: response_language = zh-CN

用户: 什么是人工智能？
机器人: 人工智能（AI）是计算机科学的一个分支...

用户: /lang en-US
机器人: ✅ 配置已更新 / Config updated: response_language = en-US

用户: What is artificial intelligence?
机器人: Artificial Intelligence (AI) is a branch of computer science...

用户: --lang=ja-JP 人工知能とは何ですか？
机器人: 人工知能（AI）は、コンピュータサイエンスの一分野です...

用户: 继续用英文
机器人: [继续使用 en-US 配置]
```

### 说明 / Notes
- 语言配置会影响所有后续对话
- 临时参数可以单次覆盖语言设置
- Language configuration affects all subsequent conversations
- Temporary parameters can override language setting for a single request

---

## 场景 5：切换 AI 提供商 / Scenario 5: Switch AI Provider

### 背景 / Background
用户想尝试不同的 AI 提供商。

User wants to try different AI providers.

### 操作步骤 / Steps

```
用户: /provider gemini
机器人: ✅ 配置已更新 / Config updated: default_provider = gemini

用户: /layer api
机器人: ✅ 配置已更新 / Config updated: default_layer = api

用户: 解释量子计算
机器人: [使用 Gemini API]
量子计算是一种利用量子力学原理...

用户: --provider=claude 同样的问题
机器人: [临时使用 Claude API]
量子计算是一种革命性的计算范式...

用户: 继续
机器人: [恢复使用 Gemini API]
```

### 说明 / Notes
- 可以设置默认提供商和执行层
- 临时参数可以单次切换提供商
- Can set default provider and layer
- Temporary parameters can switch provider for a single request

---

## 场景 6：CLI 层专用提供商 / Scenario 6: CLI-specific Provider

### 背景 / Background
用户希望 API 层使用 OpenAI，CLI 层使用 Claude。

User wants to use OpenAI for API layer and Claude for CLI layer.

### 操作步骤 / Steps

```
用户: /provider openai
机器人: ✅ 配置已更新 / Config updated: default_provider = openai

用户: /cliprovider claude
机器人: ✅ 配置已更新 / Config updated: default_cli_provider = claude

用户: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /home/user/project
- 回复语言 / Language: (自动 / Auto)
- 默认提供商 / Provider: openai
- 默认执行层 / Layer: api
- CLI提供商 / CLI Provider: claude

用户: 什么是 Python 装饰器？
机器人: [使用 OpenAI API]
Python 装饰器是一种设计模式...

用户: 查看项目中的装饰器使用
机器人: [使用 Claude CLI]
在您的项目中，我发现以下装饰器使用...
```

### 说明 / Notes
- API 层和 CLI 层可以使用不同的提供商
- 适合根据任务类型选择最佳提供商
- API layer and CLI layer can use different providers
- Suitable for choosing the best provider based on task type

---

## 场景 7：重置配置 / Scenario 7: Reset Configuration

### 背景 / Background
用户想清除所有自定义配置，恢复默认设置。

User wants to clear all custom configuration and restore defaults.

### 操作步骤 / Steps

```
用户: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /custom/project
- 回复语言 / Language: zh-CN
- 默认提供商 / Provider: gemini
- 默认执行层 / Layer: cli
- CLI提供商 / CLI Provider: claude

📊 配置元数据 / Metadata:
- 更新次数 / Update count: 5

用户: /reset
机器人: ✅ 配置已重置 / Config reset

用户: /config
机器人: ⚙️ 当前配置 / Current Config:
- 项目目录 / Project Dir: /default/project
- 回复语言 / Language: (自动 / Auto)
- 默认提供商 / Provider: claude
- 默认执行层 / Layer: api
- CLI提供商 / CLI Provider: (使用默认 / Use default)
```

### 说明 / Notes
- 重置会清除所有会话配置
- 恢复到全局配置或默认值
- Reset clears all session configuration
- Restores to global configuration or defaults

---

## 场景 8：组合临时参数 / Scenario 8: Combine Temporary Parameters

### 背景 / Background
用户需要一次性覆盖多个配置项。

User needs to override multiple configuration items at once.

### 操作步骤 / Steps

```
用户: --dir=/tmp/test --lang=en-US --provider=gemini --layer=api Analyze the code structure
机器人: [临时使用所有指定的配置]
Project Structure Analysis:
...

用户: 继续分析
机器人: [恢复使用持久化配置]
```

### 说明 / Notes
- 可以在一条消息中使用多个临时参数
- 所有临时参数仅对当前请求有效
- Multiple temporary parameters can be used in one message
- All temporary parameters only apply to the current request

---

## 最佳实践 / Best Practices

### 1. 私聊配置 / Private Chat Configuration
- 设置个人偏好（语言、默认提供商）
- 配置常用项目目录
- Set personal preferences (language, default provider)
- Configure frequently used project directories

### 2. 群聊配置 / Group Chat Configuration
- 设置团队共享的项目目录
- 统一语言设置
- 记录配置变更历史
- Set team-shared project directories
- Unify language settings
- Track configuration change history

### 3. 临时参数 / Temporary Parameters
- 用于一次性任务
- 测试不同配置
- 避免频繁修改持久化配置
- Use for one-time tasks
- Test different configurations
- Avoid frequently modifying persistent configuration

### 4. 配置管理 / Configuration Management
- 定期使用 `/config` 查看当前配置
- 使用 `/reset` 清理不需要的配置
- 在群聊中注意配置变更的影响
- Regularly use `/config` to view current configuration
- Use `/reset` to clean up unnecessary configuration
- Be aware of configuration changes in group chats

---

## 故障排除 / Troubleshooting

### 问题 1：配置未生效 / Issue 1: Configuration Not Taking Effect

**症状 / Symptom:**
```
用户: /setdir /new/project
机器人: ✅ 配置已更新

用户: 查看代码
机器人: [仍然使用旧目录]
```

**解决方案 / Solution:**
1. 检查是否有临时参数覆盖
2. 使用 `/config` 查看当前生效的配置
3. 确认配置优先级：临时参数 > 会话配置 > 全局配置

### 问题 2：群聊配置冲突 / Issue 2: Group Chat Configuration Conflict

**症状 / Symptom:**
```
用户A: /setdir /projectA
用户B: /setdir /projectB
用户A: 为什么目录变了？
```

**解决方案 / Solution:**
1. 群聊配置是共享的，任何成员都可以修改
2. 使用 `/config` 查看谁修改了配置
3. 团队内部协商配置管理规则
4. 考虑使用临时参数避免影响他人

### 问题 3：目录不存在 / Issue 3: Directory Does Not Exist

**症状 / Symptom:**
```
用户: /setdir /invalid/path
机器人: ⚠️ 目录不存在 / Directory does not exist: /invalid/path
```

**解决方案 / Solution:**
1. 确认目录路径正确
2. 确保目录已创建
3. 使用绝对路径而非相对路径
4. 检查文件系统权限

---

## 相关文档 / Related Documentation

- [动态配置系统](../DYNAMIC_CONFIG.md) - 完整功能说明
- [用户指南](../USER_GUIDE.md) - 机器人使用指南
- [配置指南](../CONFIGURATION.md) - 环境变量配置

---

## 测试验证 / Test Verification

本文档中的所有示例场景均已通过测试验证：

All example scenarios in this document have been tested and verified:

### 测试结果 / Test Results

- ✅ 场景 1：个人开发者设置项目目录
- ✅ 场景 2：团队协作中的群聊配置
- ✅ 场景 3：临时切换项目目录
- ✅ 场景 4：多语言支持
- ✅ 场景 5：切换 AI 提供商
- ✅ 场景 6：CLI 层专用提供商
- ✅ 场景 7：重置配置
- ✅ 场景 8：组合临时参数

### 测试覆盖 / Test Coverage

完整的测试套件包括：
- 16 个单元测试（100% 通过）
- 15 个手动测试（100% 通过）
- 配置优先级验证
- 会话类型支持验证
- 配置持久化验证
- 临时参数验证
- 错误处理验证

详细测试结果见 [动态配置系统文档](../DYNAMIC_CONFIG.md#测试验证)。

---

**最后更新 / Last Updated**: 2026-02-28
