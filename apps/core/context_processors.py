from apps.about.models import CooperativeInfo

def site_settings(request):
    """
    Context processor to make cooperative info available to all templates.
    """
    # Fetch the active cooperative info. 
    # Using .active().first() ensures we get the relevant active record.
    # If no record exists, info will be None.
    info = CooperativeInfo.objects.active().first()
    
    return {'site_info': info}

