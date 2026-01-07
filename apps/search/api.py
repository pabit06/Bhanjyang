from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.conf import settings
from django.utils.translation import gettext as _
from .services import SearchService, SearchAnalytics, SearchUtilities
from apps.about.models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeAffiliation, LeadershipMessage, Person
)
from apps.about.serializers import (
    CooperativeInfoSerializer, CooperativeTimelineSerializer,
    CooperativeAffiliationSerializer, LeadershipMessageSerializer,
    PersonSerializer
)

class ContentSearchAPIView(APIView):
    """
    API endpoint for content search.
    
    Provides full-text search capabilities across multiple content types.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Perform search and return paginated results.
        
        Query Parameters:
        - q: Search query (required)
        - type: Search type (all, team, events, affiliations)
        - sort: Sort order (relevance, date, title)
        - page: Page number
        - limit: Results per page
        """
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'results': [], 'total_results': 0, 'query': ''})

        # Get search parameters
        search_type = request.GET.get('type', 'all')
        sort_by = request.GET.get('sort', 'relevance')
        
        # Perform search based on type
        results = []
        if search_type == 'team':
            results = SearchService.search_team(query)
        elif search_type == 'events':
            results = SearchService.search_timeline(query)
        elif search_type == 'affiliations':
            results = SearchService.search_affiliations(query)
        else:
            # 'all' or fallback
            results = SearchService.search_all_content(query)

        # Track search
        SearchAnalytics.track_search(query, len(results), search_type)

        # Sort results
        if sort_by == 'date':
            results = sorted(results, key=lambda x: getattr(x, 'created_at', None) or getattr(x, 'event_date', None) or getattr(x, 'received_date', None) or getattr(x, 'updated_at', None), reverse=True)
        elif sort_by == 'title':
            results = sorted(results, key=lambda x: getattr(x, 'title', '') or getattr(x, 'name', '') or getattr(x, 'cooperative_name', '') or getattr(x, 'full_name', ''))

        # Manual Pagination since we have a list, not a queryset
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('limit', 20))
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        
        paginated_results = results[start_index:end_index]
        total_results = len(results)
        has_next = end_index < total_results
        has_previous = page_number > 1
        
        # Serialize results
        serialized_results = []
        for item in paginated_results:
            serialized_item = self._serialize_item(item)
            if serialized_item:
                serialized_results.append(serialized_item)
                
        return Response({
            'results': serialized_results,
            'total_results': total_results,
            'query': query,
            'page': page_number,
            'has_next': has_next,
            'has_previous': has_previous,
            'search_type': search_type,
            'sort_by': sort_by
        })

    def _serialize_item(self, item):
        """Serialize a mixed content item"""
        data = {}
        model_type = ''
        url = SearchUtilities.get_model_url(item)
        
        if isinstance(item, CooperativeInfo):
            data = CooperativeInfoSerializer(item).data
            model_type = 'cooperativeinfo'
            data['title'] = item.cooperative_name
        elif isinstance(item, CooperativeTimeline):
            data = CooperativeTimelineSerializer(item).data
            model_type = 'cooperativetimeline'
        elif isinstance(item, CooperativeAffiliation):
            data = CooperativeAffiliationSerializer(item).data
            model_type = 'cooperativeaffiliation'
            data['title'] = item.name
        elif isinstance(item, LeadershipMessage):
            data = LeadershipMessageSerializer(item).data
            model_type = 'leadershipmessage'
        elif isinstance(item, Person):
            data = PersonSerializer(item).data
            model_type = 'person'
            data['title'] = item.full_name
            # Map bio to content/description for uniform display
            data['description'] = item.bio
            
        if not data:
            return None
            
        # Standardize common fields for frontend
        data['model_type'] = model_type
        data['url'] = url
        
        # Ensure description/content field exists
        if 'description' not in data and 'content' in data:
            data['description'] = data['content']
            
        return data
