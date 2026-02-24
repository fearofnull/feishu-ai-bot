"""
Unit tests for SSL certificate configuration.

Tests cover:
- SSL_CERT_FILE environment variable setting
- SSL_CERT_DIR environment variable clearing
- Certificate path retrieval
- Configuration status checking
- Error handling

Requirements:
- Requirement 8.1: Set SSL_CERT_FILE to certifi certificate path
- Requirement 8.2: Clear SSL_CERT_DIR environment variable
"""

import os
import pytest
import certifi
from unittest.mock import patch
from feishu_bot.ssl_config import (
    configure_ssl,
    get_ssl_cert_path,
    is_ssl_configured
)


class TestConfigureSSL:
    """Test suite for configure_ssl function."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        # Save original environment
        self.original_cert_file = os.environ.get('SSL_CERT_FILE')
        self.original_cert_dir = os.environ.get('SSL_CERT_DIR')
        
        # Clear SSL environment variables
        if 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
        if 'SSL_CERT_DIR' in os.environ:
            del os.environ['SSL_CERT_DIR']
    
    def teardown_method(self):
        """Restore original environment after each test."""
        # Restore original environment
        if self.original_cert_file is not None:
            os.environ['SSL_CERT_FILE'] = self.original_cert_file
        elif 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
            
        if self.original_cert_dir is not None:
            os.environ['SSL_CERT_DIR'] = self.original_cert_dir
        elif 'SSL_CERT_DIR' in os.environ:
            del os.environ['SSL_CERT_DIR']
    
    def test_sets_ssl_cert_file(self):
        """
        Test that configure_ssl sets SSL_CERT_FILE to certifi certificate path.
        
        Validates: Requirement 8.1
        """
        # Act
        configure_ssl()
        
        # Assert
        assert 'SSL_CERT_FILE' in os.environ
        assert os.environ['SSL_CERT_FILE'] == certifi.where()
        assert os.path.exists(os.environ['SSL_CERT_FILE'])
    
    def test_clears_ssl_cert_dir(self):
        """
        Test that configure_ssl clears SSL_CERT_DIR environment variable.
        
        Validates: Requirement 8.2
        """
        # Arrange
        os.environ['SSL_CERT_DIR'] = '/some/directory'
        
        # Act
        configure_ssl()
        
        # Assert
        assert 'SSL_CERT_DIR' not in os.environ
    
    def test_clears_ssl_cert_dir_when_not_set(self):
        """
        Test that configure_ssl works correctly when SSL_CERT_DIR is not set.
        
        Validates: Requirement 8.2
        """
        # Arrange - SSL_CERT_DIR is already cleared in setup_method
        
        # Act
        configure_ssl()
        
        # Assert
        assert 'SSL_CERT_DIR' not in os.environ
        assert 'SSL_CERT_FILE' in os.environ
    
    def test_overwrites_existing_ssl_cert_file(self):
        """
        Test that configure_ssl overwrites existing SSL_CERT_FILE value.
        
        Validates: Requirement 8.1
        """
        # Arrange
        os.environ['SSL_CERT_FILE'] = '/old/path/to/cert.pem'
        
        # Act
        configure_ssl()
        
        # Assert
        assert os.environ['SSL_CERT_FILE'] == certifi.where()
        assert os.environ['SSL_CERT_FILE'] != '/old/path/to/cert.pem'
    
    def test_handles_certifi_error(self):
        """
        Test that configure_ssl raises exception when certifi.where() fails.
        """
        # Arrange
        with patch('feishu_bot.ssl_config.certifi.where', side_effect=Exception("Certifi error")):
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                configure_ssl()
            
            assert "Certifi error" in str(exc_info.value)


class TestGetSSLCertPath:
    """Test suite for get_ssl_cert_path function."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        self.original_cert_file = os.environ.get('SSL_CERT_FILE')
        if 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
    
    def teardown_method(self):
        """Restore original environment after each test."""
        if self.original_cert_file is not None:
            os.environ['SSL_CERT_FILE'] = self.original_cert_file
        elif 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
    
    def test_returns_configured_path(self):
        """
        Test that get_ssl_cert_path returns the configured certificate path.
        """
        # Arrange
        expected_path = '/path/to/cert.pem'
        os.environ['SSL_CERT_FILE'] = expected_path
        
        # Act
        result = get_ssl_cert_path()
        
        # Assert
        assert result == expected_path
    
    def test_returns_empty_string_when_not_configured(self):
        """
        Test that get_ssl_cert_path returns empty string when not configured.
        """
        # Act
        result = get_ssl_cert_path()
        
        # Assert
        assert result == ''
    
    def test_returns_certifi_path_after_configure(self):
        """
        Test that get_ssl_cert_path returns certifi path after configure_ssl.
        """
        # Arrange
        configure_ssl()
        
        # Act
        result = get_ssl_cert_path()
        
        # Assert
        assert result == certifi.where()


