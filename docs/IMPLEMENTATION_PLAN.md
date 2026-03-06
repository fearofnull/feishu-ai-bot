# 飞书机器人改造实施计划

## 概述

本文档描述如何实现飞书机器人的4个核心改进需求。这是一个实用的实施指南，包含具体的代码修改位置和实现步骤。

## 需求清单

1. **Emoji即时反馈** - 用户提问时立即发送👀表情
2. **CLI权限参数** - Claude CLI和Gemini CLI添加默认权限参数
3. **统一API接口** - 将多个AI提供商统一为@gpt，支持配置管理
4. **CLI层Git同步** - CLI执行前自动git pull最新代码

---

## 需求1: Emoji即时反馈

### 目标
用户发送消息后，机器人立即回复一个👀 emoji，让用户知道消息已被接收。

### 实现位置
文件：`feishu_bot/core/message_handler.py`

### 实现步骤

1. 在`MessageHandler`类中添加emoji响应方法：

```python
async def send_emoji_reaction(self, message_id: str, emoji: str = "👀"):
    """发送emoji反应"""
    try:
        # 调用飞书API发送emoji反应
        # 参考飞书开放平台文档：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message-reaction/create
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reactions"
        headers = {
            "Authorization": f"Bearer {self.app_token}",
            "Content-Type": "application/json"
        }
        data = {
            "reaction_type": {
                "emoji_type": emoji
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=0.2) as resp:
                if resp.status == 200:
                    logger.info(f"Emoji reaction sent for message {message_id}")
                else:
                    logger.warning(f"Failed to send emoji reaction: {resp.status}")
    except Exception as e:
        logger.warning(f"Error sending emoji reaction: {e}")
        # 不抛出异常，不影响后续处理
```

2. 在消息处理的入口处调用：

```python
async def handle_message(self, event_data):
    """处理消息事件"""
    message_id = event_data.get("message", {}).get("message_id")
    
    # 立即发送emoji反应（异步，不等待）
    asyncio.create_task(self.send_emoji_reaction(message_id))
    
    # 继续处理消息...
    content = event_data.get("message", {}).get("content")
    # ... 其他处理逻辑
```

### 注意事项
- 使用异步调用，不阻塞主流程
- 设置200ms超时
- 失败时只记录日志，不影响消息处理

---

## 需求2: CLI权限参数

### 目标
为Claude CLI和Gemini CLI添加默认权限参数，避免权限不足导致执行失败。

### 实现位置
- `feishu_bot/executors/claude_cli_executor.py`
- `feishu_bot/executors/gemini_cli_executor.py`

### Claude CLI权限参数

根据Claude Code CLI文档，需要添加 `--dangerously-skip-permissions` 参数。

修改 `claude_cli_executor.py`：

```python
def build_command(self, message: str, **kwargs) -> List[str]:
    """构建Claude CLI命令"""
    command = [
        "claude",
        "--dangerously-skip-permissions",  # 添加权限参数
        # ... 其他参数
    ]
    return command
```

### Gemini CLI权限参数

根据Gemini CLI文档，需要添加 `--yolo` 或 `-y` 参数。

修改 `gemini_cli_executor.py`：

```python
def build_command(self, message: str, **kwargs) -> List[str]:
    """构建Gemini CLI命令"""
    command = [
        "gemini",
        "--yolo",  # 或使用 "-y"
        # ... 其他参数
    ]
    return command
```

### 配置化（可选）

可以在配置文件中设置权限参数：

```json
{
  "cli_permissions": {
    "claude": ["--dangerously-skip-permissions"],
    "gemini": ["--yolo"]
  }
}
```

然后在代码中读取配置：

```python
class CLIExecutor:
    def __init__(self):
        self.permissions = self.load_permissions_config()
    
    def get_permission_params(self, provider: str) -> List[str]:
        return self.permissions.get(provider, [])
```

---

## 需求3: 统一API接口

### 目标
将@claude、@gemini、@gpt等多个命令统一为@gpt，通过配置管理后端提供商。

