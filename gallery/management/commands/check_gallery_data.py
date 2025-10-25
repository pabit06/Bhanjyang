"""
Management command to check gallery data
"""
from django.core.management.base import BaseCommand
from gallery.models import GalleryImage, GalleryAlbum


class Command(BaseCommand):
    help = 'Check gallery data'

    def handle(self, *args, **options):
        self.stdout.write('Checking gallery data...')
        
        # Check images
        total_images = GalleryImage.objects.count()
        active_images = GalleryImage.objects.filter(is_active=True).count()
        
        self.stdout.write(f'Total images: {total_images}')
        self.stdout.write(f'Active images: {active_images}')
        
        if active_images > 0:
            self.stdout.write('\nFirst 5 active images:')
            for img in GalleryImage.objects.filter(is_active=True)[:5]:
                self.stdout.write(f'- {img.title}: {img.image.url}')
                self.stdout.write(f'  Category: {img.category}, Album: {img.album}')
        else:
            self.stdout.write('No active images found!')
        
        # Check albums
        total_albums = GalleryAlbum.objects.count()
        active_albums = GalleryAlbum.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\nTotal albums: {total_albums}')
        self.stdout.write(f'Active albums: {active_albums}')
        
        if active_albums > 0:
            self.stdout.write('\nAlbums:')
            for album in GalleryAlbum.objects.filter(is_active=True):
                image_count = album.images.filter(is_active=True).count()
                self.stdout.write(f'- {album.name}: {image_count} images')
