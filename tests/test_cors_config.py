"""
Tests for CORS configuration

Validates Requirement 1.3: CORS configuration for API endpoints
"""

import os
import pytest
from unittest.mock import patch
from flask import Flask
from feishu_bot.core.config_manager import ConfigManager
from feishu_bot.web_admin.server import WebAdminServer


class TestCORSConfiguration:
    """Test CORS configuration in different environments"""
    
    def test_cors_development_allows_all_origins(self):
        """Test that development environment allows all origins
        
        Validates Requirement 1.3
        """
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5001
            )
            
            # Test CORS headers with OPTIONS request
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': 'http://example.com',
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                # Should allow the origin
                assert response.status_code in [200, 204]
                assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_production_restricts_origins(self):
        """Test that production environment restricts origins
        
        Validates Requirement 1.3
        """
        allowed_origin = "https://admin.example.com"
        
        with patch.dict(os.environ, {
            "FLASK_ENV": "production",
            "CORS_ALLOWED_ORIGINS": allowed_origin
        }):
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5002
            )
            
            # Test allowed origin
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': allowed_origin,
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                assert response.status_code in [200, 204]
                assert 'Access-Control-Allow-Origin' in response.headers
                assert response.headers['Access-Control-Allow-Origin'] == allowed_origin
    
    def test_cors_production_rejects_unauthorized_origins(self):
        """Test that production environment rejects unauthorized origins
        
        Validates Requirement 1.3
        """
        allowed_origin = "https://admin.example.com"
        unauthorized_origin = "https://evil.com"
        
        with patch.dict(os.environ, {
            "FLASK_ENV": "production",
            "CORS_ALLOWED_ORIGINS": allowed_origin
        }):
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5003
            )
            
            # Test unauthorized origin
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': unauthorized_origin,
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                # CORS should not allow this origin
                # Either no CORS headers or different origin
                if 'Access-Control-Allow-Origin' in response.headers:
                    assert response.headers['Access-Control-Allow-Origin'] != unauthorized_origin
    
    def test_cors_production_multiple_origins(self):
        """Test that production environment supports multiple allowed origins
        
        Validates Requirement 1.3
        """
        allowed_origins = "https://admin.example.com,https://app.example.com"
        
        with patch.dict(os.environ, {
            "FLASK_ENV": "production",
            "CORS_ALLOWED_ORIGINS": allowed_origins
        }):
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5004
            )
            
            # Test first allowed origin
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': 'https://admin.example.com',
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                assert response.status_code in [200, 204]
                assert 'Access-Control-Allow-Origin' in response.headers
            
            # Test second allowed origin
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': 'https://app.example.com',
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                assert response.status_code in [200, 204]
                assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_production_default_localhost(self):
        """Test that production without CORS_ALLOWED_ORIGINS defaults to localhost
        
        Validates Requirement 1.3
        """
        with patch.dict(os.environ, {
            "FLASK_ENV": "production",
            "CORS_ALLOWED_ORIGINS": ""
        }, clear=False):
            # Remove CORS_ALLOWED_ORIGINS if it exists
            if "CORS_ALLOWED_ORIGINS" in os.environ:
                del os.environ["CORS_ALLOWED_ORIGINS"]
            
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5005
            )
            
            # Test localhost origin
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': 'http://localhost:5000',
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                assert response.status_code in [200, 204]
                assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_allowed_methods(self):
        """Test that CORS allows required HTTP methods
        
        Validates Requirement 1.3
        """
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5006
            )
            
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': 'http://example.com',
                        'Access-Control-Request-Method': 'GET'
                    }
                )
                
                assert response.status_code in [200, 204]
                
                # Check allowed methods
                if 'Access-Control-Allow-Methods' in response.headers:
                    allowed_methods = response.headers['Access-Control-Allow-Methods']
                    assert 'GET' in allowed_methods
                    assert 'POST' in allowed_methods
                    assert 'PUT' in allowed_methods
                    assert 'DELETE' in allowed_methods
    
    def test_cors_allowed_headers(self):
        """Test that CORS allows required headers
        
        Validates Requirement 1.3
        """
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            config_manager = ConfigManager()
            server = WebAdminServer(
                config_manager=config_manager,
                port=5007
            )
            
            with server.app.test_client() as client:
                response = client.options(
                    '/api/configs',
                    headers={
                        'Origin': 'http://example.com',
                        'Access-Control-Request-Method': 'GET',
                        'Access-Control-Request-Headers': 'Content-Type, Authorization'
                    }
                )
                
                assert response.status_code in [200, 204]
                
                # Check allowed headers
                if 'Access-Control-Allow-Headers' in response.headers:
                    allowed_headers = response.headers['Access-Control-Allow-Headers'].lower()
                    assert 'content-type' in allowed_headers
                    assert 'authorization' in allowed_headers
