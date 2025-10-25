import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.conf import settings
import json

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    """Middleware for security monitoring and audit logging"""
    
    def process_request(self, request):
        """Log request details for security monitoring"""
        request._start_time = time.time()
        
        # Log suspicious patterns
        self.check_suspicious_patterns(request)
        
        return None
    
    def process_response(self, request, response):
        """Log response details and audit dashboard access"""
        if hasattr(request, '_start_time'):
            duration = (time.time() - request._start_time) * 1000
            
            # Log dashboard access
            if request.path.startswith('/dashboard/'):
                self.log_dashboard_access(request, response, duration)
            
            # Log admin access
            if request.path.startswith('/admin/'):
                self.log_admin_access(request, response, duration)
        
        return response
    
    def check_suspicious_patterns(self, request):
        """Check for suspicious request patterns"""
        suspicious_patterns = [
            'sqlmap',
            'nikto',
            'nmap',
            'masscan',
            'hydra',
            'medusa',
            'dirb',
            'gobuster',
            'wfuzz',
            'burp',
            'zap',
            'nessus',
            'openvas',
        ]
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        path = request.path.lower()
        
        for pattern in suspicious_patterns:
            if pattern in user_agent or pattern in path:
                self.log_suspicious_activity(request, f"Suspicious pattern detected: {pattern}")
                break
        
        # Check for rapid requests (potential DoS)
        if hasattr(request, 'session'):
            session_key = request.session.session_key
            if session_key:
                # This would need Redis or similar for production
                # For now, we'll just log the request
                pass
    
    def log_dashboard_access(self, request, response, duration):
        """Log dashboard access attempts"""
        try:
            from .models import AuditLog
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='dashboard_access',
                description=f"Dashboard access: {request.path}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_id=request.session.session_key if hasattr(request, 'session') else '',
                additional_data={
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration_ms': duration,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                }
            )
        except Exception as e:
            logger.error(f"Error logging dashboard access: {e}")
    
    def log_admin_access(self, request, response, duration):
        """Log admin access attempts"""
        try:
            from .models import AuditLog
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='admin_access',
                description=f"Admin access: {request.path}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_id=request.session.session_key if hasattr(request, 'session') else '',
                additional_data={
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration_ms': duration,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                    'is_staff': request.user.is_staff if hasattr(request, 'user') and request.user.is_authenticated else False,
                }
            )
        except Exception as e:
            logger.error(f"Error logging admin access: {e}")
    
    def log_suspicious_activity(self, request, description):
        """Log suspicious activity"""
        try:
            from .models import AuditLog
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='suspicious_activity',
                description=description,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_id=request.session.session_key if hasattr(request, 'session') else '',
                additional_data={
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                }
            )
        except Exception as e:
            logger.error(f"Error logging suspicious activity: {e}")
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SecurityUtils:
    """Utility functions for security enhancements"""
    
    @staticmethod
    def log_user_action(user, action_type, description, request=None, **kwargs):
        """Log user actions for audit trail"""
        try:
            from .models import AuditLog
            additional_data = kwargs.copy()
            
            if request:
                additional_data.update({
                    'ip_address': SecurityMiddleware().get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'session_id': request.session.session_key if hasattr(request, 'session') else '',
                    'path': request.path,
                    'method': request.method,
                })
            
            AuditLog.objects.create(
                user=user,
                action_type=action_type,
                description=description,
                additional_data=additional_data
            )
        except Exception as e:
            logger.error(f"Error logging user action: {e}")
    
    @staticmethod
    def check_rate_limit(user, action_type, limit=10, window_minutes=60):
        """Check if user has exceeded rate limit for specific action"""
        try:
            from .models import AuditLog
            from datetime import timedelta
            
            window_start = timezone.now() - timedelta(minutes=window_minutes)
            
            recent_actions = AuditLog.objects.filter(
                user=user,
                action_type=action_type,
                timestamp__gte=window_start
            ).count()
            
            return recent_actions < limit
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow action if check fails
    
    @staticmethod
    def get_user_activity_summary(user, days=30):
        """Get user activity summary for security monitoring"""
        try:
            from .models import AuditLog
            from datetime import timedelta
            
            start_date = timezone.now() - timedelta(days=days)
            
            activities = AuditLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).values('action_type').annotate(
                count=models.Count('id')
            ).order_by('-count')
            
            return list(activities)
        except Exception as e:
            logger.error(f"Error getting user activity summary: {e}")
            return []
    
    @staticmethod
    def get_security_alerts(days=7):
        """Get security alerts and suspicious activities"""
        try:
            from .models import AuditLog
            from datetime import timedelta
            
            start_date = timezone.now() - timedelta(days=days)
            
            alerts = AuditLog.objects.filter(
                action_type='suspicious_activity',
                timestamp__gte=start_date
            ).order_by('-timestamp')
            
            return list(alerts)
        except Exception as e:
            logger.error(f"Error getting security alerts: {e}")
            return []

class RoleBasedAccessControl:
    """Role-based access control for dashboard features"""
    
    PERMISSIONS = {
        'view_dashboard': ['staff', 'admin'],
        'export_data': ['admin'],
        'manage_alerts': ['admin'],
        'view_audit_logs': ['admin'],
        'manage_users': ['admin'],
        'system_settings': ['admin'],
    }
    
    @staticmethod
    def has_permission(user, permission):
        """Check if user has specific permission"""
        if not user.is_authenticated:
            return False
        
        if user.is_superuser:
            return True
        
        if user.is_staff and permission in RoleBasedAccessControl.PERMISSIONS:
            allowed_roles = RoleBasedAccessControl.PERMISSIONS[permission]
            # For now, all staff have admin permissions
            # In production, you'd have a proper role system
            return 'admin' in allowed_roles or 'staff' in allowed_roles
        
        return False
    
    @staticmethod
    def require_permission(permission):
        """Decorator to require specific permission"""
        def decorator(view_func):
            def wrapper(request, *args, **kwargs):
                if not RoleBasedAccessControl.has_permission(request.user, permission):
                    from django.http import JsonResponse
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                return view_func(request, *args, **kwargs)
            return wrapper
        return decorator
