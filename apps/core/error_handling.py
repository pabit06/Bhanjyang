"""
Standardized error handling utilities for the Bhanjyang Cooperative project.

This module provides consistent error handling, logging, and response formatting
across all views and API endpoints.
"""
import logging
import traceback
from typing import Dict, Any, Optional, Callable, Tuple
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError, IntegrityError
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def json_error(
        message: str,
        status_code: int = 400,
        errors: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> JsonResponse:
        """
        Create a standardized JSON error response.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            errors: Field-specific validation errors
            error_code: Machine-readable error code
            details: Additional error details (not exposed in production)
            
        Returns:
            JsonResponse with standardized error format
        """
        response_data = {
            'success': False,
            'message': message,
        }
        
        if errors:
            response_data['errors'] = errors
            
        if error_code:
            response_data['error_code'] = error_code
            
        # Only include details in debug mode
        if details and settings.DEBUG:
            response_data['details'] = details
            
        return JsonResponse(response_data, status=status_code)
    
    @staticmethod
    def json_success(
        message: str = 'Success',
        data: Optional[Dict[str, Any]] = None,
        status_code: int = 200
    ) -> JsonResponse:
        """
        Create a standardized JSON success response.
        
        Args:
            message: Success message
            data: Additional response data
            status_code: HTTP status code
            
        Returns:
            JsonResponse with standardized success format
        """
        response_data = {
            'success': True,
            'message': message,
        }
        
        if data:
            response_data.update(data)
            
        return JsonResponse(response_data, status=status_code)


class ErrorLogger:
    """Centralized error logging with context"""
    
    @staticmethod
    def log_error(
        exception: Exception,
        request,
        context: Optional[Dict[str, Any]] = None,
        level: str = 'error'
    ) -> None:
        """
        Log error with full context.
        
        Args:
            exception: The exception that occurred
            request: Django request object
            context: Additional context information
            level: Logging level ('error', 'warning', 'critical')
        """
        log_context = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'path': request.path,
            'method': request.method,
            'user': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
        }
        
        if context:
            log_context.update(context)
            
        log_message = (
            f"Error in {request.method} {request.path}: "
            f"{type(exception).__name__}: {str(exception)}"
        )
        
        if level == 'critical':
            logger.critical(log_message, extra=log_context, exc_info=True)
        elif level == 'warning':
            logger.warning(log_message, extra=log_context, exc_info=True)
        else:
            logger.error(log_message, extra=log_context, exc_info=True)
    
    @staticmethod
    def log_validation_error(
        errors: Dict[str, Any],
        request,
        form_name: Optional[str] = None
    ) -> None:
        """
        Log validation errors.
        
        Args:
            errors: Form validation errors
            request: Django request object
            form_name: Name of the form being validated
        """
        log_message = f"Validation error in {request.method} {request.path}"
        if form_name:
            log_message += f" (form: {form_name})"
            
        logger.warning(
            log_message,
            extra={
                'validation_errors': errors,
                'path': request.path,
                'method': request.method,
                'user': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            }
        )


