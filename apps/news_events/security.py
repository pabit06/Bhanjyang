"""
News Events Security Module
Enhanced security features for content management and user interactions
"""

import os
import hashlib
import re
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
# from django_ratelimit.decorators import ratelimit  # Commented out until installed
# from django_ratelimit.exceptions import Ratelimited  # Commented out until installed
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Security constants
MAX_CONTENT_LENGTH = 100000  # 100KB max content
MAX_COMMENT_LENGTH = 2000
MAX_TITLE_LENGTH = 200
SPAM_KEYWORDS = [
    'viagra', 'casino', 'lottery', 'winner', 'congratulations', 'free money',
    'click here', 'limited time', 'act now', 'guaranteed', 'no risk'
]
SUSPICIOUS_PATTERNS = [
    r'https?://[^\s]+',  # URLs
    r'\b\d{4}[-.]?\d{4}[-.]?\d{4}[-.]?\d{4}\b',  # Credit card numbers
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
]

class ContentSecurityValidator:
    """Content security validation"""
    
    @staticmethod
    def validate_content_security(content, content_type='article'):
        """Validate content for security issues"""
        try:
            # Check content length
            if len(content) > MAX_CONTENT_LENGTH:
                raise ValidationError(f"Content too long. Maximum {MAX_CONTENT_LENGTH} characters allowed.")
            
            # Check for spam keywords
            content_lower = content.lower()
            spam_count = sum(1 for keyword in SPAM_KEYWORDS if keyword in content_lower)
            if spam_count > 3:
                raise ValidationError("Content contains too many spam indicators.")
            
            # Check for suspicious patterns
            for pattern in SUSPICIOUS_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"Suspicious pattern detected in {content_type}: {pattern}")
            
            # Generate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            return {
                'is_valid': True,
                'content_hash': content_hash,
                'spam_score': spam_count,
                'length': len(content)
            }
            
        except Exception as e:
            logger.error(f"Content security validation failed: {e}")
            raise ValidationError(f"Content security validation failed: {str(e)}")
    
    @staticmethod
    def sanitize_content(content):
        """Sanitize content by removing potentially harmful elements"""
        try:
            import bleach
            from bleach.css_sanitizer import CSSSanitizer
            
            # Define allowed tags and attributes
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'div', 'span', 'table', 'thead',
                'tbody', 'tr', 'td', 'th', 'code', 'pre'
            ]
            
            allowed_attributes = {
                'a': ['href', 'title', 'target'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
                'table': ['border', 'cellpadding', 'cellspacing'],
                'td': ['colspan', 'rowspan'],
                'th': ['colspan', 'rowspan'],
                '*': ['class', 'id']
            }
            
            # CSS sanitizer for style attributes
            css_sanitizer = CSSSanitizer(allowed_css_properties=[
                'color', 'background-color', 'font-size', 'font-weight', 'text-align',
                'margin', 'padding', 'border', 'width', 'height'
            ])
            
            # Sanitize HTML content
            sanitized_content = bleach.clean(
                content,
                tags=allowed_tags,
                attributes=allowed_attributes,
                css_sanitizer=css_sanitizer,
                strip=True
            )
            
            # Additional manual sanitization for edge cases
            # Remove javascript: URLs
            sanitized_content = re.sub(r'javascript:', '', sanitized_content, flags=re.IGNORECASE)
            
            # Remove data: URLs that might contain scripts
            sanitized_content = re.sub(r'data:text/html[^"\']*', '', sanitized_content, flags=re.IGNORECASE)
            
            # Remove vbscript: URLs
            sanitized_content = re.sub(r'vbscript:', '', sanitized_content, flags=re.IGNORECASE)
            
            return sanitized_content
            
        except ImportError:
            # Fallback to basic sanitization if bleach is not available
            logger.warning("bleach library not available, using basic sanitization")
            
            # Remove script tags
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove javascript: URLs
            content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
            
            # Remove on* event handlers
            content = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
            
            return content
            
        except Exception as e:
            logger.error(f"Content sanitization failed: {e}")
            return content

class SpamProtectionManager:
    """Spam protection for comments and subscriptions"""
    
    @staticmethod
    def check_spam_indicators(content, author_email=None, ip_address=None):
        """Check content for spam indicators"""
        spam_score = 0
        reasons = []
        
        try:
            content_lower = content.lower()
            
            # Check spam keywords
            spam_keywords_found = [keyword for keyword in SPAM_KEYWORDS if keyword in content_lower]
            if spam_keywords_found:
                spam_score += len(spam_keywords_found) * 2
                reasons.append(f"Spam keywords: {', '.join(spam_keywords_found)}")
            
            # Check for excessive links
            link_count = len(re.findall(r'https?://[^\s]+', content))
            if link_count > 2:
                spam_score += link_count * 3
                reasons.append(f"Too many links: {link_count}")
            
            # Check for repetitive content
            words = content.split()
            if len(words) > 10:
                word_frequency = {}
                for word in words:
                    word_frequency[word.lower()] = word_frequency.get(word.lower(), 0) + 1
                
                max_frequency = max(word_frequency.values())
                if max_frequency > len(words) * 0.3:  # More than 30% repetition
                    spam_score += 5
                    reasons.append("Repetitive content detected")
            
            # Check email domain
            if author_email:
                suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
                domain = author_email.split('@')[-1].lower()
                if domain in suspicious_domains:
                    spam_score += 3
                    reasons.append(f"Suspicious email domain: {domain}")
            
            # Check IP reputation (simplified)
            if ip_address:
                # Check if IP has made many recent submissions
                cache_key = f"spam_check_{ip_address}"
                recent_submissions = cache.get(cache_key, 0)
                if recent_submissions > 5:  # More than 5 submissions in cache period
                    spam_score += 4
                    reasons.append("High submission frequency from IP")
                
                # Update cache
                cache.set(cache_key, recent_submissions + 1, 3600)  # 1 hour
            
            return {
                'is_spam': spam_score > 10,
                'spam_score': spam_score,
                'reasons': reasons,
                'threshold': 10
            }
            
        except Exception as e:
            logger.error(f"Spam check failed: {e}")
            return {
                'is_spam': False,
                'spam_score': 0,
                'reasons': ['Spam check failed'],
                'threshold': 10
            }

class RateLimitManager:
    """Rate limiting for various operations"""
    
    @staticmethod
    def check_subscription_rate_limit(request):
        """Check subscription rate limit"""
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f"subscription_rate_{ip_address}"
        
        try:
            attempts = cache.get(cache_key, 0)
            if attempts >= 3:  # Max 3 subscription attempts per hour
                return False, "Too many subscription attempts. Please try again later."
            
            cache.set(cache_key, attempts + 1, 3600)  # 1 hour
            return True, "Rate limit OK"
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, "Rate limit check failed"

    @staticmethod
    def check_comment_rate_limit(request):
        """Check comment rate limit"""
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f"comment_rate_{ip_address}"
        
        try:
            attempts = cache.get(cache_key, 0)
            if attempts >= 5:  # Max 5 comments per hour
                return False, "Too many comments. Please try again later."
            
            cache.set(cache_key, attempts + 1, 3600)  # 1 hour
            return True, "Rate limit OK"
            
        except Exception as e:
            logger.error(f"Comment rate limit check failed: {e}")
            return True, "Rate limit check failed"

class SecurityAuditLogger:
    """Security audit logging"""
    
    @staticmethod
    def log_content_action(request, content_type, content_id, action, success=True, reason=""):
        """Log content-related security actions"""
        try:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
                'user_id': request.user.id if request.user.is_authenticated else None,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'content_type': content_type,
                'content_id': content_id,
                'action': action,
                'success': success,
                'reason': reason,
                'referer': request.META.get('HTTP_REFERER', '')
            }
            
            logger.info(f"Content security action: {log_data}")
            
            # Store in cache for monitoring
            cache_key = f"security_log_{timezone.now().strftime('%Y%m%d')}"
            logs = cache.get(cache_key, [])
            logs.append(log_data)
            cache.set(cache_key, logs, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Security audit logging failed: {e}")

    @staticmethod
    def log_subscription_attempt(request, email, success=True, reason=""):
        """Log subscription attempts"""
        try:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
                'email': email,
                'success': success,
                'reason': reason,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', '')
            }
            
            logger.info(f"Subscription attempt: {log_data}")
            
        except Exception as e:
            logger.error(f"Subscription audit logging failed: {e}")

