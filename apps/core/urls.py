"""
URL configuration for core app health endpoints.
"""
from django.urls import path
from .health_views import health_check, readiness_check, liveness_check, metrics_summary

app_name = 'core'

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('readiness/', readiness_check, name='readiness_check'),
    path('liveness/', liveness_check, name='liveness_check'),
    path('metrics/', metrics_summary, name='metrics_summary'),
]