### 架构设计

```
用户消息 "@gpt 帮我分析代码"
    ↓
命令解析器（只识别@gpt）
    ↓
配置管理器（获取默认提供商配置）
    ↓
统一API接口（根据配置路由到具体执行器）
    ↓
OpenAI/Claude/Gemini执行器
```

### 实现步骤

#### 步骤1: 创建提供商配置数据模型

文件：`feishu_bot/models.py`

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ProviderConfig:
    """AI提供商配置"""
    name: str  # 配置名称，如 "openai-gpt4"
    type: str  # API类型：openai_compatible, claude_compatible, gemini_compatible
    base_url: str  # API端点
    api_key: str  # API密钥
    model: str  # 模型名称
    is_default: bool = False  # 是否为默认提供商
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "model": self.model,
            "is_default": self.is_default,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_safe_dict(self):
        """返回安全的字典（隐藏api_key）"""
        data = self.to_dict()
        if len(self.api_key) > 8:
            data["api_key"] = f"{self.api_key[:4]}{'*' * (len(self.api_key) - 8)}{self.api_key[-4:]}"
        else:
            data["api_key"] = "****"
        return data
```

#### 步骤2: 创建配置管理器

文件：`feishu_bot/core/provider_config_manager.py`

```python
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from feishu_bot.models import ProviderConfig

