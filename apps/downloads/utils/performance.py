"""
Performance tracking utilities for the Downloads app.
"""
import logging
import time
from typing import Dict, Any, Optional
from functools import wraps
from django.db import connection
from django.utils import timezone

try:
    from apps.dashboard.models import PerformanceMetric
    PERFORMANCE_METRIC_AVAILABLE = True
except ImportError:
    PERFORMANCE_METRIC_AVAILABLE = False
    PerformanceMetric = None

logger = logging.getLogger(__name__)
SLOW_OPERATION_THRESHOLD_MS = 500


def get_client_ip_from_meta(request_meta: Dict[str, Any]) -> str:
    """
    Extract client IP from request META dictionary.
    
    Note: This is a convenience function for performance tracking.
    For general use, prefer get_client_ip from utils.helpers which handles both
    HttpRequest objects and META dictionaries.
    """
    x_forwarded_for = request_meta.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request_meta.get('REMOTE_ADDR', '')
    return ip


def track_performance(metric_type: str, page_url: Optional[str] = None):
    """
    Decorator to track performance of service methods.
    
    Args:
        metric_type: Type of metric (e.g., 'download_center', 'file_download', 'bulk_download')
        page_url: Optional page URL for context
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            db_queries_start = len(connection.queries)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start_time) * 1000
                db_queries = len(connection.queries) - db_queries_start
                if duration > SLOW_OPERATION_THRESHOLD_MS:
                    logger.warning(
                        f"Slow {metric_type} operation: {duration:.2f}ms (queries: {db_queries})"
                    )
                if PERFORMANCE_METRIC_AVAILABLE:
                    try:
                        PerformanceMetric.objects.create(
                            metric_type=metric_type,
                            page_url=page_url or '',
                            value=duration,
                            unit='ms',
                            timestamp=timezone.now()
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store performance metric: {e}")
        return wrapper
    return decorator


def track_download_performance(
    download_time: float,
    file_size: int,
    request_meta: Dict[str, Any],
    user=None,
    session_id: Optional[str] = None,
    file_id: Optional[int] = None
) -> None:
    """
    Track download operation performance.
    
    Args:
        download_time: Time taken for download in milliseconds
        file_size: Size of downloaded file in bytes
        request_meta: Request META dictionary
        user: User instance (optional)
        session_id: Session ID (optional)
        file_id: File ID (optional)
    """
    if not PERFORMANCE_METRIC_AVAILABLE:
        return
    try:
        ip_address = get_client_ip_from_meta(request_meta)
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        additional_data = {
            'file_size': file_size,
            'file_id': file_id,
            'download_speed_mbps': (file_size / (1024 * 1024)) / (download_time / 1000) if download_time > 0 else 0
        }
        PerformanceMetric.objects.create(
            metric_type='file_download',
            value=download_time,
            unit='ms',
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            user=user,
            additional_data=additional_data,
            timestamp=timezone.now()
        )
        if download_time > SLOW_OPERATION_THRESHOLD_MS:
            logger.warning(f"Slow download: {download_time:.2f}ms (file_id: {file_id})")
    except Exception as e:
        logger.warning(f"Failed to track download performance: {e}")


def track_bulk_download_performance(
    total_time: float,
    file_count: int,
    total_size: int,
    request_meta: Dict[str, Any],
    user=None,
    session_id: Optional[str] = None
) -> None:
    """
    Track bulk download operation performance.
    
    Args:
        total_time: Total time taken in milliseconds
        file_count: Number of files in bulk download
        total_size: Total size of files in bytes
        request_meta: Request META dictionary
        user: User instance (optional)
        session_id: Session ID (optional)
    """
    if not PERFORMANCE_METRIC_AVAILABLE:
        return
    try:
        ip_address = get_client_ip_from_meta(request_meta)
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        additional_data = {
            'file_count': file_count,
            'total_size': total_size,
            'avg_file_size': total_size / file_count if file_count > 0 else 0,
            'avg_time_per_file': total_time / file_count if file_count > 0 else 0
        }
        PerformanceMetric.objects.create(
            metric_type='bulk_download',
            value=total_time,
            unit='ms',
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            user=user,
            additional_data=additional_data,
            timestamp=timezone.now()
        )
        if total_time > SLOW_OPERATION_THRESHOLD_MS:
            logger.warning(f"Slow bulk download: {total_time:.2f}ms ({file_count} files)")
    except Exception as e:
        logger.warning(f"Failed to track bulk download performance: {e}")


def track_api_response_time(
    response_time: float,
    endpoint: str,
    request_meta: Dict[str, Any],
    user=None,
    session_id: Optional[str] = None
) -> None:
    """
    Track API response time.
    
    Args:
        response_time: Response time in milliseconds
        endpoint: API endpoint path
        request_meta: Request META dictionary
        user: User instance (optional)
        session_id: Session ID (optional)
    """
    if not PERFORMANCE_METRIC_AVAILABLE:
        return
    try:
        ip_address = get_client_ip_from_meta(request_meta)
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        PerformanceMetric.objects.create(
            metric_type='api_response',
            page_url=endpoint,
            value=response_time,
            unit='ms',
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            user=user,
            timestamp=timezone.now()
        )
        if response_time > SLOW_OPERATION_THRESHOLD_MS:
            logger.warning(f"Slow API response: {endpoint} took {response_time:.2f}ms")
    except Exception as e:
        logger.warning(f"Failed to track API response time: {e}")


def track_cache_performance(
    operation: str,
    cache_key: str,
    hit: bool,
    lookup_time: float,
    request_meta: Optional[Dict[str, Any]] = None
) -> None:
    """
    Track cache performance (hits/misses and lookup times).
    
    Args:
        operation: Cache operation type ('get', 'set', 'delete')
        cache_key: Cache key used
        hit: Whether it was a cache hit (True) or miss (False)
        lookup_time: Time taken for cache operation in milliseconds
        request_meta: Request META dictionary (optional)
    """
    if not PERFORMANCE_METRIC_AVAILABLE:
        return
    try:
        additional_data = {
            'operation': operation,
            'cache_key': cache_key,
            'hit': hit
        }
        ip_address = get_client_ip_from_meta(request_meta) if request_meta else None
        PerformanceMetric.objects.create(
            metric_type='cache_operation',
            value=lookup_time,
            unit='ms',
            ip_address=ip_address,
            additional_data=additional_data,
            timestamp=timezone.now()
        )
    except Exception as e:
        logger.warning(f"Failed to track cache performance: {e}")
