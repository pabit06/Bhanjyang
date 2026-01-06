"""
Enhanced Security Module for Downloads App
==========================================

Based on news_events/security_enhanced.py
Provides advanced security features including:
- IP Blacklisting
- Rate Limiting
- Request validation
- Security logging

Author: Bhanjyang Dev Team
Date: January 6, 2026
"""

import hashlib
import ipaddress
import logging
from datetime import timedelta
from typing import Dict, Tuple, Optional, Any
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


# ============================================================================
# IP BLACKLIST MANAGER
# ============================================================================

class IPBlacklistManager:
    """
    Manages IP address blacklisting with automatic expiration.
    
    Features:
    - Time-based blacklisting
    - Automatic expiration
    - Blacklist reasons tracking
    - Manual whitelist support
    """
    
    BLACKLIST_PREFIX = 'downloads_ip_blacklist_'
    WHITELIST_PREFIX = 'downloads_ip_whitelist_'
    DEFAULT_DURATION = timedelta(hours=24)
    
    @classmethod
    def blacklist_ip(cls, ip_address: str, reason: str = '', duration: Optional[timedelta] = None) -> bool:
        """
        Blacklist an IP address.
        
        Args:
            ip_address: IP address to blacklist
            reason: Reason for blacklisting
            duration: How long to blacklist (default: 24 hours)
            
        Returns:
            bool: Success status
        """
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)
        except ValueError:
            logger.error(f"Invalid IP address: {ip_address}")
            return False
        
        # Check if whitelisted
        if cls.is_whitelisted(ip_address):
            logger.warning(f"Cannot blacklist whitelisted IP: {ip_address}")
            return False
        
        if duration is None:
            duration = getattr(
                settings,
                'IP_BLACKLIST_DURATION',
                cls.DEFAULT_DURATION
            )
        
        cache_key = f"{cls.BLACKLIST_PREFIX}{ip_address}"
        blacklist_data = {
            'reason': reason,
            'blacklisted_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + duration).isoformat(),
            'duration_seconds': int(duration.total_seconds())
        }
        
        cache.set(
            cache_key,
            blacklist_data,
            timeout=int(duration.total_seconds())
        )
        
        logger.warning(
            f"IP {ip_address} blacklisted for {duration}. Reason: {reason}"
        )
        return True
    
    @classmethod
    def is_blacklisted(cls, ip_address: str) -> bool:
        """
        Check if IP is blacklisted.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            bool: True if blacklisted
        """
        cache_key = f"{cls.BLACKLIST_PREFIX}{ip_address}"
        return cache.get(cache_key) is not None
    
    @classmethod
    def unblacklist_ip(cls, ip_address: str) -> bool:
        """
        Remove IP from blacklist.
        
        Args:
            ip_address: IP address to remove
            
        Returns:
            bool: Success status
        """
        cache_key = f"{cls.BLACKLIST_PREFIX}{ip_address}"
        result = cache.delete(cache_key)
        if result:
            logger.info(f"IP {ip_address} removed from blacklist")
        return result
    
    @classmethod
    def get_blacklist_info(cls, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get blacklist information for an IP.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            dict: Blacklist info or None
        """
        cache_key = f"{cls.BLACKLIST_PREFIX}{ip_address}"
        return cache.get(cache_key)
    
    @classmethod
    def whitelist_ip(cls, ip_address: str, reason: str = '') -> bool:
        """
        Add IP to whitelist (permanent).
        
        Args:
            ip_address: IP address to whitelist
            reason: Reason for whitelisting
            
        Returns:
            bool: Success status
        """
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            logger.error(f"Invalid IP address: {ip_address}")
            return False
        
        cache_key = f"{cls.WHITELIST_PREFIX}{ip_address}"
        whitelist_data = {
            'reason': reason,
            'whitelisted_at': timezone.now().isoformat()
        }
        
        # Set with very long timeout (1 year)
        cache.set(cache_key, whitelist_data, timeout=31536000)
        logger.info(f"IP {ip_address} whitelisted. Reason: {reason}")
        return True
    
    @classmethod
    def is_whitelisted(cls, ip_address: str) -> bool:
        """Check if IP is whitelisted."""
        cache_key = f"{cls.WHITELIST_PREFIX}{ip_address}"
        return cache.get(cache_key) is not None


# ============================================================================
# RATE LIMIT MANAGER
# ============================================================================

class RateLimitManager:
    """
    Rate limiting for downloads and other operations.
    
    Features:
    - Flexible rate limits
    - Multiple time windows
    - Per-user and per-IP limits
    - Detailed tracking
    """
    
    RATE_LIMIT_PREFIX = 'downloads_rate_limit_'
    
    # Default limits
    DEFAULT_LIMITS = {
        'download': {
            'max_requests': 20,
            'window': 3600  # 1 hour
        },
        'bulk_download': {
            'max_requests': 5,
            'window': 86400  # 24 hours
        },
        'view': {
            'max_requests': 100,
            'window': 3600  # 1 hour
        }
    }
    
    @classmethod
    def check_rate_limit(
        cls,
        identifier: str,
        action: str = 'download',
        max_requests: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[bool, int, int]:
        """
        Check if identifier has exceeded rate limit.
        
        Args:
            identifier: User ID, IP address, or session key
            action: Type of action (download, bulk_download, view)
            max_requests: Maximum requests allowed (overrides default)
            window: Time window in seconds (overrides default)
            
        Returns:
            tuple: (is_allowed: bool, current_count: int, reset_time: int)
        """
        # Get limits
        if max_requests is None or window is None:
            limits = cls.DEFAULT_LIMITS.get(action, cls.DEFAULT_LIMITS['download'])
            if max_requests is None:
                max_requests = limits['max_requests']
            if window is None:
                window = limits['window']
        
        cache_key = f"{cls.RATE_LIMIT_PREFIX}{action}_{identifier}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= max_requests:
            ttl = cache.ttl(cache_key) or window
            logger.warning(
                f"Rate limit exceeded for {identifier} on {action}. "
                f"Count: {current_count}/{max_requests}, Reset in: {ttl}s"
            )
            return False, current_count, ttl
        
        # Increment counter
        new_count = current_count + 1
        cache.set(cache_key, new_count, window)
        
        return True, new_count, window
    
    @classmethod
    def reset_rate_limit(cls, identifier: str, action: str = 'download') -> bool:
        """
        Reset rate limit for identifier.
        
        Args:
            identifier: User ID, IP, or session key
            action: Type of action
            
        Returns:
            bool: Success status
        """
        cache_key = f"{cls.RATE_LIMIT_PREFIX}{action}_{identifier}"
        result = cache.delete(cache_key)
        if result:
            logger.info(f"Rate limit reset for {identifier} on {action}")
        return result
    
    @classmethod
    def get_remaining_requests(
        cls,
        identifier: str,
        action: str = 'download'
    ) -> Tuple[int, int]:
        """
        Get remaining requests for identifier.
        
        Args:
            identifier: User ID, IP, or session key
            action: Type of action
            
        Returns:
            tuple: (remaining: int, reset_time: int)
        """
        limits = cls.DEFAULT_LIMITS.get(action, cls.DEFAULT_LIMITS['download'])
        max_requests = limits['max_requests']
        
        cache_key = f"{cls.RATE_LIMIT_PREFIX}{action}_{identifier}"
        current_count = cache.get(cache_key, 0)
        remaining = max(0, max_requests - current_count)
        ttl = cache.ttl(cache_key) or limits['window']
        
        return remaining, ttl


# ============================================================================
# SECURITY AUDIT ENHANCED LOGGER
# ============================================================================

class SecurityAuditEnhancedLogger:
    """
    Enhanced security audit logging.
    
    Logs all security-related events with detailed context.
    """
    
    LOG_PREFIX = 'downloads_security_'
    
    @classmethod
    def log_event(
        cls,
        event_type: str,
        user: Any,
        ip_address: str,
        details: Dict[str, Any],
        severity: str = 'INFO'
    ) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of event (DOWNLOAD, BLACKLIST, RATE_LIMIT, etc.)
            user: User object or identifier
            ip_address: Client IP address
            details: Additional event details
            severity: Log severity (INFO, WARNING, ERROR)
        """
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'user': str(user) if user else 'Anonymous',
            'ip_address': ip_address,
            'details': details,
            'severity': severity
        }
        
        # Log to Django logger
        log_message = (
            f"[{severity}] {event_type} | "
            f"User: {log_data['user']} | "
            f"IP: {ip_address} | "
            f"Details: {details}"
        )
        
        if severity == 'ERROR':
            logger.error(log_message)
        elif severity == 'WARNING':
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Store in cache for recent events (last 1000)
        cache_key = f"{cls.LOG_PREFIX}recent_events"
        recent_events = cache.get(cache_key, [])
        recent_events.insert(0, log_data)
        recent_events = recent_events[:1000]  # Keep last 1000
        cache.set(cache_key, recent_events, timeout=86400)  # 24 hours
    
    @classmethod
    def log_download(cls, user: Any, file_obj: Any, ip_address: str) -> None:
        """Log file download."""
        cls.log_event(
            'DOWNLOAD',
            user,
            ip_address,
            {
                'file_id': file_obj.id,
                'file_title': file_obj.title,
                'file_category': file_obj.category,
                'success': True
            },
            'INFO'
        )
    
    @classmethod
    def log_failed_access(
        cls,
        user: Any,
        file_obj: Any,
        ip_address: str,
        reason: str
    ) -> None:
        """Log failed access attempt."""
        cls.log_event(
            'FAILED_ACCESS',
            user,
            ip_address,
            {
                'file_id': file_obj.id,
                'file_title': file_obj.title,
                'reason': reason,
                'success': False
            },
            'WARNING'
        )
    
    @classmethod
    def log_rate_limit_exceeded(
        cls,
        identifier: str,
        ip_address: str,
        action: str,
        count: int
    ) -> None:
        """Log rate limit violation."""
        cls.log_event(
            'RATE_LIMIT_EXCEEDED',
            identifier,
            ip_address,
            {
                'action': action,
                'request_count': count
            },
            'WARNING'
        )
    
    @classmethod
    def log_ip_blacklisted(
        cls,
        ip_address: str,
        reason: str,
        duration: int
    ) -> None:
        """Log IP blacklist event."""
        cls.log_event(
            'IP_BLACKLISTED',
            'System',
            ip_address,
            {
                'reason': reason,
                'duration_seconds': duration
            },
            'WARNING'
        )
    
    @classmethod
    def get_recent_events(cls, limit: int = 100) -> list:
        """Get recent security events."""
        cache_key = f"{cls.LOG_PREFIX}recent_events"
        events = cache.get(cache_key, [])
        return events[:limit]


# ============================================================================
# REQUEST VALIDATOR
# ============================================================================

class RequestValidator:
    """
    Validates incoming requests for security.
    """
    
    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """
        Get client IP address from request.
        
        Handles X-Forwarded-For header for proxies.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    @staticmethod
    def validate_request_signature(request: HttpRequest) -> bool:
        """
        Validate request signature (if implemented).
        
        TODO: Implement request signing for API calls.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            bool: True if valid
        """
        # Placeholder for future implementation
        return True


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'IPBlacklistManager',
    'RateLimitManager',
    'SecurityAuditEnhancedLogger',
    'RequestValidator',
]