def handle_view_errors(view_func: Callable) -> Callable:
    """
    Decorator to handle errors in view functions consistently.
    
    Usage:
        @handle_view_errors
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except ValidationError as e:
            ErrorLogger.log_validation_error(
                {'validation': str(e)},
                request,
                form_name=getattr(view_func, '__name__', 'unknown')
            )
            return ErrorResponse.json_error(
                message='Validation error',
                status_code=400,
                errors={'validation': str(e)},
                error_code='VALIDATION_ERROR'
            )
        except PermissionDenied as e:
            ErrorLogger.log_error(e, request, level='warning')
            return ErrorResponse.json_error(
                message='Permission denied',
                status_code=403,
                error_code='PERMISSION_DENIED'
            )
        except (DatabaseError, IntegrityError) as e:
            ErrorLogger.log_error(e, request, level='critical')
            return ErrorResponse.json_error(
                message='A database error occurred. Please try again later.',
                status_code=500,
                error_code='DATABASE_ERROR',
                details={'exception': str(e)} if settings.DEBUG else None
            )
        except ValueError as e:
            ErrorLogger.log_error(e, request, level='warning')
            return ErrorResponse.json_error(
                message=str(e) if settings.DEBUG else 'Invalid input provided',
                status_code=400,
                error_code='INVALID_INPUT',
                details={'exception': str(e)} if settings.DEBUG else None
            )
        except Exception as e:
            ErrorLogger.log_error(e, request, level='error')
            return ErrorResponse.json_error(
                message='An unexpected error occurred. Please try again later.',
                status_code=500,
                error_code='INTERNAL_ERROR',
                details={'exception': str(e)} if settings.DEBUG else None
            )
    
    return wrapper


def handle_api_errors(api_view_func: Callable) -> Callable:
    """
    Decorator to handle errors in API views consistently.
    Similar to handle_view_errors but optimized for API responses.
    
    Usage:
        @handle_api_errors
        def my_api_view(request):
            ...
    """
    @wraps(api_view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return api_view_func(request, *args, **kwargs)
        except ValidationError as e:
            ErrorLogger.log_validation_error(
                {'validation': str(e)},
                request,
                form_name=getattr(api_view_func, '__name__', 'unknown')
            )
            return ErrorResponse.json_error(
                message='Validation error',
                status_code=400,
                errors={'validation': str(e)},
                error_code='VALIDATION_ERROR'
            )
        except PermissionDenied:
            return ErrorResponse.json_error(
                message='Permission denied',
                status_code=403,
                error_code='PERMISSION_DENIED'
            )
        except (DatabaseError, IntegrityError) as e:
            ErrorLogger.log_error(e, request, level='critical')
            return ErrorResponse.json_error(
                message='Database error occurred',
                status_code=500,
                error_code='DATABASE_ERROR'
            )
        except ValueError as e:
            ErrorLogger.log_error(e, request, level='warning')
            return ErrorResponse.json_error(
                message='Invalid input',
                status_code=400,
                error_code='INVALID_INPUT'
            )
        except Exception as e:
            ErrorLogger.log_error(e, request, level='error')
            return ErrorResponse.json_error(
                message='Internal server error',
                status_code=500,
                error_code='INTERNAL_ERROR'
            )
    
    return wrapper


def safe_json_parse(request) -> Tuple[Optional[Dict[str, Any]], Optional[JsonResponse]]:
    """
    Safely parse JSON from request body.
    
    Args:
        request: Django request object
        
    Returns:
        Tuple of (parsed_data, error_response)
        If parsing succeeds: (data, None)
        If parsing fails: (None, JsonResponse with error)
    """
    try:
        import json
        data = json.loads(request.body)
        return data, None
    except json.JSONDecodeError as e:
        ErrorLogger.log_error(e, request, level='warning')
        return None, ErrorResponse.json_error(
            message='Invalid JSON data',
            status_code=400,
            error_code='INVALID_JSON'
        )
    except Exception as e:
        ErrorLogger.log_error(e, request)
        return None, ErrorResponse.json_error(
            message='Error parsing request data',
            status_code=400,
            error_code='PARSE_ERROR'
        )


def safe_int_conversion(value: Any, default: int = 0, field_name: str = 'value') -> Tuple[int, Optional[str]]:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        field_name: Name of the field (for error messages)
        
    Returns:
        Tuple of (converted_value, error_message)
    """
    try:
        return int(value), None
    except (ValueError, TypeError):
        return default, f"Invalid {field_name}: must be a number"


def safe_float_conversion(value: Any, default: float = 0.0, field_name: str = 'value') -> Tuple[float, Optional[str]]:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        field_name: Name of the field (for error messages)
        
    Returns:
        Tuple of (converted_value, error_message)
    """
    try:
        return float(value), None
    except (ValueError, TypeError):
        return default, f"Invalid {field_name}: must be a number"

