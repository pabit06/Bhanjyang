# apps/downloads/context_processors.py

def admin_stats(request):
    """Add statistics to admin context."""
    if not request.path.startswith('/admin/'):
        return {}

    try:
        from .models import DownloadableFile
        downloads_count = DownloadableFile.objects.count()
    except Exception:
        downloads_count = 0

    try:
        from apps.news_events.models import NewsArticle
        updates_count = NewsArticle.objects.filter(status='PB').count()
    except Exception:
        updates_count = 0

    try:
        from apps.team.models import Person, Staff
        team_count = Person.objects.count() + Staff.objects.count()
    except Exception:
        team_count = 0

    try:
        from apps.services.models import ServiceCategory
        services_count = ServiceCategory.objects.count()
    except Exception:
        services_count = 0

    return {
        'downloads_count': downloads_count,
        'updates_count': updates_count,
        'team_count': team_count,
        'services_count': services_count,
    }
