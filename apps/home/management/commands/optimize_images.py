from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from PIL import Image, ImageOps
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Optimize images in the media directory according to website guidelines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['hero', 'news', 'team', 'service', 'logo'],
            help='Type of images to optimize',
        )
        parser.add_argument(
            '--path',
            type=str,
            help='Specific path to optimize (relative to media/)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Bhanjyang Cooperative Image Optimizer')
        )
        self.stdout.write('=' * 50)
        
        # Image specifications
        specs = {
            'hero': {'size': (1920, 1080), 'max_kb': 500, 'format': 'JPEG'},
            'news': {'size': (800, 600), 'max_kb': 200, 'format': 'JPEG'},
            'team': {'size': (400, 400), 'max_kb': 100, 'format': 'JPEG'},
            'service': {'size': (600, 400), 'max_kb': 150, 'format': 'JPEG'},
            'logo': {'size': (300, 100), 'max_kb': 50, 'format': 'PNG'}
        }
        
        # Determine paths to process
        media_root = default_storage.location
        paths_to_process = []
        
        if options['path']:
            paths_to_process.append(options['path'])
        elif options['type']:
            type_mapping = {
                'hero': 'main/images/',
                'news': 'updates/images/',
                'team': 'person_photos/',
                'service': 'services/',
                'logo': 'main/images/'
            }
            if options['type'] in type_mapping:
                paths_to_process.append(type_mapping[options['type']])
        else:
            # Process all common image directories
            paths_to_process = [
                'main/images/',
                'updates/images/',
                'person_photos/',
                'services/',
                'downloads/'
            ]
        
        total_processed = 0
        total_saved = 0
        
        for path in paths_to_process:
            full_path = os.path.join(media_root, path)
            if not os.path.exists(full_path):
                self.stdout.write(
                    self.style.WARNING(f'Path not found: {path}')
                )
                continue
            
            self.stdout.write(f'\nProcessing: {path}')
            
            # Find images in directory
            image_files = []
            for file in os.listdir(full_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                    image_files.append(file)
            
            if not image_files:
                self.stdout.write('   No images found')
                continue
            
            for filename in image_files:
                file_path = os.path.join(full_path, filename)
                
                try:
                    # Analyze current image
                    with Image.open(file_path) as img:
                        current_size = os.path.getsize(file_path) / 1024
                        width, height = img.size
                        
                        # Determine image type based on filename or dimensions
                        image_type = self.detect_image_type(filename, width, height)
                        
                        if image_type not in specs:
                            self.stdout.write(
                                self.style.WARNING(f'   Unknown type: {filename}')
                            )
                            continue
                        
                        spec = specs[image_type]
                        
                        # Check if optimization is needed
                        needs_optimization = (
                            width != spec['size'][0] or 
                            height != spec['size'][1] or 
                            current_size > spec['max_kb'] or
                            img.format != spec['format']
                        )
                        
                        if not needs_optimization:
                            self.stdout.write(f'   OK {filename} (already optimized)')
                            continue
                        
                        if options['dry_run']:
                            self.stdout.write(
                                self.style.WARNING(f'   Would optimize: {filename}')
                            )
                            self.stdout.write(f'      Current: {width}x{height}, {current_size:.1f}KB')
                            self.stdout.write(f'      Target: {spec["size"][0]}x{spec["size"][1]}, max {spec["max_kb"]}KB')
                            continue
                        
                        # Create backup
                        backup_path = file_path + '.backup'
                        if not os.path.exists(backup_path):
                            import shutil
                            shutil.copy2(file_path, backup_path)
                        
                        # Optimize image
                        optimized_path = file_path + '.optimized'
                        success = self.optimize_image(file_path, optimized_path, spec)
                        
                        if success:
                            # Replace original with optimized version
                            os.replace(optimized_path, file_path)
                            new_size = os.path.getsize(file_path) / 1024
                            saved = current_size - new_size
                            
                            self.stdout.write(
                                self.style.SUCCESS(f'   OK {filename}: {current_size:.1f}KB -> {new_size:.1f}KB (saved {saved:.1f}KB)')
                            )
                            total_processed += 1
                            total_saved += saved
                        else:
                            # Remove failed optimization
                            if os.path.exists(optimized_path):
                                os.remove(optimized_path)
                            self.stdout.write(
                                self.style.ERROR(f'   FAILED to optimize: {filename}')
                            )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   ERROR processing {filename}: {e}')
                    )
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run completed - no changes made'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Optimization complete!')
            )
            self.stdout.write(f'   Processed: {total_processed} images')
            self.stdout.write(f'   Space saved: {total_saved:.1f}KB')
    
    def detect_image_type(self, filename, width, height):
        """Detect image type based on filename and dimensions"""
        filename_lower = filename.lower()
        
        if 'hero' in filename_lower or (width >= 1800 and height >= 1000):
            return 'hero'
        elif 'logo' in filename_lower or (width <= 400 and height <= 200):
            return 'logo'
        elif 'team' in filename_lower or 'person' in filename_lower or (width == height and width <= 500):
            return 'team'
        elif 'service' in filename_lower or (600 <= width <= 800 and 400 <= height <= 600):
            return 'service'
        else:
            return 'news'  # Default fallback
    
    def optimize_image(self, input_path, output_path, spec):
        """Optimize image according to specifications"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    if spec['format'] == 'JPEG':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    else:
                        img = img.convert('RGBA')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image maintaining aspect ratio
                img = ImageOps.fit(img, spec['size'], Image.Resampling.LANCZOS)
                
                # Save with optimization
                save_kwargs = {
                    'format': spec['format'],
                    'optimize': True,
                    'quality': 85
                }
                
                if spec['format'] == 'JPEG':
                    save_kwargs['progressive'] = True
                
                img.save(output_path, **save_kwargs)
                
                # Check file size
                file_size_kb = os.path.getsize(output_path) / 1024
                return file_size_kb <= spec['max_kb']
        
        except Exception:
            return False