class ProviderConfigManager:
    """提供商配置管理器"""
    
    def __init__(self, config_path: str = "data/provider_configs.json"):
        self.config_path = config_path
        self.configs: Dict[str, ProviderConfig] = {}
        self.version = "1.0"
        self.load()
    
    def add_config(self, config: ProviderConfig) -> Tuple[bool, str]:
        """添加配置"""
        if config.name in self.configs:
            return False, f"配置 {config.name} 已存在"
        
        config.created_at = datetime.now().isoformat()
        config.updated_at = config.created_at
        self.configs[config.name] = config
        self.save()
        return True, "配置添加成功"
    
    def update_config(self, name: str, config: ProviderConfig) -> Tuple[bool, str]:
        """更新配置"""
        if name not in self.configs:
            return False, f"配置 {name} 不存在"
        
        config.updated_at = datetime.now().isoformat()
        config.created_at = self.configs[name].created_at
        self.configs[name] = config
        self.save()
        return True, "配置更新成功"
    
    def delete_config(self, name: str) -> Tuple[bool, str]:
        """删除配置"""
        if name not in self.configs:
            return False, f"配置 {name} 不存在"
        
        del self.configs[name]
        self.save()
        return True, "配置删除成功"
    
    def get_config(self, name: str) -> Optional[ProviderConfig]:
        """获取配置"""
        return self.configs.get(name)
    
    def list_configs(self) -> List[ProviderConfig]:
        """列出所有配置"""
        return list(self.configs.values())
    
    def set_default(self, name: str) -> Tuple[bool, str]:
        """设置默认提供商"""
        if name not in self.configs:
            return False, f"配置 {name} 不存在"
        
        # 取消其他默认标记
        for config in self.configs.values():
            config.is_default = False
        
        # 设置新的默认
        self.configs[name].is_default = True
        self.save()
        return True, f"已将 {name} 设为默认提供商"
    
    def get_default(self) -> Optional[ProviderConfig]:
        """获取默认提供商"""
        for config in self.configs.values():
            if config.is_default:
                return config
        return None
    
    def save(self) -> bool:
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            data = {
                "version": self.version,
                "configs": [config.to_dict() for config in self.configs.values()]
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 设置文件权限为600
            os.chmod(self.config_path, 0o600)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load(self) -> bool:
        """从文件加载配置"""
        try:
            if not os.path.exists(self.config_path):
                return True  # 文件不存在，使用空配置
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.version = data.get("version", "1.0")
            configs_data = data.get("configs", [])
            
            self.configs = {}
            for config_data in configs_data:
                config = ProviderConfig(**config_data)
                self.configs[config.name] = config
            
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.configs = {}
            return False
```

#### 步骤3: 创建统一API接口

文件：`feishu_bot/core/unified_api.py`

```python
from typing import Optional
from feishu_bot.core.provider_config_manager import ProviderConfigManager
from feishu_bot.core.executor_registry import ExecutorRegistry

class UnifiedAPIInterface:
    """统一API接口"""
    
    def __init__(
        self,
        config_manager: ProviderConfigManager,
        executor_registry: ExecutorRegistry
    ):
        self.config_manager = config_manager
        self.executor_registry = executor_registry
    
    async def execute(self, message: str, **kwargs):
        """执行统一API调用"""
        # 获取默认提供商配置
        config = self.config_manager.get_default()
        
        if not config:
            return {
                "success": False,
                "error": "未配置有效的AI提供商"
            }
        
        # 根据配置类型获取执行器
        if config.type == "openai_compatible":
            executor = self.executor_registry.get_openai_executor(
                base_url=config.base_url,
                api_key=config.api_key,
                model=config.model
            )
        elif config.type == "claude_compatible":
            # TODO: 实现Claude兼容执行器
            return {
                "success": False,
                "error": "Claude兼容类型暂未实现"
            }
        elif config.type == "gemini_compatible":
            # TODO: 实现Gemini兼容执行器
            return {
                "success": False,
                "error": "Gemini兼容类型暂未实现"
            }
        else:
            return {
                "success": False,
                "error": f"不支持的API类型: {config.type}"
            }
        
        # 执行API调用
        try:
            result = await executor.execute(message, **kwargs)
            return {
                "success": True,
                "result": result,
                "provider": config.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"{config.name} 调用失败: {str(e)}"
            }
```

#### 步骤4: 修改命令解析器

文件：`feishu_bot/utils/command_parser.py`

```python
def parse_command(self, message: str):
    """解析命令"""
    # 只识别 @gpt 前缀
    if message.startswith("@gpt"):
        return {
            "type": "unified_api",
            "content": message[4:].strip()  # 去掉 @gpt 前缀
        }
    
    # 其他命令...
    return None
```

#### 步骤5: 修改智能路由器

文件：`feishu_bot/core/smart_router.py`

```python
async def route(self, command):
    """路由命令"""
    if command["type"] == "unified_api":
        # 使用统一API接口
        result = await self.unified_api.execute(command["content"])
        return result
    
    # 其他路由逻辑...
```

#### 步骤6: 创建Web配置API

文件：`feishu_bot/web_admin/provider_api_routes.py`

```python
from flask import Blueprint, request, jsonify
from feishu_bot.core.provider_config_manager import ProviderConfigManager
from feishu_bot.models import ProviderConfig

provider_bp = Blueprint('provider', __name__, url_prefix='/api/providers')
config_manager = ProviderConfigManager()

@provider_bp.route('', methods=['GET'])
def list_providers():
    """获取所有提供商配置"""
    configs = config_manager.list_configs()
    return jsonify({
        "success": True,
        "data": [config.to_safe_dict() for config in configs]
    })

@provider_bp.route('', methods=['POST'])
def create_provider():
    """创建新提供商配置"""
    data = request.json
    
    # 验证必填字段
    required_fields = ['name', 'type', 'api_key', 'model']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"缺少必填字段: {field}"
            }), 400
    
    config = ProviderConfig(**data)
    success, message = config_manager.add_config(config)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400

@provider_bp.route('/<name>', methods=['PUT'])
def update_provider(name):
    """更新提供商配置"""
    data = request.json
    config = ProviderConfig(**data)
    success, message = config_manager.update_config(name, config)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400

@provider_bp.route('/<name>', methods=['DELETE'])
def delete_provider(name):
    """删除提供商配置"""
    success, message = config_manager.delete_config(name)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 404

@provider_bp.route('/<name>/set-default', methods=['POST'])
def set_default_provider(name):
    """设置默认提供商"""
    success, message = config_manager.set_default(name)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 404

