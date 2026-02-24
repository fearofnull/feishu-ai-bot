"""
CommandParser 属性测试

使用 Hypothesis 进行基于属性的测试，验证命令解析器的通用正确性属性
"""
import pytest
from hypothesis import given, strategies as st, settings
from feishu_bot.command_parser import CommandParser
from feishu_bot.models import ParsedCommand


class TestCommandParserProperties:
    """CommandParser 属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = CommandParser()
    
    # Feature: feishu-ai-bot, Property 36: 命令前缀解析
    # Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.7, 11.8
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_claude_api_prefix_parsing(self, message_content):
        """
        Property 36: 命令前缀解析 - Claude API
        
        For any message with @claude-api or @claude prefix,
        the parser should extract "claude" as provider and "api" as execution layer,
        and remove the prefix from the message content.
        
        Validates: Requirements 11.1, 11.7, 11.8
        """
        # Test @claude-api prefix
        message = f"@claude-api {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "claude", \
            f"Expected provider 'claude', got '{result.provider}'"
        assert result.execution_layer == "api", \
            f"Expected layer 'api', got '{result.execution_layer}'"
        # Parser strips whitespace, so compare with stripped content
        assert result.message == message_content.strip(), \
            f"Expected message '{message_content.strip()}', got '{result.message}'"
        assert result.explicit is True, \
            "Expected explicit=True for prefixed command"
        
        # Test @claude prefix (short form)
        message = f"@claude {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "claude"
        assert result.execution_layer == "api"
        assert result.message == message_content.strip()
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_gemini_api_prefix_parsing(self, message_content):
        """
        Property 36: 命令前缀解析 - Gemini API
        
        For any message with @gemini-api or @gemini prefix,
        the parser should extract "gemini" as provider and "api" as execution layer.
        
        Validates: Requirements 11.2, 11.7, 11.8
        """
        # Test @gemini-api prefix
        message = f"@gemini-api {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "gemini"
        assert result.execution_layer == "api"
        assert result.message == message_content.strip()
        assert result.explicit is True
        
        # Test @gemini prefix (short form)
        message = f"@gemini {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "gemini"
        assert result.execution_layer == "api"
        assert result.message == message_content.strip()
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_openai_api_prefix_parsing(self, message_content):
        """
        Property 36: 命令前缀解析 - OpenAI API
        
        For any message with @openai or @gpt prefix,
        the parser should extract "openai" as provider and "api" as execution layer.
        
        Validates: Requirements 11.3, 11.7, 11.8
        """
        # Test @openai prefix
        message = f"@openai {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "openai"
        assert result.execution_layer == "api"
        assert result.message == message_content.strip()
        assert result.explicit is True
        
        # Test @gpt prefix (short form)
        message = f"@gpt {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "openai"
        assert result.execution_layer == "api"
        assert result.message == message_content.strip()
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_claude_cli_prefix_parsing(self, message_content):
        """
        Property 36: 命令前缀解析 - Claude CLI
        
        For any message with @claude-cli or @code prefix,
        the parser should extract "claude" as provider and "cli" as execution layer.
        
        Validates: Requirements 11.4, 11.7, 11.8
        """
        # Test @claude-cli prefix
        message = f"@claude-cli {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "claude"
        assert result.execution_layer == "cli"
        assert result.message == message_content.strip()
        assert result.explicit is True
        
        # Test @code prefix (short form)
        message = f"@code {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "claude"
        assert result.execution_layer == "cli"
        assert result.message == message_content.strip()
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_gemini_cli_prefix_parsing(self, message_content):
        """
        Property 36: 命令前缀解析 - Gemini CLI
        
        For any message with @gemini-cli prefix,
        the parser should extract "gemini" as provider and "cli" as execution layer.
        
        Validates: Requirements 11.5, 11.7, 11.8
        """
        message = f"@gemini-cli {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "gemini"
        assert result.execution_layer == "cli"
        assert result.message == message_content.strip()
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(
            lambda x: not any(x.lower().startswith(prefix.lower()) 
                            for prefix in ["@claude", "@gemini", "@openai", "@gpt", "@code"])
        )
    )
    def test_no_prefix_returns_not_explicit(self, message_content):
        """
        Property 36: 命令前缀解析 - 无前缀
        
        For any message without an AI provider prefix,
        the parser should mark the command as not explicit (explicit=false).
        
        Validates: Requirements 11.7
        """
        result = self.parser.parse_command(message_content)
        
        assert result.explicit is False, \
            "Expected explicit=False for message without prefix"
        assert result.message == message_content, \
            "Message content should remain unchanged when no prefix"
    
    @settings(max_examples=100)
    @given(
        prefix=st.sampled_from([
            "@claude-api", "@claude", "@gemini-api", "@gemini",
            "@openai", "@gpt", "@claude-cli", "@code", "@gemini-cli"
        ]),
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_prefix_removal_consistency(self, prefix, message_content):
        """
        Property 36: 命令前缀解析 - 前缀去除
        
        For any valid prefix and message content,
        the parser should remove the prefix from the message content.
        
        Validates: Requirements 11.7
        """
        message = f"{prefix} {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.message == message_content.strip(), \
            f"Expected message '{message_content.strip()}', got '{result.message}'"
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        prefix=st.sampled_from([
            "@claude-api", "@CLAUDE-API", "@Claude-Api",
            "@gemini", "@GEMINI", "@Gemini",
            "@openai", "@OPENAI", "@OpenAI",
            "@claude-cli", "@CLAUDE-CLI", "@Claude-Cli"
        ]),
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_case_insensitive_prefix_matching(self, prefix, message_content):
        """
        Property 36: 命令前缀解析 - 大小写不敏感
        
        For any prefix with different case combinations,
        the parser should support case-insensitive prefix matching.
        
        Validates: Requirements 11.8
        """
        message = f"{prefix} {message_content}"
        result = self.parser.parse_command(message)
        
        # Should successfully parse regardless of case
        assert result.explicit is True, \
            f"Expected explicit=True for prefix '{prefix}'"
        assert result.message == message_content.strip(), \
            f"Expected message '{message_content.strip()}', got '{result.message}'"
        
        # Verify provider is correctly identified
        prefix_lower = prefix.lower()
        if "claude" in prefix_lower:
            assert result.provider == "claude"
            if "cli" in prefix_lower or "code" in prefix_lower:
                assert result.execution_layer == "cli"
            else:
                assert result.execution_layer == "api"
        elif "gemini" in prefix_lower:
            assert result.provider == "gemini"
            if "cli" in prefix_lower:
                assert result.execution_layer == "cli"
            else:
                assert result.execution_layer == "api"
        elif "openai" in prefix_lower or "gpt" in prefix_lower:
            assert result.provider == "openai"
            assert result.execution_layer == "api"
    
    @settings(max_examples=100)
    @given(
        prefix=st.sampled_from([
            "@claude-api", "@claude", "@gemini-api", "@gemini",
            "@openai", "@gpt", "@claude-cli", "@code", "@gemini-cli"
        ]),
        whitespace=st.text(
            alphabet=st.characters(whitelist_categories=("Zs",)),
            min_size=0,
            max_size=10
        ),
        message_content=st.text(min_size=1, max_size=100)
    )
    def test_prefix_with_variable_whitespace(self, prefix, whitespace, message_content):
        """
        Property 36: 命令前缀解析 - 处理可变空白字符
        
        For any prefix followed by variable whitespace,
        the parser should correctly extract the message content
        without leading/trailing whitespace.
        
        Validates: Requirements 11.7
        """
        message = f"{prefix}{whitespace}{message_content}"
        result = self.parser.parse_command(message)
        
        assert result.explicit is True
        # The message should be trimmed of leading/trailing whitespace
        assert result.message == message_content.strip() or result.message == message_content, \
            f"Expected message '{message_content}' (or trimmed), got '{result.message}'"
    
    @settings(max_examples=100)
    @given(
        provider_prefix=st.sampled_from([
            ("@claude-api", "claude", "api"),
            ("@claude", "claude", "api"),
            ("@gemini-api", "gemini", "api"),
            ("@gemini", "gemini", "api"),
            ("@openai", "openai", "api"),
            ("@gpt", "openai", "api"),
            ("@claude-cli", "claude", "cli"),
            ("@code", "claude", "cli"),
            ("@gemini-cli", "gemini", "cli"),
        ]),
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_all_prefixes_map_correctly(self, provider_prefix, message_content):
        """
        Property 36: 命令前缀解析 - 所有前缀映射正确
        
        For any valid prefix-provider-layer combination,
        the parser should correctly map the prefix to the expected provider and layer.
        
        Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
        """
        prefix, expected_provider, expected_layer = provider_prefix
        message = f"{prefix} {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == expected_provider, \
            f"For prefix '{prefix}', expected provider '{expected_provider}', got '{result.provider}'"
        assert result.execution_layer == expected_layer, \
            f"For prefix '{prefix}', expected layer '{expected_layer}', got '{result.execution_layer}'"
        assert result.message == message_content.strip()
        assert result.explicit is True
    
    @settings(max_examples=100)
    @given(
        message_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
    )
    def test_longer_prefix_takes_precedence(self, message_content):
        """
        Property 36: 命令前缀解析 - 更长前缀优先
        
        When a message could match multiple prefixes (e.g., @claude-cli vs @claude),
        the parser should match the longer, more specific prefix first.
        
        Validates: Requirements 11.4, 11.7
        """
        # @claude-cli should match as CLI, not as @claude (API)
        message = f"@claude-cli {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "claude"
        assert result.execution_layer == "cli", \
            "Expected 'cli' layer for @claude-cli, not 'api' from @claude"
        assert result.message == message_content.strip()
        
        # @gemini-cli should match as CLI, not as @gemini (API)
        message = f"@gemini-cli {message_content}"
        result = self.parser.parse_command(message)
        
        assert result.provider == "gemini"
        assert result.execution_layer == "cli", \
            "Expected 'cli' layer for @gemini-cli, not 'api' from @gemini"
        assert result.message == message_content.strip()

    # Feature: feishu-ai-bot, Property 37: CLI 关键词检测
    # Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            # 代码相关 - 中文
            "查看代码", "分析代码", "代码库",
            # 代码相关 - 英文
            "view code", "analyze code", "codebase",
        ]),
        prefix=st.text(min_size=0, max_size=50),
        suffix=st.text(min_size=0, max_size=50)
    )
    def test_code_related_keywords_detected(self, keyword, prefix, suffix):
        """
        Property 37: CLI 关键词检测 - 代码相关关键词
        
        For any message containing code-related keywords (e.g., "查看代码", "view code", 
        "分析代码", "analyze code", "代码库", "codebase"),
        the detect_cli_keywords method should return true.
        
        Validates: Requirements 12.1, 12.7
        """
        message = f"{prefix}{keyword}{suffix}"
        result = self.parser.detect_cli_keywords(message)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for message containing '{keyword}'"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            # 文件操作 - 中文
            "修改文件", "读取文件", "写入文件", "创建文件",
            # 文件操作 - 英文
            "modify file", "read file", "write file", "create file",
        ]),
        prefix=st.text(min_size=0, max_size=50),
        suffix=st.text(min_size=0, max_size=50)
    )
    def test_file_operation_keywords_detected(self, keyword, prefix, suffix):
        """
        Property 37: CLI 关键词检测 - 文件操作关键词
        
        For any message containing file operation keywords (e.g., "修改文件", "modify file",
        "读取文件", "read file"),
        the detect_cli_keywords method should return true.
        
        Validates: Requirements 12.2, 12.7
        """
        message = f"{prefix}{keyword}{suffix}"
        result = self.parser.detect_cli_keywords(message)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for message containing '{keyword}'"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            # 命令执行 - 中文
            "执行命令", "运行脚本",
            # 命令执行 - 英文
            "execute command", "run script",
        ]),
        prefix=st.text(min_size=0, max_size=50),
        suffix=st.text(min_size=0, max_size=50)
    )
    def test_command_execution_keywords_detected(self, keyword, prefix, suffix):
        """
        Property 37: CLI 关键词检测 - 命令执行关键词
        
        For any message containing command execution keywords (e.g., "执行命令", "execute command",
        "运行脚本", "run script"),
        the detect_cli_keywords method should return true.
        
        Validates: Requirements 12.3, 12.7
        """
        message = f"{prefix}{keyword}{suffix}"
        result = self.parser.detect_cli_keywords(message)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for message containing '{keyword}'"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            # 项目分析 - 中文
            "分析项目", "项目结构",
            # 项目分析 - 英文
            "analyze project", "project structure",
        ]),
        prefix=st.text(min_size=0, max_size=50),
        suffix=st.text(min_size=0, max_size=50)
    )
    def test_project_analysis_keywords_detected(self, keyword, prefix, suffix):
        """
        Property 37: CLI 关键词检测 - 项目分析关键词
        
        For any message containing project analysis keywords (e.g., "分析项目", "analyze project",
        "项目结构", "project structure"),
        the detect_cli_keywords method should return true.
        
        Validates: Requirements 12.4, 12.7
        """
        message = f"{prefix}{keyword}{suffix}"
        result = self.parser.detect_cli_keywords(message)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for message containing '{keyword}'"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
            "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
            "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
            "分析项目", "analyze project", "项目结构", "project structure",
        ])
    )
    def test_all_cli_keywords_detected(self, keyword):
        """
        Property 37: CLI 关键词检测 - 所有 CLI 关键词
        
        For any message containing any CLI keyword (Chinese or English),
        the detect_cli_keywords method should return true.
        
        Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.7
        """
        # Test keyword alone
        result = self.parser.detect_cli_keywords(keyword)
        assert result is True, \
            f"Expected detect_cli_keywords to return True for keyword '{keyword}'"
        
        # Test keyword in a sentence
        message = f"请帮我{keyword}，谢谢"
        result = self.parser.detect_cli_keywords(message)
        assert result is True, \
            f"Expected detect_cli_keywords to return True for message containing '{keyword}'"
    
    @settings(max_examples=100)
    @given(
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: not any(
                keyword.lower() in x.lower() 
                for keyword in [
                    "查看代码", "view code", "分析代码", "analyze code", "代码库", "codebase",
                    "修改文件", "modify file", "读取文件", "read file", "写入文件", "write file",
                    "创建文件", "create file", "执行命令", "execute command", "运行脚本", "run script",
                    "分析项目", "analyze project", "项目结构", "project structure",
                ]
            )
        )
    )
    def test_no_cli_keywords_returns_false(self, message):
        """
        Property 37: CLI 关键词检测 - 无 CLI 关键词
        
        For any message that does not contain any CLI keywords,
        the detect_cli_keywords method should return false.
        
        Validates: Requirements 12.6
        """
        result = self.parser.detect_cli_keywords(message)
        
        assert result is False, \
            f"Expected detect_cli_keywords to return False for message without CLI keywords: '{message}'"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            "查看代码", "VIEW CODE", "View Code",
            "修改文件", "MODIFY FILE", "Modify File",
            "执行命令", "EXECUTE COMMAND", "Execute Command",
            "分析项目", "ANALYZE PROJECT", "Analyze Project",
            "代码库", "CODEBASE", "CodeBase",
        ])
    )
    def test_case_insensitive_keyword_detection(self, keyword):
        """
        Property 37: CLI 关键词检测 - 大小写不敏感
        
        For any CLI keyword with different case combinations,
        the detect_cli_keywords method should support case-insensitive matching.
        
        Validates: Requirements 12.7
        """
        result = self.parser.detect_cli_keywords(keyword)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for keyword '{keyword}' (case-insensitive)"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            "查看代码", "view code", "修改文件", "modify file",
            "执行命令", "execute command", "分析项目", "analyze project",
        ]),
        other_text=st.text(min_size=10, max_size=100)
    )
    def test_keyword_detection_in_context(self, keyword, other_text):
        """
        Property 37: CLI 关键词检测 - 上下文中的关键词
        
        For any CLI keyword embedded in a larger message context,
        the detect_cli_keywords method should still detect it.
        
        Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.7
        """
        # Test keyword at the beginning
        message = f"{keyword} {other_text}"
        result = self.parser.detect_cli_keywords(message)
        assert result is True, \
            f"Expected to detect keyword '{keyword}' at the beginning of message"
        
        # Test keyword in the middle
        message = f"{other_text[:len(other_text)//2]} {keyword} {other_text[len(other_text)//2:]}"
        result = self.parser.detect_cli_keywords(message)
        assert result is True, \
            f"Expected to detect keyword '{keyword}' in the middle of message"
        
        # Test keyword at the end
        message = f"{other_text} {keyword}"
        result = self.parser.detect_cli_keywords(message)
        assert result is True, \
            f"Expected to detect keyword '{keyword}' at the end of message"
    
    @settings(max_examples=100)
    @given(
        keywords=st.lists(
            st.sampled_from([
                "查看代码", "view code", "修改文件", "modify file",
                "执行命令", "execute command", "分析项目", "analyze project",
                "代码库", "codebase", "项目结构", "project structure",
            ]),
            min_size=2,
            max_size=5
        )
    )
    def test_multiple_keywords_detected(self, keywords):
        """
        Property 37: CLI 关键词检测 - 多个关键词
        
        For any message containing multiple CLI keywords,
        the detect_cli_keywords method should return true.
        
        Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.7
        """
        message = " ".join(keywords)
        result = self.parser.detect_cli_keywords(message)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for message with multiple keywords: '{message}'"
    
    @settings(max_examples=100)
    @given(
        keyword=st.sampled_from([
            "查看代码", "view code", "修改文件", "modify file",
            "执行命令", "execute command", "代码库", "codebase",
        ])
    )
    def test_chinese_and_english_keywords_both_work(self, keyword):
        """
        Property 37: CLI 关键词检测 - 中英文关键词支持
        
        For any CLI keyword (Chinese or English),
        the detect_cli_keywords method should detect it correctly.
        
        Validates: Requirements 12.7
        """
        result = self.parser.detect_cli_keywords(keyword)
        
        assert result is True, \
            f"Expected detect_cli_keywords to return True for keyword '{keyword}'"
        
        # Verify both Chinese and English versions work
        if "code" in keyword.lower() or "代码" in keyword:
            # Test both versions
            chinese_result = self.parser.detect_cli_keywords("查看代码")
            english_result = self.parser.detect_cli_keywords("view code")
            assert chinese_result is True and english_result is True, \
                "Both Chinese and English versions should be detected"
