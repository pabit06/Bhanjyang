"""
Utility functions for News Events App.

Provides helper functions for common operations, validation, and data processing.
"""
"""
Utility functions for News Events App.

Provides helper functions for common operations, validation, and data processing.
"""
from typing import Dict, Any, Optional, List, Tuple
from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta
import logging
import re

from .models import NewsArticle, Event, Category

logger = logging.getLogger(__name__)


class NewsEventsValidator:
    """Validation utilities for News Events app."""
    
    @staticmethod
    def validate_category_id(category_id: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate category ID.
        
        Args:
            category_id: Category ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if category_id is None:
            return False, "Category ID is required"
        
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return False, "Category ID must be a valid integer"
        
        if category_id <= 0:
            return False, "Category ID must be a positive integer"
        
        if not Category.objects.filter(pk=category_id, is_active=True).exists():
            return False, f"Category with id {category_id} does not exist or is inactive"
        
        return True, None
    
    @staticmethod
    def validate_date_range(start_date: Any, end_date: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date and end_date:
            if end_date < start_date:
                return False, "End date cannot be before start date"
        
        return True, None
    
    @staticmethod
    def validate_pagination_params(page: Any, page_size: Any) -> Tuple[bool, Optional[str], int, int]:
        """
        Validate and normalize pagination parameters.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (is_valid, error_message, normalized_page, normalized_page_size)
        """
        try:
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 20
        except (ValueError, TypeError):
            return False, "Page and page_size must be valid integers", 1, 20
        
        if page < 1:
            return False, "Page must be greater than 0", 1, 20
        
        if page_size < 1:
            return False, "Page size must be greater than 0", 1, 20
        
        if page_size > 100:
            return False, "Page size cannot exceed 100", 1, 20
        
        return True, None, page, page_size


class NewsEventsHelper:
    """Helper functions for News Events app."""
    
    @staticmethod
    def get_optimized_article_queryset() -> QuerySet:
        """
        Get optimized article queryset with select_related and prefetch_related.
        
        Returns:
            Optimized QuerySet for NewsArticle
        """
        return NewsArticle.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'comments'
        )
    
    @staticmethod
    def get_optimized_event_queryset() -> QuerySet:
        """
        Get optimized event queryset.
        
        Returns:
            Optimized QuerySet for Event
        """
        return Event.objects.select_related().all()
    
    @staticmethod
    def format_error_response(error_message: str, detail: Optional[str] = None) -> Dict[str, Any]:
        """
        Format standardized error response.
        
        Args:
            error_message: Main error message
            detail: Additional error details
            
        Returns:
            Formatted error dictionary
        """
        response = {'error': error_message}
        if detail:
            response['detail'] = detail
        return response
    
    @staticmethod
    def get_time_range_filter(days: int = 30) -> Dict[str, Any]:
        """
        Get time range filter for date-based queries.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with date filter parameters
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        return {
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def calculate_pagination_info(count: int, page: int, page_size: int) -> Dict[str, Any]:
        """
        Calculate pagination information.
        
        Args:
            count: Total number of items
            page: Current page number
            page_size: Items per page
            
        Returns:
            Dictionary with pagination info
        """
        total_pages = (count + page_size - 1) // page_size if count > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        return {
            'count': count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_previous': has_previous
        }


class NewsEventsCacheHelper:
    """Helper functions for caching operations."""
    
    @staticmethod
    def get_cache_key(prefix: str, **kwargs) -> str:
        """
        Generate cache key with prefix and parameters.
        
        Args:
            prefix: Cache key prefix
            **kwargs: Additional parameters for cache key
            
        Returns:
            Generated cache key string
        """
        key_parts = [prefix]
        for key, value in sorted(kwargs.items()):
            if value is not None:
                key_parts.append(f"{key}:{value}")
        return ":".join(key_parts)
    
    @staticmethod
    def invalidate_pattern(pattern: str) -> None:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Cache key pattern to invalidate
        """
        from django.core.cache import cache
        try:
            # This is a simplified version - in production, use cache.delete_pattern
            # or implement custom cache invalidation
            logger.info(f"Cache invalidation requested for pattern: {pattern}")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}", exc_info=True)


class NewsEventsDataValidator:
    """Data validation utilities for News Events app."""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email cannot be empty"
        
        email = email.strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_slug(slug: str) -> Tuple[bool, Optional[str]]:
        """
        Validate slug format.
        
        Args:
            slug: Slug to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not slug or not slug.strip():
            return False, "Slug cannot be empty"
        
        slug = slug.strip()
        slug_pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
        
        if not re.match(slug_pattern, slug):
            return False, "Slug must contain only lowercase letters, numbers, and hyphens"
        
        if len(slug) > 250:
            return False, "Slug cannot exceed 250 characters"
        
        return True, None
    
    @staticmethod
    def validate_content_length(content: str, min_length: int = 10, max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate content length.
        
        Args:
            content: Content to validate
            min_length: Minimum length required
            max_length: Maximum length allowed (None for no limit)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Content cannot be empty"
        
        content_length = len(content.strip())
        
        if content_length < min_length:
            return False, f"Content must be at least {min_length} characters long"
        
        if max_length and content_length > max_length:
            return False, f"Content cannot exceed {max_length} characters"
        
        return True, None
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text by removing extra whitespace.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        return " ".join(text.split())

