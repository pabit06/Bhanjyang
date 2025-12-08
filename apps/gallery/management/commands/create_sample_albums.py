from django.core.management.base import BaseCommand
from apps.gallery.models import GalleryAlbum, GalleryImage


class Command(BaseCommand):
    help = 'Create sample albums for the gallery'

    def handle(self, *args, **options):
        # Create root albums
        albums_data = [
            {
                'name': 'Annual Events',
                'description': 'Annual celebrations and events',
                'is_featured': True,
                'order': 1
            },
            {
                'name': 'Board Meetings',
                'description': 'Board meetings and official gatherings',
                'is_featured': True,
                'order': 2
            },
            {
                'name': 'Community Service',
                'description': 'Community service activities and initiatives',
                'is_featured': False,
                'order': 3
            },
            {
                'name': 'Member Activities',
                'description': 'Member-focused activities and events',
                'is_featured': False,
                'order': 4
            },
            {
                'name': 'Awards & Recognition',
                'description': 'Awards ceremonies and recognition events',
                'is_featured': True,
                'order': 5
            }
        ]
        
        created_albums = []
        for album_data in albums_data:
            album, created = GalleryAlbum.objects.get_or_create(
                name=album_data['name'],
                defaults=album_data
            )
            if created:
                created_albums.append(album)
                self.stdout.write(
                    self.style.SUCCESS(f'Created album: {album.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Album already exists: {album.name}')
                )
        
        # Create sub-albums for Annual Events
        annual_events = GalleryAlbum.objects.get(name='Annual Events')
        sub_albums_data = [
            {
                'name': 'Annual General Meeting',
                'description': 'Annual General Meeting photos',
                'parent_album': annual_events,
                'order': 1
            },
            {
                'name': 'Festival Celebrations',
                'description': 'Festival and cultural celebrations',
                'parent_album': annual_events,
                'order': 2
            }
        ]
        
        for sub_album_data in sub_albums_data:
            sub_album, created = GalleryAlbum.objects.get_or_create(
                name=sub_album_data['name'],
                parent_album=sub_album_data['parent_album'],
                defaults=sub_album_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created sub-album: {sub_album.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Sub-album already exists: {sub_album.name}')
                )
        
        # Assign some existing images to albums
        images = GalleryImage.objects.filter(is_active=True)
        albums = GalleryAlbum.objects.filter(is_active=True)
        
        if images.exists() and albums.exists():
            # Assign images to albums based on category
            category_album_mapping = {
                'events': albums.filter(name__icontains='event').first(),
                'team': albums.filter(name__icontains='board').first(),
                'community': albums.filter(name__icontains='community').first(),
                'awards': albums.filter(name__icontains='award').first(),
            }
            
            assigned_count = 0
            for image in images:
                album = category_album_mapping.get(image.category)
                if album and not image.album:
                    image.album = album
                    image.save()
                    assigned_count += 1
            
            if assigned_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Assigned {assigned_count} images to albums')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Sample albums created successfully!')
        )
