from django.contrib.admin import AdminSite
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Avg
from apps.dashboard.models import PageView, ErrorLog, UserSession
from apps.downloads.models import DownloadableFile
from apps.news_events.models import NewsArticle
from apps.about.models import Person, Staff
from apps.services.models import SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief
from django.utils import timezone
from datetime import timedelta

class BhanjyangAdminSite(AdminSite):
    """Custom admin site with enhanced dashboard"""
    
    site_header = "Bhanjyang Cooperative Admin"
    site_title = "Bhanjyang Admin"
    index_title = "Dashboard"
    
    def index(self, request, extra_context=None):
        """Custom admin index with dashboard stats"""
        extra_context = extra_context or {}
        
        # Get dashboard stats
        today = timezone.now().date()
        week_ago = timezone.now() - timedelta(days=7)
        
        # Dashboard performance stats
        dashboard_stats = {
            'page_views_today': PageView.objects.filter(timestamp__date=today).count(),
            'avg_load_time': PageView.objects.filter(timestamp__date=today).aggregate(
                avg=Avg('load_time')
            )['avg'] or 0,
            'errors_today': ErrorLog.objects.filter(timestamp__date=today).count(),
            'active_sessions': UserSession.objects.filter(
                start_time__gte=week_ago,
                end_time__isnull=True
            ).count(),
        }
        
        # Content stats
        content_stats = {
            'downloads_count': DownloadableFile.objects.filter(is_active=True).count(),
            'updates_count': NewsArticle.objects.filter(status='PB').count(),  # PB = Published
            'team_count': Person.objects.count() + Staff.objects.count(),
            'services_count': (
                SavingsAccount.objects.filter(is_active=True).count() +
                FixedDeposit.objects.filter(is_active=True).count() +
                LoanType.objects.filter(is_active=True).count() +
                RemittanceService.objects.filter(is_active=True).count() +
                MemberRelief.objects.filter(is_active=True).count()
            ),
        }
        
        extra_context.update({
            'dashboard_stats': dashboard_stats,
            **content_stats
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = BhanjyangAdminSite(name='bhanjyang_admin')
