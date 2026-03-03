"""
Tests for Web Admin Logging Configuration

This module tests the logging configuration and functionality.
"""

import pytest
import os
import tempfile
import shutil
import logging
from flask import Flask
from feishu_bot.web_admin.logging_config import (
    configure_logging,
    log_authentication_attempt,
    log_api_error,
    log_config_change,
    get_logger
)


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files"""
    log_dir = tempfile.mkdtemp()
    yield log_dir
    # Cleanup
    shutil.rmtree(log_dir, ignore_errors=True)


@pytest.fixture
def test_app(temp_log_dir):
    """Create a test Flask app with logging configured"""
    app = Flask(__name__)
    configure_logging(
        app,
        log_level="DEBUG",
        log_dir=temp_log_dir,
        enable_file_logging=True
    )
    return app


def test_configure_logging_creates_log_files(test_app, temp_log_dir):
    """Test that logging configuration creates log files"""
    # Trigger some logging
    logger = get_logger(__name__)
    logger.info("Test message")
    logger.error("Test error")
    
    # Check that log files are created
    assert os.path.exists(os.path.join(temp_log_dir, "web_admin.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "web_admin_error.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "web_admin_access.log"))
    assert os.path.exists(os.path.join(temp_log_dir, "web_admin_auth.log"))


def test_log_authentication_attempt_success(temp_log_dir):
    """Test logging successful authentication"""
    # Configure logging
    app = Flask(__name__)
    configure_logging(app, log_level="INFO", log_dir=temp_log_dir)
    
    # Log successful authentication
    log_authentication_attempt(
        success=True,
        username="admin",
        ip_address="192.168.1.100"
    )
    
    # Check auth log file
    auth_log_file = os.path.join(temp_log_dir, "web_admin_auth.log")
    assert os.path.exists(auth_log_file)
    
    with open(auth_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Authentication successful" in content
        assert "user=admin" in content
        assert "ip=192.168.1.100" in content


def test_log_authentication_attempt_failure(temp_log_dir):
    """Test logging failed authentication"""
    # Configure logging
    app = Flask(__name__)
    configure_logging(app, log_level="INFO", log_dir=temp_log_dir)
    
    # Log failed authentication
    log_authentication_attempt(
        success=False,
        username="admin",
        ip_address="192.168.1.100",
        reason="Invalid password"
    )
    
    # Check auth log file
    auth_log_file = os.path.join(temp_log_dir, "web_admin_auth.log")
    assert os.path.exists(auth_log_file)
    
    with open(auth_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Authentication failed" in content
        assert "user=admin" in content
        assert "ip=192.168.1.100" in content
        assert "reason=Invalid password" in content


def test_log_api_error(temp_log_dir):
    """Test logging API errors"""
    # Configure logging
    app = Flask(__name__)
    configure_logging(app, log_level="INFO", log_dir=temp_log_dir)
    
    # Log API error
    error = ValueError("Invalid provider")
    log_api_error(
        endpoint="/api/configs",
        error=error,
        status_code=400,
        user="admin"
    )
    
    # Check error log file
    error_log_file = os.path.join(temp_log_dir, "web_admin_error.log")
    assert os.path.exists(error_log_file)
    
    with open(error_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "API error in /api/configs" in content
        assert "ValueError" in content
        assert "status=400" in content
        assert "user=admin" in content


def test_log_config_change(temp_log_dir):
    """Test logging configuration changes"""
    # Configure logging
    app = Flask(__name__)
    configure_logging(app, log_level="INFO", log_dir=temp_log_dir)
    
    # Log config change
    log_config_change(
        session_id="ou_123",
        action="update",
        user="admin",
        changes={"default_provider": "claude", "default_layer": "api"}
    )
    
    # Check application log file
    app_log_file = os.path.join(temp_log_dir, "web_admin.log")
    assert os.path.exists(app_log_file)
    
    with open(app_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Config update" in content
        assert "session=ou_123" in content
        assert "user=admin" in content
        assert "default_provider" in content


def test_log_levels(temp_log_dir):
    """Test different log levels"""
    # Configure logging with INFO level
    app = Flask(__name__)
    configure_logging(app, log_level="INFO", log_dir=temp_log_dir)
    
    logger = get_logger(__name__)
    
    # Log at different levels
    logger.debug("Debug message")  # Should not appear
    logger.info("Info message")    # Should appear
    logger.warning("Warning message")  # Should appear
    logger.error("Error message")  # Should appear
    
    # Check application log
    app_log_file = os.path.join(temp_log_dir, "web_admin.log")
    with open(app_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Debug message" not in content  # DEBUG not logged at INFO level
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content


def test_log_format(temp_log_dir):
    """Test log format includes timestamp, level, and module"""
    # Configure logging
    app = Flask(__name__)
    configure_logging(app, log_level="INFO", log_dir=temp_log_dir)
    
    logger = get_logger(__name__)
    logger.info("Test format message")
    
    # Check log format
    app_log_file = os.path.join(temp_log_dir, "web_admin.log")
    with open(app_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Format: [YYYY-MM-DD HH:MM:SS] [LEVEL] [module] message
        assert "[INFO]" in content
        assert "Test format message" in content
        # Check timestamp format (basic check)
        assert content.count('[') >= 3  # At least [timestamp] [level] [module]


def test_error_log_only_errors(temp_log_dir):
    """Test that error log only contains ERROR level messages"""
    # Configure logging
    app = Flask(__name__)
    configure_logging(app, log_level="DEBUG", log_dir=temp_log_dir)
    
    logger = get_logger(__name__)
    
    # Log at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Check error log only has errors
    error_log_file = os.path.join(temp_log_dir, "web_admin_error.log")
    with open(error_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" not in content
        assert "Error message" in content


def test_get_logger():
    """Test getting a logger instance"""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_logging_without_file_logging():
    """Test logging configuration without file logging"""
    app = Flask(__name__)
    
    # Configure without file logging
    configure_logging(
        app,
        log_level="INFO",
        enable_file_logging=False
    )
    
    # Should not raise any errors
    logger = get_logger(__name__)
    logger.info("Test message")
    logger.error("Test error")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
