"""
Management command to test gallery JSON data generation
"""
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.template import Context, Template
from apps.gallery.models import GalleryImage, GalleryAlbum


class Command(BaseCommand):
    help = 'Test gallery JSON data generation'

    def handle(self, *args, **options):
        self.stdout.write('Testing gallery JSON data generation...')
        
        # Get gallery data like the view does
        gallery_images = GalleryImage.objects.filter(is_active=True).select_related('album').order_by('order', '-created_at')
        albums = GalleryAlbum.objects.filter(is_active=True).prefetch_related('images', 'sub_albums').order_by('order', '-created_at')
        
        self.stdout.write(f'Found {gallery_images.count()} images and {albums.count()} albums')
        
        # Test JSON generation
        json_template = '''
{
    "images": [
        {% for image in gallery_images %}
        {
            "id": {{ image.id }},
            "src": "{{ image.image.url|escapejs }}",
            "mobileSrc": "{{ image.get_mobile_image_url|escapejs }}",
            "tabletSrc": "{{ image.get_mobile_image_url|escapejs }}",
            "thumbnailSrc": "{{ image.get_thumbnail_url|escapejs }}",
            "alt": "{{ image.title|escapejs }}",
            "caption": "{{ image.description|escapejs }}",
            "title": "{{ image.title|escapejs }}",
            "category": "{{ image.category }}",
            "album": {% if image.album %}{{ image.album.id }}{% else %}null{% endif %},
            "albumName": "{% if image.album %}{{ image.album.name|escapejs }}{% else %}No Album{% endif %}",
            "isFeatured": {{ image.is_featured|yesno:"true,false" }},
            "fileSize": {{ image.get_file_size_mb }},
            "dimensions": {{ image.get_image_dimensions|safe }}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    ],
    "albums": {
        {% for album in albums %}
        "{{ album.id }}": {
            "id": {{ album.id }},
            "name": "{{ album.name|escapejs }}",
            "description": "{{ album.description|escapejs }}",
            "coverImage": "{% if album.cover_image %}{{ album.cover_image.url|escapejs }}{% else %}null{% endif %}",
            "imageCount": {{ album.get_image_count }},
            "subAlbumCount": {{ album.get_sub_album_count }},
            "parentAlbum": {% if album.parent_album %}{{ album.parent_album.id }}{% else %}null{% endif %}
        }{% if not forloop.last %},{% endif %}
        {% endfor %}
    }
}
        '''
        
        template = Template(json_template)
        context = Context({
            'gallery_images': gallery_images[:3],  # Test with first 3 images
            'albums': albums[:2]  # Test with first 2 albums
        })
        
        try:
            json_output = template.render(context)
            self.stdout.write('JSON generation successful!')
            self.stdout.write('Sample JSON output:')
            self.stdout.write(json_output[:500] + '...')
        except Exception as e:
            self.stdout.write(f'JSON generation failed: {e}')
            import traceback
            traceback.print_exc()