@provider_bp.route('/default', methods=['GET'])
def get_default_provider():
    """获取默认提供商"""
    config = config_manager.get_default()
    
    if config:
        return jsonify({
            "success": True,
            "data": config.to_safe_dict()
        })
    else:
        return jsonify({
            "success": False,
            "error": "未设置默认提供商"
        }), 404
```

#### 步骤7: 创建Web配置前端页面

文件：`feishu_bot/web_admin/templates/providers.html`

参考你提供的图片设计，创建一个卡片布局的配置页面：

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI提供商配置</title>
    <style>
        .provider-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            position: relative;
        }
        .provider-card.default {
            border-color: #4CAF50;
            background-color: #f1f8f4;
        }
        .provider-card .badge {
            position: absolute;
            top: 16px;
            right: 16px;
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .provider-card h3 {
            margin: 0 0 8px 0;
        }
        .provider-card .info {
            color: #666;
            font-size: 14px;
            margin: 4px 0;
        }
        .provider-card .actions {
            margin-top: 12px;
        }
        .provider-card button {
            margin-right: 8px;
            padding: 6px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            cursor: pointer;
        }
        .provider-card button:hover {
            background: #f5f5f5;
        }
        .add-button {
            background: #2196F3;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>AI提供商配置</h1>
    <button class="add-button" onclick="showAddForm()">+ 添加提供商</button>
    
    <div id="providers-list"></div>
    
    <script>
        // 加载提供商列表
        async function loadProviders() {
            const response = await fetch('/api/providers');
            const data = await response.json();
            
            const listDiv = document.getElementById('providers-list');
            listDiv.innerHTML = '';
            
            data.data.forEach(provider => {
                const card = document.createElement('div');
                card.className = 'provider-card' + (provider.is_default ? ' default' : '');
                card.innerHTML = `
                    ${provider.is_default ? '<span class="badge">默认</span>' : ''}
                    <h3>${provider.name}</h3>
                    <div class="info">类型: ${provider.type}</div>
                    <div class="info">Base URL: ${provider.base_url}</div>
                    <div class="info">模型: ${provider.model}</div>
                    <div class="actions">
                        ${!provider.is_default ? `<button onclick="setDefault('${provider.name}')">设为默认</button>` : ''}
                        <button onclick="editProvider('${provider.name}')">编辑</button>
                        <button onclick="deleteProvider('${provider.name}')">删除</button>
                    </div>
                `;
                listDiv.appendChild(card);
            });
        }
        
        // 设置默认提供商
        async function setDefault(name) {
            await fetch(`/api/providers/${name}/set-default`, { method: 'POST' });
            loadProviders();
        }
        
        // 删除提供商
        async function deleteProvider(name) {
            if (confirm(`确定要删除 ${name} 吗？`)) {
                await fetch(`/api/providers/${name}`, { method: 'DELETE' });
                loadProviders();
            }
        }
        
        // 页面加载时获取列表
        loadProviders();
    </script>
</body>
</html>
```

---

## 需求4: CLI层Git同步

### 目标
CLI执行前自动在工作目录执行git pull，确保代码是最新的。

### 实现位置
- `feishu_bot/executors/claude_cli_executor.py`
- `feishu_bot/executors/gemini_cli_executor.py`

### 实现步骤

#### 步骤1: 创建Git同步模块

文件：`feishu_bot/utils/git_sync.py`

