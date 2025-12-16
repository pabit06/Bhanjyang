from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
import re

from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeAffiliation, LeadershipMessage, Person
)

class SearchService:
    """Service to handle search logic across the application"""
    
    @staticmethod
    def search_all_content(query):
        """Search across all content types"""
        results = []
        
        results.extend(SearchService.search_cooperative_info(query))
        results.extend(SearchService.search_timeline(query))
        results.extend(SearchService.search_achievements(query))
        results.extend(SearchService.search_affiliations(query))
        results.extend(SearchService.search_leadership(query))
        results.extend(SearchService.search_team(query))
        
        return results

    @staticmethod
    def search_cooperative_info(query):
        return list(CooperativeInfo.objects.filter(
            Q(cooperative_name__icontains=query) |
            Q(description__icontains=query) |
            Q(mission__icontains=query) |
            Q(vision__icontains=query) |
            Q(values__icontains=query)
        ).filter(is_active=True))

    @staticmethod
    def search_timeline(query):
        return list(CooperativeTimeline.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True))

    @staticmethod
    def search_achievements(query):
        return list(CooperativeAchievement.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(awarding_organization__icontains=query)
        ).filter(is_active=True))

    @staticmethod
    def search_affiliations(query):
        return list(CooperativeAffiliation.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True))

    @staticmethod
    def search_leadership(query):
        return list(LeadershipMessage.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author_name__icontains=query) |
            Q(author_position__icontains=query)
        ).filter(is_active=True))

    @staticmethod
    def search_team(query):
        return list(Person.objects.filter(
            Q(full_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(position_general__icontains=query)
        ).filter(is_active=True))
    
    @staticmethod
    def get_search_suggestions(query, limit=5):
        """Get search suggestions based on query"""
        if len(query) < 2:
            return []
            
        cache_key = f'search_suggestions_{query}_{limit}'
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results
        
        suggestions = []
        # Suggestion logic can be improved, sticking to basic starts/contains for now
        # Timeline
        suggestions.extend(CooperativeTimeline.objects.filter(title__icontains=query).values_list('title', flat=True)[:3])
        # Achievement
        suggestions.extend(CooperativeAchievement.objects.filter(title__icontains=query).values_list('title', flat=True)[:3])
        # Team
        suggestions.extend(Person.objects.filter(full_name__icontains=query).values_list('full_name', flat=True)[:3])
        
        unique_suggestions = list(set(suggestions))[:limit]
        cache.set(cache_key, unique_suggestions, 300) # Cache for 5 mins
        return unique_suggestions

class SearchAnalytics:
    """Track search analytics"""
    
    @staticmethod
    def track_search(query, results_count, search_type='all'):
        """Track search query for analytics"""
        try:
            # Store likely in DB or log
            search_data = {
                'query': query,
                'results_count': results_count,
                'search_type': search_type,
                'timestamp': timezone.now().isoformat()
            }
            # Placeholder for actual logging/DB storage
            # print(f"Search tracked: {search_data}") 
        except Exception:
            pass

class SearchUtilities:
    """Utilities for search display and helper functions"""
    
    @staticmethod
    def get_model_url(instance):
        """Get URL for a model instance"""
        # Ideally models should have get_absolute_url
        if hasattr(instance, 'get_absolute_url'):
            return instance.get_absolute_url()
            
        # Fallback mapping
        if isinstance(instance, CooperativeTimeline):
            return '/about/timeline/'
        elif isinstance(instance, CooperativeAchievement):
            return '/about/achievements/'
        elif isinstance(instance, CooperativeAffiliation):
            return '/about/affiliations/'
        elif isinstance(instance, Person):
            return '/about/team/'
        elif isinstance(instance, LeadershipMessage):
            return '/about/leadership/'
        return '/'

    @staticmethod
    def highlight_search_terms(text, query):
        """Highlight search terms in text"""
        if not query:
            return text
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        # return pattern.sub(f'<mark>{query}</mark>', text) # Simple replace replaces case too.
        # Better: keep original case
        return pattern.sub(lambda m: f'<mark>{m.group()}</mark>', text)
