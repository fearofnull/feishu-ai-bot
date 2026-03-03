"""
Tests for Web Admin Error Handling

This module tests the unified error handling system for the web admin interface.
"""

import pytest
from flask import Flask, jsonify
from feishu_bot.web_admin.errors import (
    WebAdminError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    InternalError,
    handle_errors,
    format_error_response,
    format_success_response,
    HTTP_STATUS_CODES,
    get_status_code_for_error
)


class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_web_admin_error(self):
        """Test base WebAdminError"""
        error = WebAdminError(
            message="Test error",
            code="TEST_ERROR",
            status_code=400,
            field="test_field"
        )
        
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status_code == 400
        assert error.field == "test_field"
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Invalid value", field="username")
        
        assert error.message == "Invalid value"
        assert error.code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.field == "username"
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError("Invalid credentials")
        
        assert error.message == "Invalid credentials"
        assert error.code == "AUTHENTICATION_ERROR"
        assert error.status_code == 401
    
    def test_not_found_error(self):
        """Test NotFoundError"""
        error = NotFoundError("Config not found", resource_type="Configuration")
        
        assert error.message == "Config not found"
        assert error.code == "NOT_FOUND"
        assert error.status_code == 404
        assert error.resource_type == "Configuration"
    
    def test_internal_error(self):
        """Test InternalError"""
        error = InternalError("Database connection failed")
        
        assert error.message == "Database connection failed"
        assert error.code == "INTERNAL_ERROR"
        assert error.status_code == 500


class TestErrorFormatting:
    """Test error response formatting"""
    
    def test_format_error_response(self):
        """Test error response formatting"""
        error = ValueError("Invalid input")
        response, status_code = format_error_response(
            error,
            status_code=400,
            code="VALIDATION_ERROR",
            field="email"
        )
        
        assert response['success'] is False
        assert response['data'] is None
        assert response['error']['code'] == "VALIDATION_ERROR"
        assert response['error']['message'] == "Invalid input"
        assert response['error']['field'] == "email"
        assert status_code == 400
    
    def test_format_error_response_without_field(self):
        """Test error response formatting without field"""
        error = Exception("Something went wrong")
        response, status_code = format_error_response(
            error,
            status_code=500,
            code="INTERNAL_ERROR"
        )
        
        assert response['success'] is False
        assert response['error']['code'] == "INTERNAL_ERROR"
        assert 'field' not in response['error']
        assert status_code == 500
    
    def test_format_success_response(self):
        """Test success response formatting"""
        data = {'id': 1, 'name': 'Test'}
        response = format_success_response(data, "Operation completed")
        
        assert response['success'] is True
        assert response['data'] == data
        assert response['message'] == "Operation completed"
    
    def test_format_success_response_default_message(self):
        """Test success response with default message"""
        response = format_success_response({'result': 'ok'})
        
        assert response['success'] is True
        assert response['message'] == "Operation successful"


