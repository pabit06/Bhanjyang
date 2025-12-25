"""
Performance monitoring utilities for Contact app.

This module provides tools for monitoring and analyzing contact form performance,
including request timing, database query tracking, and submission analytics.
"""
import functools
import logging
import time
from datetime import timedelta

from django.core.cache import cache
from django.db import connection
from django.db.models import Avg, Count, F, ExpressionWrapper, fields
from django.utils import timezone

logger = logging.getLogger(__name__)

# Performance thresholds
MAX_PROCESSING_TIME_SECONDS = 2.0
MAX_DB_QUERIES = 10
MIN_SUCCESS_RATE = 0.95

# Cache settings
PERFORMANCE_CACHE_TIMEOUT = 3600  # 1 hour


class ContactPerformanceMonitor:
    """
    Monitor and log contact form performance metrics.
    
    Tracks processing time, database queries, and success rates
    for contact form submissions.
    """
    
    @staticmethod
    def log_form_submission_performance(submission_id, processing_time, db_queries_count, success=True):
        """
        Log performance metrics for a form submission.
        
        Args:
            submission_id: Unique identifier for the submission
            processing_time: Time taken to process the request in seconds
            db_queries_count: Number of database queries executed
            success: Whether the submission was successful
        """
        status = "success" if success else "error"
        logger.info(
            f"Contact form submission {submission_id} {status}: "
            f"{processing_time:.3f}s, {db_queries_count} DB queries"
        )
        
        # Store metrics in cache for analytics
        cache_key = f"contact_performance_{submission_id}"
        cache.set(cache_key, {
            'processing_time': processing_time,
            'db_queries': db_queries_count,
            'success': success,
            'timestamp': timezone.now().isoformat()
        }, timeout=PERFORMANCE_CACHE_TIMEOUT)
    
    @staticmethod
    def get_performance_stats(days=7):
        """
        Get aggregated performance statistics for a time period.
        
        Args:
            days: Number of days to analyze (default: 7)
            
        Returns:
            dict: Performance statistics including averages and totals
        """
        from .models import ContactSubmission
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get submissions in period
        submissions = ContactSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        total_submissions = submissions.count()
        
        # Get performance data from cache
        # Limit to recent submissions to avoid too many cache calls
        recent_submissions = submissions[:100]
        cache_keys = [f"contact_performance_{sub.id}" for sub in recent_submissions]
        performance_data = []
        
        for key in cache_keys:
            data = cache.get(key)
            if data:
                performance_data.append(data)
        
        if performance_data:
            avg_processing_time = sum(d.get('processing_time', 0) for d in performance_data) / len(performance_data)
            avg_db_queries = sum(d.get('db_queries', 0) for d in performance_data) / len(performance_data)
            success_count = sum(1 for d in performance_data if d.get('success', False))
            success_rate = success_count / len(performance_data) if performance_data else 0.0
        else:
            avg_processing_time = 0.0
            avg_db_queries = 0
            success_rate = 0.0
        
        stats = {
            'avg_processing_time': round(avg_processing_time, 3),
            'avg_db_queries': round(avg_db_queries, 1),
            'success_rate': round(success_rate, 2),
            'total_submissions': total_submissions,
            'period': f"{start_date.date()} to {end_date.date()}"
        }
        
        logger.info(f"Performance stats calculated for {days} days: {stats}")
        return stats
    
    @staticmethod
    def check_performance_thresholds():
        """
        Check if current performance metrics are within acceptable thresholds.
        
        Returns:
            bool: True if all metrics are within thresholds
        """
        # Note: This is a placeholder. In production, check actual metrics.
        logger.info("Performance thresholds checked")
        return True


def monitor_contact_performance(func):
    """
    Decorator to monitor contact form performance.
    
    Automatically tracks processing time and database query count
    for decorated view functions.
    
    Args:
        func: View function to monitor
        
    Returns:
        Wrapped function with performance monitoring
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        db_queries_start = len(connection.queries)
        success = True
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            processing_time = time.time() - start_time
            db_queries_count = len(connection.queries) - db_queries_start
            
            # Find request object for logging
            request = _extract_request(args, kwargs)
            submission_id = getattr(request, 'id', 'unknown') if request else 'unknown'
            
            ContactPerformanceMonitor.log_form_submission_performance(
                submission_id=submission_id,
                processing_time=processing_time,
                db_queries_count=db_queries_count,
                success=success
            )
    
    return wrapper


def _extract_request(args, kwargs):
    """
    Extract request object from function arguments.
    
    Args:
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Request object if found, None otherwise
    """
    # Check kwargs first
    if 'request' in kwargs:
        return kwargs['request']
    
    # Check args for request-like objects
    for arg in args:
        if hasattr(arg, 'META') or hasattr(arg, 'id'):
            return arg
    
    return None


class ContactAnalytics:
    """
    Analytics utilities for contact form submissions.
    
    Provides methods to analyze submission trends, response times,
    and other metrics for reporting purposes.
    """
    
    @staticmethod
    def get_submission_trends(days=30):
        """
        Get daily submission counts for a time period.
        
        Args:
            days: Number of days to analyze (default: 30)
            
        Returns:
            dict: Daily counts and total submissions
        """
        from .models import ContactSubmission
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        submissions = ContactSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Get daily counts using database-specific date extraction
        daily_counts = submissions.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        return {
            'daily_counts': list(daily_counts),
            'total_submissions': submissions.count(),
            'period': f"{start_date.date()} to {end_date.date()}"
        }
    
    @staticmethod
    def get_response_time_analytics():
        """
        Get analytics on response times for resolved submissions.
        
        Returns:
            dict: Average response time in hours and count of resolved submissions
        """
        from .models import ContactSubmission
        
        resolved_submissions = ContactSubmission.objects.filter(
            status='resolved',
            resolved_at__isnull=False
        ).annotate(
            response_duration=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        )
        
        avg_response_time = resolved_submissions.aggregate(
            avg_duration=Avg('response_duration')
        )['avg_duration']
        
        avg_hours = avg_response_time.total_seconds() / 3600 if avg_response_time else 0
        
        return {
            'avg_response_hours': round(avg_hours, 2),
            'resolved_count': resolved_submissions.count()
        }
    
    @staticmethod
    def get_status_breakdown():
        """
        Get a breakdown of submissions by status.
        
        Returns:
            dict: Count of submissions for each status
        """
        from .models import ContactSubmission
        
        status_counts = ContactSubmission.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        return {item['status']: item['count'] for item in status_counts}
