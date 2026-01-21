# apps/downloads/context_processors.py

def admin_stats(request):
    """Add statistics to admin context."""
    if not request.path.startswith('/admin/'):
        return {}

    try:
        from .models import DownloadableFile
        downloads_count = DownloadableFile.objects.count()
    except (ImportError, Exception) as e:
        # Log error but don't crash
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error getting downloads count: {e}")
        downloads_count = 0

    try:
        from apps.news_events.models import NewsArticle
        updates_count = NewsArticle.objects.filter(status='PB').count()
    except (ImportError, Exception) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error getting news count: {e}")
        updates_count = 0

    try:
        from apps.team.models import Person, Staff
        team_count = Person.objects.count() + Staff.objects.count()
    except (ImportError, Exception) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error getting team count: {e}")
        team_count = 0

    try:
        from apps.services.models import ServiceCategory
        services_count = ServiceCategory.objects.count()
    except (ImportError, Exception) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error getting services count: {e}")
        services_count = 0

    return {
        'downloads_count': downloads_count,
        'updates_count': updates_count,
        'team_count': team_count,
        'services_count': services_count,
    }
