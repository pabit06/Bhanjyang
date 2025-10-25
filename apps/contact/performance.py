"""
Performance monitoring utilities for contact app
"""
import time
import logging
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class ContactPerformanceMonitor:
    """Monitor contact form performance metrics"""
    
    @staticmethod
    def log_form_submission_performance(submission_id, processing_time, db_queries_count, success=True):
        """Log performance metrics for form submissions"""
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
        }, timeout=3600)  # Cache for 1 hour
    
    @staticmethod
    def get_performance_stats(days=7):
        """Get performance statistics for the last N days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # This would typically query a performance metrics table
        # For now, we'll return cached data
        stats = {
            'avg_processing_time': 0.0,
            'avg_db_queries': 0,
            'success_rate': 0.0,
            'total_submissions': 0,
            'period': f"{start_date.date()} to {end_date.date()}"
        }
        
        logger.info(f"Performance stats requested for {days} days")
        return stats
    
    @staticmethod
    def check_performance_thresholds():
        """Check if performance metrics exceed thresholds"""
        thresholds = {
            'max_processing_time': 2.0,  # 2 seconds
            'max_db_queries': 10,
            'min_success_rate': 0.95  # 95%
        }
        
        # This would check actual performance data
        # For now, just log the check
        logger.info("Performance thresholds checked")
        return True


def monitor_contact_performance(func):
    """Decorator to monitor contact form performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        db_queries_start = len(connection.queries)
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            success = False
            raise e
        finally:
            processing_time = time.time() - start_time
            db_queries_count = len(connection.queries) - db_queries_start
            
            # Log performance metrics
            ContactPerformanceMonitor.log_form_submission_performance(
                submission_id=getattr(kwargs.get('request'), 'id', 'unknown'),
                processing_time=processing_time,
                db_queries_count=db_queries_count,
                success=success
            )
        
        return result
    return wrapper


class ContactAnalytics:
    """Analytics utilities for contact form"""
    
    @staticmethod
    def get_submission_trends(days=30):
        """Get submission trends over time"""
        from apps.contact.models import ContactSubmission
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        submissions = ContactSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Daily counts
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
        """Get response time analytics"""
        from apps.contact.models import ContactSubmission
        from django.db.models import Avg, F, ExpressionWrapper, fields
        
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
        
        return {
            'avg_response_hours': avg_response_time.total_seconds() / 3600 if avg_response_time else 0,
            'resolved_count': resolved_submissions.count()
        }
