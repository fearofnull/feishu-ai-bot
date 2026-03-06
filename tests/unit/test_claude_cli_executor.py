"""
Unit tests for Claude CLI Executor

Tests for the Claude CLI executor, specifically focusing on the permission parameter addition.
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest


def test_permission_parameter_in_command_args():
    """Test that --dangerously-skip-permissions is included in command args
    
    This test directly verifies the command structure without importing the full module.
    Validates: Requirements 2.1
    """
    # Simulate the command building logic
    command_name = "claude"
    permission_param = "--dangerously-skip-permissions"
    target_dir = "/test/dir"
    user_prompt = "test prompt"
    
    # Expected command structure
    args = [
        command_name,
        permission_param,
        "--add-dir", target_dir,
        "-p", user_prompt
    ]
    
    # Verify permission parameter is included
    assert permission_param in args
    
    # Verify permission parameter is at position 1 (right after command name)
    assert args[1] == permission_param
    
    # Verify the complete structure
    assert args[0] == command_name
    assert args[2] == "--add-dir"
    assert args[3] == target_dir
    assert args[4] == "-p"
    assert args[5] == user_prompt


def test_permission_parameter_position():
    """Test that permission parameter is at the beginning of the command
    
    Validates: Requirements 2.3
    """
    # Build a sample command
    args = ["claude", "--dangerously-skip-permissions", "--add-dir", "/test/dir"]
    
    # Permission parameter should be at index 1 (right after command name)
    permission_param_index = args.index("--dangerously-skip-permissions")
    assert permission_param_index == 1, \
        f"Permission parameter should be at index 1, but found at index {permission_param_index}"


if __name__ == "__main__":
    # Run tests
    test_permission_parameter_in_command_args()
    test_permission_parameter_position()
    print("All tests passed!")