# Rate limiting decorators
def rate_limit_subscriptions(func):
    """Rate limit subscription attempts"""
    def wrapper(request, *args, **kwargs):
        can_proceed, reason = RateLimitManager.check_subscription_rate_limit(request)
        if not can_proceed:
            SecurityAuditLogger.log_subscription_attempt(request, request.POST.get('email', ''), False, reason)
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'message': reason}, status=429)
        
        return func(request, *args, **kwargs)
    return wrapper

def rate_limit_comments(func):
    """Rate limit comment submissions"""
    def wrapper(request, *args, **kwargs):
        can_proceed, reason = RateLimitManager.check_comment_rate_limit(request)
        if not can_proceed:
            SecurityAuditLogger.log_content_action(request, 'comment', 0, 'submit', False, reason)
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'message': reason}, status=429)
        
        return func(request, *args, **kwargs)
    return wrapper

def require_content_permission(func):
    """Require permission to view content"""
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated for protected content
        if hasattr(request, 'content_requires_login') and request.content_requires_login:
            if not request.user.is_authenticated:
                SecurityAuditLogger.log_content_action(request, 'article', kwargs.get('pk', 0), 'view', False, "Login required")
                from django.shortcuts import redirect
                return redirect('auth:login')
        
        return func(request, *args, **kwargs)
    return wrapper

class EmailSecurityManager:
    """Email security and validation"""
    
    @staticmethod
    def validate_email_security(email):
        """Validate email for security issues"""
        try:
            # Check for disposable email domains
            disposable_domains = [
                '10minutemail.com', 'tempmail.com', 'guerrillamail.com',
                'mailinator.com', 'yopmail.com', 'temp-mail.org'
            ]
            
            domain = email.split('@')[-1].lower()
            if domain in disposable_domains:
                return False, "Disposable email addresses are not allowed"
            
            # Check email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "Invalid email format"
            
            return True, "Email is valid"
            
        except Exception as e:
            logger.error(f"Email validation failed: {e}")
            return False, "Email validation failed"

    @staticmethod
    def send_confirmation_email(subscriber):
        """Send email confirmation"""
        try:
            token = subscriber.generate_confirmation_token()
            subscriber.save()
            
            confirmation_url = f"{settings.SITE_URL}/news-events/confirm-subscription/{token}/"
            
            subject = "Confirm Your Newsletter Subscription"
            message = f"""
            Hello {subscriber.first_name or 'there'},
            
            Thank you for subscribing to our newsletter!
            
            Please confirm your subscription by clicking the link below:
            {confirmation_url}
            
            If you didn't subscribe to our newsletter, please ignore this email.
            
            Best regards,
            Bhanjyang Cooperative Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Confirmation email failed: {e}")
            return False
