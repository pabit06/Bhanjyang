# Downloads App User Guide
# (Downloads App प्रयोगकर्ता गाइड)

**Version:** 2.0.1  
**Last Updated:** January 21, 2026  
**Status:** ✅ Production Ready  
**Audience:** End Users, Administrators, Developers

---

## 📖 Table of Contents

1. [For End Users](#for-end-users)
2. [For Administrators](#for-administrators)
3. [For Developers](#for-developers)
4. [REST API Usage](#rest-api-usage) ✅ **NEW**
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)
8. [What's New in v2.0](#whats-new-in-v20) ✅ **NEW**

---

## 👥 For End Users

### Accessing Downloads

1. **Navigate to Downloads Page:**
   - Click "Downloads" in main menu
   - Or visit: `https://bhanjyang.coop/downloads/`

2. **Browse Files:**
   - Files are organized by category
   - Categories: Forms, Reports, Policies, Publications, etc.

3. **Search Files:**
   - Use search bar at top
   - Search by title, description, or tags
   - Example: "application form"

4. **Filter Files:**
   - By Category: Click category name
   - By Priority: High/Medium/Low
   - Featured Files: Toggle featured filter

### Downloading Files

**Simple Download:**
1. Find the file you want
2. Click the file title or "Download" button
3. File will download to your default folder

**Login-Required Files:**
1. Some files require login (🔒 icon shown)
2. Click file → redirected to login
3. After login → file downloads automatically

**Bulk Download:**
1. Select multiple files (checkbox)
2. Click "Download Selected" button
3. **Small downloads (<10 files)**: ZIP created immediately
4. **Large downloads (10+ files)**: Processed asynchronously
   - You'll receive an email when ZIP is ready
   - Or check download status via API
5. Download ZIP file

**Note:** Rate limit applies to bulk downloads (5 per day per user)

### File Information

**Understanding File Cards:**
```
┌─────────────────────────────────┐
│ 📁 Category Badge               │
│ ⭐ Featured (if applicable)     │
│                                  │
│ File Title                       │
│ Description...                   │
│                                  │
│ 📊 2.5 MB  |  PDF                │
│ 👁️ 150 views  |  ⬇️ 45 downloads │
│ 📅 Uploaded: Jan 1, 2024        │
│ 🔒 Login Required (if yes)       │
│                                  │
│ [📥 Download]  [ℹ️ Details]     │
└─────────────────────────────────┘
```

---

## 👨‍💼 For Administrators

### Uploading Files

**Via Django Admin:**

1. **Access Admin Panel:**
   - Visit: `/admin/`
   - Login with admin credentials

2. **Navigate to Downloads:**
   - Click "Downloads" in sidebar
   - Click "Downloadable Files"
   - Click "Add Downloadable File"

3. **Fill Form:**
   ```
   Required Fields:
   - Category: Select from dropdown
   - Title: Descriptive name
   - File: Upload file
   
   Optional Fields:
   - Description: Details about file
   - Priority: High/Medium/Low/Urgent
   - Is Featured: Check to feature
   - Requires Login: Check if login needed
   - Expires At: Set expiration date
   - Tags: Comma-separated tags
   - Thumbnail: Upload preview image
   ```

4. **Save:**
   - Click "Save and continue editing" OR
   - Click "Save and add another" OR
   - Click "Save"

### Managing Files

**Edit File:**
1. Go to Downloads admin
2. Click file title
3. Modify fields
4. Save changes

**Delete File:**
1. Select file(s) with checkbox
2. Choose "Delete selected" from dropdown
3. Confirm deletion

**Bulk Actions:**
1. Select multiple files
2. Choose action:
   - Mark as featured
   - Mark as not featured
   - Set to require login
   - Delete selected

### Best Practices

**File Organization:**
- Use clear, descriptive titles
- Add detailed descriptions
- Tag files appropriately
- Set correct category
- Set priorities correctly

**Security:**
- Mark sensitive files as "requires_login"
- Set expiration dates for temporary files
- Review uploaded files regularly
- Monitor download patterns
- Review security audit logs weekly
- Check IP blacklist monthly
- Monitor rate limit violations
- Verify file integrity checks are working

**Maintenance:**
- Clean up expired files monthly
- Archive old files
- Update outdated documents
- Check broken links

---

## 💻 For Developers

### Development Setup

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install ClamAV:**
```bash
# Ubuntu/Debian
sudo apt-get install clamav clamav-daemon

# macOS
brew install clamav

# Start daemon
sudo freshclam
sudo service clamav-daemon start
```

3. **Configure Settings:**
```python
# config/settings.py
DOWNLOADS_SETTINGS = {
    'ENABLE_VIRUS_SCAN': True,
    'MAX_FILE_SIZE': 50 * 1024 * 1024,
    'ALLOWED_EXTENSIONS': ['pdf', 'doc', ...],
}
```

4. **Run Migrations:**
```bash
python manage.py makemigrations downloads
python manage.py migrate downloads
```

### Adding New Features

**1. Create Service Method:**
```python
# apps/downloads/services.py
class DownloadsService:
    @staticmethod
    def new_feature():
        # Business logic here
        pass
```

**2. Create View:**
```python
# apps/downloads/views.py
def new_view(request):
    result = DownloadsService.new_feature()
    return render(request, 'template.html', {'data': result})
```

**3. Add URL:**
```python
# apps/downloads/urls.py
urlpatterns = [
    path('new-feature/', views.new_view, name='new-feature'),
]
```

**4. Write Tests:**
```python
# apps/downloads/tests/test_new_feature.py
class NewFeatureTestCase(TestCase):
    def test_new_feature(self):
        # Test code here
        pass
```

### Code Style

**Follow PEP 8:**
```python
# Good
def process_file_download(request, file_obj):
    """Process file download with security checks."""
    pass

# Bad
def processFileDownload(req, fileObj):    # Don't use camelCase
    pass    # Missing docstring
```

**Type Hints (Required):**
```python
from typing import Tuple, Optional, Dict, Any
from django.http import HttpRequest

def validate_file(file: UploadedFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    pass
```

**Using the API:**
```python
# apps/downloads/api_views.py
from rest_framework import viewsets
from .models import DownloadableFile
from .serializers import DownloadableFileSerializer

class DownloadableFileViewSet(viewsets.ModelViewSet):
    queryset = DownloadableFile.objects.all()
    serializer_class = DownloadableFileSerializer
```

**Security Best Practices:**
```python
# Always use security features
from apps.downloads.security_enhanced import (
    IPBlacklistManager,
    RateLimitManager,
    SecurityAuditEnhancedLogger
)

# Check IP blacklist
if IPBlacklistManager.is_blacklisted(client_ip):
    return HttpResponseForbidden()

# Check rate limit
allowed, count, reset = RateLimitManager.check_rate_limit(
    identifier=user_id,
    action='download'
)

# Log security events
SecurityAuditEnhancedLogger.log_download(user, file_obj, ip_address)
```

---

## 🔧 Common Tasks

### Task 1: Upload a New Form

**Goal:** Add a membership application form

**Steps:**
1. Login to admin (`/admin/`)
2. Go to Downloads → Downloadable Files
3. Click "Add"
4. Fill in:
   - Category: Form
   - Title: "Membership Application Form 2024"
   - Description: "Fill out to become a member"
   - File: Upload PDF
   - Priority: High
   - Is Featured: ✓
   - Tags: "membership, application, form"
5. Save

**Result:** Form appears in Featured section and Forms category

### Task 2: Make a File Login-Required

**Goal:** Restrictinternal policy document

**Steps:**
1. Find file in admin
2. Check "Requires login"
3. Save

**Result:** Users must login before downloading

### Task 3: Set File Expiration

**Goal:** Temporary announcement valid until Feb 1

**Steps:**
1. Edit file
2. Set "Expires at": 2024-02-01 00:00
3. Save

**Result:** File auto-hides after expiration

### Task 4: Bulk Download Multiple Reports

**Goal:** Download all annual reports

**Steps:**
1. Go to Downloads page
2. Filter: Category = Reports
3. Check boxes for desired files
4. Click "Download Selected" button
5. Download ZIP file

**Result:** All reports in one ZIP

### Task 5: Find Most Popular Files

**Goal:** See what members download most

**Steps:**
1. Admin → Downloads → Downloadable Files
2. Click "Download count" column header
3. Files sorted by popularity

**Result:** Top downloads at top of list

### Task 6: Use REST API to Download Files ✅ **NEW**

**Goal:** Automate file downloads via API

**Steps:**
1. Get authentication token (if needed)
2. Use API endpoint: `GET /api/downloads/files/`
3. Filter/search as needed
4. Download via: `POST /api/downloads/files/{id}/download/`

**Example:**
```python
import requests

# List files
response = requests.get('http://example.com/api/downloads/files/?category=FRM')
files = response.json()['results']

# Download file
file_id = files[0]['id']
response = requests.post(
    f'http://example.com/api/downloads/files/{file_id}/download/',
    headers={'Authorization': 'Token your-token'}
)
```

**Result:** Programmatic access to files

---

## 🔍 Troubleshooting

### Problem: File Won't Upload

**Symptoms:**
- Upload button doesn't work
- Error message appears
- File rejected

**Solutions:**

1. **Check File Size:**
   - Max: 50MB
   - Solution: Compress file or split into parts

2. **Check File Type:**
   - Allowed: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, JPG, PNG
   - Solution: Convert to allowed format

3. **Check Virus Scan:**
   - ClamAV might have detected virus
   - Solution: Scan file locally first

4. **Check Permissions:**
   - Must be admin
   - Solution: Contact system admin

### Problem: Download Won't Start

**Symptoms:**
- Click download, nothing happens
- Error page appears
- Redirect loop

**Solutions:**

1. **Login Required:**
   - File marked as login-required
   - Solution: Login first

2. **File Expired:**
   - File past expiration date
   - Solution: Contact admin for updated version

3. **Browser Cache:**
   - Old cached data interfering
   - Solution: Clear cache (Ctrl+Shift+Delete)

4. **Rate Limit:**
   - Too many downloads (20 per hour limit)
   - Solution: Wait an hour, try again
   - Note: Rate limits apply per user and per IP address

5. **File Integrity Check:**
   - File may have been tampered with
   - Solution: Contact admin to re-upload file

6. **Virus Detection:**
   - File failed virus scan on download
   - Solution: Contact admin immediately

### Problem: Search Not Working

**Symptoms:**
- Search returns no results
- Wrong files appear

**Solutions:**

1. **Check Spelling:**
   - Typos in search term
   - Solution: Try different keywords

2. **File Inactive:**
   - File exists but marked inactive
   - Solution: Only admins can see inactive files

3. **Case Sensitivity:**
   - Search might be case-sensitive
   - Solution: Try lowercase

### Problem: Bulk Download Fails

**Symptoms:**
- ZIP creation times out
- Incomplete ZIP file
- Error message

**Solutions:**

1. **Too Many Files:**
   - Limit: 20 files per ZIP
   - Solution: Select fewer files

2. **Files Too Large:**
   - Total size too big
   - Solution: Download individually

3. **Server Timeout:**
   - Processing taking too long
   - Solution: Try again later or contact admin

---

## ❓ FAQ

### General

**Q: How do I access the downloads page?**  
A: Click "Downloads" in the main menu or visit `/downloads/`

**Q: Are all files free to download?**  
A: Yes, but some require login for members only.

**Q: Can I download files on my phone?**  
A: Yes, the page is mobile-responsive.

**Q: How often are new files added?**  
A: Regularly. Check back weekly for updates.

### For Members

**Q: Why do some files require login?**  
A: Member-only documents (reports, policies) require authentication.

**Q: Can I download multiple files at once?**  
A: Yes, use the bulk download feature (select files, click "Download Selected").

**Q: How long are files available?**  
A: Most files are permanent. Temporary files show expiration date.

**Q: Can I share downloaded files?**  
A: Personal use only. Don't share member-only documents publicly.

### For Admins

**Q: How do I know if a file has been downloaded?**  
A: Check the download count in the admin panel.

**Q: Can I track who downloaded what?**  
A: Yes, check audit logs (requires admin access).

**Q: How do I remove old files?**  
A: Use the "cleanup_expired_files" management command or delete manually.

**Q: What's the maximum file size?**  
A: 50MB by default. Change in settings if needed.

**Q: How does bulk download work for large files?**  
A: Large bulk downloads (10+ files) are processed asynchronously. You'll receive an email when the ZIP is ready.

**Q: Are files served securely?**  
A: Yes, all files are served through secure Django views with access control, integrity checks, and virus scanning.

**Q: How do I feature a file?**  
A: Edit file, check "Is featured" box, save.

### Technical

**Q: What file formats are supported?**  
A: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, JPG, JPEG, PNG

**Q: Are files scanned for viruses?**  
A: Yes, ClamAV scans all uploads automatically.

**Q: Where are files stored?**  
A: Secure server storage (configurable: local or cloud).

**Q: Can files be edited after upload?**  
A: Admins can replace files by re-uploading.

---

## 🌐 REST API Usage ✅ **NEW**

### Overview

The Downloads app provides a complete REST API for programmatic access to files.

### Authentication

**For Public Access:**
- Read operations (list, detail) are public
- No authentication required

**For Admin Operations:**
- Write operations require admin authentication
- Use Django REST Framework authentication (Token, Session, etc.)

### API Endpoints

**List Files:**
```bash
GET /api/downloads/files/
```

**Query Parameters:**
- `category`: Filter by category (FRM, RPT, PCY, etc.)
- `priority`: Filter by priority (HIGH, MED, LOW, URG)
- `is_featured`: Filter featured files (true/false)
- `search`: Search in title, description, tags
- `ordering`: Order by field (-uploaded_at, download_count, etc.)

**Example:**
```bash
GET /api/downloads/files/?category=FRM&priority=HIGH&search=application
```

**Get File Details:**
```bash
GET /api/downloads/files/{id}/
```

**Download File:**
```bash
POST /api/downloads/files/{id}/download/
```

**Get Featured Files:**
```bash
GET /api/downloads/files/featured/
```

**Get Statistics (Admin Only):**
```bash
GET /api/downloads/files/stats/
```

### Using the API

**Python Example:**
```python
import requests

# List files
response = requests.get('http://example.com/api/downloads/files/')
files = response.json()['results']

# Get file details
file_id = 1
response = requests.get(f'http://example.com/api/downloads/files/{file_id}/')
file_data = response.json()

# Download file (requires authentication)
headers = {'Authorization': 'Token your-token-here'}
response = requests.post(
    f'http://example.com/api/downloads/files/{file_id}/download/',
    headers=headers
)
```

**JavaScript Example:**
```javascript
// List files
fetch('/api/downloads/files/?category=FRM')
  .then(response => response.json())
  .then(data => {
    console.log('Files:', data.results);
  });

// Download file
fetch('/api/downloads/files/1/download/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log('Download URL:', data.file_url);
  });
```

### API Response Format

**List Response:**
```json
{
  "count": 100,
  "next": "http://example.com/api/downloads/files/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Application Form",
      "category": "FRM",
      "file_size": "2.5 MB",
      "download_count": 45,
      "file_url": "http://example.com/media/downloads/file.pdf"
    }
  ]
}
```

**File Detail Response:**
```json
{
  "id": 1,
  "title": "Application Form",
  "description": "Membership application form",
  "category": "FRM",
  "priority": "HIGH",
  "is_featured": true,
  "requires_login": false,
  "file_size": "2.5 MB",
  "download_count": 45,
  "view_count": 150,
  "uploaded_at": "2024-01-01T00:00:00Z",
  "file_url": "http://example.com/media/downloads/file.pdf"
}
```

For complete API documentation, see [README.md - API Section](README.md#-api).

---

## 🆕 What's New in v2.0 ✅ **NEW**

### Version 2.0.1 (January 21, 2026)

**Improvements:**
- ✅ Test coverage increased to 86%
- ✅ Fixed regression issues
- ✅ Enhanced stability
- ✅ Complete API documentation

### Version 2.0.0 (January 20, 2026)

**Major New Features:**

1. **REST API** ✅
   - Complete RESTful API with Django REST Framework
   - 11 endpoints for file management
   - Filtering, searching, and ordering support

2. **Enhanced Security** ✅
   - **File Integrity Verification**: SHA-256 hash verification on every download
   - **Virus Scanning on Download**: Files scanned before serving (not just on upload)
   - **IP Blacklisting**: Automatic blocking of malicious IPs
   - **Advanced Rate Limiting**: Per-user and per-IP rate limiting
   - **Security Headers**: CSP, X-Frame-Options, and more

3. **Performance Improvements** ✅
   - **Chunked Downloads**: Large files (50MB+) streamed efficiently
   - **Asynchronous Bulk Downloads**: Large ZIP files created in background
   - **CDN Support**: CloudFront/Cloudflare integration
   - **Performance Monitoring**: Comprehensive tracking and alerting

4. **Enhanced Features** ✅
   - **Secure File Serving**: All files served through Django views
   - **Structured Error Codes**: Consistent error handling
   - **Enhanced Logging**: Better audit trails
   - **Type Hints**: Full type hints throughout codebase

### Migration Guide

**For End Users:**
- No changes required - all features work the same
- New: Rate limiting (20 downloads/hour)
- New: Files automatically scanned on download

**For Administrators:**
- No changes required
- New: API available for automation
- New: Enhanced security logging

**For Developers:**
- See [README.md](README.md) for API documentation
- See [SECURITY.md](SECURITY.md) for security updates
- See [RATING.md](RATING.md) for quality assessment

---

## 📞 Support

**Need Help?**

- **Email:** info@bhanjyang.coop
- **Phone:** +977-9856083101
- **Hours:** Sun-Fri, 10 AM - 5 PM NPT

**Report Issues:**
- Security issues: info@bhanjyang.coop
- Bug reports: Create GitHub issue
- Feature requests: Contact development team

---

## 📚 Additional Resources

- [README.md](README.md) - Technical documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [SECURITY.md](SECURITY.md) - Security details
- [Django Admin Docs](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)

---

**Last Updated:** January 6, 2026  
**Version:** 1.0.0  
**Feedback:** We welcome your feedback! Contact us with suggestions.
