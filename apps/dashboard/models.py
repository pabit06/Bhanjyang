from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json

class PerformanceMetric(models.Model):
    """Model to store performance metrics"""
    
    METRIC_TYPES = [
        ('page_load', 'Page Load Time'),
        ('image_load', 'Image Load Time'),
        ('search_time', 'Search Response Time'),
        ('form_submit', 'Form Submission Time'),
        ('api_response', 'API Response Time'),
        ('database_query', 'Database Query Time'),
        ('memory_usage', 'Memory Usage'),
        ('cpu_usage', 'CPU Usage'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    page_url = models.URLField(max_length=500, blank=True, null=True)
    value = models.FloatField(help_text="Metric value (e.g., milliseconds, bytes)")
    unit = models.CharField(max_length=20, default='ms', help_text="Unit of measurement")
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['page_url', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_type}: {self.value}{self.unit} at {self.timestamp}"

class PageView(models.Model):
    """Model to track page views and performance"""
    
    page_url = models.URLField(max_length=500)
    page_title = models.CharField(max_length=200, blank=True)
    load_time = models.FloatField(help_text="Page load time in milliseconds")
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    referrer = models.URLField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_mobile = models.BooleanField(default=False)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['page_url', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_mobile']),
        ]
    
    def __str__(self):
        return f"{self.page_title} - {self.load_time}ms"

class ErrorLog(models.Model):
    """Model to track errors and exceptions"""
    
    ERROR_TYPES = [
        ('404', 'Page Not Found'),
        ('500', 'Server Error'),
        ('template', 'Template Error'),
        ('database', 'Database Error'),
        ('validation', 'Validation Error'),
        ('permission', 'Permission Error'),
        ('timeout', 'Timeout Error'),
    ]
    
    error_type = models.CharField(max_length=20, choices=ERROR_TYPES)
    error_message = models.TextField()
    page_url = models.URLField(max_length=500, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    stack_trace = models.TextField(blank=True, null=True)
    additional_data = models.JSONField(default=dict, blank=True)
    resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['error_type', 'timestamp']),
            models.Index(fields=['resolved', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.error_type}: {self.error_message[:50]}..."

class UserSession(models.Model):
    """Model to track user sessions and behavior"""
    
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)
    total_load_time = models.FloatField(default=0)
    is_mobile = models.BooleanField(default=False)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['start_time']),
            models.Index(fields=['user', 'start_time']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.page_views} views"

class PerformanceReport(models.Model):
    """Model to store generated performance reports"""
    
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('custom', 'Custom Report'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    generated_at = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    report_data = models.JSONField()
    summary = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_type} Report - {self.start_date.date()} to {self.end_date.date()}"

class PerformanceAlert(models.Model):
    """Model to store performance alerts and thresholds"""
    
    ALERT_TYPES = [
        ('load_time', 'Load Time Alert'),
        ('error_rate', 'Error Rate Alert'),
        ('traffic_spike', 'Traffic Spike Alert'),
        ('memory_usage', 'Memory Usage Alert'),
        ('cpu_usage', 'CPU Usage Alert'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold_value = models.FloatField(help_text="Threshold value for triggering alert")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, help_text="Description of the alert")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} Alert - {self.threshold_value} ({self.severity})"
    
    def check_threshold(self, current_value):
        """Check if current value exceeds threshold"""
        return current_value > self.threshold_value

class AlertLog(models.Model):
    """Model to log triggered alerts"""
    
    alert = models.ForeignKey(PerformanceAlert, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True)
    current_value = models.FloatField()
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    
    class Meta:
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"Alert {self.alert.alert_type} - {self.triggered_at}"

class DashboardWidget(models.Model):
    """Model to store dashboard widget configurations"""
    
    WIDGET_TYPES = [
        ('metric_card', 'Metric Card'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('gauge', 'Gauge'),
        ('map', 'Map'),
    ]
    
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    config = models.JSONField(default=dict, help_text="Widget configuration")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.name} ({self.widget_type})"

class UserDashboardPreference(models.Model):
    """Model to store user-specific dashboard preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ])
    refresh_interval = models.IntegerField(default=30, help_text="Refresh interval in seconds")
    widgets = models.ManyToManyField(DashboardWidget, blank=True)
    layout_config = models.JSONField(default=dict, help_text="Dashboard layout configuration")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Dashboard Preferences"

class AuditLog(models.Model):
    """Model to store audit logs for security monitoring"""
    
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('dashboard_access', 'Dashboard Access'),
        ('data_export', 'Data Export'),
        ('alert_resolve', 'Alert Resolution'),
        ('preference_update', 'Preference Update'),
        ('admin_access', 'Admin Access'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.user.username if self.user else 'Anonymous'} - {self.timestamp}"