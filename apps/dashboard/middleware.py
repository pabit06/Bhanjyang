import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.conf import settings
from django.utils import timezone
from .models import PerformanceMetric, UserSession, ErrorLog
import json

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to track server-side performance metrics"""
    
    def process_request(self, request):
        """Start timing the request"""
        request._start_time = time.time()
        request._db_queries_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Track request performance and create metrics"""
        if hasattr(request, '_start_time'):
            # Calculate request duration
            duration = (time.time() - request._start_time) * 1000  # Convert to milliseconds
            
            # Count database queries
            db_queries = len(connection.queries) - getattr(request, '_db_queries_start', 0)
            
            # Track performance metrics
            try:
                PerformanceMetric.objects.create(
                    metric_type='page_load',
                    page_url=request.build_absolute_uri(),
                    value=duration,
                    unit='ms',
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    ip_address=self.get_client_ip(request),
                    session_id=request.session.session_key,
                    user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    additional_data={
                        'method': request.method,
                        'status_code': response.status_code,
                        'db_queries': db_queries,
                        'response_size': len(response.content) if hasattr(response, 'content') else 0,
                        'path': request.path,
                        'query_params': dict(request.GET),
                        'user_authenticated': hasattr(request, 'user') and request.user.is_authenticated,
                        'is_ajax': request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest',
                        'referer': request.META.get('HTTP_REFERER', ''),
                    }
                )
                
                # Track user session
                self.track_user_session(request, duration)
                
            except Exception as e:
                logger.error(f"Failed to track performance metric: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """Track exceptions and errors"""
        try:
            ErrorLog.objects.create(
                error_type='500',
                error_message=str(exception),
                page_url=request.build_absolute_uri(),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=self.get_client_ip(request),
                session_id=request.session.session_key,
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                stack_trace=self.get_stack_trace(exception),
                additional_data={
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'post_data': dict(request.POST) if request.method == 'POST' else {},
                    'user_authenticated': hasattr(request, 'user') and request.user.is_authenticated,
                    'is_ajax': request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest',
                    'referer': request.META.get('HTTP_REFERER', ''),
                }
            )
        except Exception as e:
            logger.error(f"Failed to track error: {e}")
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_stack_trace(self, exception):
        """Get stack trace for exception"""
        import traceback
        return traceback.format_exc()
    
    def track_user_session(self, request, duration):
        """Track or update user session"""
        session_id = request.session.session_key
        if not session_id:
            return
        
        try:
            # Get or create session
            session, created = UserSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'user': request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    'is_mobile': self.is_mobile(request),
                    'browser': self.get_browser(request),
                    'os': self.get_os(request),
                }
            )
            
            # Update session data
            session.page_views += 1
            session.total_load_time += duration
            
            # Update end time if this is likely the last request
            if not request.META.get('HTTP_X_REQUESTED_WITH'):  # Not an AJAX request
                session.end_time = timezone.now()
            
            session.save()
            
        except Exception as e:
            logger.error(f"Failed to track user session: {e}")
    
    def is_mobile(self, request):
        """Check if request is from mobile device"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'blackberry', 'windows phone']
        return any(indicator in user_agent for indicator in mobile_indicators)
    
    def get_browser(self, request):
        """Extract browser from user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'chrome' in user_agent.lower():
            return 'Chrome'
        elif 'firefox' in user_agent.lower():
            return 'Firefox'
        elif 'safari' in user_agent.lower():
            return 'Safari'
        elif 'edge' in user_agent.lower():
            return 'Edge'
        elif 'opera' in user_agent.lower():
            return 'Opera'
        else:
            return 'Unknown'
    
    def get_os(self, request):
        """Extract OS from user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'windows' in user_agent.lower():
            return 'Windows'
        elif 'mac' in user_agent.lower():
            return 'macOS'
        elif 'linux' in user_agent.lower():
            return 'Linux'
        elif 'android' in user_agent.lower():
            return 'Android'
        elif 'ios' in user_agent.lower():
            return 'iOS'
        else:
            return 'Unknown'
