from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import json
import logging

from .models import OfficeLocation

logger = logging.getLogger(__name__)


def interactive_map_view(request):
    """Interactive map view showing office locations"""
    context = {
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Contact', 'url': '/contact/'},
            {'name': 'Locations', 'url': '/contact/map/'}
        ],
    }
    return render(request, 'contact/interactive_map.html', context)


@require_http_methods(["GET"])
def map_locations_api(request):
    """API endpoint for map locations"""
    # Check cache first
    cache_key = 'map_locations'
    cached_locations = cache.get(cache_key)
    if cached_locations:
        return JsonResponse(cached_locations)
    
    # Fetch from database
    try:
        locations_qs = OfficeLocation.objects.filter(is_active=True).order_by('order', 'name')
        
        if not locations_qs.exists():
            # Fallback to default location (Pokhara area)
            logger.warning("No active office locations found in database, returning default location")
            return JsonResponse({
                'locations': [],
                'center': {'latitude': 28.0, 'longitude': 84.0, 'zoom': 10}
            })
        
        locations = []
        latitudes = []
        longitudes = []
        
        for loc in locations_qs:
            location_data = {
                'id': loc.id,
                'name': loc.name,
                'address': loc.address,
                'latitude': float(loc.latitude),
                'longitude': float(loc.longitude),
                'type': loc.location_type,
                'phone': loc.phone,
                'email': loc.email,
                'hours': loc.hours,
                'services': loc.services or [],
                'description': loc.description,
            }
            
            # Add image URL if available
            if loc.image:
                location_data['image'] = loc.image.url
            else:
                location_data['image'] = None
            
            locations.append(location_data)
            latitudes.append(float(loc.latitude))
            longitudes.append(float(loc.longitude))
        
        # Calculate center from actual locations
        center = {
            'latitude': sum(latitudes) / len(latitudes) if latitudes else 28.0,
            'longitude': sum(longitudes) / len(longitudes) if longitudes else 84.0,
            'zoom': 10
        }
        
        response_data = {
            'locations': locations,
            'center': center
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 3600)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching map locations: {e}", exc_info=True)
        # Return empty response on error
        return JsonResponse({
            'locations': [],
            'center': {'latitude': 28.0, 'longitude': 84.0, 'zoom': 10},
            'error': 'Unable to load locations'
        }, status=500)


@require_http_methods(["POST"])
def map_directions_api(request):
    """API endpoint for getting directions"""
    try:
        data = json.loads(request.body)
        origin = data.get('origin')
        destination = data.get('destination')
        
        # In a real implementation, you would integrate with Google Maps API or similar
        # For now, return mock directions
        directions = {
            'status': 'success',
            'distance': '15.2 km',
            'duration': '25 minutes',
            'steps': [
                'Start from your location',
                'Head north on Main Road',
                'Turn right at Bhanjyang Chowk',
                'Continue for 5 km',
                'Arrive at Bhanjyang Cooperative'
            ]
        }
        
        return JsonResponse(directions)
        
    except Exception as e:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@require_http_methods(["POST"])
def map_analytics(request):
    """Track map interactions for analytics"""
    try:
        data = json.loads(request.body)
        interaction_type = data.get('type')  # 'view', 'click', 'directions'
        location_id = data.get('location_id')
        
        # Track analytics using logger
        logger.info(f"Map interaction: {interaction_type} for location {location_id}")
        
        # In a real implementation, you would store this in a database
        # For now, we just log it
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in map analytics request: {e}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error tracking map analytics: {e}", exc_info=True)
        return JsonResponse({'error': 'Invalid request'}, status=400)

