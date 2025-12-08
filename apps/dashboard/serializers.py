from rest_framework import serializers
from .models import (
    PerformanceMetric, PageView, ErrorLog, UserSession,
    PerformanceReport, PerformanceAlert, AlertLog, DashboardWidget
)

class PageViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = PageView
        fields = [
            'id', 'page_url', 'page_title', 'load_time', 
            'user_agent', 'ip_address', 'session_id', 'user',
            'referrer', 'timestamp', 'is_mobile', 'browser', 'os'
        ]
        read_only_fields = ['user', 'ip_address', 'user_agent', 'session_id']

class ErrorLogSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = ErrorLog
        fields = [
            'id', 'error_type', 'error_message', 'page_url',
            'user_agent', 'ip_address', 'session_id', 'user',
            'timestamp', 'stack_trace', 'additional_data', 'resolved'
        ]
        read_only_fields = ['user', 'ip_address', 'user_agent', 'session_id']

class PerformanceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceAlert
        fields = '__all__'

class AlertLogSerializer(serializers.ModelSerializer):
    alert_type = serializers.CharField(source='alert.alert_type', read_only=True)
    severity = serializers.CharField(source='alert.severity', read_only=True)
    threshold = serializers.FloatField(source='alert.threshold_value', read_only=True)

    class Meta:
        model = AlertLog
        fields = [
            'id', 'alert', 'alert_type', 'severity', 'threshold',
            'triggered_at', 'current_value', 'message', 
            'is_resolved', 'resolved_at', 'resolved_by'
        ]
        read_only_fields = ['triggered_at', 'resolved_at', 'resolved_by']

class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = '__all__'

class PerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetric
        fields = '__all__'

class DashboardFilterSerializer(serializers.Serializer):
    type = serializers.CharField(default='page_load')
    days = serializers.IntegerField(default=7, min_value=1, max_value=365)
    date_range = serializers.CharField(required=False)
    device_type = serializers.CharField(required=False, allow_blank=True)
    browser = serializers.CharField(required=False, allow_blank=True)
    page_type = serializers.CharField(required=False, allow_blank=True)

class DashboardDataResponseSerializer(serializers.Serializer):
    """Serializer for main dashboard data response"""
    avg_load_time_today = serializers.FloatField()
    avg_load_time_week = serializers.FloatField()
    avg_load_time_month = serializers.FloatField()
    page_views_today = serializers.IntegerField()
    page_views_week = serializers.IntegerField()
    page_views_month = serializers.IntegerField()
    errors_today = serializers.IntegerField()
    error_rate = serializers.FloatField()
    active_alerts = serializers.IntegerField()
    recent_errors = ErrorLogSerializer(many=True)

class DashboardReportRequestSerializer(serializers.Serializer):
    """Serializer for generating reports"""
    type = serializers.ChoiceField(choices=['weekly', 'monthly', 'custom'], default='weekly')
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

class DashboardReportResponseSerializer(serializers.Serializer):
    """Serializer for report generation response"""
    success = serializers.BooleanField()
    report_id = serializers.IntegerField()
    data = serializers.DictField()

class ExportDataRequestSerializer(serializers.Serializer):
    """Serializer for export data parameters"""
    format = serializers.ChoiceField(choices=['csv', 'json'], default='csv')
    data_type = serializers.ChoiceField(choices=['page_views', 'errors', 'performance', 'analytics'], default='page_views')
    days = serializers.IntegerField(default=7, min_value=1, max_value=365)
