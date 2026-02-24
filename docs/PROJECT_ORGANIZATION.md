# 项目文件整理说明

## 整理时间
2026-02-24

## 整理目的
将测试脚本和文档从根目录移动到专门的目录中，使项目结构更清晰、更易于维护。

## 目录结构变更

### 新增目录

#### 1. `test_scripts/` - 测试脚本目录
存放所有用于测试的Python脚本。

**移入文件**:
- `bot_send_to_user.py`
- `check_chat_history.py`
- `check_latest_messages.py`
- `get_chat_id.py`
- `run_integration_test.py`
- `send_test_message.py`
- `test_bot_message.py`
- `test_openai_api.py`
- `test_openai_direct.py`

#### 2. `docs/` - 文档目录
存放所有项目文档和总结。

**移入文件**:
- `测试总结.md`
- `重构完成总结.md`
- `GITHUB_SETUP.md`
- `GitHub上传成功.md`
- `INTEGRATION_TEST_RESULTS.md`
- `INTEGRATION_TESTING_GUIDE.md`
- `QUICK_START_INTEGRATION_TEST.md`
- `QUICK_TEST.md`
- `README_TEST.md`
- `TASK_7.4_SUMMARY.md`

### 根目录保留文件

**核心文件**:
- `lark_bot.py` - 主程序
- `config.py` - 配置管理
- `requirements.txt` - 依赖列表
- `README.md` - 项目说明
- `SECURITY.md` - 安全说明

**配置文件**:
- `.env` - 环境变量（不提交）
- `.env.example` - 环境变量模板
- `.gitignore` - Git忽略规则

**目录**:
- `feishu_bot/` - 核心代码
- `tests/` - 单元测试
- `data/` - 数据存储
- `examples/` - 示例代码
- `.kiro/` - Kiro配置

## 整理后的优势

### 1. 清晰的项目结构
- 根目录只保留核心文件
- 测试脚本集中管理
- 文档统一存放

### 2. 更好的可维护性
- 新开发者更容易理解项目结构
- 测试脚本易于查找和使用
- 文档集中便于更新

### 3. 符合最佳实践
- 遵循Python项目标准结构
- 分离关注点（代码、测试、文档）
- 便于CI/CD集成

## 使用指南

### 运行测试脚本
```bash
# 从根目录运行
python test_scripts/run_integration_test.py

# 或进入目录运行
cd test_scripts
python run_integration_test.py
```

### 查看文档
```bash
# 查看测试结果
cat docs/INTEGRATION_TEST_RESULTS.md

# 查看快速开始指南
cat docs/QUICK_START_INTEGRATION_TEST.md
```

### 开发新功能
1. 核心代码放在 `feishu_bot/`
2. 单元测试放在 `tests/`
3. 集成测试脚本放在 `test_scripts/`
4. 文档放在 `docs/`

## 注意事项

1. **路径引用**: 如果测试脚本中有相对路径引用，可能需要调整
2. **导入语句**: Python导入语句保持不变（因为是从根目录运行）
3. **文档链接**: README中的文档链接已更新

## 后续建议

1. 考虑将 `examples/` 目录也整理一下
2. 可以添加 `scripts/` 目录存放部署和维护脚本
3. 考虑添加 `logs/` 目录存放日志文件
4. 可以创建 `config/` 目录存放配置文件模板

## 回滚方法

如果需要恢复原来的结构：
```bash
# 移回测试脚本
Move-Item test_scripts/* . -Force

# 移回文档
Move-Item docs/* . -Force

# 删除空目录
Remove-Item test_scripts, docs
```
