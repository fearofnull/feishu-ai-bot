# 项目文档目录

本目录包含飞书AI机器人项目的各种文档。

## 📚 可用文档

### 用户文档
- **[USER_GUIDE.md](USER_GUIDE.md)** - 用户使用指南
  - 如何使用机器人
  - 命令前缀说明
  - 会话管理功能
  - 使用示例

- **[CONFIGURATION.md](CONFIGURATION.md)** - 配置指南
  - 环境变量配置
  - AI服务配置
  - 会话管理配置
  - 高级配置选项

### 测试文档
- **[QUICK_START_INTEGRATION_TEST.md](QUICK_START_INTEGRATION_TEST.md)** - 5分钟快速测试
  - 快速验证机器人功能
  - 基础测试场景
  - 常见问题排查

- **[INTEGRATION_TESTING_GUIDE.md](INTEGRATION_TESTING_GUIDE.md)** - 集成测试指南
  - 完整测试流程
  - 测试不同AI提供商
  - 会话管理测试
  - 性能测试

- **[TESTING_STRUCTURE.md](TESTING_STRUCTURE.md)** - 测试体系说明
  - 测试架构概述
  - 单元测试说明
  - 属性测试说明
  - 集成测试说明

### 测试结果
- **INTEGRATION_TEST_RESULTS.md** - 集成测试结果报告
  - ⚠️ 此文件包含用户信息，不提交到Git仓库
  - 本地生成和查看
  - 用于验证功能正确性

## 🚀 快速开始

### 新用户推荐阅读顺序

1. **[../README.md](../README.md)** - 项目主文档
   - 了解项目概述和功能特性
   
2. **[CONFIGURATION.md](CONFIGURATION.md)** - 配置机器人
   - 设置环境变量
   - 配置AI服务
   
3. **[QUICK_START_INTEGRATION_TEST.md](QUICK_START_INTEGRATION_TEST.md)** - 快速测试
   - 验证配置是否正确
   - 测试基本功能
   
4. **[USER_GUIDE.md](USER_GUIDE.md)** - 开始使用
   - 学习如何使用机器人
   - 了解各种命令和功能

### 开发者推荐阅读顺序

1. **[../README.md](../README.md)** - 项目架构
   - 了解系统设计
   - 可扩展性说明
   
2. **[TESTING_STRUCTURE.md](TESTING_STRUCTURE.md)** - 测试体系
   - 了解测试架构
   - 运行测试套件
   
3. **[INTEGRATION_TESTING_GUIDE.md](INTEGRATION_TESTING_GUIDE.md)** - 集成测试
   - 完整测试流程
   - 故障排查

## 📖 文档说明

### 用户指南 (USER_GUIDE.md)
详细的使用说明，包括：
- 基本对话功能
- 命令前缀使用（@claude、@gemini、@openai等）
- 会话管理命令（/new、/session、/history）
- 智能路由功能
- 常见使用场景

### 配置指南 (CONFIGURATION.md)
完整的配置说明，包括：
- 必需配置项（飞书凭证、AI API密钥）
- 可选配置项（CLI工具、会话管理）
- 配置验证方法
- 配置最佳实践

### 测试指南
- **快速测试**：5分钟验证基本功能
- **集成测试**：完整的功能测试流程
- **测试结构**：了解测试体系和如何运行测试

## 🔒 安全注意事项

### 不应提交到Git的文件
以下文件包含敏感信息或用户数据，已添加到 `.gitignore`：
- `INTEGRATION_TEST_RESULTS.md` - 包含测试过程中的用户ID等信息
- 其他包含真实凭证或用户数据的文档

### 文档中的占位符
文档中使用以下占位符代替真实信息：
- `your_app_id_here` - 飞书应用ID
- `your_app_secret_here` - 飞书应用密钥
- `your_chat_id_here` - 测试群聊ID
- `[user_id]` - 用户ID

## 📝 文档维护

### 更新原则
- 保持文档与代码同步
- 使用占位符代替敏感信息
- 定期审查和更新过时内容
- 添加新功能时同步更新文档

### 贡献指南
如需更新文档：
1. 确保不包含敏感信息
2. 使用清晰的标题和结构
3. 提供实际可运行的示例
4. 添加必要的说明和注释

## 🔗 相关链接

### 项目文档
- [主README](../README.md) - 项目概述和架构

### 外部资源
- [飞书开放平台](https://open.feishu.cn/)
- [Claude API文档](https://docs.anthropic.com/)
- [Gemini API文档](https://ai.google.dev/)
- [OpenAI API文档](https://platform.openai.com/docs/)

---

**最后更新**: 2024
**维护者**: 项目团队
