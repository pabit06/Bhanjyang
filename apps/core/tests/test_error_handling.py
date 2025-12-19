"""
Comprehensive tests for error handling utilities
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError, IntegrityError
from django.http import JsonResponse
from unittest.mock import Mock, patch
import json

from apps.core.error_handling import (
    ErrorResponse,
    ErrorLogger,
    handle_view_errors,
    handle_api_errors,
    safe_json_parse,
    safe_int_conversion,
    safe_float_conversion
)

User = get_user_model()


class ErrorResponseTest(TestCase):
    """Test suite for ErrorResponse class"""
    
    def test_json_error_basic(self):
        """Test basic JSON error response"""
        response = ErrorResponse.json_error('Test error')
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Test error')
    
    def test_json_error_with_status_code(self):
        """Test JSON error with custom status code"""
        response = ErrorResponse.json_error('Not found', status_code=404)
        self.assertEqual(response.status_code, 404)
    
    def test_json_error_with_errors(self):
        """Test JSON error with field errors"""
        errors = {'field1': ['Error 1'], 'field2': ['Error 2']}
        response = ErrorResponse.json_error('Validation failed', errors=errors)
        data = json.loads(response.content)
        self.assertEqual(data['errors'], errors)
    
    def test_json_error_with_error_code(self):
        """Test JSON error with error code"""
        response = ErrorResponse.json_error('Error', error_code='TEST_ERROR')
        data = json.loads(response.content)
        self.assertEqual(data['error_code'], 'TEST_ERROR')
    
    def test_json_error_with_details_debug(self):
        """Test JSON error with details in debug mode"""
        with self.settings(DEBUG=True):
            details = {'exception': 'Test exception'}
            response = ErrorResponse.json_error('Error', details=details)
            data = json.loads(response.content)
            self.assertEqual(data['details'], details)
    
    def test_json_error_with_details_production(self):
        """Test JSON error without details in production"""
        with self.settings(DEBUG=False):
            details = {'exception': 'Test exception'}
            response = ErrorResponse.json_error('Error', details=details)
            data = json.loads(response.content)
            self.assertNotIn('details', data)
    
    def test_json_success_basic(self):
        """Test basic JSON success response"""
        response = ErrorResponse.json_success()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Success')
    
    def test_json_success_with_message(self):
        """Test JSON success with custom message"""
        response = ErrorResponse.json_success('Operation completed')
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Operation completed')
    
    def test_json_success_with_data(self):
        """Test JSON success with data"""
        data = {'result': 'test'}
        response = ErrorResponse.json_success(data=data)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['result'], 'test')
    
    def test_json_success_with_status_code(self):
        """Test JSON success with custom status code"""
        response = ErrorResponse.json_success(status_code=201)
        self.assertEqual(response.status_code, 201)


class ErrorLoggerTest(TestCase):
    """Test suite for ErrorLogger class"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_log_error_basic(self):
        """Test basic error logging"""
        request = self.factory.get('/test/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Test Agent'
        
        exception = ValueError('Test error')
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_error(exception, request)
            mock_logger.error.assert_called_once()
    
    def test_log_error_anonymous_user(self):
        """Test error logging with anonymous user"""
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        exception = ValueError('Test error')
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_error(exception, request)
            mock_logger.error.assert_called_once()
    
    def test_log_error_critical(self):
        """Test critical error logging"""
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        exception = ValueError('Critical error')
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_error(exception, request, level='critical')
            mock_logger.critical.assert_called_once()
    
    def test_log_error_warning(self):
        """Test warning error logging"""
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        exception = ValueError('Warning')
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_error(exception, request, level='warning')
            mock_logger.warning.assert_called_once()
    
    def test_log_error_with_context(self):
        """Test error logging with additional context"""
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        exception = ValueError('Test error')
        context = {'extra': 'data'}
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_error(exception, request, context=context)
            call_args = mock_logger.error.call_args
            self.assertIn('extra', call_args[1]['extra'])
    
    def test_log_validation_error(self):
        """Test validation error logging"""
        request = self.factory.post('/test/')
        request.user = Mock(is_authenticated=False)
        errors = {'field1': ['Error 1']}
        
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_validation_error(errors, request)
            mock_logger.warning.assert_called_once()
    
    def test_log_validation_error_with_form_name(self):
        """Test validation error logging with form name"""
        request = self.factory.post('/test/')
        request.user = Mock(is_authenticated=False)
        errors = {'field1': ['Error 1']}
        
        with patch('apps.core.error_handling.logger') as mock_logger:
            ErrorLogger.log_validation_error(errors, request, form_name='TestForm')
            call_args = mock_logger.warning.call_args
            self.assertIn('TestForm', call_args[0][0])


class ErrorHandlingDecoratorsTest(TestCase):
    """Test suite for error handling decorators"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_handle_view_errors_success(self):
        """Test handle_view_errors with successful view"""
        @handle_view_errors
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_handle_view_errors_validation_error(self):
        """Test handle_view_errors with ValidationError"""
        @handle_view_errors
        def test_view(request):
            raise ValidationError('Invalid data')
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'VALIDATION_ERROR')
    
    def test_handle_view_errors_permission_denied(self):
        """Test handle_view_errors with PermissionDenied"""
        @handle_view_errors
        def test_view(request):
            raise PermissionDenied('Access denied')
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['error_code'], 'PERMISSION_DENIED')
    
    def test_handle_view_errors_database_error(self):
        """Test handle_view_errors with DatabaseError"""
        @handle_view_errors
        def test_view(request):
            raise DatabaseError('Database error')
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['error_code'], 'DATABASE_ERROR')
    
    def test_handle_view_errors_value_error(self):
        """Test handle_view_errors with ValueError"""
        @handle_view_errors
        def test_view(request):
            raise ValueError('Invalid input')
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        with self.settings(DEBUG=True):
            response = test_view(request)
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.content)
            self.assertEqual(data['error_code'], 'INVALID_INPUT')
    
    def test_handle_view_errors_generic_exception(self):
        """Test handle_view_errors with generic Exception"""
        @handle_view_errors
        def test_view(request):
            raise Exception('Unexpected error')
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['error_code'], 'INTERNAL_ERROR')
    
    def test_handle_api_errors_success(self):
        """Test handle_api_errors with successful view"""
        @handle_api_errors
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_handle_api_errors_validation_error(self):
        """Test handle_api_errors with ValidationError"""
        @handle_api_errors
        def test_view(request):
            raise ValidationError('Invalid data')
        
        request = self.factory.get('/test/')
        request.user = Mock(is_authenticated=False)
        response = test_view(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['error_code'], 'VALIDATION_ERROR')


class SafeConversionFunctionsTest(TestCase):
    """Test suite for safe conversion functions"""
    
    def test_safe_int_conversion_valid(self):
        """Test safe_int_conversion with valid input"""
        value, error = safe_int_conversion('123')
        self.assertEqual(value, 123)
        self.assertIsNone(error)
    
    def test_safe_int_conversion_invalid(self):
        """Test safe_int_conversion with invalid input"""
        value, error = safe_int_conversion('abc')
        self.assertEqual(value, 0)
        self.assertIsNotNone(error)
    
    def test_safe_int_conversion_with_default(self):
        """Test safe_int_conversion with custom default"""
        value, error = safe_int_conversion('abc', default=10)
        self.assertEqual(value, 10)
    
    def test_safe_int_conversion_with_field_name(self):
        """Test safe_int_conversion with field name"""
        value, error = safe_int_conversion('abc', field_name='age')
        self.assertIn('age', error)
    
    def test_safe_float_conversion_valid(self):
        """Test safe_float_conversion with valid input"""
        value, error = safe_float_conversion('123.45')
        self.assertEqual(value, 123.45)
        self.assertIsNone(error)
    
    def test_safe_float_conversion_invalid(self):
        """Test safe_float_conversion with invalid input"""
        value, error = safe_float_conversion('abc')
        self.assertEqual(value, 0.0)
        self.assertIsNotNone(error)
    
    def test_safe_float_conversion_with_default(self):
        """Test safe_float_conversion with custom default"""
        value, error = safe_float_conversion('abc', default=10.5)
        self.assertEqual(value, 10.5)


class SafeJsonParseTest(TestCase):
    """Test suite for safe_json_parse function"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
    
    def test_safe_json_parse_valid(self):
        """Test safe_json_parse with valid JSON"""
        data = {'test': 'data'}
        request = self.factory.post(
            '/test/',
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = Mock(is_authenticated=False)
        
        parsed_data, error = safe_json_parse(request)
        self.assertEqual(parsed_data, data)
        self.assertIsNone(error)
    
    def test_safe_json_parse_invalid(self):
        """Test safe_json_parse with invalid JSON"""
        request = self.factory.post(
            '/test/',
            data='invalid json',
            content_type='application/json'
        )
        request.user = Mock(is_authenticated=False)
        
        parsed_data, error = safe_json_parse(request)
        self.assertIsNone(parsed_data)
        self.assertIsNotNone(error)
        self.assertIsInstance(error, JsonResponse)
        self.assertEqual(error.status_code, 400)

