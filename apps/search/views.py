from django.db.models import Q, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.cache import cache
import json
import re
from apps.about.models import (
    CooperativeInfo, CooperativeTimeline, CooperativeAchievement,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)


class AdvancedSearchView(ListView):
    """Advanced search view with full-text search capabilities"""
    template_name = 'search/advanced_search.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return []

        # Get search parameters
        search_type = self.request.GET.get('type', 'all')
        sort_by = self.request.GET.get('sort', 'relevance')
        
        # Perform search based on type
        if search_type == 'all':
            results = self.search_all_content(query)
        elif search_type == 'team':
            results = self.search_team(query)
        elif search_type == 'events':
            results = self.search_events(query)
        elif search_type == 'achievements':
            results = self.search_achievements(query)
        elif search_type == 'affiliations':
            results = self.search_affiliations(query)
        else:
            results = self.search_all_content(query)

        # Sort results
        if sort_by == 'date':
            results = sorted(results, key=lambda x: getattr(x, 'created_at', None) or getattr(x, 'event_date', None) or getattr(x, 'received_date', None), reverse=True)
        elif sort_by == 'title':
            results = sorted(results, key=lambda x: getattr(x, 'title', '') or getattr(x, 'name', '') or getattr(x, 'cooperative_name', ''))

        return results

    def search_all_content(self, query):
        """Search across all content types"""
        results = []
        
        # Search cooperative info
        cooperative_results = self.search_cooperative_info(query)
        results.extend(cooperative_results)
        
        # Search timeline events
        timeline_results = self.search_timeline(query)
        results.extend(timeline_results)
        
        # Search achievements
        achievement_results = self.search_achievements(query)
        results.extend(achievement_results)
        
        # Search affiliations
        affiliation_results = self.search_affiliations(query)
        results.extend(affiliation_results)
        
        # Search leadership messages
        leadership_results = self.search_leadership(query)
        results.extend(leadership_results)
        
        # Search team members
        team_results = self.search_team(query)
        results.extend(team_results)
        
        return results

    def search_cooperative_info(self, query):
        """Search cooperative information"""
        return CooperativeInfo.objects.filter(
            Q(cooperative_name__icontains=query) |
            Q(description__icontains=query) |
            Q(mission__icontains=query) |
            Q(vision__icontains=query) |
            Q(values__icontains=query)
        ).filter(is_active=True)

    def search_timeline(self, query):
        """Search timeline events"""
        return CooperativeTimeline.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True)

    def search_achievements(self, query):
        """Search achievements"""
        return CooperativeAchievement.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(awarding_organization__icontains=query)
        ).filter(is_active=True)

    def search_affiliations(self, query):
        """Search affiliations"""
        return CooperativeAffiliation.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True)

    def search_leadership(self, query):
        """Search leadership messages"""
        return LeadershipMessage.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author_name__icontains=query) |
            Q(author_position__icontains=query)
        ).filter(is_active=True)

    def search_team(self, query):
        """Search team members"""
        return Person.objects.filter(
            Q(full_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(position_general__icontains=query)
        ).filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['search_type'] = self.request.GET.get('type', 'all')
        context['sort_by'] = self.request.GET.get('sort', 'relevance')
        context['total_results'] = len(context['results'])
        
        # Add search suggestions
        context['suggestions'] = self.get_search_suggestions(context['query'])
        
        return context

    def get_search_suggestions(self, query):
        """Get search suggestions based on query"""
        if len(query) < 2:
            return []
        
        suggestions = []
        
        # Get suggestions from different models
        try:
            # Timeline suggestions
            timeline_suggestions = CooperativeTimeline.objects.filter(
                title__icontains=query
            ).values_list('title', flat=True)[:3]
            suggestions.extend(timeline_suggestions)
            
            # Achievement suggestions
            achievement_suggestions = CooperativeAchievement.objects.filter(
                title__icontains=query
            ).values_list('title', flat=True)[:3]
            suggestions.extend(achievement_suggestions)
            
            # Team suggestions
            team_suggestions = Person.objects.filter(
                full_name__icontains=query
            ).values_list('full_name', flat=True)[:3]
            suggestions.extend(team_suggestions)
            
        except Exception as e:
            pass
        
        return list(set(suggestions))[:5]


@csrf_exempt
@require_http_methods(["GET"])
def search_api(request):
    """API endpoint for search suggestions and autocomplete"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Check cache first
    cache_key = f'search_suggestions_{query}_{limit}'
    cached_results = cache.get(cache_key)
    if cached_results:
        return JsonResponse(cached_results)
    
    suggestions = []
    
    try:
        # Get suggestions from different models
        models_data = [
            (CooperativeTimeline, 'title', 'Timeline Event'),
            (CooperativeAchievement, 'title', 'Achievement'),
            (CooperativeAffiliation, 'name', 'Affiliation'),
            (Person, 'full_name', 'Team Member'),
            (LeadershipMessage, 'title', 'Leadership Message'),
        ]
        
        for model, field, type_label in models_data:
            try:
                results = model.objects.filter(
                    **{f'{field}__icontains': query}
                ).values(field)[:limit]
                
                for result in results:
                    suggestions.append({
                        'text': result[field],
                        'type': type_label,
                        'url': get_model_url(model, result)
                    })
            except Exception as e:
                continue
        
        # Sort by relevance (exact matches first)
        suggestions.sort(key=lambda x: (
            0 if query.lower() in x['text'].lower() else 1,
            len(x['text'])
        ))
        
        response_data = {
            'suggestions': suggestions[:limit],
            'query': query
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': 'Search failed'}, status=500)


def get_model_url(model, result):
    """Get URL for a model result"""
    url_mapping = {
        CooperativeTimeline: '/about/timeline/',
        CooperativeAchievement: '/about/achievements/',
        CooperativeAffiliation: '/about/affiliations/',
        Person: '/about/team/',
        LeadershipMessage: '/about/leadership/',
    }
    return url_mapping.get(model, '/')


class SearchAnalytics:
    """Track search analytics"""
    
    @staticmethod
    def track_search(query, results_count, search_type='all'):
        """Track search query for analytics"""
        try:
            # Store search analytics in cache or database
            search_data = {
                'query': query,
                'results_count': results_count,
                'search_type': search_type,
                'timestamp': timezone.now().isoformat()
            }
            
            # You can implement actual analytics storage here
            # For now, just log it
            print(f"Search tracked: {search_data}")
            
        except Exception as e:
            pass


# Search filters and utilities
class SearchFilters:
    """Search filtering utilities"""
    
    @staticmethod
    def filter_by_date_range(queryset, start_date, end_date):
        """Filter queryset by date range"""
        if start_date and end_date:
            return queryset.filter(
                created_at__date__range=[start_date, end_date]
            )
        return queryset
    
    @staticmethod
    def filter_by_category(queryset, category):
        """Filter queryset by category"""
        if category:
            return queryset.filter(category=category)
        return queryset
    
    @staticmethod
    def highlight_search_terms(text, query):
        """Highlight search terms in text"""
        if not query:
            return text
        
        # Simple highlighting (you can make this more sophisticated)
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(f'<mark>{query}</mark>', text)