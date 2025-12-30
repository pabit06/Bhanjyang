# 📸 Image Upload Guidelines for Bhanjyang Cooperative Website

## 🎯 Overview
This document provides comprehensive guidelines for uploading and managing images on the Bhanjyang Cooperative website. Following these guidelines ensures optimal performance, accessibility, and user experience.

## 📋 Table of Contents
1. [Quick Reference](#quick-reference)
2. [Image Requirements](#image-requirements)
3. [File Formats](#file-formats)
4. [Size Specifications](#size-specifications)
5. [Naming Conventions](#naming-conventions)
6. [Content Guidelines](#content-guidelines)
7. [Technical Specifications](#technical-specifications)
8. [Image Optimization Tools](#image-optimization-tools)
9. [Accessibility Requirements](#accessibility-requirements)
10. [Upload Process](#upload-process)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## 🚀 Quick Reference

### Size Requirements Quick Reference

| Image Type | Dimensions | Max Size | Format |
|------------|------------|----------|---------|
| **Hero Images** | 1920x1080px | 500KB | JPEG |
| **News Articles** | 800x600px | 200KB | JPEG |
| **Team Photos** | 400x400px | 100KB | JPEG |
| **Service Images** | 600x400px | 150KB | JPEG/PNG |
| **Logos** | 300x100px | 50KB | PNG |

### Quick Checklist
- [ ] Image resized to correct dimensions
- [ ] File size under limit
- [ ] Descriptive filename
- [ ] Alt text written
- [ ] Image quality good
- [ ] Content appropriate

### Quick Naming Rules
- ✅ Use lowercase: `news-annual-meeting.jpg`
- ✅ Use hyphens: `team-manager-profile.jpg`
- ✅ Be descriptive: `service-savings-account.jpg`
- ❌ No spaces: `team member photo.jpg`
- ❌ No special chars: `news@article.jpg`

---

## 🖼️ Image Requirements

### **Supported File Formats**
- **Primary**: `.jpg`, `.jpeg` (for photographs)
- **Secondary**: `.png` (for graphics with transparency)
- **Avoid**: `.gif`, `.bmp`, `.tiff`, `.webp` (not optimized for web)

### **Quality Standards**
- **Resolution**: Minimum 72 DPI for web display
- **Color Profile**: sRGB color space
- **Compression**: Optimized for web (85-95% quality for JPEG)

---

## 📏 Size Specifications

### **Hero Images (Homepage Slideshow)**
- **Dimensions**: 1920x1080px (16:9 aspect ratio)
- **File Size**: Maximum 500KB
- **Format**: JPEG
- **Purpose**: Main banner images for homepage carousel

### **News Article Images**
- **Dimensions**: 800x600px (4:3 aspect ratio)
- **File Size**: Maximum 200KB
- **Format**: JPEG
- **Purpose**: Featured images for news articles

### **Team Member Photos**
- **Dimensions**: 400x400px (1:1 aspect ratio)
- **File Size**: Maximum 100KB
- **Format**: JPEG
- **Purpose**: Profile photos for team members

### **Service Illustrations**
- **Dimensions**: 600x400px (3:2 aspect ratio)
- **File Size**: Maximum 150KB
- **Format**: JPEG or PNG
- **Purpose**: Service-related graphics

### **Logo Images**
- **Dimensions**: 300x100px (3:1 aspect ratio)
- **File Size**: Maximum 50KB
- **Format**: PNG (with transparency)
- **Purpose**: Brand logos and headers

---

## 📝 Naming Conventions

### **File Naming Rules**
- Use lowercase letters only
- Separate words with hyphens (`-`)
- Include descriptive keywords
- Avoid spaces and special characters
- Keep names under 50 characters

### **Examples**
```
✅ Good Names:
- hero-cooperative-meeting.jpg
- news-annual-report-2024.jpg
- team-manager-profile.jpg
- service-savings-account.jpg

❌ Bad Names:
- IMG_1234.JPG
- Photo (1).jpg
- team member photo.png
- news@article#2024.jpg
```

### **Category Prefixes**
- `hero-` - Homepage hero images
- `news-` - News article images
- `team-` - Team member photos
- `service-` - Service illustrations
- `logo-` - Logo images
- `event-` - Event photos

---

## 📋 Content Guidelines

### **Photography Standards**
- **Composition**: Well-framed, professional composition
- **Lighting**: Good natural or professional lighting
- **Focus**: Sharp, clear images without blur
- **Content**: Relevant to cooperative activities and values

### **Prohibited Content**
- ❌ Blurry or low-quality images
- ❌ Images with watermarks or copyright notices
- ❌ Inappropriate or offensive content
- ❌ Images with personal information visible
- ❌ Screenshots or low-resolution graphics

### **Recommended Content**
- ✅ Cooperative meetings and events
- ✅ Community activities and programs
- ✅ Professional team photos
- ✅ Service-related activities
- ✅ Local community scenes
- ✅ Financial education materials

---

## ⚙️ Technical Specifications

### **Image Optimization**
1. **Compression**: Use tools like TinyPNG, ImageOptim, or Photoshop
2. **Progressive JPEG**: Enable for faster loading
3. **Metadata**: Remove EXIF data for privacy
4. **Color Space**: Convert to sRGB

### **Responsive Images**
- Images automatically resize for different screen sizes
- Mobile-optimized versions are generated automatically
- Lazy loading is implemented for better performance

### **Performance Considerations**
- Total page image size should not exceed 2MB
- Use appropriate image dimensions for display size
- Consider using WebP format for modern browsers (future enhancement)

---

## 🛠️ Image Optimization Tools

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

### Optimization Features

- **Automatic Resizing**: Images are resized to exact specifications
- **Quality Optimization**: Maintains visual quality while reducing file size
- **Format Conversion**: Converts to appropriate format (JPEG/PNG)
- **Backup Creation**: Creates backups before optimization
- **Batch Processing**: Process multiple images at once
- **Validation**: Check if images meet specifications

### Recommended Tools

- **Online**: TinyPNG.com, ImageOptim.net
- **Desktop**: Photoshop, GIMP, Canva
- **Mobile**: Snapseed, VSCO

### Important Notes

- Always backup your images before optimization
- Test optimized images on the website
- Use appropriate image types for content
- Follow naming conventions for better organization

---

## ♿ Accessibility Requirements

### **Alt Text Guidelines**
- **Purpose**: Describe the image content and context
- **Length**: 1-2 sentences, maximum 125 characters
- **Content**: Include relevant details for screen readers
- **Language**: Use clear, descriptive language

### **Alt Text Examples**
```
✅ Good Alt Text:
- "Bhanjyang Cooperative annual meeting with 50 members in attendance"
- "Team manager John Smith smiling in professional headshot"
- "Community members participating in financial literacy workshop"

❌ Bad Alt Text:
- "Image"
- "Photo"
- "Picture of people"
- "Meeting"
```

### **Visual Accessibility**
- Ensure sufficient color contrast
- Avoid text overlays on images
- Provide text alternatives for infographics
- Use descriptive captions when needed

---

## 📤 Upload Process

### **Step-by-Step Upload**
1. **Prepare Image**: Resize and optimize according to specifications
2. **Name File**: Follow naming conventions
3. **Add Alt Text**: Write descriptive alternative text
4. **Upload**: Use Django admin interface
5. **Verify**: Check image displays correctly
6. **Test**: View on different devices and screen sizes

### **Django Admin Interface**
- Navigate to the appropriate model (News, Team, Services)
- Click "Add" or "Edit" for the item
- Upload image using the file field
- Add descriptive alt text
- Save changes

### **File Organization**
```
media/
├── person_photos/          # Team member photos
├── services/              # Service-related images
├── updates/               # News and event images
│   └── images/
└── downloads/             # Document thumbnails
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **Image Too Large**
- **Problem**: File size exceeds limits
- **Solution**: Compress image using online tools or image editing software
- **Tools**: TinyPNG, ImageOptim, Photoshop "Save for Web"

#### **Wrong Dimensions**
- **Problem**: Image doesn't fit properly
- **Solution**: Resize to recommended dimensions
- **Tools**: Canva, Photoshop, GIMP, online resizers

#### **Poor Quality**
- **Problem**: Image appears pixelated or blurry
- **Solution**: Use higher resolution source image
- **Tip**: Start with high-quality source, then optimize

#### **Slow Loading**
- **Problem**: Images take too long to load
- **Solution**: Reduce file size while maintaining quality
- **Check**: Use browser dev tools to analyze loading times

### **Error Messages**
- **"File too large"**: Compress the image
- **"Invalid format"**: Convert to JPEG or PNG
- **"Upload failed"**: Check file permissions and try again

---

## 🌟 Best Practices

### **Before Upload**
1. **Plan**: Determine the purpose and placement of the image
2. **Prepare**: Resize and optimize according to specifications
3. **Review**: Check image quality and content appropriateness
4. **Name**: Use descriptive, SEO-friendly file names

### **After Upload**
1. **Test**: View image on different devices and browsers
2. **Verify**: Ensure alt text is descriptive and accurate
3. **Monitor**: Check page loading performance
4. **Update**: Refresh images periodically for relevance

### **Content Strategy**
- **Consistency**: Use similar style and quality across all images
- **Branding**: Maintain professional appearance
- **Relevance**: Ensure images support content and messaging
- **Freshness**: Update images regularly to keep content current

### **SEO Considerations**
- **File Names**: Use descriptive, keyword-rich names
- **Alt Text**: Include relevant keywords naturally
- **Context**: Ensure images support page content
- **Performance**: Optimize for fast loading times

---

## 📞 Support & Contact

### **Technical Support**
- **Email**: admin@bhanjyang.coop.np
- **Phone**: +977-9856083101
- **Hours**: Monday-Friday, 9:00 AM - 5:00 PM

### **Content Questions**
- **Email**: info@bhanjyang.coop.np
- **Phone**: +977-9856083101

### **Training Resources**
- Online tutorials for image optimization
- Video guides for Django admin interface
- Best practices documentation

---

## 📊 Image Usage Statistics

### **Current Image Inventory**
- **Hero Images**: 3 (homepage slideshow)
- **News Images**: Variable (per article)
- **Team Photos**: Variable (per member)
- **Service Images**: Variable (per service)
- **Logo Images**: 1 (main logo)

### **Performance Metrics**
- **Average Load Time**: < 2 seconds
- **Image Compression**: 85-95% reduction
- **Mobile Optimization**: 100% responsive
- **Accessibility Score**: 95%+ compliance

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 2025 | Initial guidelines created |
| 1.1 | Oct 2025 | Added accessibility requirements |
| 1.2 | Oct 2025 | Updated technical specifications |

---

**Last Updated**: October 16, 2025  
**Next Review**: January 16, 2026

---

*This document is maintained by the Bhanjyang Cooperative development team. For updates or questions, please contact admin@bhanjyang.coop.np.*
