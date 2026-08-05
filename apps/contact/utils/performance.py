"""
Performance tracking utilities for the Contact app.
"""
import logging
import time
from typing import Dict, Any, Optional
from functools import wraps
from django.db import connection
from django.utils import timezone
from apps.shared_security import get_client_ip_from_meta as resolve_client_ip_from_meta

try:
    from apps.dashboard.models import PerformanceMetric
    PERFORMANCE_METRIC_AVAILABLE = True
except ImportError:
    PERFORMANCE_METRIC_AVAILABLE = False
    PerformanceMetric = None

logger = logging.getLogger(__name__)
SLOW_OPERATION_THRESHOLD_MS = 500


def get_client_ip_from_meta(request_meta: Dict[str, Any]) -> str:
    return resolve_client_ip_from_meta(request_meta, default='')

def track_performance(metric_type: str, page_url: Optional[str] = None):
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
                    logger.warning(f"Slow {metric_type} operation: {duration:.2f}ms (queries: {db_queries})")
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

def track_form_submission_performance(
    form_validation_time: float,
    file_upload_time: float,
    email_queue_time: float,
    total_time: float,
    request_meta: Dict[str, Any],
    user=None,
    session_id: Optional[str] = None,
    submission_id: Optional[int] = None
) -> None:
    if not PERFORMANCE_METRIC_AVAILABLE:
        return
    try:
        ip_address = get_client_ip_from_meta(request_meta)
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        additional_data = {
            'form_validation_time': form_validation_time,
            'file_upload_time': file_upload_time,
            'email_queue_time': email_queue_time,
            'submission_id': submission_id
        }
        PerformanceMetric.objects.create(
            metric_type='form_submit',
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
            logger.warning(f"Slow form submission: {total_time:.2f}ms")
    except Exception as e:
        logger.warning(f"Failed to track form submission performance: {e}")

def track_api_response_time(
    response_time: float,
    endpoint: str,
    request_meta: Dict[str, Any],
    user=None,
    session_id: Optional[str] = None
) -> None:
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
    except Exception as e:
        logger.warning(f"Failed to track API response time: {e}")

def track_pdf_generation_time(
    generation_time: float,
    request_meta: Dict[str, Any],
    user=None,
    submission_id: Optional[int] = None
) -> None:
    if not PERFORMANCE_METRIC_AVAILABLE:
        return
    try:
        ip_address = get_client_ip_from_meta(request_meta)
        user_agent = request_meta.get('HTTP_USER_AGENT', '')
        additional_data = {'submission_id': submission_id} if submission_id else {}
        PerformanceMetric.objects.create(
            metric_type='form_submit',
            value=generation_time,
            unit='ms',
            ip_address=ip_address,
            user_agent=user_agent,
            user=user,
            additional_data=additional_data,
            timestamp=timezone.now()
        )
        if generation_time > SLOW_OPERATION_THRESHOLD_MS:
            logger.warning(f"Slow PDF generation: {generation_time:.2f}ms")
    except Exception as e:
        logger.warning(f"Failed to track PDF generation time: {e}")