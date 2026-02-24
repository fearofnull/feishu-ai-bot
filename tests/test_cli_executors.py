"""
Unit tests for AI CLI executors

Tests for ClaudeCodeCLIExecutor and GeminiCLIExecutor.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import tempfile
import os
import json
from feishu_bot.claude_cli_executor import ClaudeCodeCLIExecutor
from feishu_bot.gemini_cli_executor import GeminiCLIExecutor
from feishu_bot.models import ExecutionResult


class TestClaudeCodeCLIExecutor(unittest.TestCase):
    """Test ClaudeCodeCLIExecutor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = os.path.join(self.temp_dir, "sessions.json")
        self.executor = ClaudeCodeCLIExecutor(
            target_dir=self.temp_dir,
            timeout=10,
            use_native_session=True,
            session_storage_path=self.session_file
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_command_name_windows(self):
        """Test command name on Windows"""
        with patch('platform.system', return_value='Windows'):
            executor = ClaudeCodeCLIExecutor(self.temp_dir)
            self.assertEqual(executor.get_command_name(), 'claude.cmd')
    
    def test_get_command_name_unix(self):
        """Test command name on Unix-like systems"""
        with patch('platform.system', return_value='Linux'):
            executor = ClaudeCodeCLIExecutor(self.temp_dir)
            self.assertEqual(executor.get_command_name(), 'claude')
    
    def test_verify_directory_exists(self):
        """Test directory verification when directory exists"""
        self.assertTrue(self.executor.verify_directory())
    
    def test_verify_directory_not_exists(self):
        """Test directory verification when directory doesn't exist"""
        executor = ClaudeCodeCLIExecutor("/nonexistent/path")
        self.assertFalse(executor.verify_directory())
    
    def test_build_command_args_basic(self):
        """Test building basic command arguments"""
        args = self.executor.build_command_args("test prompt")
        
        self.assertIn(self.executor.get_command_name(), args)
        self.assertIn("--add-dir", args)
        self.assertIn(self.temp_dir, args)
        self.assertIn("-p", args)
        self.assertIn("test prompt", args)
    
    def test_build_command_args_with_session(self):
        """Test building command arguments with session"""
        # Set up a session
        self.executor.session_map["user123"] = "session456"
        
        args = self.executor.build_command_args(
            "test prompt",
            additional_params={"user_id": "user123"}
        )
        
        self.assertIn("--session", args)
        self.assertIn("session456", args)
    
    def test_build_command_args_with_additional_params(self):
        """Test building command arguments with additional parameters"""
        args = self.executor.build_command_args(
            "test prompt",
            additional_params={
                "model": "claude-3-5-sonnet",
                "max-tokens": 4096,
                "json": True
            }
        )
        
        self.assertIn("--model", args)
        self.assertIn("claude-3-5-sonnet", args)
        self.assertIn("--max-tokens", args)
        self.assertIn("4096", args)
        self.assertIn("--json", args)
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.executor.execute("test prompt")
        
        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "Success output")
        self.assertIsNone(result.error_message)
    
    @patch('subprocess.run')
    def test_execute_failure(self, mock_run):
        """Test failed command execution"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result
        
        result = self.executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertEqual(result.stderr, "Error output")
        self.assertIsNotNone(result.error_message)
    
    @patch('subprocess.run')
    def test_execute_timeout(self, mock_run):
        """Test command execution timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("claude", 10)
        
        result = self.executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertIn("超时", result.error_message)
    
    @patch('subprocess.run')
    def test_execute_command_not_found(self, mock_run):
        """Test command execution when CLI not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertIn("未安装", result.error_message)
    
    def test_execute_directory_not_exists(self):
        """Test execution when target directory doesn't exist"""
        executor = ClaudeCodeCLIExecutor("/nonexistent/path")
        result = executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertIn("目标目录不存在", result.error_message)
    
    def test_session_mapping_persistence(self):
        """Test session mapping save and load"""
        # Save a session mapping
        self.executor.session_map["user123"] = "session456"
        self.executor.save_session_mappings()
        
        # Create a new executor and load
        new_executor = ClaudeCodeCLIExecutor(
            target_dir=self.temp_dir,
            session_storage_path=self.session_file
        )
        
        self.assertEqual(new_executor.session_map.get("user123"), "session456")
    
    def test_clear_session(self):
        """Test clearing a user session"""
        self.executor.session_map["user123"] = "session456"
        self.executor.clear_session("user123")
        
        self.assertNotIn("user123", self.executor.session_map)
    
    def test_update_session_id(self):
        """Test updating session ID"""
        self.executor.update_session_id("user123", "new_session")
        
        self.assertEqual(self.executor.session_map["user123"], "new_session")


