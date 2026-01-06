# Downloads App User Guide
# (Downloads App प्रयोगकर्ता गाइड)

**Version:** 1.0.0  
**Audience:** End Users, Administrators, Developers

---

## 📖 Table of Contents

1. [For End Users](#for-end-users)
2. [For Administrators](#for-administrators)
3. [For Developers](#for-developers)
4. [Common Tasks](#common-tasks)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

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
3. Wait for ZIP creation
4. Download ZIP file

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

**Type Hints:**
```python
from typing import Tuple, Optional

def validate_file(file: UploadedFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    pass
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
   - Too many downloads
   - Solution: Wait an hour, try again

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

## 📞 Support

**Need Help?**

- **Email:** tech@bhanjyang.coop
- **Phone:** +977-9856083101
- **Hours:** Sun-Fri, 10 AM - 5 PM NPT

**Report Issues:**
- Security issues: security@bhanjyang.coop
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
