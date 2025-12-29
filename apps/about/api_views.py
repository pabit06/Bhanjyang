from typing import Dict, Any, Optional
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, QuerySet
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
# NewsletterSignupForm removed - no longer needed
from .serializers import (
    CooperativeInfoSerializer, CooperativeTimelineSerializer,
    CooperativeStatisticSerializer,
    CooperativeAffiliationSerializer, LeadershipMessageSerializer,
    PersonSerializer, CommitteeSerializer, MembershipSerializer,
    StaffSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination configuration for API responses.
    
    Provides consistent pagination across all API endpoints with:
    - Default page size: 20 items
    - Configurable page size via query parameter
    - Maximum page size limit: 100 items
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CooperativeInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for cooperative information.
    
    Provides read-only access to cooperative information with:
    - List and detail views
    - Search functionality (name, description, mission, vision, values)
    - Ordering by created_at or updated_at
    - Statistics endpoint for related statistics
    
    Endpoints:
    - GET /api/v1/about/cooperative-info/ - List all active cooperative info
    - GET /api/v1/about/cooperative-info/{id}/ - Get specific cooperative info
    - GET /api/v1/about/cooperative-info/statistics/ - Get related statistics
    """
    serializer_class = CooperativeInfoSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['cooperative_name', 'description', 'mission', 'vision', 'values']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active cooperative information.
        
        Returns:
            QuerySet of active CooperativeInfo objects
        """
        return CooperativeInfo.objects.active()

    @action(detail=False, methods=['get'])
    def statistics(self, request: Request) -> Response:
        """
        Get cooperative statistics.
        
        Note: This endpoint is kept here for backward compatibility.
        Statistics technically belong to CooperativeStatistic model.
        
        Returns:
            Response with list of active statistics ordered by creation date
        """
        stats = CooperativeStatistic.objects.active().order_by('-created_at')
        serializer = CooperativeStatisticSerializer(stats, many=True)
        return Response(serializer.data)


class CooperativeTimelineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for cooperative timeline events.
    
    Provides read-only access to timeline events with:
    - List and detail views
    - Filtering by event_type and is_featured
    - Search by title and description
    - Ordering by event_date, created_at, or order
    - Featured and recent events endpoints
    
    Endpoints:
    - GET /api/v1/about/timeline/ - List all active timeline events
    - GET /api/v1/about/timeline/{id}/ - Get specific timeline event
    - GET /api/v1/about/timeline/featured/ - Get top 5 featured events
    - GET /api/v1/about/timeline/recent/ - Get 10 most recent events
    """
    serializer_class = CooperativeTimelineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['event_date', 'created_at', 'order']
    ordering = ['-event_date']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active timeline events.
        
        Returns:
            QuerySet of active CooperativeTimeline objects
        """
        return CooperativeTimeline.objects.active()

    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """
        Get featured timeline events.
        
        Returns the top 5 featured timeline events, ordered by their
        configured order or creation date.
        
        Returns:
            Response with list of up to 5 featured timeline events
        """
        featured_events = self.get_queryset().filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request: Request) -> Response:
        """
        Get recent timeline events.
        
        Returns the 10 most recent timeline events ordered by event date
        (newest first).
        
        Returns:
            Response with list of up to 10 most recent timeline events
        """
        recent_events = self.get_queryset().order_by('-event_date')[:10]
        serializer = self.get_serializer(recent_events, many=True)
        return Response(serializer.data)


class CooperativeAffiliationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for cooperative affiliations.
    
    Provides read-only access to affiliations with:
    - List and detail views
    - Search by name and description
    - Ordering by created_at or order
    - Featured affiliations endpoint
    
    Endpoints:
    - GET /api/v1/about/affiliations/ - List all active affiliations
    - GET /api/v1/about/affiliations/{id}/ - Get specific affiliation
    - GET /api/v1/about/affiliations/featured/ - Get top 5 featured affiliations
    """
    serializer_class = CooperativeAffiliationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'order']
    ordering = ['order']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active affiliations.
        
        Returns:
            QuerySet of active CooperativeAffiliation objects
        """
        return CooperativeAffiliation.objects.active()

    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """
        Get featured affiliations.
        
        Returns the top 5 featured affiliations, ordered by their
        configured order.
        
        Returns:
            Response with list of up to 5 featured affiliations
        """
        featured_affiliations = self.get_queryset().filter(is_featured=True)[:5]
        serializer = self.get_serializer(featured_affiliations, many=True)
        return Response(serializer.data)


class LeadershipMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for leadership messages.
    
    Provides read-only access to leadership messages with:
    - List and detail views
    - Search by title, content, author name, and author position
    - Ordering by created_at or order
    - Featured messages endpoint
    
    Endpoints:
    - GET /api/v1/about/leadership/ - List all active leadership messages
    - GET /api/v1/about/leadership/{id}/ - Get specific leadership message
    - GET /api/v1/about/leadership/featured/ - Get top 3 featured messages
    """
    serializer_class = LeadershipMessageSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'author_name', 'author_position']
    ordering_fields = ['created_at', 'order']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active leadership messages.
        
        Returns:
            QuerySet of active LeadershipMessage objects
        """
        return LeadershipMessage.objects.active()

    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """
        Get featured leadership messages.
        
        Returns the top 3 featured leadership messages, ordered by their
        configured order or creation date.
        
        Returns:
            Response with list of up to 3 featured leadership messages
        """
        featured_messages = self.get_queryset().filter(is_featured=True)[:3]
        serializer = self.get_serializer(featured_messages, many=True)
        return Response(serializer.data)


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for team members (Person model).
    
    Provides read-only access to team members with:
    - List and detail views
    - Search by full name, bio, and position
    - Ordering by created_at or full_name
    - Current team, past team, and by-position endpoints
    
    Endpoints:
    - GET /api/v1/about/team/ - List all active team members
    - GET /api/v1/about/team/{id}/ - Get specific team member
    - GET /api/v1/about/team/current_team/ - Get current active team members
    - GET /api/v1/about/team/past_team/ - Get past team members
    - GET /api/v1/about/team/by_position/?position=X - Get members by position
    """
    serializer_class = PersonSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'bio', 'position_general']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['full_name']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active team members.
        
        Returns:
            QuerySet of active Person objects
        """
        return Person.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def current_team(self, request: Request) -> Response:
        """
        Get current team members.
        
        Returns team members who have active memberships with no end date,
        indicating they are currently part of committees.
        
        Returns:
            Response with list of current team members
        """
        current_members = self.get_queryset().filter(
            memberships__is_active=True,
            memberships__end_date__isnull=True
        ).distinct()
        serializer = self.get_serializer(current_members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past_team(self, request: Request) -> Response:
        """
        Get past team members.
        
        Returns team members who have memberships with an end date,
        indicating they are no longer part of committees.
        
        Returns:
            Response with list of past team members
        """
        past_members = self.get_queryset().filter(
            memberships__is_active=True,
            memberships__end_date__isnull=False
        ).distinct()
        serializer = self.get_serializer(past_members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_position(self, request: Request) -> Response:
        """
        Get team members filtered by position.
        
        Query Parameters:
            position (str, required): Position name to filter by (case-insensitive partial match)
        
        Returns:
            Response with list of team members matching the position, or
            400 error if position parameter is missing
        
        Example:
            GET /api/v1/about/team/by_position/?position=chairman
        """
        position = request.query_params.get('position')
        if position:
            members = self.get_queryset().filter(position_general__icontains=position)
            serializer = self.get_serializer(members, many=True)
            return Response(serializer.data)
        return Response({'error': 'Position parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for committees.
    
    Provides read-only access to committees with:
    - List and detail views
    - Search by name and description
    - Ordering by created_at or order
    - Members endpoint for each committee
    
    Endpoints:
    - GET /api/v1/about/committees/ - List all active committees
    - GET /api/v1/about/committees/{id}/ - Get specific committee
    - GET /api/v1/about/committees/{id}/members/ - Get members of a committee
    """
    serializer_class = CommitteeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'order']
    ordering = ['order']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active committees.
        
        Returns:
            QuerySet of active Committee objects
        """
        return Committee.objects.filter(is_active=True)

    @action(detail=True, methods=['get'])
    def members(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        Get members of a specific committee.
        
        Returns all active memberships for the specified committee,
        including person details and positions.
        
        Args:
            pk: Primary key of the committee
        
        Returns:
            Response with list of active memberships for the committee
        """
        committee = self.get_object()
        members = committee.memberships.filter(is_active=True)
        serializer = MembershipSerializer(members, many=True)
        return Response(serializer.data)


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for staff members.
    
    Provides read-only access to staff members with:
    - List and detail views
    - Search by person name, position, and department
    - Ordering by created_at or person full name
    - By-department endpoint
    
    Endpoints:
    - GET /api/v1/about/staff/ - List all active staff members
    - GET /api/v1/about/staff/{id}/ - Get specific staff member
    - GET /api/v1/about/staff/by_department/?department=X - Get staff by department
    """
    serializer_class = StaffSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['person__full_name', 'position', 'department']
    ordering_fields = ['created_at', 'person__full_name']
    ordering = ['person__full_name']

    def get_queryset(self) -> QuerySet:
        """
        Get queryset of active staff members.
        
        Returns:
            QuerySet of active Staff objects with related Person data
        """
        return Staff.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def by_department(self, request: Request) -> Response:
        """
        Get staff members filtered by department.
        
        Query Parameters:
            department (str, required): Department name to filter by (case-insensitive partial match)
        
        Returns:
            Response with list of staff members in the department, or
            400 error if department parameter is missing
        
        Example:
            GET /api/v1/about/staff/by_department/?department=IT
        """
        department = request.query_params.get('department')
        if department:
            staff = self.get_queryset().filter(department__icontains=department)
            serializer = self.get_serializer(staff, many=True)
            return Response(serializer.data)
        return Response({'error': 'Department parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class SearchAPIView(APIView):
    """
    Global search API endpoint for the About app.
    
    Performs a comprehensive search across all About app models including:
    - Cooperative information (name, description, mission, vision)
    - Timeline events (title, description)
    - Affiliations (name, description)
    - Leadership messages (title, content, author)
    - Team members (name, bio, position)
    
    Results are cached for 5 minutes to improve performance.
    
    Query Parameters:
        q (str, required): Search query string
    
    Returns:
        Response with search results grouped by model type, or
        400 error if query parameter is missing
    
    Example:
        GET /api/v1/about/search/?q=cooperative
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """
        Perform global search across About app models.
        
        Args:
            request: HTTP request with 'q' query parameter
        
        Returns:
            Response with serialized search results from all models
        """
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
    """
    API endpoint for aggregated site statistics.
    
    Provides comprehensive statistics about the About app including:
    - Counts of all active models (cooperative info, timeline, affiliations, etc.)
    - Team and staff counts
    - Last updated timestamp
    
    Results are cached for 1 hour to improve performance.
    
    Returns:
        Response with dictionary containing counts and last_updated timestamp
    
    Example:
        GET /api/v1/about/statistics/
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """
        Get aggregated statistics for the About app.
        
        Args:
            request: HTTP request (no parameters required)
        
        Returns:
            Response with statistics dictionary including counts and timestamp
        """
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


# ContactAPIView has been removed - use contact app's API endpoint instead
# This consolidation ensures all contact submissions are saved to the database

# NewsletterAPIView has been removed - no longer needed
