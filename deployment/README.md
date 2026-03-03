# 部署配置文件

本目录包含生产环境部署所需的配置文件。

## 文件说明

### nginx.conf.example

Nginx 反向代理配置示例文件，用于在生产环境中部署 Web 管理界面。

**功能特性**：

- **反向代理**：将 API 请求代理到 Gunicorn 后端服务器
- **静态文件服务**：高效地提供前端静态资源（HTML、CSS、JS、图片等）
- **HTTPS 支持**：完整的 SSL/TLS 配置，支持 TLS 1.2 和 1.3
- **安全头**：包含 HSTS、CSP、X-Frame-Options 等安全响应头
- **Gzip 压缩**：自动压缩文本资源以减少传输大小
- **缓存策略**：为静态资源配置长期缓存，为 HTML 和 API 禁用缓存
- **SPA 路由支持**：正确处理 Vue Router 的前端路由

**安装步骤**：

1. 复制配置文件到 Nginx 配置目录：
```bash
sudo cp deployment/nginx.conf.example /etc/nginx/sites-available/feishu-bot-web-admin
```

2. 根据实际部署环境修改配置文件：
```bash
sudo nano /etc/nginx/sites-available/feishu-bot-web-admin
```

需要修改的配置项：
- `server_name`: 替换为你的域名（例如：admin.example.com）
- `root`: 前端构建产物的路径（默认：/opt/feishu-bot/frontend/dist）
- `ssl_certificate`: SSL 证书文件路径
- `ssl_certificate_key`: SSL 私钥文件路径
- `upstream feishu_bot_backend`: 后端服务器地址（默认：127.0.0.1:5000）

3. 创建符号链接启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/feishu-bot-web-admin /etc/nginx/sites-enabled/
```

4. 测试 Nginx 配置：
```bash
sudo nginx -t
```

5. 重新加载 Nginx：
```bash
sudo systemctl reload nginx
```

**SSL 证书获取（使用 Let's Encrypt）**：

```bash
# 安装 Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 获取证书（Certbot 会自动配置 Nginx）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

**可选配置**：

- **IP 访问限制**：取消注释 `geo $allowed_ip` 部分以限制访问 IP
- **速率限制**：取消注释 `limit_req_zone` 部分以启用 API 速率限制
- **Unix Socket**：修改 upstream 配置使用 Unix socket 以获得更好的性能

### feishu-bot-web-admin.service

Systemd 服务单元文件，用于在 Linux 系统上管理 Web 管理界面服务。

**安装步骤**：

1. 复制服务文件到 systemd 目录：
```bash
sudo cp deployment/feishu-bot-web-admin.service /etc/systemd/system/
```

2. 根据实际部署路径修改服务文件中的路径：
```bash
sudo nano /etc/systemd/system/feishu-bot-web-admin.service
```

需要修改的路径：
- `WorkingDirectory`: 项目根目录
- `Environment="PATH=..."`: Python 虚拟环境路径
- `EnvironmentFile`: .env 文件路径
- `ExecStart`: Gunicorn 可执行文件路径和配置文件路径
- `ReadWritePaths`: 日志和数据目录路径

3. 重新加载 systemd 并启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start feishu-bot-web-admin
sudo systemctl enable feishu-bot-web-admin
```

4. 查看服务状态：
```bash
sudo systemctl status feishu-bot-web-admin
```

**服务管理命令**：

```bash
# 启动服务
sudo systemctl start feishu-bot-web-admin

# 停止服务
sudo systemctl stop feishu-bot-web-admin

# 重启服务
sudo systemctl restart feishu-bot-web-admin

# 重新加载配置（优雅重启）
sudo systemctl reload feishu-bot-web-admin

# 查看服务状态
sudo systemctl status feishu-bot-web-admin

# 查看服务日志
sudo journalctl -u feishu-bot-web-admin -f

# 查看最近的错误日志
sudo journalctl -u feishu-bot-web-admin -p err --since today
```

## 相关文档

- [Gunicorn 部署指南](../docs/deployment/GUNICORN_DEPLOYMENT.md) - 详细的 Gunicorn 配置和部署说明
- [部署指南](../docs/deployment/DEPLOYMENT.md) - 完整的部署文档
- [快速部署](../docs/deployment/QUICKSTART.md) - 快速开始指南

## 文件权限设置

为了增强安全性，建议在生产环境中设置正确的文件权限：

**自动设置（推荐）**：

使用提供的脚本自动设置所有文件权限：

```bash
python scripts/set_file_permissions.py
```

该脚本会：
- 将配置文件（.env、session_configs.json、备份文件）权限设置为 600（仅所有者可读写）
- 将日志文件权限设置为 640（所有者可读写，组可读）

**手动设置**：

如果需要手动设置权限：

```bash
# 设置配置文件权限为 600
chmod 600 .env
chmod 600 data/session_configs.json
chmod 600 data/session_configs.json.backup*

# 设置日志文件权限为 640
chmod 640 logs/*.log*

# 设置目录权限
chmod 755 data
chmod 755 logs
```

**验证权限**：

```bash
# 查看配置文件权限
ls -l .env data/session_configs.json*

# 查看日志文件权限
ls -l logs/*.log*
```

**注意**：
- 在 Windows 系统上，Unix 风格的文件权限可能不会完全生效
- 建议在 Linux/Unix 系统上运行权限设置脚本
- 权限设置应该在部署后立即执行

## 注意事项

1. **安全性**：
   - 确保 `.env` 文件权限设置为 600（仅所有者可读写）
   - 确保配置文件和备份文件权限设置为 600
   - 确保日志文件权限设置为 640（所有者可读写，组可读）
   - 使用强密码作为 `WEB_ADMIN_PASSWORD`
   - 定期轮换 `JWT_SECRET_KEY`

2. **资源限制**：
   - 根据服务器配置调整 worker 数量
   - 监控内存和 CPU 使用情况
   - 配置适当的超时时间

3. **日志管理**：
   - 定期检查日志文件大小
   - 配置日志轮转（logrotate）
   - 监控错误日志

4. **备份**：
   - 定期备份 `data/` 目录
   - 备份 `.env` 配置文件
   - 备份日志文件（可选）

## 故障排除

如果服务无法启动，请检查：

1. 环境变量是否正确配置（`.env` 文件）
2. Python 虚拟环境是否正确安装
3. 所有依赖是否已安装（`pip install -r requirements.txt`）
4. 端口是否被占用（`netstat -tuln | grep 5000`）
5. 文件和目录权限是否正确
6. 查看详细错误日志（`sudo journalctl -u feishu-bot-web-admin -n 50`）

## 获取帮助

如果遇到问题，请：

1. 查看 [Gunicorn 部署指南](../docs/deployment/GUNICORN_DEPLOYMENT.md)
2. 查看服务日志获取详细错误信息
3. 提交 GitHub Issue 并附上错误日志
