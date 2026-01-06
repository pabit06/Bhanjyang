"""
Contact App DRF ViewSets

REST API views for Contact app.

Author: Bhanjyang Tech Team
Created: 2026-01-06
"""

from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Count, Q

from .models import ContactSubmission, PrivacyPolicy
from apps.about.models import Staff
from .serializers import (
    ContactSubmissionSerializer,
    ContactSubmissionCreateSerializer,
    InformationOfficerSerializer,
    PrivacyPolicySerializer,
    ContactStatsSerializer
)
from .services import ContactService
import logging

logger = logging.getLogger(__name__)


class ContactViewSet(viewsets.GenericViewSet):
    """
    ViewSet for contact operations.
    
    Endpoints:
    - POST /api/v1/contact/submit/
    - GET /api/v1/contact/officer/
    - GET /api/v1/contact/privacy/
    - GET /api/v1/contact/stats/ (admin only)
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def submit(self, request):
        """
        Submit contact form via API.
        
        **Endpoint:** POST /api/v1/contact/submit/
        """
        serializer = ContactSubmissionCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Process through ContactService
                result = ContactService.process_submission(
                    form_data=serializer.validated_data,
                    request=request
                )
                
                if result.get('success'):
                    logger.info(
                        f"API contact submission successful: "
                        f"ID {result.get('submission_id')} from {request.META.get('REMOTE_ADDR')}"
                    )
                    return Response({
                        'success': True,
                        'message': result.get('message', 'Submission received successfully'),
                        'submission_id': result.get('submission_id')
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'success': False,
                        'errors': {'__all__': [result.get('message', 'Submission failed')]}
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"API contact submission error: {str(e)}")
                return Response({
                    'success': False,
                    'errors': {'__all__': ['An error occurred. Please try again.']}
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def officer(self, request):
        """
        Get current RTI officer information.
        
        **Endpoint:** GET /api/v1/contact/officer/
        """
        try:
            # Query Staff model for information officer
            officer = Staff.objects.filter(is_information_officer=True, is_active=True).first()
            
            if not officer:
                return Response({
                    'message': 'No active RTI officer found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = InformationOfficerSerializer(
                officer,
                context={'request': request}
            )
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching RTI officer: {str(e)}")
            return Response({
                'error': 'Failed to fetch officer information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def privacy(self, request):
        """
        Get current privacy policy.
        
        **Endpoint:** GET /api/v1/contact/privacy/
        """
        try:
            policy = PrivacyPolicy.objects.filter(is_active=True).first()
            
            if not policy:
                return Response({
                    'message': 'No active privacy policy found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PrivacyPolicySerializer(policy)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching privacy policy: {str(e)}")
            return Response({
                'error': 'Failed to fetch privacy policy'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """
        Get contact submission statistics (Admin only).
        
        **Endpoint:** GET /api/v1/contact/stats/
        """
        try:
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = now - timedelta(days=7)
            month_start = now - timedelta(days=30)
            
            stats = {
                'total_submissions': ContactSubmission.objects.count(),
                'pending_count': ContactSubmission.objects.filter(status='pending').count(),
                'replied_count': ContactSubmission.objects.filter(status='replied').count(),
                'spam_count': ContactSubmission.objects.filter(status='spam').count(),
                'today_count': ContactSubmission.objects.filter(
                    submitted_at__gte=today_start
                ).count(),
                'this_week_count': ContactSubmission.objects.filter(
                    submitted_at__gte=week_start
                ).count(),
                'this_month_count': ContactSubmission.objects.filter(
                    submitted_at__gte=month_start
                ).count()
            }
            
            serializer = ContactStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching contact stats: {str(e)}")
            return Response({
                'error': 'Failed to fetch statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
