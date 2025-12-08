"""
Member Middleware
"""

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import logout
import logging

logger = logging.getLogger('members.middleware')


class MemberAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to ensure only authenticated members access member areas
    """
    
    def process_request(self, request):
        # Only apply to member URLs
        if not request.path.startswith('/members/'):
            return None
        
        # Skip authentication for public member URLs
        public_urls = [
            '/members/register/',
            '/members/login/',
            '/members/logout/',
            '/members/password-reset/',
            '/members/password-reset-done/',
            '/members/password-reset-confirm/',
            '/members/password-reset-complete/',
        ]
        
        if any(request.path.startswith(url) for url in public_urls):
            return None
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(
                request,
                _('सदस्य क्षेत्रमा पहुँच गर्न लगइन गर्नुहोस्।')
            )
            return redirect('members:member_login')
        
        # Check if user is a member
        if not request.user.is_member:
            messages.warning(
                request,
                _('तपाईं अहिले सदस्य हुनुहुन्न। सदस्यता दर्ता गर्नुहोस्।')
            )
            return redirect('members:member_register')
        
        # Check if member is verified
        if not request.user.is_verified:
            messages.warning(
                request,
                _('तपाईंको सदस्यता अहिले प्रमाणित छैन। प्रतीक्षा गर्नुहोस्।')
            )
            return redirect('members:member_dashboard')
        
        # Check if member profile exists and is active
        if not hasattr(request.user, 'member_profile'):
            messages.error(
                request,
                _('सदस्य प्रोफाइल फेला परेन। प्रशासकसँग सम्पर्क गर्नुहोस्।')
            )
            return redirect('members:member_login')
        
        if not request.user.member_profile.is_active:
            messages.error(
                request,
                _('तपाईंको सदस्यता निष्क्रिय छ। प्रशासकसँग सम्पर्क गर्नुहोस्।')
            )
            return redirect('members:member_login')
        
        return None


class MemberActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track member activity
    """
    
    def process_request(self, request):
        if (request.user.is_authenticated and 
            request.user.is_member and 
            hasattr(request.user, 'member_profile')):
            
            # Update last login IP
            if request.META.get('REMOTE_ADDR'):
                request.user.last_login_ip = request.META.get('REMOTE_ADDR')
                request.user.save(update_fields=['last_login_ip'])
        
        return None


class MemberSecurityMiddleware(MiddlewareMixin):
    """
    Middleware for member-specific security measures
    """
    
    def process_request(self, request):
        # Only apply to member URLs
        if not request.path.startswith('/members/'):
            return None
        
        # Check for suspicious activity
        if self.is_suspicious_request(request):
            logger.warning(
                f"Suspicious request from {request.META.get('REMOTE_ADDR')}: "
                f"{request.path} - User: {request.user}"
            )
            
            # Log out user if suspicious
            if request.user.is_authenticated:
                messages.error(
                    request,
                    _('सुरक्षा कारणले तपाईंलाई लगआउट गरियो।')
                )
                logout(request)
                return redirect('members:member_login')
        
        return None
    
    def is_suspicious_request(self, request):
        """
        Check for suspicious request patterns
        """
        # Check for SQL injection attempts
        suspicious_patterns = [
            'union', 'select', 'insert', 'update', 'delete', 'drop',
            'script', 'javascript', 'onload', 'onerror'
        ]
        
        query_string = request.GET.urlencode().lower()
        for pattern in suspicious_patterns:
            if pattern in query_string:
                return True
        
        # Check for XSS attempts
        if any(pattern in request.path.lower() for pattern in ['<script', 'javascript:', 'onload=']):
            return True
        
        return False
