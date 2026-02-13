# 安全注意事项

## ⚠️ 敏感信息保护

### 当前代码中的敏感信息

以下文件包含敏感信息，**上传到GitHub前必须处理**：

1. **lark_bot.py**
   ```python
   lark.APP_ID = 'cli_a9f47e209db8dcc5'  # 需要移除
   lark.APP_SECRET = 'nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT'  # 需要移除
   ```

2. **test_bot_message.py**
   ```python
   APP_ID = 'cli_a9f47e209db8dcc5'  # 需要移除
   APP_SECRET = 'nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT'  # 需要移除
   ```

3. **其他测试文件**
   - send_test_message.py
   - check_chat_history.py
   - bot_send_to_user.py
   - get_chat_id.py

### 推荐的安全做法

#### 方案1: 使用环境变量（推荐）

1. 创建 `.env` 文件（已在.gitignore中）：
```bash
FEISHU_APP_ID=cli_a9f47e209db8dcc5
FEISHU_APP_SECRET=nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT
FEISHU_CHAT_ID=oc_585f29d10679c7a0b5c3bf0d34adba90
FEISHU_USER_ID=155529283
```

2. 安装 python-dotenv：
```bash
pip install python-dotenv
```

3. 在代码中使用：
```python
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID = os.getenv('FEISHU_APP_ID')
APP_SECRET = os.getenv('FEISHU_APP_SECRET')
```

#### 方案2: 使用配置文件

1. 创建 `config.json`（已在.gitignore中）：
```json
{
  "app_id": "cli_a9f47e209db8dcc5",
  "app_secret": "nS3exdQZS8ZsO6FHEEgnueAeiY1K0DnT",
  "chat_id": "oc_585f29d10679c7a0b5c3bf0d34adba90",
  "user_id": "155529283"
}
```

2. 创建 `config.example.json`（可以提交）：
```json
{
  "app_id": "your_app_id_here",
  "app_secret": "your_app_secret_here",
  "chat_id": "your_chat_id_here",
  "user_id": "your_user_id_here"
}
```

3. 在代码中使用：
```python
import json

with open('config.json', 'r') as f:
    config = json.load(f)

APP_ID = config['app_id']
APP_SECRET = config['app_secret']
```

### 上传前检查清单

- [ ] 确认 `.gitignore` 已创建
- [ ] 确认敏感信息已从代码中移除
- [ ] 确认 `.env` 或 `config.json` 在 `.gitignore` 中
- [ ] 创建了 `config.example.json` 作为模板
- [ ] 更新了 README.md 中的配置说明
- [ ] 检查所有文件，确保没有遗漏的敏感信息

### Git历史清理

如果不小心提交了敏感信息，需要清理Git历史：

```bash
# 使用 git filter-branch（不推荐，仅作参考）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <文件名>" \
  --prune-empty --tag-name-filter cat -- --all

# 推荐使用 BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/
```

### 最佳实践

1. **永远不要**将凭证硬编码在代码中
2. **始终使用**环境变量或配置文件
3. **定期轮换**API密钥和凭证
4. **限制权限**，只授予必要的权限
5. **监控使用**，定期检查API调用日志
6. **使用私有仓库**存储包含配置的代码

### 紧急情况

如果敏感信息已经泄露：

1. **立即**在飞书开放平台重置 APP_SECRET
2. **立即**撤销相关权限
3. **检查**是否有异常API调用
4. **清理**Git历史中的敏感信息
5. **通知**相关人员

## 联系方式

如发现安全问题，请立即联系项目维护者。
