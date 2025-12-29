"""
View mixins for the About app.

Provides reusable functionality for views including error handling
and context data management.
"""
from typing import Dict, Any, Optional, Callable
from django.http import HttpRequest
from apps.core.error_handling import ErrorLogger


class SafeContextDataMixin:
    """
    Mixin that provides safe context data retrieval with error handling.
    
    Usage:
        class MyView(SafeContextDataMixin, TemplateView):
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(self.safe_get_data('my_key', self._get_my_data))
                return context
            
            def _get_my_data(self):
                # Your data fetching logic
                return {'my_key': some_data}
    """
    
    def safe_get_data(
        self,
        key: str,
        data_func: Callable[[], Any],
        default: Any = None
    ) -> Dict[str, Any]:
        """
        Safely execute a data fetching function and return result in dict format.
        
        Args:
            key: The key to use in the returned dictionary
            data_func: Function that returns the data (can raise exceptions)
            default: Default value if function fails (default: None)
            
        Returns:
            Dictionary with the key and fetched data (or default value)
        """
        try:
            data = data_func()
            return {key: data}
        except Exception as e:
            # Log error if request is available
            if hasattr(self, 'request'):
                ErrorLogger.log_error(e, self.request)
            return {key: default if default is not None else []}

