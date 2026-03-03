# Scripts 目录

本目录包含项目的各种脚本工具。

## 目录结构

```
scripts/
├── deploy.sh                  # 部署管理脚本
├── set_file_permissions.py    # 文件权限设置脚本
├── start_web_admin.sh         # Web 管理界面启动脚本
├── verify_config.py           # 配置验证脚本
├── test/                      # 测试相关脚本
│   ├── get_chat_id.py
│   ├── run_integration_test.py
│   ├── send_test_message.py
│   └── README.md
└── README.md                  # 本文件
```

## 脚本说明

### deploy.sh - 部署管理脚本

用于管理 Docker 容器的部署、启动、停止等操作。

**用法**：
```bash
./scripts/deploy.sh [命令]
```

**命令**：
- `start` - 启动服务
- `stop` - 停止服务
- `restart` - 重启服务
- `logs` - 查看日志
- `status` - 查看状态
- `update` - 更新服务
- `backup` - 备份数据
- `help` - 显示帮助

**示例**：
```bash
# 启动服务
./scripts/deploy.sh start

# 查看日志
./scripts/deploy.sh logs

# 更新服务
./scripts/deploy.sh update
```

### verify_config.py - 配置验证脚本

验证环境变量配置是否正确。

**用法**：
```bash
python scripts/verify_config.py
```

**功能**：
- 检查必需的配置项是否存在
- 显示配置状态（隐藏敏感信息）
- 验证配置的有效性

**示例输出**：
```
✅ 已加载配置文件: E:\TraeProjects\lark-bot\.env
============================================================
配置状态
============================================================
APP_ID: ✅ 已配置
APP_SECRET: ✅ 已配置
CHAT_ID: ⚠️ 未配置（测试时需要）
USER_ID: ⚠️ 未配置（测试时需要）
TARGET_PROJECT_DIR: ✅ 已配置
============================================================

✅ 配置验证通过
```

### set_file_permissions.py - 文件权限设置脚本

设置配置文件和日志文件的安全权限，用于生产环境安全加固。

**用法**：
```bash
python scripts/set_file_permissions.py
```

**功能**：
- 将配置文件（.env、session_configs.json、备份文件）权限设置为 600（仅所有者可读写）
- 将日志文件权限设置为 640（所有者可读写，组可读）
- 自动创建必要的目录（data、logs）
- 验证权限设置是否成功

**示例输出**：
```
============================================================
文件权限设置脚本
============================================================

=== 设置配置文件权限 (600) ===
✓ 已设置 .env 权限为 0o600
✓ 已设置 data/session_configs.json 权限为 0o600

配置文件: 2/2 成功

=== 设置日志文件权限 (640) ===
✓ 已设置 logs/web_admin.log 权限为 0o640
✓ 已设置 logs/web_admin_access.log 权限为 0o640

日志文件: 2/2 成功

============================================================
✓ 所有文件权限设置成功
============================================================
```

**注意**：
- 在 Windows 系统上，Unix 风格的文件权限可能不会完全生效
- 建议在 Linux/Unix 系统上运行此脚本
- 权限设置应该在部署后立即执行

### start_web_admin.sh - Web 管理界面启动脚本

启动 Web 管理界面服务的便捷脚本。

**用法**：
```bash
./scripts/start_web_admin.sh [模式]
```

**模式**：
- `development` - 开发模式（使用 Flask 开发服务器）
- `production` - 生产模式（使用 Gunicorn）

**示例**：
```bash
# 开发模式
./scripts/start_web_admin.sh development

# 生产模式
./scripts/start_web_admin.sh production
```

## 测试脚本

测试相关的脚本位于 `test/` 子目录，详见 [test/README.md](test/README.md)。

## 添加新脚本

如果需要添加新的脚本：

1. 将脚本放在 `scripts/` 目录下
2. 如果是测试相关的脚本，放在 `scripts/test/` 目录下
3. 添加适当的注释和文档
4. 更新本 README 文件

## 注意事项

- 所有脚本都应该从项目根目录运行
- 脚本中的路径应该相对于项目根目录
- 确保脚本有执行权限（Linux/Mac）：`chmod +x scripts/script_name.sh`
