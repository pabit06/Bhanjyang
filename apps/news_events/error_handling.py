"""
Enhanced Error Handling for News Events App

Provides structured error logging, recovery mechanisms, and user-friendly error handling.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError, IntegrityError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

logger = logging.getLogger(__name__)


class StructuredErrorLogger:
    """
    Structured error logging with context and categorization.
    """
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = 'error',
        request=None
    ) -> None:
        """
        Log error with structured context.
        
        Args:
            error: Exception object
            context: Additional context dictionary
            level: Log level (error, warning, critical)
            request: HTTP request object for additional context
        """
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
        }
        
        if context:
            error_context.update(context)
        
        if request:
            error_context.update({
                'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
                'path': request.path,
                'method': request.method,
                'ip_address': getattr(request, 'META', {}).get('REMOTE_ADDR', 'unknown'),
            })
        
        log_method = getattr(logger, level, logger.error)
        log_method(f"News Events Error: {error_context}", extra=error_context)
    
    @staticmethod
    def log_validation_error(
        field: str,
        value: Any,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log validation errors with context."""
        error_context = {
            'error_type': 'ValidationError',
            'field': field,
            'value': str(value)[:100],  # Truncate long values
            'error_message': error_message,
        }
        
        if context:
            error_context.update(context)
        
        logger.warning(f"Validation Error: {error_context}", extra=error_context)
    
    @staticmethod
    def log_performance_issue(
        operation: str,
        duration: float,
        threshold: float = 2.0,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log performance issues."""
        if duration > threshold:
            error_context = {
                'error_type': 'PerformanceIssue',
                'operation': operation,
                'duration': duration,
                'threshold': threshold,
            }
            
            if context:
                error_context.update(context)
            
            logger.warning(f"Performance Issue: {error_context}", extra=error_context)


class ErrorRecovery:
    """
    Error recovery mechanisms for graceful degradation.
    """
    
    @staticmethod
    def retry_on_failure(
        max_retries: int = 3,
        delay: float = 1.0,
        exceptions: tuple = (DatabaseError, IntegrityError)
    ):
        """
        Decorator to retry operations on failure.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
            exceptions: Tuple of exceptions to catch and retry
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}: {str(e)}"
                            )
                            time.sleep(delay * (attempt + 1))  # Exponential backoff
                        else:
                            logger.error(
                                f"All retry attempts failed for {func.__name__}: {str(e)}"
                            )
                
                raise last_exception
            
            return wrapper
        return decorator
    
    @staticmethod
    def fallback_on_error(
        fallback_value: Any = None,
        fallback_func: Optional[Callable] = None,
        exceptions: tuple = (Exception,)
    ):
        """
        Decorator to provide fallback on error.
        
        Args:
            fallback_value: Value to return on error
            fallback_func: Function to call on error
            exceptions: Tuple of exceptions to catch
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    StructuredErrorLogger.log_error(e, {'function': func.__name__})
                    
                    if fallback_func:
                        return fallback_func(*args, **kwargs)
                    return fallback_value
            
            return wrapper
        return decorator


class UserFriendlyErrorHandler:
    """
    Generate user-friendly error messages and responses.
    """
    
    @staticmethod
    def get_error_message(error: Exception, request=None) -> str:
        """
        Get user-friendly error message based on error type.
        
        Args:
            error: Exception object
            request: HTTP request object
            
        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        
        error_messages = {
            'ValidationError': _("Please fill in all required fields correctly."),
            'PermissionDenied': _("You do not have permission to perform this action."),
            'DatabaseError': _("A database error occurred. Please try again later."),
            'IntegrityError': _("The data is invalid. Please check and try again."),
            'Http404': _("The requested page was not found."),
            'ValueError': _("An invalid value was provided."),
            'TypeError': _("Incorrect data type provided."),
        }
        
        # Default message
        default_message = _("An error occurred. Please try again later.")
        
        # Get specific message or default
        message = error_messages.get(error_type, default_message)
        
        # In debug mode, include technical details
        if settings.DEBUG and hasattr(error, '__str__'):
            message += f" (Debug: {str(error)})"
        
        return message
    
    @staticmethod
    def get_json_error_response(
        error: Exception,
        status_code: int = 400,
        request=None
    ) -> JsonResponse:
        """
        Get JSON error response with user-friendly message.
        
        Args:
            error: Exception object
            status_code: HTTP status code
            request: HTTP request object
            
        Returns:
            JsonResponse with error details
        """
        message = UserFriendlyErrorHandler.get_error_message(error, request)
        
        response_data = {
            'success': False,
            'error': message,
            'error_type': type(error).__name__,
        }
        
        # Add debug information in development
        if settings.DEBUG:
            response_data['debug'] = {
                'message': str(error),
                'traceback': traceback.format_exc().split('\n')[-5:],  # Last 5 lines
            }
        
        return JsonResponse(response_data, status=status_code)
    
    @staticmethod
    def get_html_error_response(
        error: Exception,
        template: str = 'news_events/error.html',
        status_code: int = 400,
        request=None
    ) -> HttpResponse:
        """
        Get HTML error response with user-friendly message.
        
        Args:
            error: Exception object
            template: Template to render
            status_code: HTTP status code
            request: HTTP request object
            
        Returns:
            HttpResponse with error page
        """
        from django.shortcuts import render
        
        message = UserFriendlyErrorHandler.get_error_message(error, request)
        
        context = {
            'error_message': message,
            'error_type': type(error).__name__,
            'status_code': status_code,
        }
        
        # Add debug information in development
        if settings.DEBUG:
            context['debug_info'] = {
                'message': str(error),
                'traceback': traceback.format_exc(),
            }
        
        return render(request, template, context, status=status_code)


def handle_view_errors(view_func: Callable) -> Callable:
    """
    Decorator to handle errors in view functions with structured logging and recovery.
    
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
            StructuredErrorLogger.log_validation_error(
                'form', request.POST if hasattr(request, 'POST') else None,
                str(e), {'view': view_func.__name__}
            )
            return UserFriendlyErrorHandler.get_json_error_response(e, 400, request)
        except PermissionDenied as e:
            StructuredErrorLogger.log_error(e, {'view': view_func.__name__}, 'warning', request)
            return UserFriendlyErrorHandler.get_json_error_response(e, 403, request)
        except (DatabaseError, IntegrityError) as e:
            StructuredErrorLogger.log_error(e, {'view': view_func.__name__}, 'critical', request)
            return UserFriendlyErrorHandler.get_json_error_response(e, 500, request)
        except Exception as e:
            StructuredErrorLogger.log_error(e, {'view': view_func.__name__}, 'error', request)
            return UserFriendlyErrorHandler.get_json_error_response(e, 500, request)
    
    return wrapper

