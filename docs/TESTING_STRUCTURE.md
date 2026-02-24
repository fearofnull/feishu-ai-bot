# 测试结构说明

## 测试目录对比

### `tests/` - 自动化测试套件
**用途**: pytest驱动的自动化测试，用于持续集成和开发验证

**内容**:
- 30+ 个测试文件
- 单元测试（test_*.py）
- 属性测试（test_*_properties.py）
- 集成测试（test_integration.py）

**运行方式**:
```bash
# 运行所有测试
pytest tests/

# 运行特定类型
pytest tests/ -k property  # 属性测试
pytest tests/ -k unit      # 单元测试

# 查看覆盖率
pytest tests/ --cov=feishu_bot
```

**特点**:
- ✅ 自动化执行
- ✅ 快速反馈
- ✅ 适合CI/CD
- ✅ 代码覆盖率分析

### `test_scripts/` - 手动测试工具
**用途**: 实际环境中的手动集成测试和调试工具

**内容**:
- 9 个独立脚本
- 消息发送工具
- 聊天历史查看
- API直接测试
- 集成测试运行器

**运行方式**:
```bash
# 运行集成测试
python test_scripts/run_integration_test.py

# 发送测试消息
python test_scripts/test_bot_message.py

# 查看聊天历史
python test_scripts/check_chat_history.py
```

**特点**:
- ✅ 真实环境测试
- ✅ 交互式调试
- ✅ 灵活的测试场景
- ✅ 适合手动验证

## 为什么保持分离？

### 不同的测试目标
- `tests/` 关注代码正确性和单元行为
- `test_scripts/` 关注端到端功能和用户体验

### 不同的运行环境
- `tests/` 使用mock和stub，不需要真实服务
- `test_scripts/` 需要真实的飞书环境和API凭证

### 不同的执行频率
- `tests/` 每次代码提交都运行
- `test_scripts/` 在功能完成或部署前运行

## 建议的工作流程

### 开发阶段
1. 编写代码
2. 运行 `pytest tests/` 验证单元测试
3. 使用 `test_scripts/` 中的工具手动验证功能

### 提交前
1. 运行完整测试套件: `pytest tests/ --cov=feishu_bot`
2. 确保覆盖率达标
3. 运行关键集成测试脚本

### 部署前
1. 运行 `python test_scripts/run_integration_test.py`
2. 验证所有10项集成测试通过
3. 手动测试关键用户场景

## 未来优化建议

### tests/ 目录结构优化
可以考虑进一步细分：
```
tests/
├── unit/              # 单元测试
├── property/          # 属性测试
├── integration/       # 集成测试
└── conftest.py        # pytest配置
```

### test_scripts/ 保持现状
作为独立的工具集，便于快速访问和使用。

## 总结

两个目录各司其职，不建议合并：
- ✅ `tests/` = 自动化测试框架（开发者工具）
- ✅ `test_scripts/` = 手动测试工具（调试和验证工具）
