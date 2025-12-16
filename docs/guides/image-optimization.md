# 🖼️ Image Optimization Tools

This directory contains tools to help optimize images for the Bhanjyang Cooperative website according to our guidelines.

## 📁 Files

- `IMAGE_UPLOAD_GUIDELINES.md` - Comprehensive guidelines for image uploads
- `IMAGE_UPLOAD_QUICK_REFERENCE.md` - Quick reference card for content managers
- `optimize_images.py` - Standalone Python script for image optimization
- `main/management/commands/optimize_images.py` - Django management command

## 🚀 Usage

### Django Management Command (Recommended)

```bash
# Optimize all images
python manage.py optimize_images

# Optimize specific type
python manage.py optimize_images --type hero
python manage.py optimize_images --type news
python manage.py optimize_images --type team

# Optimize specific path
python manage.py optimize_images --path person_photos/

# Dry run (see what would be optimized)
python manage.py optimize_images --dry-run
```

### Standalone Python Script

```bash
# Optimize single image
python optimize_images.py optimize input.jpg output.jpg --type hero

# Batch optimize directory
python optimize_images.py batch input_dir/ output_dir/ --type news

# Validate image
python optimize_images.py validate image.jpg --type team
```

## 📏 Image Specifications

| Type | Dimensions | Max Size | Format |
|------|------------|----------|---------|
| Hero | 1920x1080px | 500KB | JPEG |
| News | 800x600px | 200KB | JPEG |
| Team | 400x400px | 100KB | JPEG |
| Service | 600x400px | 150KB | JPEG/PNG |
| Logo | 300x100px | 50KB | PNG |

## 🔧 Features

- **Automatic Resizing**: Images are resized to exact specifications
- **Quality Optimization**: Maintains visual quality while reducing file size
- **Format Conversion**: Converts to appropriate format (JPEG/PNG)
- **Backup Creation**: Creates backups before optimization
- **Batch Processing**: Process multiple images at once
- **Validation**: Check if images meet specifications

## ⚠️ Important Notes

- Always backup your images before optimization
- Test optimized images on the website
- Use appropriate image types for content
- Follow naming conventions for better organization

## 📞 Support

For questions or issues with image optimization:
- Email: admin@bhanjyang.coop.np
- Phone: +977-9856083101
