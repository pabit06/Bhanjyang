from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from .services import NewsService, EventService
from .performance import performance_monitor

class NewsEventsAPIView(View):
    """
    API endpoint for fetching news articles and events dynamically.
    Supports filtering, sorting, and pagination.
    """
    
    @method_decorator(performance_monitor)
    def get(self, request, content_type):
        """
        Get list of content (articles or events).
        
        Args:
            content_type: 'articles' or 'events'
        """
        try:
            params = request.GET.dict()
            
            if content_type == 'articles':
                data = NewsService.get_article_list(params)
                page_obj = data['page_obj']
                
                results = []
                for article in page_obj:
                    results.append({
                        'id': article.id,
                        'title': article.title,
                        'slug': article.slug,
                        'excerpt': article.excerpt,
                        'content': article.content, # Be careful with full content size
                        'image_url': article.image.url if article.image else None,
                        'published_date': article.published_date.isoformat(),
                        'author_name': article.author.get_full_name() or article.author.username,
                        'category_name': article.category.name if article.category else 'Uncategorized',
                        'view_count': article.view_count,
                        'read_time': article.read_time,
                        'is_featured': article.is_featured,
                        'detail_url': article.get_absolute_url()
                    })
                    
                response_data = {
                    'results': results,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'num_pages': page_obj.paginator.num_pages,
                    'current_page': page_obj.number,
                }
                return JsonResponse(response_data)
                
            elif content_type == 'events':
                # Map 'type' param to 'event_type' for service compatibility if needed
                # Service usually handles 'type' directly from params
                
                data = EventService.get_event_list(params)
                page_obj = data['page_obj']
                
                results = []
                for event in page_obj:
                    results.append({
                        'id': event.id,
                        'title': event.title,
                        'slug': event.slug,
                        'description': event.description,
                        'image_url': event.image.url if event.image else None,
                        'event_date': event.event_date.isoformat(),
                        'location': event.location,
                        'event_type': event.get_event_type_display(),
                        'event_type_choices': event.event_type, # Raw choice value
                        'status': event.status,
                        'status_display': event.get_status_display(),
                        'view_count': event.view_count,
                        'is_featured': event.is_featured,
                        'registration_required': event.registration_required,
                        'detail_url': event.get_absolute_url()
                    })
                    
                response_data = {
                    'results': results,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'num_pages': page_obj.paginator.num_pages,
                    'current_page': page_obj.number,
                }
                return JsonResponse(response_data)
            
            else:
                return JsonResponse({'error': 'Invalid content type'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