```python
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

class GitSyncModule:
    """Git代码同步模块"""
    
    def __init__(self, enabled: bool = True, timeout: int = 30):
        self.enabled = enabled
        self.timeout = timeout
    
    def is_git_repo(self, working_dir: str) -> bool:
        """检查是否为Git仓库"""
        git_dir = os.path.join(working_dir, '.git')
        return os.path.isdir(git_dir)
    
    def sync(self, working_dir: str) -> tuple[bool, str]:
        """同步代码
        
        Returns:
            (是否成功, 输出信息)
        """
        if not self.enabled:
            logger.info("Git同步已禁用")
            return True, "Git同步已禁用"
        
        # 检查是否为Git仓库
        if not self.is_git_repo(working_dir):
            logger.warning(f"{working_dir} 不是Git仓库，跳过同步")
            return True, "不是Git仓库，跳过同步"
        
        try:
            # 执行git pull
            result = subprocess.run(
                ['git', 'pull'],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                logger.info(f"Git sync completed for {working_dir}")
                logger.debug(f"Git pull output: {output}")
                return True, output
            else:
                logger.error(f"Git pull failed: {output}")
                # 失败但不中断后续执行
                return True, f"Git pull失败但继续执行: {output}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"Git pull timeout after {self.timeout}s")
            return True, "Git pull超时但继续执行"
        except Exception as e:
            logger.error(f"Git sync error: {e}")
            return True, f"Git同步错误但继续执行: {e}"
```

#### 步骤2: 在CLI执行器中集成Git同步

修改 `claude_cli_executor.py` 和 `gemini_cli_executor.py`：

```python
from feishu_bot.utils.git_sync import GitSyncModule

class ClaudeCLIExecutor:
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or os.getcwd()
        self.git_sync = GitSyncModule(enabled=True, timeout=30)
    
    async def execute(self, message: str, **kwargs):
        """执行Claude CLI命令"""
        # 1. 先执行Git同步
        success, output = self.git_sync.sync(self.working_dir)
        logger.info(f"Git sync result: {output}")
        
        # 2. 构建命令（包含权限参数）
        command = self.build_command(message, **kwargs)
        
        # 3. 执行CLI命令
        result = await self.run_command(command)
        
        return result
    
    def build_command(self, message: str, **kwargs) -> List[str]:
        """构建命令"""
        command = [
            "claude",
            "--dangerously-skip-permissions",  # 权限参数
            # ... 其他参数
        ]
        return command
```

#### 步骤3: 添加配置选项

在配置文件中添加Git同步开关：

```json
{
  "git_sync": {
    "enabled": true,
    "timeout": 30
  }
}
```

---

## 实施顺序建议

按照以下顺序实施，可以逐步验证每个功能：

### 第一阶段：快速改进（1-2天）
1. **Emoji即时反馈** - 最简单，立即提升用户体验
2. **CLI权限参数** - 修改简单，解决权限问题

### 第二阶段：Git同步（1天）
3. **CLI层Git同步** - 独立功能，不影响其他模块

### 第三阶段：统一API（3-5天）
4. **统一API接口** - 最复杂，需要重构多个模块
   - 先实现OpenAI兼容类型
   - 后端API和配置管理
   - Web配置界面
   - Claude和Gemini兼容类型可以后续添加

---

## 测试验证

### Emoji反馈测试
1. 发送消息给机器人
2. 检查是否立即收到👀反应
3. 检查日志是否记录"Emoji reaction sent"

### CLI权限测试
1. 触发Claude CLI执行
2. 检查命令是否包含`--dangerously-skip-permissions`
3. 触发Gemini CLI执行
4. 检查命令是否包含`--yolo`

### Git同步测试
1. 修改工作目录的代码
2. 触发CLI执行
3. 检查日志是否显示"Git sync completed"
4. 验证代码已更新到最新版本

### 统一API测试
1. 添加一个OpenAI提供商配置
2. 设置为默认
3. 发送"@gpt 测试消息"
4. 验证是否正确路由到OpenAI API
5. 在Web界面切换默认提供商
6. 验证下次调用使用新的提供商

---

## 需要确认的问题

1. **飞书API Token获取方式** - 当前代码中如何获取app_token？
2. **工作目录配置** - CLI的工作目录是在哪里配置的？
3. **现有执行器结构** - 当前的executor_registry是如何组织的？
4. **Web框架** - Web管理界面使用的是Flask还是其他框架？
5. **配置文件位置** - 是否已有统一的配置文件管理？

请告诉我这些问题的答案，我可以提供更具体的实施指导。