class TestErrorHandlingDecorator:
    """Test error handling decorator"""
    
    def test_handle_errors_with_web_admin_error(self):
        """Test decorator handles WebAdminError"""
        app = Flask(__name__)
        
        @app.route('/test')
        @handle_errors
        def test_endpoint():
            raise ValidationError("Invalid input", field="username")
        
        with app.test_client() as client:
            response = client.get('/test')
            data = response.get_json()
            
            assert response.status_code == 400
            assert data['success'] is False
            assert data['error']['code'] == "VALIDATION_ERROR"
            assert data['error']['message'] == "Invalid input"
            assert data['error']['field'] == "username"
    
    def test_handle_errors_with_value_error(self):
        """Test decorator handles ValueError"""
        app = Flask(__name__)
        
        @app.route('/test')
        @handle_errors
        def test_endpoint():
            raise ValueError("Invalid value provided")
        
        with app.test_client() as client:
            response = client.get('/test')
            data = response.get_json()
            
            assert response.status_code == 400
            assert data['success'] is False
            assert data['error']['code'] == "VALIDATION_ERROR"
    
    def test_handle_errors_with_key_error(self):
        """Test decorator handles KeyError"""
        app = Flask(__name__)
        
        @app.route('/test')
        @handle_errors
        def test_endpoint():
            raise KeyError("missing_field")
        
        with app.test_client() as client:
            response = client.get('/test')
            data = response.get_json()
            
            assert response.status_code == 400
            assert data['success'] is False
            assert data['error']['code'] == "MISSING_FIELD"
            assert "missing_field" in data['error']['message']
    
    def test_handle_errors_with_generic_exception(self):
        """Test decorator handles generic Exception"""
        app = Flask(__name__)
        
        @app.route('/test')
        @handle_errors
        def test_endpoint():
            raise Exception("Unexpected error")
        
        with app.test_client() as client:
            response = client.get('/test')
            data = response.get_json()
            
            assert response.status_code == 500
            assert data['success'] is False
            assert data['error']['code'] == "INTERNAL_ERROR"
            assert data['error']['message'] == "An internal error occurred"
    
    def test_handle_errors_with_success(self):
        """Test decorator allows successful responses"""
        app = Flask(__name__)
        
        @app.route('/test')
        @handle_errors
        def test_endpoint():
            return jsonify({'success': True, 'data': 'test'}), 200
        
        with app.test_client() as client:
            response = client.get('/test')
            data = response.get_json()
            
            assert response.status_code == 200
            assert data['success'] is True
            assert data['data'] == 'test'


class TestStatusCodeMapping:
    """Test HTTP status code mapping"""
    
    def test_http_status_codes(self):
        """Test HTTP status code constants"""
        assert HTTP_STATUS_CODES['OK'] == 200
        assert HTTP_STATUS_CODES['CREATED'] == 201
        assert HTTP_STATUS_CODES['BAD_REQUEST'] == 400
        assert HTTP_STATUS_CODES['UNAUTHORIZED'] == 401
        assert HTTP_STATUS_CODES['NOT_FOUND'] == 404
        assert HTTP_STATUS_CODES['INTERNAL_SERVER_ERROR'] == 500
    
    def test_get_status_code_for_error(self):
        """Test error code to status code mapping"""
        assert get_status_code_for_error('AUTHENTICATION_ERROR') == 401
        assert get_status_code_for_error('VALIDATION_ERROR') == 400
        assert get_status_code_for_error('NOT_FOUND') == 404
        assert get_status_code_for_error('INTERNAL_ERROR') == 500
    
    def test_get_status_code_for_unknown_error(self):
        """Test default status code for unknown error"""
        assert get_status_code_for_error('UNKNOWN_ERROR') == 500
    
    def test_all_validation_errors_map_to_400(self):
        """Test all validation-related errors map to 400"""
        validation_codes = [
            'VALIDATION_ERROR',
            'MISSING_FIELD',
            'INVALID_PROVIDER',
            'INVALID_LAYER',
            'INVALID_JSON'
        ]
        
        for code in validation_codes:
            assert get_status_code_for_error(code) == 400
    
    def test_all_auth_errors_map_to_401(self):
        """Test all authentication errors map to 401"""
        auth_codes = [
            'AUTHENTICATION_ERROR',
            'INVALID_CREDENTIALS',
            'INVALID_TOKEN',
            'TOKEN_EXPIRED'
        ]
        
        for code in auth_codes:
            assert get_status_code_for_error(code) == 401


class TestErrorResponseStructure:
    """Test error response structure consistency"""
    
    def test_error_response_has_required_fields(self):
        """Test error response contains all required fields"""
        error = ValueError("Test error")
        response, _ = format_error_response(error, 400, "TEST_ERROR")
        
        assert 'success' in response
        assert 'data' in response
        assert 'error' in response
        assert 'code' in response['error']
        assert 'message' in response['error']
    
    def test_success_response_has_required_fields(self):
        """Test success response contains all required fields"""
        response = format_success_response({'test': 'data'})
        
        assert 'success' in response
        assert 'data' in response
        assert 'message' in response
    
    def test_error_response_success_is_false(self):
        """Test error response has success=False"""
        error = Exception("Error")
        response, _ = format_error_response(error, 500, "ERROR")
        
        assert response['success'] is False
    
    def test_success_response_success_is_true(self):
        """Test success response has success=True"""
        response = format_success_response(None)
        
        assert response['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
