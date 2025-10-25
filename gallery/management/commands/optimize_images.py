from django.core.management.base import BaseCommand
from gallery.models import GalleryImage
from django.core.files.storage import default_storage
from PIL import Image
import io
import os
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Optimize all gallery images for mobile devices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of already optimized images',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='JPEG quality (1-100, default: 85)',
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
        force = options['force']
        quality = options['quality']
        max_width = options['max_width']
        max_height = options['max_height']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting image optimization with quality={quality}, max_size=({max_width}x{max_height})'
            )
        )
        
        images = GalleryImage.objects.filter(is_active=True)
        total_images = images.count()
        optimized_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, image in enumerate(images, 1):
            try:
                self.stdout.write(f'Processing {i}/{total_images}: {image.title}')
                
                # Check if mobile version already exists
                if not force:
                    mobile_url = image.get_mobile_image_url()
                    if mobile_url != image.image.url:
                        self.stdout.write(f'  Skipping (already optimized)')
                        skipped_count += 1
                        continue
                
                # Get original image info
                original_size = image.get_file_size_mb()
                original_dimensions = image.get_image_dimensions()
                
                # Optimize for mobile
                mobile_path = image.optimize_image_for_mobile(
                    size=(max_width, max_height),
                    quality=quality
                )
                
                if mobile_path:
                    # Get optimized image info
                    mobile_size = default_storage.size(mobile_path) / (1024 * 1024)
                    mobile_url = default_storage.url(mobile_path)
                    
                    self.stdout.write(
                        f'  ✓ Optimized: {original_dimensions[0]}x{original_dimensions[1]} '
                        f'({original_size:.2f}MB) → ({mobile_size:.2f}MB) '
                        f'({((original_size - mobile_size) / original_size * 100):.1f}% reduction)'
                    )
                    optimized_count += 1
                else:
                    self.stdout.write(f'  ✗ Failed to optimize')
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(f'  ✗ Error: {str(e)}')
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Optimization Complete!'))
        self.stdout.write(f'Total images: {total_images}')
        self.stdout.write(self.style.SUCCESS(f'Optimized: {optimized_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))
        self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if optimized_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully optimized {optimized_count} images for mobile devices!'
                )
            )
