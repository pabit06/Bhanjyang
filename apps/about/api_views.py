from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.core.cache import cache
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)
from apps.about.services import AboutService
from apps.about.forms import ContactForm, NewsletterSignupForm
from .serializers import (
    CooperativeInfoSerializer, CooperativeTimelineSerializer,
    CooperativeStatisticSerializer,
    CooperativeAffiliationSerializer, LeadershipMessageSerializer,
    PersonSerializer, CommitteeSerializer, MembershipSerializer,
    StaffSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CooperativeInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for cooperative information"""
    serializer_class = CooperativeInfoSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['cooperative_name', 'description', 'mission', 'vision', 'values']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return CooperativeInfo.objects.active()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get cooperative statistics"""
        # Note: This technically belongs to CooperativeStatistic, but kept here for backward compatibility
        stats = CooperativeStatistic.objects.active().order_by('-created_at')
        serializer = CooperativeStatisticSerializer(stats, many=True)
        return Response(serializer.data)


class CooperativeTimelineViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for cooperative timeline events"""
    serializer_class = CooperativeTimelineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['event_date', 'created_at', 'order']
    ordering = ['-event_date']

    def get_queryset(self):
        return CooperativeTimeline.objects.active()

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured timeline events"""
        featured_events = self.get_queryset().filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent timeline events"""
        recent_events = self.get_queryset().order_by('-event_date')[:10]
        serializer = self.get_serializer(recent_events, many=True)
        return Response(serializer.data)


class CooperativeAffiliationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for cooperative affiliations"""
    serializer_class = CooperativeAffiliationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'order']
    ordering = ['order']

    def get_queryset(self):
        return CooperativeAffiliation.objects.active()

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured affiliations"""
        featured_affiliations = self.get_queryset().filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_affiliations, many=True)
        return Response(serializer.data)


class LeadershipMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for leadership messages"""
    serializer_class = LeadershipMessageSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'author_name', 'author_position']
    ordering_fields = ['created_at', 'order']
    ordering = ['-created_at']

    def get_queryset(self):
        return LeadershipMessage.objects.active()

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured leadership messages"""
        featured_messages = self.get_queryset().filter(is_featured=True)[:3]
        serializer = self.get_serializer(featured_messages, many=True)
        return Response(serializer.data)


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for team members"""
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'bio', 'position_general']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['full_name']

    def get_queryset(self):
        return Person.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def current_team(self, request):
        """Get current team members"""
        current_members = self.get_queryset().filter(
            memberships__is_active=True,
            memberships__end_date__isnull=True
        ).distinct()
        serializer = self.get_serializer(current_members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past_team(self, request):
        """Get past team members"""
        past_members = self.get_queryset().filter(
            memberships__is_active=True,
            memberships__end_date__isnull=False
        ).distinct()
        serializer = self.get_serializer(past_members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_position(self, request):
        """Get team members by position"""
        position = request.query_params.get('position')
        if position:
            members = self.get_queryset().filter(position_general__icontains=position)
            serializer = self.get_serializer(members, many=True)
            return Response(serializer.data)
        return Response({'error': 'Position parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for committees"""
    serializer_class = CommitteeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'order']
    ordering = ['order']

    def get_queryset(self):
        return Committee.objects.filter(is_active=True)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get committee members"""
        committee = self.get_object()
        members = committee.memberships.filter(is_active=True)
        serializer = MembershipSerializer(members, many=True)
        return Response(serializer.data)


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for staff members"""
    serializer_class = StaffSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['person__full_name', 'position', 'department']
    ordering_fields = ['created_at', 'person__full_name']
    ordering = ['person__full_name']

    def get_queryset(self):
        return Staff.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get staff by department"""
        department = request.query_params.get('department')
        if department:
            staff = self.get_queryset().filter(department__icontains=department)
            serializer = self.get_serializer(staff, many=True)
            return Response(serializer.data)
        return Response({'error': 'Department parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class SearchAPIView(APIView):
    """Global search API endpoint"""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check cache first
        cache_key = f'search_api_{query}'
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(cached_results)

        # Use service to get search results
        results = AboutService.get_search_results(query)
        
        # Serialize results
        serialized_results = {
            'query': results['query'],
            'cooperative_info': CooperativeInfoSerializer(results['cooperative_info'], many=True).data,
            'timeline': CooperativeTimelineSerializer(results['timeline'], many=True).data,
            'affiliations': CooperativeAffiliationSerializer(results['affiliations'], many=True).data,
            'leadership': LeadershipMessageSerializer(results['leadership'], many=True).data,
            'team': PersonSerializer(results['team'], many=True).data
        }

        # Cache results for 5 minutes
        cache.set(cache_key, serialized_results, 300)

        return Response(serialized_results)


class StatisticsAPIView(APIView):
    """API endpoint for site statistics"""
    permission_classes = [AllowAny]

    def get(self, request):
        # Check cache first
        cache_key = 'site_statistics'
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response(cached_stats)

        # Use service to get statistics
        stats = AboutService.get_site_statistics()

        # Cache for 1 hour
        cache.set(cache_key, stats, 3600)

        return Response(stats)


class ContactAPIView(APIView):
    """API endpoint for contact form submissions"""
    permission_classes = [AllowAny]

    def post(self, request):
        form = ContactForm(request.data)
        if form.is_valid():
            try:
                # Use AboutService to handle logic and email sending
                success = AboutService.send_contact_emails(form.cleaned_data)
                
                if success:
                    response_data = {
                        'success': True,
                        'message': 'Thank you for your message. We will get back to you soon.',
                        'submission_id': f'contact_{timezone.now().timestamp()}'
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                     return Response({
                        'success': False,
                        'message': 'Failed to send contact email.',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'An error occurred while processing your request.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'success': False,
                'message': 'Invalid data provided.',
                'errors': form.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class NewsletterAPIView(APIView):
    """API endpoint for newsletter subscriptions"""
    permission_classes = [AllowAny]

    def post(self, request):
        form = NewsletterSignupForm(request.data)
        if form.is_valid():
            try:
                # Use AboutService to handle logic and email sending
                success = AboutService.send_newsletter_welcome_email(form.cleaned_data)
                
                if success:
                    response_data = {
                        'success': True,
                        'message': 'Thank you for subscribing to our newsletter!',
                        'subscriber_id': f'newsletter_{timezone.now().timestamp()}'
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                     return Response({
                        'success': False,
                        'message': 'Failed to process newsletter subscription.',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'An error occurred while processing your subscription.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'success': False,
                'message': 'Invalid data provided.',
                'errors': form.errors
            }, status=status.HTTP_400_BAD_REQUEST)
