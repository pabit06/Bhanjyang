# downloads/views.py

from django.shortcuts import render
from .models import Download

def download_center_view(request):
    """
    Renders the download center page, displaying all available downloadable files.
    """
    downloads = Download.objects.all() # Fetch all Download objects from the database
    context = {
        'downloads': downloads,
    }
    return render(request, 'downloads/download.html', context)
