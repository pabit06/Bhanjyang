from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.core.cache import cache

from .services import SearchService, SearchAnalytics, SearchUtilities
from apps.about.models import (
    CooperativeTimeline, CooperativeAchievement,
    CooperativeAffiliation, LeadershipMessage, Person
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
        elif search_type == 'achievements':
            results = SearchService.search_achievements(query)
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

@csrf_exempt
@require_http_methods(["GET"])
def search_api(request):
    """API endpoint for search suggestions and autocomplete"""
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
        # We put this logic here as it's specific to the API response format
        models_data = [
            (CooperativeTimeline, 'title', 'Timeline Event'),
            (CooperativeAchievement, 'title', 'Achievement'),
            (CooperativeAffiliation, 'name', 'Affiliation'),
            (Person, 'full_name', 'Team Member'),
            (LeadershipMessage, 'title', 'Leadership Message'),
        ]
        
        for model, field, type_label in models_data:
            results = model.objects.filter(
                **{f'{field}__icontains': query}
            ).values(field)[:limit]
            
            for result in results:
                # We need a dummy instance to get URL if using our helper, 
                # or just use the model class mapping.
                # Since we don't have the full object here (just dict), we might need to be careful with get_model_url if it expects instance.
                # The original code's get_model_url used model class if result passed? No, it used dict in original!
                # Original: url_mapping.get(model, '/') w/o using result instance. 
                # Let's reproduce that safe behavior or improve it.
                # Actually original was:
                # def get_model_url(model, result): ... url_mapping.get(model, '/')
                # So it ignored result instance.
                
                # Let's improve it slightly by manually mapping here or using the utility properly if possible.
                # Our new utility expects an instance.
                # We'll just hardcode simple mapping here like before for speed/simplicity
                url = '/'
                if model == CooperativeTimeline: url = '/about/timeline/'
                elif model == CooperativeAchievement: url = '/about/achievements/'
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