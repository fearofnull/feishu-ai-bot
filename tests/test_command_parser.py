"""
CommandParser 单元测试

测试命令解析器的各种功能
"""
import pytest
from feishu_bot.command_parser import CommandParser
from feishu_bot.models import ParsedCommand


class TestCommandParser:
    """CommandParser 单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = CommandParser()
    
    def test_parse_claude_api_prefix(self):
        """测试解析 Claude API 前缀"""
        result = self.parser.parse_command("@claude-api 你好")
        assert result.provider == "claude"
        assert result.execution_layer == "api"
        assert result.message == "你好"
        assert result.explicit is True
    
    def test_parse_claude_short_prefix(self):
        """测试解析 Claude 短前缀"""
        result = self.parser.parse_command("@claude 帮我写代码")
        assert result.provider == "claude"
        assert result.execution_layer == "api"
        assert result.message == "帮我写代码"
        assert result.explicit is True
    
    def test_parse_gemini_api_prefix(self):
        """测试解析 Gemini API 前缀"""
        result = self.parser.parse_command("@gemini-api 分析这段代码")
        assert result.provider == "gemini"
        assert result.execution_layer == "api"
        assert result.message == "分析这段代码"
        assert result.explicit is True
    
    def test_parse_gemini_short_prefix(self):
        """测试解析 Gemini 短前缀"""
        result = self.parser.parse_command("@gemini 什么是Python")
        assert result.provider == "gemini"
        assert result.execution_layer == "api"
        assert result.message == "什么是Python"
        assert result.explicit is True
    
    def test_parse_openai_prefix(self):
        """测试解析 OpenAI 前缀"""
        result = self.parser.parse_command("@openai 翻译这段文字")
        assert result.provider == "openai"
        assert result.execution_layer == "api"
        assert result.message == "翻译这段文字"
        assert result.explicit is True
    
    def test_parse_gpt_prefix(self):
        """测试解析 GPT 前缀"""
        result = self.parser.parse_command("@gpt 解释一下量子计算")
        assert result.provider == "openai"
        assert result.execution_layer == "api"
        assert result.message == "解释一下量子计算"
        assert result.explicit is True
    
    def test_parse_claude_cli_prefix(self):
        """测试解析 Claude CLI 前缀"""
        result = self.parser.parse_command("@claude-cli 查看代码")
        assert result.provider == "claude"
        assert result.execution_layer == "cli"
        assert result.message == "查看代码"
        assert result.explicit is True
    
    def test_parse_code_prefix(self):
        """测试解析 @code 前缀"""
        result = self.parser.parse_command("@code 修改文件")
        assert result.provider == "claude"
        assert result.execution_layer == "cli"
        assert result.message == "修改文件"
        assert result.explicit is True
    
    def test_parse_gemini_cli_prefix(self):
        """测试解析 Gemini CLI 前缀"""
        result = self.parser.parse_command("@gemini-cli 分析项目结构")
        assert result.provider == "gemini"
        assert result.execution_layer == "cli"
        assert result.message == "分析项目结构"
        assert result.explicit is True
    
    def test_parse_no_prefix(self):
        """测试没有前缀的消息"""
        result = self.parser.parse_command("普通消息")
        assert result.provider == "claude"  # 默认提供商
        assert result.execution_layer == "api"  # 默认执行层
        assert result.message == "普通消息"
        assert result.explicit is False
    
    def test_case_insensitive_prefix(self):
        """测试大小写不敏感的前缀匹配"""
        # 大写前缀
        result = self.parser.parse_command("@CLAUDE-API 测试")
        assert result.provider == "claude"
        assert result.execution_layer == "api"
        assert result.message == "测试"
        assert result.explicit is True
        
        # 混合大小写
        result = self.parser.parse_command("@ClAuDe 测试")
        assert result.provider == "claude"
        assert result.execution_layer == "api"
        assert result.message == "测试"
        assert result.explicit is True
    
    def test_prefix_removal(self):
        """测试前缀去除后的消息内容"""
        result = self.parser.parse_command("@claude-api    多个空格")
        assert result.message == "多个空格"  # 应该去除前缀和多余空格
        
        result = self.parser.parse_command("@claude没有空格")
        assert result.message == "没有空格"
    
    def test_detect_cli_keywords_chinese(self):
        """测试检测中文 CLI 关键词"""
        assert self.parser.detect_cli_keywords("查看代码") is True
        assert self.parser.detect_cli_keywords("修改文件") is True
        assert self.parser.detect_cli_keywords("执行命令") is True
        assert self.parser.detect_cli_keywords("分析项目") is True
        assert self.parser.detect_cli_keywords("代码库") is True
    
    def test_detect_cli_keywords_english(self):
        """测试检测英文 CLI 关键词"""
        assert self.parser.detect_cli_keywords("view code") is True
        assert self.parser.detect_cli_keywords("modify file") is True
        assert self.parser.detect_cli_keywords("execute command") is True
        assert self.parser.detect_cli_keywords("analyze project") is True
        assert self.parser.detect_cli_keywords("codebase") is True
    
    def test_detect_cli_keywords_case_insensitive(self):
        """测试 CLI 关键词大小写不敏感"""
        assert self.parser.detect_cli_keywords("VIEW CODE") is True
        assert self.parser.detect_cli_keywords("Modify File") is True
        assert self.parser.detect_cli_keywords("CODEBASE") is True
    
    def test_detect_cli_keywords_in_sentence(self):
        """测试在句子中检测 CLI 关键词"""
        assert self.parser.detect_cli_keywords("请帮我查看代码中的错误") is True
        assert self.parser.detect_cli_keywords("Can you help me view code?") is True
        assert self.parser.detect_cli_keywords("我想分析项目的结构") is True
    
    def test_no_cli_keywords(self):
        """测试不包含 CLI 关键词的消息"""
        assert self.parser.detect_cli_keywords("什么是Python") is False
        assert self.parser.detect_cli_keywords("解释一下量子计算") is False
        assert self.parser.detect_cli_keywords("翻译这段文字") is False
    
    def test_extract_provider_prefix_returns_none(self):
        """测试提取前缀返回 None"""
        result = self.parser.extract_provider_prefix("没有前缀的消息")
        assert result is None
    
    def test_extract_provider_prefix_returns_tuple(self):
        """测试提取前缀返回元组"""
        result = self.parser.extract_provider_prefix("@claude 测试")
        assert result is not None
        provider, layer, message = result
        assert provider == "claude"
        assert layer == "api"
        assert message == "测试"
    
    def test_all_prefixes_mapped(self):
        """测试所有前缀都有映射"""
        prefixes = [
            "@claude-api", "@claude", "@gemini-api", "@gemini",
            "@openai", "@gpt", "@claude-cli", "@code", "@gemini-cli"
        ]
        for prefix in prefixes:
            result = self.parser.extract_provider_prefix(f"{prefix} test")
            assert result is not None, f"Prefix {prefix} should be mapped"
    
    def test_all_cli_keywords_detected(self):
        """测试所有 CLI 关键词都能被检测"""
        keywords = [
            "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
            "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
            "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
            "分析项目", "analyze project", "项目结构", "project structure"
        ]
        for keyword in keywords:
            assert self.parser.detect_cli_keywords(keyword) is True, \
                f"Keyword '{keyword}' should be detected"
    
    def test_prefix_with_special_characters(self):
        """测试前缀后跟特殊字符的情况"""
        # 前缀后直接跟标点符号
        result = self.parser.parse_command("@claude，帮我写代码")
        assert result.provider == "claude"
        assert result.message == "，帮我写代码"
        
        # 前缀后跟换行符
        result = self.parser.parse_command("@claude\n帮我写代码")
        assert result.provider == "claude"
        assert result.message == "帮我写代码"
    
    def test_empty_message_after_prefix(self):
        """测试前缀后消息为空的情况"""
        result = self.parser.parse_command("@claude")
        assert result.provider == "claude"
        assert result.execution_layer == "api"
        assert result.message == ""
        assert result.explicit is True
        
        result = self.parser.parse_command("@claude   ")
        assert result.message == ""
    
    def test_prefix_in_middle_of_message(self):
        """测试前缀在消息中间的情况（不应该被识别）"""
        result = self.parser.parse_command("请使用 @claude 帮我")
        assert result.explicit is False  # 前缀不在开头，不应该被识别
        assert result.message == "请使用 @claude 帮我"
    
    def test_multiple_prefixes(self):
        """测试消息包含多个前缀的情况（只识别第一个）"""
        result = self.parser.parse_command("@claude @gemini 测试")
        assert result.provider == "claude"
        assert result.message == "@gemini 测试"  # 第二个前缀作为消息内容
    
    def test_cli_keywords_with_punctuation(self):
        """测试 CLI 关键词周围有标点符号的情况"""
        assert self.parser.detect_cli_keywords("请帮我「查看代码」") is True
        assert self.parser.detect_cli_keywords("Can you (view code)?") is True
        assert self.parser.detect_cli_keywords("需要：修改文件。") is True
    
    def test_partial_keyword_match(self):
        """测试部分关键词匹配（应该匹配）"""
        # "代码库" 应该匹配 "代码库管理"
        assert self.parser.detect_cli_keywords("代码库管理") is True
        # "view code" 应该匹配 "please view code now"
        assert self.parser.detect_cli_keywords("please view code now") is True
    
    def test_similar_but_not_keyword(self):
        """测试相似但不是关键词的情况"""
        # "代码" 不是关键词（需要 "查看代码" 或 "代码库"）
        assert self.parser.detect_cli_keywords("什么是代码") is False
        # "file" 单独出现不是关键词（需要 "modify file" 等）
        assert self.parser.detect_cli_keywords("what is a file") is False
    
    def test_unicode_and_emoji(self):
        """测试 Unicode 字符和 emoji"""
        result = self.parser.parse_command("@claude 帮我写代码 😊")
        assert result.provider == "claude"
        assert result.message == "帮我写代码 😊"
        
        # CLI 关键词检测应该不受 emoji 影响
        assert self.parser.detect_cli_keywords("查看代码 🔍") is True
    
    def test_very_long_message(self):
        """测试非常长的消息"""
        long_message = "测试" * 1000
        result = self.parser.parse_command(f"@claude {long_message}")
        assert result.provider == "claude"
        assert result.message == long_message
        assert len(result.message) == 2000  # "测试" is 2 characters, * 1000 = 2000
    
    def test_prefix_priority(self):
        """测试前缀优先级（更长的前缀应该优先匹配）"""
        # @claude-cli 应该优先于 @claude
        result = self.parser.parse_command("@claude-cli 测试")
        assert result.provider == "claude"
        assert result.execution_layer == "cli"
        assert result.message == "测试"
        
        # @gemini-api 应该优先于 @gemini
        result = self.parser.parse_command("@gemini-api 测试")
        assert result.provider == "gemini"
        assert result.execution_layer == "api"
        assert result.message == "测试"
