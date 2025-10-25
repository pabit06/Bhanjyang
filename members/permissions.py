"""
Member Permissions and Middleware
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger('members')


class IsMember:
    """
    Permission class to check if user is a member
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'member_profile') and
            request.user.is_member
        )


class IsVerifiedMember:
    """
    Permission class to check if user is a verified member
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'member_profile') and
            request.user.is_member and
            request.user.is_verified
        )


class IsActiveMember:
    """
    Permission class to check if user is an active member
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'member_profile') and
            request.user.is_member and
            request.user.is_verified and
            request.user.member_profile.is_active
        )


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
                from django.contrib.auth import logout
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


def create_member_permissions():
    """
    Create custom permissions for member management
    """
    from .models import Member, MemberRegistration, MemberAccount, MemberLoan
    
    # Member permissions
    member_ct = ContentType.objects.get_for_model(Member)
    Permission.objects.get_or_create(
        codename='can_view_member_dashboard',
        name='Can view member dashboard',
        content_type=member_ct
    )
    Permission.objects.get_or_create(
        codename='can_manage_member_profile',
        name='Can manage member profile',
        content_type=member_ct
    )
    
    # Member Registration permissions
    registration_ct = ContentType.objects.get_for_model(MemberRegistration)
    Permission.objects.get_or_create(
        codename='can_approve_registrations',
        name='Can approve member registrations',
        content_type=registration_ct
    )
    Permission.objects.get_or_create(
        codename='can_reject_registrations',
        name='Can reject member registrations',
        content_type=registration_ct
    )
    
    # Member Account permissions
    account_ct = ContentType.objects.get_for_model(MemberAccount)
    Permission.objects.get_or_create(
        codename='can_view_member_accounts',
        name='Can view member accounts',
        content_type=account_ct
    )
    Permission.objects.get_or_create(
        codename='can_manage_member_accounts',
        name='Can manage member accounts',
        content_type=account_ct
    )
    
    # Member Loan permissions
    loan_ct = ContentType.objects.get_for_model(MemberLoan)
    Permission.objects.get_or_create(
        codename='can_view_member_loans',
        name='Can view member loans',
        content_type=loan_ct
    )
    Permission.objects.get_or_create(
        codename='can_approve_member_loans',
        name='Can approve member loans',
        content_type=loan_ct
    )
    Permission.objects.get_or_create(
        codename='can_reject_member_loans',
        name='Can reject member loans',
        content_type=loan_ct
    )


class MemberAccessControl:
    """
    Utility class for member access control
    """
    
    @staticmethod
    def can_access_member_area(user):
        """
        Check if user can access member area
        """
        return (
            user.is_authenticated and
            user.is_member and
            user.is_verified and
            hasattr(user, 'member_profile') and
            user.member_profile.is_active
        )
    
    @staticmethod
    def can_apply_for_loan(user):
        """
        Check if user can apply for loan
        """
        if not MemberAccessControl.can_access_member_area(user):
            return False
        
        member = user.member_profile
        
        # Check if member has active loans
        active_loans = MemberLoan.objects.filter(
            member=member,
            status__in=['active', 'disbursed']
        ).count()
        
        # Maximum 2 active loans
        return active_loans < 2
    
    @staticmethod
    def can_view_sensitive_data(user):
        """
        Check if user can view sensitive financial data
        """
        if not MemberAccessControl.can_access_member_area(user):
            return False
        
        member = user.member_profile
        
        # Additional checks for sensitive data access
        return (
            member.is_verified and
            member.membership_fee_paid
        )
    
    @staticmethod
    def get_member_permissions(user):
        """
        Get list of permissions for a member
        """
        permissions = []
        
        if MemberAccessControl.can_access_member_area(user):
            permissions.extend([
                'view_dashboard',
                'view_profile',
                'update_profile',
                'view_accounts',
                'view_transactions',
                'view_notifications'
            ])
        
        if MemberAccessControl.can_apply_for_loan(user):
            permissions.append('apply_loan')
        
        if MemberAccessControl.can_view_sensitive_data(user):
            permissions.extend([
                'view_detailed_transactions',
                'download_statements',
                'view_loan_details'
            ])
        
        return permissions


class MemberAuditLogger:
    """
    Utility class for member audit logging
    """
    
    @staticmethod
    def log_member_action(user, action, details=None):
        """
        Log member action for audit trail
        """
        logger.info(
            f"Member Action: User {user.id} ({user.email}) "
            f"performed action '{action}' - Details: {details}"
        )
    
    @staticmethod
    def log_admin_action(admin_user, action, target_member, details=None):
        """
        Log admin action on member for audit trail
        """
        logger.info(
            f"Admin Action: Admin {admin_user.id} ({admin_user.email}) "
            f"performed action '{action}' on member {target_member.id} "
            f"({target_member.user.email}) - Details: {details}"
        )
    
    @staticmethod
    def log_security_event(event_type, user, details=None):
        """
        Log security-related events
        """
        logger.warning(
            f"Security Event: {event_type} - User {user.id if user else 'Anonymous'} "
            f"({user.email if user else 'N/A'}) - Details: {details}"
        )
