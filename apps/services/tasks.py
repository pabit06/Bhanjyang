"""
Background tasks for the Services app.

This module contains task functions for exchange rate fetching and other background operations.
These can be used with Celery when installed, or run synchronously.
"""
import logging
from datetime import timedelta

from django.utils import timezone

from .services import ExchangeRateService

logger = logging.getLogger(__name__)

# Celery configuration - check if Celery is available
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a no-op decorator when Celery is not available
    def shared_task(*args, **kwargs):
        """No-op decorator when Celery is not installed"""
        def decorator(func):
            return func
        return decorator


@shared_task(name='services.fetch_nrb_exchange_rates', max_retries=3)
def fetch_nrb_exchange_rates_task(date=None):
    """
    Celery task to fetch exchange rates from NRB API.
    
    This task can be scheduled to run periodically (e.g., daily) to automatically
    update exchange rates from Nepal Rastra Bank.
    
    Args:
        date: Optional date to fetch rates for. If None, fetches today's rates.
        
    Returns:
        int: Number of rates fetched and saved
    """
    try:
        if date is None:
            date = timezone.now().date()
        
        logger.info(f"Starting automatic NRB exchange rate fetch for {date}")
        count = ExchangeRateService.fetch_nrb_rates(date)
        
        if count > 0:
            logger.info(f"Successfully fetched {count} exchange rates from NRB for {date}")
        else:
            logger.warning(f"No exchange rates fetched from NRB for {date}")
        
        return count
        
    except Exception as e:
        logger.error(f"Error in fetch_nrb_exchange_rates_task: {str(e)}", exc_info=True)
        # Retry the task
        raise fetch_nrb_exchange_rates_task.retry(exc=e, countdown=300)  # Retry after 5 minutes


@shared_task(name='services.fetch_nrb_exchange_rates_daily')
def fetch_nrb_exchange_rates_daily():
    """
    Daily task to fetch today's exchange rates from NRB.
    
    This should be scheduled to run once per day (e.g., at 6 AM Nepal time)
    to fetch the latest exchange rates.
    """
    return fetch_nrb_exchange_rates_task.delay()

