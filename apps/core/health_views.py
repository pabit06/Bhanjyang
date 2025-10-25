"""
Health check and monitoring endpoints for the Bhanjyang Cooperative application.
"""
import time
import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.conf import settings

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@never_cache
def health_check(request) -> JsonResponse:
    """
    Comprehensive health check endpoint for monitoring.
    
    Returns:
        JsonResponse: Health status with detailed component information
    """
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': getattr(settings, 'RELEASE_VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'components': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
            db_response_time = (time.time() - start_time) * 1000
    except Exception as e:
        db_status = "unhealthy"
        db_response_time = None
        logger.error(f"Database health check failed: {e}")
        health_status['status'] = 'unhealthy'
    
    health_status['components']['database'] = {
        'status': db_status,
        'response_time_ms': db_response_time,
        'engine': settings.DATABASES['default']['ENGINE']
    }
    
    # Check cache connectivity
    try:
        cache_start = time.time()
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        cache_status = "healthy" if cache_value == 'ok' else "unhealthy"
        cache_response_time = (time.time() - cache_start) * 1000
    except Exception as e:
        cache_status = "unhealthy"
        cache_response_time = None
        logger.error(f"Cache health check failed: {e}")
        health_status['status'] = 'unhealthy'
    
    health_status['components']['cache'] = {
        'status': cache_status,
        'response_time_ms': cache_response_time,
        'backend': settings.CACHES['default']['BACKEND']
    }
    
    # Check Redis connectivity (if using Redis)
    if 'redis' in settings.CACHES['default']['BACKEND'].lower():
        try:
            redis_start = time.time()
            redis_client = cache.get_master_client()
            redis_client.ping()
            redis_status = "healthy"
            redis_response_time = (time.time() - redis_start) * 1000
        except Exception as e:
            redis_status = "unhealthy"
            redis_response_time = None
            logger.error(f"Redis health check failed: {e}")
            health_status['status'] = 'unhealthy'
        
        health_status['components']['redis'] = {
            'status': redis_status,
            'response_time_ms': redis_response_time
        }
    
    # Overall response time
    health_status['response_time_ms'] = (time.time() - start_time) * 1000
    
    # Return appropriate HTTP status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


@require_http_methods(["GET"])
@never_cache
def readiness_check(request) -> JsonResponse:
    """
    Readiness check endpoint for Kubernetes/container orchestration.
    
    Returns:
        JsonResponse: Readiness status
    """
    try:
        # Check if database is ready
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check if cache is ready
        cache.set('readiness_check', 'ok', 5)
        cache.get('readiness_check')
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': timezone.now().isoformat()
        }, status=200)
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=503)


@require_http_methods(["GET"])
@never_cache
def liveness_check(request) -> JsonResponse:
    """
    Liveness check endpoint for Kubernetes/container orchestration.
    
    Returns:
        JsonResponse: Liveness status
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': timezone.now().isoformat(),
        'uptime': time.time() - getattr(settings, '_start_time', time.time())
    }, status=200)


@require_http_methods(["GET"])
def metrics_summary(request) -> JsonResponse:
    """
    Basic metrics summary endpoint.
    
    Returns:
        JsonResponse: Application metrics
    """
    try:
        # Database metrics
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
        
        # Cache metrics (if using Redis)
        cache_metrics = {}
        if 'redis' in settings.CACHES['default']['BACKEND'].lower():
            try:
                redis_client = cache.get_master_client()
                info = redis_client.info()
                cache_metrics = {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                }
            except Exception:
                pass
        
        return JsonResponse({
            'timestamp': timezone.now().isoformat(),
            'database': {
                'migration_count': migration_count,
                'engine': settings.DATABASES['default']['ENGINE']
            },
            'cache': cache_metrics,
            'settings': {
                'debug': settings.DEBUG,
                'timezone': str(settings.TIME_ZONE),
                'language': settings.LANGUAGE_CODE
            }
        })
        
    except Exception as e:
        logger.error(f"Metrics summary failed: {e}")
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
