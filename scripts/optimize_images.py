#!/usr/bin/env python
"""
Image optimization script for the Django project
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse

def optimize_image(input_path, output_path=None, quality=85, max_width=1920, max_height=1080):
    """
    Optimize an image by resizing and compressing
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new dimensions maintaining aspect ratio
            original_width, original_height = img.size
            ratio = min(max_width / original_width, max_height / original_height)
            
            if ratio < 1:
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            if output_path is None:
                output_path = input_path
            
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # Get file sizes
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            savings = ((original_size - optimized_size) / original_size) * 100
            
            return {
                'success': True,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings_percent': savings,
                'new_dimensions': img.size
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def optimize_directory(directory_path, quality=85, max_width=1920, max_height=1080, backup=True):
    """
    Optimize all images in a directory
    """
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory {directory_path} does not exist!")
        return
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    optimized_count = 0
    total_savings = 0
    total_original_size = 0
    
    print(f"Optimizing images in {directory_path}...")
    print(f"Quality: {quality}%, Max dimensions: {max_width}x{max_height}")
    print("-" * 60)
    
    for file_path in directory.rglob('*'):
        if file_path.suffix.lower() in image_extensions:
            print(f"Processing: {file_path.name}")
            
            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
                if not backup_path.exists():
                    import shutil
                    shutil.copy2(file_path, backup_path)
            
            # Optimize image
            result = optimize_image(file_path, quality=quality, max_width=max_width, max_height=max_height)
            
            if result['success']:
                optimized_count += 1
                total_savings += result['savings_percent']
                total_original_size += result['original_size']
                
                print(f"  ✓ Optimized: {result['original_size']:,} → {result['optimized_size']:,} bytes "
                      f"({result['savings_percent']:.1f}% savings)")
                print(f"  ✓ Dimensions: {result['new_dimensions']}")
            else:
                print(f"  ✗ Error: {result['error']}")
            
            print()
    
    if optimized_count > 0:
        avg_savings = total_savings / optimized_count
        print("-" * 60)
        print(f"Optimization complete!")
        print(f"Images processed: {optimized_count}")
        print(f"Average savings: {avg_savings:.1f}%")
        print(f"Total original size: {total_original_size:,} bytes")
        print(f"Estimated total savings: {total_original_size * (avg_savings / 100):,.0f} bytes")
    else:
        print("No images were optimized.")

def create_webp_versions(directory_path, quality=80):
    """
    Create WebP versions of images for better web performance
    """
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory {directory_path} does not exist!")
        return
    
    image_extensions = {'.jpg', '.jpeg', '.png'}
    webp_count = 0
    
    print(f"Creating WebP versions in {directory_path}...")
    print("-" * 60)
    
    for file_path in directory.rglob('*'):
        if file_path.suffix.lower() in image_extensions:
            webp_path = file_path.with_suffix('.webp')
            
            if not webp_path.exists():
                try:
                    with Image.open(file_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        img.save(webp_path, 'WebP', quality=quality, optimize=True)
                        
                        original_size = os.path.getsize(file_path)
                        webp_size = os.path.getsize(webp_path)
                        savings = ((original_size - webp_size) / original_size) * 100
                        
                        print(f"Created WebP: {file_path.name} → {webp_path.name}")
                        print(f"  Size: {original_size:,} → {webp_size:,} bytes ({savings:.1f}% savings)")
                        webp_count += 1
                        
                except Exception as e:
                    print(f"Error creating WebP for {file_path.name}: {e}")
    
    print(f"\nCreated {webp_count} WebP versions.")

def main():
    parser = argparse.ArgumentParser(description='Optimize images for web performance')
    parser.add_argument('path', help='Path to image file or directory')
    parser.add_argument('--quality', type=int, default=85, help='JPEG quality (1-100)')
    parser.add_argument('--max-width', type=int, default=1920, help='Maximum width')
    parser.add_argument('--max-height', type=int, default=1080, help='Maximum height')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups')
    parser.add_argument('--webp', action='store_true', help='Create WebP versions')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        # Single file
        result = optimize_image(path, quality=args.quality, 
                              max_width=args.max_width, max_height=args.max_height)
        if result['success']:
            print(f"Optimized {path.name}")
            print(f"Size: {result['original_size']:,} → {result['optimized_size']:,} bytes")
            print(f"Savings: {result['savings_percent']:.1f}%")
        else:
            print(f"Error: {result['error']}")
    
    elif path.is_dir():
        # Directory
        optimize_directory(path, quality=args.quality, 
                         max_width=args.max_width, max_height=args.max_height,
                         backup=not args.no_backup)
        
        if args.webp:
            create_webp_versions(path, quality=args.quality)
    
    else:
        print(f"Path {args.path} does not exist!")

if __name__ == '__main__':
    main()