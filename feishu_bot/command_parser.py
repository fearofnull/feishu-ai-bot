"""
命令解析器模块

负责解析用户消息，识别 AI 提供商指令和命令类型
"""
import re
from typing import Optional
from .models import ParsedCommand


class CommandParser:
    """命令解析器
    
    解析用户消息，识别 AI 提供商前缀和 CLI 关键词
    """
    
    # AI 提供商前缀映射：前缀 -> (provider, layer)
    PREFIX_MAPPING = {
        # Claude API
        "@claude-api": ("claude", "api"),
        "@claude": ("claude", "api"),
        # Gemini API
        "@gemini-api": ("gemini", "api"),
        "@gemini": ("gemini", "api"),
        # OpenAI API
        "@openai": ("openai", "api"),
        "@gpt": ("openai", "api"),
        # Claude CLI
        "@claude-cli": ("claude", "cli"),
        "@code": ("claude", "cli"),
        # Gemini CLI
        "@gemini-cli": ("gemini", "cli"),
    }
    
    # CLI 关键词（中英文）
    CLI_KEYWORDS = [
        # 代码相关
        "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
        # 文件操作
        "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
        "创建文件", "create file",
        # 命令执行
        "执行命令", "execute command", "运行脚本", "run script",
        # 项目分析
        "分析项目", "analyze project", "项目结构", "project structure",
    ]
    
    def parse_command(self, message: str) -> ParsedCommand:
        """解析用户消息，返回解析结果
        
        Args:
            message: 用户消息
            
        Returns:
            ParsedCommand: 包含 AI 提供商、执行层、实际消息内容
        """
        # 提取 AI 提供商前缀
        prefix_result = self.extract_provider_prefix(message)
        
        if prefix_result:
            provider, layer, clean_message = prefix_result
            return ParsedCommand(
                provider=provider,
                execution_layer=layer,
                message=clean_message,
                explicit=True
            )
        
        # 没有显式指定，返回默认值
        return ParsedCommand(
            provider="claude",  # 默认提供商
            execution_layer="api",  # 默认执行层
            message=message,
            explicit=False
        )
    
    def extract_provider_prefix(self, message: str) -> Optional[tuple[str, str, str]]:
        """提取 AI 提供商前缀
        
        Args:
            message: 用户消息
            
        Returns:
            Optional[tuple]: (provider, layer, clean_message) 或 None
        """
        # 大小写不敏感匹配
        message_lower = message.lower()
        
        # 按前缀长度降序排序，优先匹配更长的前缀
        # 这样 @claude-cli 会在 @claude 之前匹配
        sorted_prefixes = sorted(
            self.PREFIX_MAPPING.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for prefix, (provider, layer) in sorted_prefixes:
            # 检查消息是否以前缀开头
            if message_lower.startswith(prefix.lower()):
                # 去除前缀，保留原始消息的大小写
                clean_message = message[len(prefix):].strip()
                return provider, layer, clean_message
        
        return None
    
    def detect_cli_keywords(self, message: str) -> bool:
        """检测消息是否包含需要 CLI 层的关键词
        
        Args:
            message: 用户消息
            
        Returns:
            bool: True 如果包含 CLI 关键词
        """
        # 大小写不敏感匹配
        message_lower = message.lower()
        
        for keyword in self.CLI_KEYWORDS:
            if keyword.lower() in message_lower:
                return True
        
        return False
