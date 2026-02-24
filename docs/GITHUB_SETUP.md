# GitHub 仓库设置指南

## 步骤1: 在GitHub上创建私有仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `feishu-ai-bot` （或你喜欢的名字）
   - **Description**: 飞书AI机器人 - 集成多个AI服务的智能机器人
   - **Visibility**: ✅ **Private** （重要：选择私有仓库）
   - **不要**勾选 "Initialize this repository with a README"
   - **不要**添加 .gitignore 或 license（我们已经有了）
3. 点击 "Create repository"

## 步骤2: 连接本地仓库到GitHub

GitHub会显示一些命令，你需要执行以下命令（替换为你的仓库URL）：

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/feishu-ai-bot.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

### 完整示例

假设你的GitHub用户名是 `yourname`，仓库名是 `feishu-ai-bot`：

```bash
git remote add origin https://github.com/yourname/feishu-ai-bot.git
git branch -M main
git push -u origin main
```

## 步骤3: 验证上传

1. 刷新GitHub仓库页面
2. 确认所有文件都已上传
3. 检查 `.env` 文件**没有**被上传（应该只有 `.env.example`）

## 步骤4: 设置仓库保护（可选但推荐）

1. 进入仓库的 Settings → Branches
2. 添加分支保护规则：
   - Branch name pattern: `main`
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging

## 步骤5: 添加协作者（如果需要）

1. 进入仓库的 Settings → Collaborators
2. 点击 "Add people"
3. 输入协作者的GitHub用户名或邮箱

## 常见问题

### Q: 如何更新GitHub上的代码？

```bash
# 1. 添加修改的文件
git add .

# 2. 提交修改
git commit -m "描述你的修改"

# 3. 推送到GitHub
git push
```

### Q: 如果不小心提交了敏感信息怎么办？

1. 立即在飞书开放平台重置 APP_SECRET
2. 使用以下命令清理Git历史：

```bash
# 删除包含敏感信息的文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <文件名>" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（危险操作，谨慎使用）
git push origin --force --all
```

### Q: 如何克隆仓库到其他电脑？

```bash
# 克隆仓库
git clone https://github.com/yourname/feishu-ai-bot.git

# 进入目录
cd feishu-ai-bot

# 复制环境变量模板
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac

# 编辑 .env 文件，填入配置

# 安装依赖
pip install -r requirements.txt

# 验证配置
python config.py

# 运行机器人
python lark_bot.py
```

## 安全检查清单

在推送代码前，请确认：

- [ ] `.env` 文件在 `.gitignore` 中
- [ ] `.env` 文件没有被提交
- [ ] 所有代码中的硬编码凭证已移除
- [ ] `.env.example` 只包含示例值，不包含真实凭证
- [ ] 仓库设置为私有
- [ ] README.md 中没有敏感信息

## 下一步

代码已安全上传到GitHub！现在你可以：

1. 继续开发新功能
2. 定期提交和推送代码
3. 使用GitHub Issues跟踪任务
4. 使用GitHub Projects管理项目进度
