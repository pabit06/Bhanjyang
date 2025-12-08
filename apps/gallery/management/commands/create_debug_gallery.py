"""
Management command to create a debug gallery page
"""
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.template import Context, Template
from apps.gallery.models import GalleryImage, GalleryAlbum


class Command(BaseCommand):
    help = 'Create a debug gallery page'

    def handle(self, *args, **options):
        self.stdout.write('Creating debug gallery page...')
        
        # Get gallery data
        gallery_images = GalleryImage.objects.filter(is_active=True).select_related('album').order_by('order', '-created_at')
        albums = GalleryAlbum.objects.filter(is_active=True).prefetch_related('images', 'sub_albums').order_by('order', '-created_at')
        
        # Create a simple debug template
        debug_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gallery Debug</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .image { margin: 10px; padding: 10px; border: 1px solid #ccc; display: inline-block; }
        .image img { max-width: 200px; max-height: 200px; }
        .debug-info { background: #f0f0f0; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Gallery Debug Page</h1>
    
    <div class="debug-info">
        <h3>Debug Information:</h3>
        <p>Total Images: {{ gallery_images|length }}</p>
        <p>Total Albums: {{ albums|length }}</p>
    </div>
    
    <h2>Images:</h2>
    {% for image in gallery_images %}
    <div class="image">
        <img src="{{ image.image.url }}" alt="{{ image.title }}" onerror="this.style.border='2px solid red'">
        <p><strong>{{ image.title }}</strong></p>
        <p>Category: {{ image.category }}</p>
        <p>Album: {{ image.album.name|default:"No Album" }}</p>
        <p>URL: {{ image.image.url }}</p>
    </div>
    {% endfor %}
    
    <h2>Albums:</h2>
    {% for album in albums %}
    <div class="debug-info">
        <h4>{{ album.name }}</h4>
        <p>Description: {{ album.description }}</p>
        <p>Image Count: {{ album.get_image_count }}</p>
        <p>Cover Image: {% if album.cover_image %}{{ album.cover_image.url }}{% else %}None{% endif %}</p>
    </div>
    {% endfor %}
    
    <script>
        console.log('Debug page loaded');
        console.log('Images count:', {{ gallery_images|length }});
        console.log('Albums count:', {{ albums|length }});
    </script>
</body>
</html>
        '''
        
        template = Template(debug_template)
        context = Context({
            'gallery_images': gallery_images,
            'albums': albums
        })
        
        html_output = template.render(context)
        
        # Save to file
        with open('debug_gallery.html', 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        self.stdout.write('Debug gallery page created: debug_gallery.html')
        self.stdout.write('Open this file in your browser to see the images')