class TestIsSSLConfigured:
    """Test suite for is_ssl_configured function."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        self.original_cert_file = os.environ.get('SSL_CERT_FILE')
        self.original_cert_dir = os.environ.get('SSL_CERT_DIR')
        
        if 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
        if 'SSL_CERT_DIR' in os.environ:
            del os.environ['SSL_CERT_DIR']
    
    def teardown_method(self):
        """Restore original environment after each test."""
        if self.original_cert_file is not None:
            os.environ['SSL_CERT_FILE'] = self.original_cert_file
        elif 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
            
        if self.original_cert_dir is not None:
            os.environ['SSL_CERT_DIR'] = self.original_cert_dir
        elif 'SSL_CERT_DIR' in os.environ:
            del os.environ['SSL_CERT_DIR']
    
    def test_returns_true_when_properly_configured(self):
        """
        Test that is_ssl_configured returns True when SSL is properly configured.
        
        Validates: Requirements 8.1, 8.2
        """
        # Arrange
        configure_ssl()
        
        # Act
        result = is_ssl_configured()
        
        # Assert
        assert result is True
    
    def test_returns_false_when_cert_file_not_set(self):
        """
        Test that is_ssl_configured returns False when SSL_CERT_FILE is not set.
        """
        # Act
        result = is_ssl_configured()
        
        # Assert
        assert result is False
    
    def test_returns_false_when_cert_file_empty(self):
        """
        Test that is_ssl_configured returns False when SSL_CERT_FILE is empty.
        """
        # Arrange
        os.environ['SSL_CERT_FILE'] = ''
        
        # Act
        result = is_ssl_configured()
        
        # Assert
        assert result is False
    
    def test_returns_false_when_cert_dir_set(self):
        """
        Test that is_ssl_configured returns False when SSL_CERT_DIR is set.
        
        Validates: Requirement 8.2
        """
        # Arrange
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['SSL_CERT_DIR'] = '/some/directory'
        
        # Act
        result = is_ssl_configured()
        
        # Assert
        assert result is False


class TestSSLConfigurationIntegration:
    """Integration tests for SSL configuration."""
    
    def setup_method(self):
        """Clean up environment variables before each test."""
        self.original_cert_file = os.environ.get('SSL_CERT_FILE')
        self.original_cert_dir = os.environ.get('SSL_CERT_DIR')
        
        if 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
        if 'SSL_CERT_DIR' in os.environ:
            del os.environ['SSL_CERT_DIR']
    
    def teardown_method(self):
        """Restore original environment after each test."""
        if self.original_cert_file is not None:
            os.environ['SSL_CERT_FILE'] = self.original_cert_file
        elif 'SSL_CERT_FILE' in os.environ:
            del os.environ['SSL_CERT_FILE']
            
        if self.original_cert_dir is not None:
            os.environ['SSL_CERT_DIR'] = self.original_cert_dir
        elif 'SSL_CERT_DIR' in os.environ:
            del os.environ['SSL_CERT_DIR']
    
    def test_full_configuration_workflow(self):
        """
        Test the complete SSL configuration workflow.
        
        Validates: Requirements 8.1, 8.2
        """
        # Initial state - not configured
        assert not is_ssl_configured()
        assert get_ssl_cert_path() == ''
        
        # Configure SSL
        configure_ssl()
        
        # Verify configuration
        assert is_ssl_configured()
        assert get_ssl_cert_path() == certifi.where()
        assert 'SSL_CERT_FILE' in os.environ
        assert 'SSL_CERT_DIR' not in os.environ
    
    def test_reconfiguration_workflow(self):
        """
        Test that SSL can be reconfigured multiple times.
        """
        # First configuration
        configure_ssl()
        first_path = get_ssl_cert_path()
        
        # Modify environment
        os.environ['SSL_CERT_DIR'] = '/some/directory'
        assert not is_ssl_configured()
        
        # Reconfigure
        configure_ssl()
        
        # Verify reconfiguration
        assert is_ssl_configured()
        assert get_ssl_cert_path() == first_path
        assert 'SSL_CERT_DIR' not in os.environ
    
    def test_idempotent_configuration(self):
        """
        Test that calling configure_ssl multiple times is safe.
        """
        # Configure multiple times
        configure_ssl()
        first_path = get_ssl_cert_path()
        
        configure_ssl()
        second_path = get_ssl_cert_path()
        
        configure_ssl()
        third_path = get_ssl_cert_path()
        
        # All paths should be the same
        assert first_path == second_path == third_path == certifi.where()
        assert is_ssl_configured()
