from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
import json
import uuid


class UserSession(models.Model):
    """Track user sessions"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='about_user_sessions')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Session {self.session_id} - {self.user or 'Anonymous'}"


class PageView(models.Model):
    """Track individual page views"""
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='view_logs')
    url = models.URLField()
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    referrer = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)
    scroll_depth = models.FloatField(default=0.0)  # Percentage of page scrolled
    exit_page = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.path} - {self.timestamp}"


class UserEvent(models.Model):
    """Track user events and interactions"""
    EVENT_TYPES = [
        ('click', 'Click'),
        ('scroll', 'Scroll'),
        ('form_submit', 'Form Submit'),
        ('download', 'Download'),
        ('search', 'Search'),
        ('video_play', 'Video Play'),
        ('video_pause', 'Video Pause'),
        ('video_complete', 'Video Complete'),
        ('gallery_view', 'Gallery View'),
        ('map_interaction', 'Map Interaction'),
        ('dark_mode_toggle', 'Dark Mode Toggle'),
        ('pwa_install', 'PWA Install'),
        ('newsletter_signup', 'Newsletter Signup'),
        ('contact_form', 'Contact Form'),
        ('feedback', 'Feedback'),
    ]
    
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    element_id = models.CharField(max_length=100, blank=True)
    element_class = models.CharField(max_length=100, blank=True)
    element_text = models.TextField(blank=True)
    url = models.URLField()
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"


class UserDevice(models.Model):
    """Track user device information"""
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='devices')
    device_type = models.CharField(max_length=50)  # desktop, mobile, tablet
    browser = models.CharField(max_length=100)
    browser_version = models.CharField(max_length=50)
    operating_system = models.CharField(max_length=100)
    screen_resolution = models.CharField(max_length=20)
    viewport_size = models.CharField(max_length=20)
    is_mobile = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_desktop = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.device_type} - {self.browser}"


class UserLocation(models.Model):
    """Track user location (country/city level)"""
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='locations')
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.city}, {self.country}"


class AnalyticsSummary(models.Model):
    """Daily analytics summaries"""
    date = models.DateField(unique=True)
    total_sessions = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    total_page_views = models.PositiveIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    bounce_rate = models.FloatField(default=0.0)
    top_pages = models.JSONField(default=list)
    top_referrers = models.JSONField(default=list)
    device_breakdown = models.JSONField(default=dict)
    browser_breakdown = models.JSONField(default=dict)
    country_breakdown = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics Summary - {self.date}"


class AnalyticsTracker:
    """Main analytics tracking class"""
    
    def __init__(self, request):
        self.request = request
        self.session_id = self.get_or_create_session()
    
    def get_or_create_session(self):
        """Get or create user session"""
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        
        # Try to get existing session
        try:
            session = UserSession.objects.get(session_id=session_key)
            return session
        except UserSession.DoesNotExist:
            pass
        
        # Create new session
        session = UserSession.objects.create(
            session_id=session_key,
            user=self.request.user if self.request.user.is_authenticated else None,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            referrer=self.request.META.get('HTTP_REFERER', ''),
        )
        
        return session
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def track_page_view(self, url, title='', duration=None, scroll_depth=0.0, exit_page=False):
        """Track a page view"""
        PageView.objects.create(
            session=self.session_id,
            url=url,
            path=self.request.path,
            title=title,
            referrer=self.request.META.get('HTTP_REFERER', ''),
            duration=duration,
            scroll_depth=scroll_depth,
            exit_page=exit_page,
        )
        
        # Update session page view count
        self.session_id.page_views += 1
        self.session_id.save()
    
    def track_event(self, event_type, element_id='', element_class='', element_text='', metadata=None):
        """Track a user event"""
        UserEvent.objects.create(
            session=self.session_id,
            event_type=event_type,
            element_id=element_id,
            element_class=element_class,
            element_text=element_text,
            url=self.request.build_absolute_uri(),
            metadata=metadata or {},
        )
    
    def track_device_info(self, device_data):
        """Track device information"""
        UserDevice.objects.update_or_create(
            session=self.session_id,
            defaults=device_data
        )
    
    def track_location(self, location_data):
        """Track location information"""
        UserLocation.objects.update_or_create(
            session=self.session_id,
            defaults=location_data
        )
    
    def end_session(self):
        """End the current session"""
        self.session_id.end_time = timezone.now()
        self.session_id.duration = self.session_id.end_time - self.session_id.start_time
        self.session_id.is_active = False
        self.session_id.save()


class AnalyticsMiddleware:
    """Middleware to automatically track analytics"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip tracking for admin, static files, etc.
        if self.should_skip_tracking(request):
            return self.get_response(request)
        
        # Initialize analytics tracker
        tracker = AnalyticsTracker(request)
        
        # Track page view
        tracker.track_page_view(
            url=request.build_absolute_uri(),
            title=getattr(request, 'page_title', ''),
        )
        
        # Add tracker to request for use in views
        request.analytics = tracker
        
        response = self.get_response(request)
        
        return response
    
    def should_skip_tracking(self, request):
        """Determine if tracking should be skipped"""
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
        ]
        
        path = request.path
        return any(path.startswith(skip_path) for skip_path in skip_paths)


