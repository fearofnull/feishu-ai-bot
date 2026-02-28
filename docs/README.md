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

- **[DYNAMIC_CONFIG.md](DYNAMIC_CONFIG.md)** - 动态配置系统
  - 在对话窗口中配置机器人
  - 配置优先级说明
  - 私聊和群聊配置
  - 临时参数使用
  - ✅ 已通过 16 个单元测试和 15 个手动测试验证

- **[examples/DYNAMIC_CONFIG_EXAMPLES.md](examples/DYNAMIC_CONFIG_EXAMPLES.md)** - 动态配置使用示例
  - 8 个实际使用场景
  - 最佳实践
  - 故障排除案例
  - ✅ 所有示例场景已验证

- **[LANGUAGE_CONFIGURATION.md](LANGUAGE_CONFIGURATION.md)** - 语言配置说明
  - 如何设置AI回复语言
  - 支持的语言列表
  - 配置示例

### 部署文档
- **[deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - 完整部署指南
  - Docker 部署
  - 云服务商部署
  - 监控和维护

- **[deployment/QUICKSTART.md](deployment/QUICKSTART.md)** - 5分钟快速部署
  - 快速部署到云端
  - 常用命令
  - 故障排除

### 测试文档
- **[INTEGRATION_TEST_RESULTS.md](INTEGRATION_TEST_RESULTS.md)** - 测试结果报告
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

3. **[DYNAMIC_CONFIG.md](DYNAMIC_CONFIG.md)** - 动态配置
   - 学习如何在对话中配置机器人
   - 了解配置优先级
   
4. **[deployment/QUICKSTART.md](deployment/QUICKSTART.md)** - 快速部署
   - 5分钟部署到云端
   - 验证配置是否正确
   
5. **[USER_GUIDE.md](USER_GUIDE.md)** - 开始使用
   - 学习如何使用机器人
   - 了解各种命令和功能

### 开发者推荐阅读顺序

1. **[../README.md](../README.md)** - 项目架构
   - 了解系统设计
   - 可扩展性说明
   
2. **[../STRUCTURE.md](../STRUCTURE.md)** - 项目结构
   - 了解目录组织
   - 代码模块说明

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

### 部署指南
- **完整部署**：Docker 和云服务商部署方案
- **快速部署**：5分钟快速部署指南

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
