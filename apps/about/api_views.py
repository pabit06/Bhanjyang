from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.core.cache import cache
from django.utils import timezone
import json

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)
from .serializers import (
    CooperativeInfoSerializer, CooperativeTimelineSerializer,
    CooperativeAchievementSerializer, CooperativeStatisticSerializer,
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
    queryset = CooperativeInfo.objects.filter(is_active=True)
    serializer_class = CooperativeInfoSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['cooperative_name', 'description', 'mission', 'vision', 'values']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured cooperative information"""
        featured_info = self.queryset.filter(is_featured=True).first()
        if featured_info:
            serializer = self.get_serializer(featured_info)
            return Response(serializer.data)
        return Response({'message': 'No featured information available'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get cooperative statistics"""
        stats = CooperativeStatistic.objects.filter(is_active=True).order_by('-created_at')
        serializer = CooperativeStatisticSerializer(stats, many=True)
        return Response(serializer.data)


class CooperativeTimelineViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for cooperative timeline events"""
    queryset = CooperativeTimeline.objects.filter(is_active=True)
    serializer_class = CooperativeTimelineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['event_date', 'created_at', 'order']
    ordering = ['-event_date']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured timeline events"""
        featured_events = self.queryset.filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent timeline events"""
        recent_events = self.queryset.order_by('-event_date')[:10]
        serializer = self.get_serializer(recent_events, many=True)
        return Response(serializer.data)


class CooperativeAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for cooperative achievements"""
    queryset = CooperativeAchievement.objects.filter(is_active=True)
    serializer_class = CooperativeAchievementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['achievement_type', 'is_featured']
    search_fields = ['title', 'description', 'awarding_organization']
    ordering_fields = ['received_date', 'created_at', 'order']
    ordering = ['-received_date']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured achievements"""
        featured_achievements = self.queryset.filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_achievements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get achievements by type"""
        achievement_type = request.query_params.get('type')
        if achievement_type:
            achievements = self.queryset.filter(achievement_type=achievement_type)
            serializer = self.get_serializer(achievements, many=True)
            return Response(serializer.data)
        return Response({'error': 'Type parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class CooperativeAffiliationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for cooperative affiliations"""
    queryset = CooperativeAffiliation.objects.filter(is_active=True)
    serializer_class = CooperativeAffiliationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'order']
    ordering = ['order']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured affiliations"""
        featured_affiliations = self.queryset.filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_affiliations, many=True)
        return Response(serializer.data)


class LeadershipMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for leadership messages"""
    queryset = LeadershipMessage.objects.filter(is_active=True)
    serializer_class = LeadershipMessageSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'author_name', 'author_position']
    ordering_fields = ['created_at', 'order']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured leadership messages"""
        featured_messages = self.queryset.filter(is_featured=True)[:3]
        serializer = self.get_serializer(featured_messages, many=True)
        return Response(serializer.data)


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for team members"""
    queryset = Person.objects.filter(is_active=True)
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'bio', 'position_general']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['full_name']

    @action(detail=False, methods=['get'])
    def current_team(self, request):
        """Get current team members"""
        current_members = self.queryset.filter(
            memberships__is_active=True,
            memberships__end_date__isnull=True
        ).distinct()
        serializer = self.get_serializer(current_members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past_team(self, request):
        """Get past team members"""
        past_members = self.queryset.filter(
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
            members = self.queryset.filter(position_general__icontains=position)
            serializer = self.get_serializer(members, many=True)
            return Response(serializer.data)
        return Response({'error': 'Position parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for committees"""
    queryset = Committee.objects.filter(is_active=True)
    serializer_class = CommitteeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'order']
    ordering = ['order']

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get committee members"""
        committee = self.get_object()
        members = committee.memberships.filter(is_active=True)
        serializer = MembershipSerializer(members, many=True)
        return Response(serializer.data)


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for staff members"""
    queryset = Staff.objects.filter(is_active=True)
    serializer_class = StaffSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['person__full_name', 'position', 'department']
    ordering_fields = ['created_at', 'person__full_name']
    ordering = ['person__full_name']

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get staff by department"""
        department = request.query_params.get('department')
        if department:
            staff = self.queryset.filter(department__icontains=department)
            serializer = self.get_serializer(staff, many=True)
            return Response(serializer.data)
        return Response({'error': 'Department parameter required'}, status=status.HTTP_400_BAD_REQUEST)


# Additional API Views
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


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

        results = {
            'query': query,
            'cooperative_info': [],
            'timeline': [],
            'achievements': [],
            'affiliations': [],
            'leadership': [],
            'team': []
        }

        # Search cooperative info
        cooperative_info = CooperativeInfo.objects.filter(
            Q(cooperative_name__icontains=query) |
            Q(description__icontains=query) |
            Q(mission__icontains=query) |
            Q(vision__icontains=query)
        ).filter(is_active=True)[:5]
        results['cooperative_info'] = CooperativeInfoSerializer(cooperative_info, many=True).data

        # Search timeline
        timeline = CooperativeTimeline.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True)[:5]
        results['timeline'] = CooperativeTimelineSerializer(timeline, many=True).data

        # Search achievements
        achievements = CooperativeAchievement.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(awarding_organization__icontains=query)
        ).filter(is_active=True)[:5]
        results['achievements'] = CooperativeAchievementSerializer(achievements, many=True).data

        # Search affiliations
        affiliations = CooperativeAffiliation.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True)[:5]
        results['affiliations'] = CooperativeAffiliationSerializer(affiliations, many=True).data

        # Search leadership messages
        leadership = LeadershipMessage.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author_name__icontains=query)
        ).filter(is_active=True)[:5]
        results['leadership'] = LeadershipMessageSerializer(leadership, many=True).data

        # Search team members
        team = Person.objects.filter(
            Q(full_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(position_general__icontains=query)
        ).filter(is_active=True)[:5]
        results['team'] = PersonSerializer(team, many=True).data

        # Cache results for 5 minutes
        cache.set(cache_key, results, 300)

        return Response(results)


class StatisticsAPIView(APIView):
    """API endpoint for site statistics"""
    permission_classes = [AllowAny]

    def get(self, request):
        # Check cache first
        cache_key = 'site_statistics'
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response(cached_stats)

        stats = {
            'cooperative_info_count': CooperativeInfo.objects.filter(is_active=True).count(),
            'timeline_events_count': CooperativeTimeline.objects.filter(is_active=True).count(),
            'achievements_count': CooperativeAchievement.objects.filter(is_active=True).count(),
            'affiliations_count': CooperativeAffiliation.objects.filter(is_active=True).count(),
            'leadership_messages_count': LeadershipMessage.objects.filter(is_active=True).count(),
            'team_members_count': Person.objects.filter(is_active=True).count(),
            'committees_count': Committee.objects.filter(is_active=True).count(),
            'staff_count': Staff.objects.filter(is_active=True).count(),
            'last_updated': timezone.now().isoformat()
        }

        # Cache for 1 hour
        cache.set(cache_key, stats, 3600)

        return Response(stats)


class ContactAPIView(APIView):
    """API endpoint for contact form submissions"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            # Process contact form data
            # In a real implementation, you would save to database and send email
            
            response_data = {
                'success': True,
                'message': 'Thank you for your message. We will get back to you soon.',
                'submission_id': f'contact_{timezone.now().timestamp()}'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while processing your request.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NewsletterAPIView(APIView):
    """API endpoint for newsletter subscriptions"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            name = data.get('name', '')
            
            if not email:
                return Response({
                    'success': False,
                    'message': 'Email address is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process newsletter subscription
            # In a real implementation, you would save to database
            
            response_data = {
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!',
                'subscriber_id': f'newsletter_{timezone.now().timestamp()}'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while processing your subscription.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
