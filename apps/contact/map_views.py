from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import json


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
    
    # Sample locations data (in real implementation, this would come from database)
    locations = [
        {
            'id': 1,
            'name': 'Bhanjyang Cooperative Main Office',
            'address': 'Bhanjyang, Kavre, Nepal',
            'latitude': 27.7172,
            'longitude': 85.3240,
            'type': 'main_office',
            'phone': '+977-11-123456',
            'email': 'info@bhanjyangcoop.com',
            'hours': '9:00 AM - 5:00 PM',
            'services': ['Savings', 'Loans', 'Insurance', 'Consultation'],
            'description': 'Our main office providing comprehensive cooperative services to the community.',
            'image': '/static/images/office-main.jpg'
        },
        {
            'id': 2,
            'name': 'Bhanjyang Cooperative Branch Office',
            'address': 'Panauti, Kavre, Nepal',
            'latitude': 27.5833,
            'longitude': 85.5167,
            'type': 'branch_office',
            'phone': '+977-11-234567',
            'email': 'panauti@bhanjyangcoop.com',
            'hours': '9:00 AM - 4:00 PM',
            'services': ['Savings', 'Loans'],
            'description': 'Convenient branch office serving the Panauti area.',
            'image': '/static/images/office-branch.jpg'
        },
        {
            'id': 3,
            'name': 'Bhanjyang Cooperative ATM Center',
            'address': 'Banepa, Kavre, Nepal',
            'latitude': 27.6333,
            'longitude': 85.5167,
            'type': 'atm_center',
            'phone': '+977-11-345678',
            'email': 'atm@bhanjyangcoop.com',
            'hours': '24/7',
            'services': ['ATM Services', 'Cash Withdrawal', 'Balance Inquiry'],
            'description': '24/7 ATM services for your convenience.',
            'image': '/static/images/atm-center.jpg'
        }
    ]
    
    response_data = {
        'locations': locations,
        'center': {
            'latitude': 27.6500,
            'longitude': 85.4500,
            'zoom': 10
        }
    }
    
    # Cache for 1 hour
    cache.set(cache_key, response_data, 3600)
    
    return JsonResponse(response_data)


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


def map_analytics(request):
    """Track map interactions for analytics"""
    try:
        data = json.loads(request.body)
        interaction_type = data.get('type')  # 'view', 'click', 'directions'
        location_id = data.get('location_id')
        
        # Track analytics (in real implementation, store in database)
        print(f"Map interaction: {interaction_type} for location {location_id}")
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': 'Invalid request'}, status=400)