class TestGeminiCLIExecutor(unittest.TestCase):
    """Test GeminiCLIExecutor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = os.path.join(self.temp_dir, "sessions.json")
        self.executor = GeminiCLIExecutor(
            target_dir=self.temp_dir,
            timeout=10,
            use_native_session=True,
            session_storage_path=self.session_file
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_command_name(self):
        """Test command name"""
        self.assertEqual(self.executor.get_command_name(), 'gemini')
    
    def test_verify_directory_exists(self):
        """Test directory verification when directory exists"""
        self.assertTrue(self.executor.verify_directory())
    
    def test_verify_directory_not_exists(self):
        """Test directory verification when directory doesn't exist"""
        executor = GeminiCLIExecutor("/nonexistent/path")
        self.assertFalse(executor.verify_directory())
    
    def test_build_command_args_basic(self):
        """Test building basic command arguments"""
        args = self.executor.build_command_args("test prompt")
        
        self.assertIn("gemini", args)
        self.assertIn("--cwd", args)
        self.assertIn(self.temp_dir, args)
        self.assertIn("--prompt", args)
        self.assertIn("test prompt", args)
    
    def test_build_command_args_with_session(self):
        """Test building command arguments with session"""
        # Set up a session
        self.executor.session_map["user123"] = "session456"
        
        args = self.executor.build_command_args(
            "test prompt",
            additional_params={"user_id": "user123"}
        )
        
        self.assertIn("--session", args)
        self.assertIn("session456", args)
    
    def test_build_command_args_with_additional_params(self):
        """Test building command arguments with additional parameters"""
        args = self.executor.build_command_args(
            "test prompt",
            additional_params={
                "model": "gemini-2.0-flash",
                "temperature": 0.7,
                "json": True
            }
        )
        
        self.assertIn("--model", args)
        self.assertIn("gemini-2.0-flash", args)
        self.assertIn("--temperature", args)
        self.assertIn("0.7", args)
        self.assertIn("--json", args)
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.executor.execute("test prompt")
        
        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "Success output")
        self.assertIsNone(result.error_message)
    
    @patch('subprocess.run')
    def test_execute_failure(self, mock_run):
        """Test failed command execution"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result
        
        result = self.executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertEqual(result.stderr, "Error output")
        self.assertIsNotNone(result.error_message)
    
    @patch('subprocess.run')
    def test_execute_timeout(self, mock_run):
        """Test command execution timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("gemini", 10)
        
        result = self.executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertIn("超时", result.error_message)
    
    @patch('subprocess.run')
    def test_execute_command_not_found(self, mock_run):
        """Test command execution when CLI not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertIn("未安装", result.error_message)
    
    def test_execute_directory_not_exists(self):
        """Test execution when target directory doesn't exist"""
        executor = GeminiCLIExecutor("/nonexistent/path")
        result = executor.execute("test prompt")
        
        self.assertFalse(result.success)
        self.assertIn("目标目录不存在", result.error_message)
    
    def test_session_mapping_persistence(self):
        """Test session mapping save and load"""
        # Save a session mapping
        self.executor.session_map["user123"] = "session456"
        self.executor.save_session_mappings()
        
        # Create a new executor and load
        new_executor = GeminiCLIExecutor(
            target_dir=self.temp_dir,
            session_storage_path=self.session_file
        )
        
        self.assertEqual(new_executor.session_map.get("user123"), "session456")
    
    def test_clear_session(self):
        """Test clearing a user session"""
        self.executor.session_map["user123"] = "session456"
        self.executor.clear_session("user123")
        
        self.assertNotIn("user123", self.executor.session_map)
    
    def test_update_session_id(self):
        """Test updating session ID"""
        self.executor.update_session_id("user123", "new_session")
        
        self.assertEqual(self.executor.session_map["user123"], "new_session")
    
    def test_shared_session_storage(self):
        """Test that Claude and Gemini executors share session storage"""
        # Create both executors with same storage path
        claude_executor = ClaudeCodeCLIExecutor(
            target_dir=self.temp_dir,
            session_storage_path=self.session_file
        )
        gemini_executor = GeminiCLIExecutor(
            target_dir=self.temp_dir,
            session_storage_path=self.session_file
        )
        
        # Save sessions from both
        claude_executor.session_map["user1"] = "claude_session_1"
        claude_executor.save_session_mappings()
        
        gemini_executor.session_map["user2"] = "gemini_session_2"
        gemini_executor.save_session_mappings()
        
        # Load and verify both sessions exist
        with open(self.session_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("claude_cli_sessions", data)
        self.assertIn("gemini_cli_sessions", data)
        self.assertEqual(data["claude_cli_sessions"]["user1"], "claude_session_1")
        self.assertEqual(data["gemini_cli_sessions"]["user2"], "gemini_session_2")


if __name__ == '__main__':
    unittest.main()
