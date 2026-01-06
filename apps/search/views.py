from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.core.cache import cache
from django.utils.translation import activate

from apps.core.view_mixins import NepaliLanguageMixin
from .services import SearchService, SearchAnalytics, SearchUtilities
from apps.about.models import (
    CooperativeTimeline,
    CooperativeAffiliation, LeadershipMessage, Person
)

class AdvancedSearchView(NepaliLanguageMixin, ListView):
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
        if search_type == 'team':
            results = SearchService.search_team(query)
        elif search_type == 'events':
            # Note: search_events was called in original code but not defined in original methods!
            # It likely fell through or failed. 
            # Original code:
            # elif search_type == 'events':
            #    results = self.search_events(query)
            # But search_events method was NOT present in the file I read!
            # It only had search_timeline. I'll assume events -> timeline for now or just generic all.
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
            # Best effort sort by date fields
            results = sorted(results, key=lambda x: getattr(x, 'created_at', None) or getattr(x, 'event_date', None) or getattr(x, 'received_date', None) or getattr(x, 'updated_at', None), reverse=True)
        elif sort_by == 'title':
            results = sorted(results, key=lambda x: getattr(x, 'title', '') or getattr(x, 'name', '') or getattr(x, 'cooperative_name', '') or getattr(x, 'full_name', ''))

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query
        context['search_type'] = self.request.GET.get('type', 'all')
        context['sort_by'] = self.request.GET.get('sort', 'relevance')
        context['total_results'] = len(context['results']) if isinstance(context['results'], list) else 0
        
        # Add search suggestions (simple strings for UI)
        context['suggestions'] = SearchService.get_search_suggestions(query)
        
        return context

from django.views import View
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class SearchAPIView(View):
    """API endpoint for search suggestions and autocomplete"""
    
    def get(self, request):
        activate('ne')
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # Check cache first
        cache_key = f'search_api_suggestions_{query}_{limit}'
        cached_results = cache.get(cache_key)
        if cached_results:
            return JsonResponse(cached_results)
        
        suggestions = []
        
        try:
            # Get suggestions from different models with type and url info
            models_data = [
                (CooperativeTimeline, 'title', 'Timeline Event'),
                (CooperativeAffiliation, 'name', 'Affiliation'),
                (Person, 'full_name', 'Team Member'),
                (LeadershipMessage, 'title', 'Leadership Message'),
            ]
            
            for model, field, type_label in models_data:
                results = model.objects.filter(
                    **{f'{field}__icontains': query}
                ).values(field)[:limit]
                
                for result in results:
                    url = '/'
                    if model == CooperativeTimeline: url = '/about/timeline/'
                    elif model == CooperativeAffiliation: url = '/about/affiliations/'
                    elif model == Person: url = '/about/team/'
                    elif model == LeadershipMessage: url = '/about/leadership/'

                    suggestions.append({
                        'text': result[field],
                        'type': type_label,
                        'url': url
                    })
            
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
            
        except Exception:
            return JsonResponse({'error': 'Search failed'}, status=500)

# Compatibility mapping
search_api = SearchAPIView.as_view()