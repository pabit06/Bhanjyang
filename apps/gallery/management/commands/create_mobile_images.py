from django.core.management.base import BaseCommand
from apps.gallery.models import GalleryImage
from django.core.files.storage import default_storage
from PIL import Image
import io
import os
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Create mobile-optimized versions of gallery images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quality',
            type=int,
            default=80,
            help='JPEG quality (1-100, default: 80)',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=800,
            help='Maximum width for mobile images (default: 800)',
        )
        parser.add_argument(
            '--max-height',
            type=int,
            default=600,
            help='Maximum height for mobile images (default: 600)',
        )

    def handle(self, *args, **options):
        quality = options['quality']
        max_width = options['max_width']
        max_height = options['max_height']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Creating mobile-optimized versions with quality={quality}, max_size=({max_width}x{max_height})'
            )
        )
        
        images = GalleryImage.objects.filter(is_active=True)
        total_images = images.count()
        optimized_count = 0
        error_count = 0
        
        for i, image in enumerate(images, 1):
            try:
                self.stdout.write(f'Processing {i}/{total_images}: {image.title}')
                
                # Get original image info
                original_size = image.get_file_size_mb()
                original_dimensions = image.get_image_dimensions()
                
                # Create mobile-optimized version
                mobile_path = image.optimize_image_for_mobile(
                    size=(max_width, max_height),
                    quality=quality
                )
                
                if mobile_path:
                    # Get optimized image info
                    mobile_size = default_storage.size(mobile_path) / (1024 * 1024)
                    
                    self.stdout.write(
                        f'  [OK] Created mobile version: {original_dimensions[0]}x{original_dimensions[1]} '
                        f'({original_size:.2f}MB) -> ({mobile_size:.2f}MB) '
                        f'({((original_size - mobile_size) / original_size * 100):.1f}% reduction)'
                    )
                    optimized_count += 1
                else:
                    self.stdout.write(f'  [FAIL] Failed to create mobile version')
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(f'  [ERROR] Error: {str(e)}')
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Mobile Optimization Complete!'))
        self.stdout.write(f'Total images: {total_images}')
        self.stdout.write(self.style.SUCCESS(f'Mobile versions created: {optimized_count}'))
        self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if optimized_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created mobile-optimized versions for {optimized_count} images!'
                )
            )