class AnalyticsAPI:
    """API for analytics data"""
    
    @staticmethod
    def get_session_stats(days=30):
        """Get session statistics"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        sessions = UserSession.objects.filter(
            start_time__date__range=[start_date, end_date]
        )
        
        return {
            'total_sessions': sessions.count(),
            'unique_users': sessions.values('user').distinct().count(),
            'average_duration': sessions.aggregate(
                avg_duration=models.Avg('duration')
            )['avg_duration'],
            'total_page_views': sessions.aggregate(
                total_views=models.Sum('page_views')
            )['total_views'],
        }
    
    @staticmethod
    def get_top_pages(days=30, limit=10):
        """Get top pages"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        return PageView.objects.filter(
            timestamp__date__range=[start_date, end_date]
        ).values('path').annotate(
            views=models.Count('id')
        ).order_by('-views')[:limit]
    
    @staticmethod
    def get_device_breakdown(days=30):
        """Get device breakdown"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        sessions = UserSession.objects.filter(
            start_time__date__range=[start_date, end_date]
        )
        
        devices = UserDevice.objects.filter(session__in=sessions)
        
        return {
            'desktop': devices.filter(is_desktop=True).count(),
            'mobile': devices.filter(is_mobile=True).count(),
            'tablet': devices.filter(is_tablet=True).count(),
        }
    
    @staticmethod
    def get_browser_breakdown(days=30):
        """Get browser breakdown"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        sessions = UserSession.objects.filter(
            start_time__date__range=[start_date, end_date]
        )
        
        devices = UserDevice.objects.filter(session__in=sessions)
        
        return devices.values('browser').annotate(
            count=models.Count('id')
        ).order_by('-count')
    
    @staticmethod
    def get_country_breakdown(days=30):
        """Get country breakdown"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        sessions = UserSession.objects.filter(
            start_time__date__range=[start_date, end_date]
        )
        
        locations = UserLocation.objects.filter(session__in=sessions)
        
        return locations.values('country').annotate(
            count=models.Count('id')
        ).order_by('-count')
    
    @staticmethod
    def get_event_stats(days=30):
        """Get event statistics"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        events = UserEvent.objects.filter(
            timestamp__date__range=[start_date, end_date]
        )
        
        return events.values('event_type').annotate(
            count=models.Count('id')
        ).order_by('-count')
    
    @staticmethod
    def generate_daily_summary(date=None):
        """Generate daily analytics summary"""
        from django.utils import timezone
        from datetime import timedelta
        
        if date is None:
            date = timezone.now().date()
        
        # Get sessions for the date
        sessions = UserSession.objects.filter(
            start_time__date=date
        )
        
        # Calculate metrics
        total_sessions = sessions.count()
        unique_visitors = sessions.values('user').distinct().count()
        total_page_views = sessions.aggregate(
            total=models.Sum('page_views')
        )['total'] or 0
        
        average_duration = sessions.aggregate(
            avg=models.Avg('duration')
        )['avg']
        
        # Calculate bounce rate (sessions with only 1 page view)
        bounce_sessions = sessions.filter(page_views=1).count()
        bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get top pages
        top_pages = PageView.objects.filter(
            timestamp__date=date
        ).values('path').annotate(
            views=models.Count('id')
        ).order_by('-views')[:10]
        
        # Get top referrers
        top_referrers = sessions.exclude(
            referrer__isnull=True
        ).values('referrer').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
        
        # Get device breakdown
        device_breakdown = AnalyticsAPI.get_device_breakdown(1)
        
        # Get browser breakdown
        browser_breakdown = list(AnalyticsAPI.get_browser_breakdown(1))
        
        # Get country breakdown
        country_breakdown = list(AnalyticsAPI.get_country_breakdown(1))
        
        # Create or update summary
        summary, created = AnalyticsSummary.objects.update_or_create(
            date=date,
            defaults={
                'total_sessions': total_sessions,
                'unique_visitors': unique_visitors,
                'total_page_views': total_page_views,
                'average_session_duration': average_duration,
                'bounce_rate': bounce_rate,
                'top_pages': list(top_pages),
                'top_referrers': list(top_referrers),
                'device_breakdown': device_breakdown,
                'browser_breakdown': browser_breakdown,
                'country_breakdown': country_breakdown,
            }
        )
        
        return summary
