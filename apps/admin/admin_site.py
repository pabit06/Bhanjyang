from django.contrib.admin import AdminSite
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Avg
from apps.dashboard.models import PageView, ErrorLog, UserSession
from apps.downloads.models import DownloadableFile
from apps.news_events.models import NewsArticle
from apps.about.models import Person, Staff
from apps.services.models import SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief
from apps.home.models import HomePageContent, Testimonial, Statistic, Announcement
from apps.home.services import HomeService
from django.utils import timezone
from datetime import timedelta

class BhanjyangAdminSite(AdminSite):
    """Custom admin site with enhanced dashboard"""
    
    site_header = "Bhanjyang Cooperative Admin"
    site_title = "Bhanjyang Admin"
    index_title = "Dashboard"
    
    # Use custom templates - these will be found in apps/admin/templates/admin/
    index_template = 'admin/index.html'
    login_template = 'admin/login.html'
    app_index_template = 'admin/app_index.html'
    
    def each_context(self, request):
        """Add custom context to all admin pages"""
        context = super().each_context(request)
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        return context
    
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
        
        # Home app content status stats
        try:
            home_content_stats = HomeService.get_content_stats()
            content_stats['home_content_stats'] = home_content_stats
            
            # Calculate totals
            total_published = (
                home_content_stats['homepage_content']['published'] +
                home_content_stats['testimonials']['published'] +
                home_content_stats['statistics']['published'] +
                home_content_stats['announcements']['published']
            )
            total_draft = (
                home_content_stats['homepage_content']['draft'] +
                home_content_stats['testimonials']['draft'] +
                home_content_stats['statistics']['draft'] +
                home_content_stats['announcements']['draft']
            )
            total_scheduled = (
                home_content_stats['homepage_content']['scheduled'] +
                home_content_stats['testimonials']['scheduled'] +
                home_content_stats['statistics']['scheduled'] +
                home_content_stats['announcements']['scheduled']
            )
            
            content_stats['home_total_published'] = total_published
            content_stats['home_total_draft'] = total_draft
            content_stats['home_total_scheduled'] = total_scheduled
        except Exception as e:
            # If home app not available, skip
            pass
        
        extra_context.update({
            'dashboard_stats': dashboard_stats,
            **content_stats
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = BhanjyangAdminSite(name='bhanjyang_admin')

# Register gallery models with custom admin site
# This will be called after all apps are loaded to avoid import errors
def register_gallery_models():
    """Register gallery models with the custom admin site"""
    try:
        from apps.gallery.models import GalleryImage, GalleryAlbum, SmartCollection, SmartCollectionImage, AutoCategorizationRule, ImageAnalysisJob
        from apps.gallery.admin import (
            GalleryImageAdmin, GalleryAlbumAdmin,
            SmartCollectionAdmin, SmartCollectionImageAdmin,
            AutoCategorizationRuleAdmin, ImageAnalysisJobAdmin
        )
        
        # Unregister from default admin site if already registered
        from django.contrib import admin
        for model in [GalleryImage, GalleryAlbum, SmartCollection, SmartCollectionImage, AutoCategorizationRule, ImageAnalysisJob]:
            if model in admin.site._registry:
                admin.site.unregister(model)
        
        # Register with custom admin site
        admin_site.register(GalleryImage, GalleryImageAdmin)
        admin_site.register(GalleryAlbum, GalleryAlbumAdmin)
        admin_site.register(SmartCollection, SmartCollectionAdmin)
        admin_site.register(SmartCollectionImage, SmartCollectionImageAdmin)
        admin_site.register(AutoCategorizationRule, AutoCategorizationRuleAdmin)
        admin_site.register(ImageAnalysisJob, ImageAnalysisJobAdmin)
        
        # Register tracking models
        from apps.gallery.admin import (
            GalleryImageLikeAdmin, GalleryImageCommentAdmin,
            GalleryImageShareAdmin, GalleryImageDownloadAdmin
        )
        from apps.gallery.models import GalleryImageLike, GalleryImageComment, GalleryImageShare, GalleryImageDownload
        
        # Unregister from default admin if needed
        for model in [GalleryImageLike, GalleryImageComment, GalleryImageShare, GalleryImageDownload]:
            if model in admin.site._registry:
                admin.site.unregister(model)
        
        admin_site.register(GalleryImageLike, GalleryImageLikeAdmin)
        admin_site.register(GalleryImageComment, GalleryImageCommentAdmin)
        admin_site.register(GalleryImageShare, GalleryImageShareAdmin)
        admin_site.register(GalleryImageDownload, GalleryImageDownloadAdmin)
        
    except ImportError as e:
        # Gallery app not available or not yet loaded
        pass

