"""
Tests for Downloads app helper functions.
"""
from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpRequest
from django.utils import timezone
from datetime import timedelta

from apps.downloads.utils.helpers import (
    get_client_ip,
    format_file_size_display,
    sanitize_filename,
    is_recent_download,
    get_file_extension,
    validate_file_extension
)


class DownloadsHelpersTest(TestCase):
    """Test cases for Downloads helper functions"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
    
    def test_get_client_ip_from_request(self):
        """Test get_client_ip with HttpRequest object"""
        request = self.factory.get('/downloads/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_from_meta(self):
        """Test get_client_ip with META dictionary"""
        meta = {'REMOTE_ADDR': '10.0.0.1'}
        ip = get_client_ip(meta)
        self.assertEqual(ip, '10.0.0.1')
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test get_client_ip with X-Forwarded-For header"""
        request = self.factory.get('/downloads/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        # Untrusted X-Forwarded-For is ignored...
        with override_settings(TRUSTED_PROXY_COUNT=0):
            self.assertEqual(get_client_ip(request), '192.168.1.100')
        # ...and with one proxy in front, its appended entry is the client.
        with override_settings(TRUSTED_PROXY_COUNT=1):
            self.assertEqual(get_client_ip(request), '192.168.1.1')
    
    def test_format_file_size_display_bytes(self):
        """Test format_file_size_display with bytes"""
        self.assertEqual(format_file_size_display(0), "0 B")
        self.assertEqual(format_file_size_display(500), "500.0 B")
        self.assertEqual(format_file_size_display(1023), "1023.0 B")
    
    def test_format_file_size_display_kb(self):
        """Test format_file_size_display with KB"""
        self.assertEqual(format_file_size_display(1024), "1.0 KB")
        self.assertEqual(format_file_size_display(2048), "2.0 KB")
    
    def test_format_file_size_display_mb(self):
        """Test format_file_size_display with MB"""
        self.assertEqual(format_file_size_display(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size_display(2 * 1024 * 1024), "2.0 MB")
    
    def test_sanitize_filename_basic(self):
        """Test sanitize_filename with basic filename"""
        filename = "test_file.pdf"
        sanitized = sanitize_filename(filename)
        self.assertIn("test_file", sanitized)
        self.assertIn(".pdf", sanitized)
        self.assertNotEqual(filename, sanitized)  # Should have UUID prefix
    
    def test_sanitize_filename_with_path(self):
        """Test sanitize_filename removes directory path"""
        filename = "../../etc/passwd"
        sanitized = sanitize_filename(filename)
        self.assertNotIn("../", sanitized)
        self.assertNotIn("/", sanitized)
    
    def test_sanitize_filename_dangerous_chars(self):
        """Test sanitize_filename removes dangerous characters"""
        filename = "test<script>alert('xss')</script>.pdf"
        sanitized = sanitize_filename(filename)
        self.assertNotIn("<script>", sanitized)
        self.assertNotIn("alert", sanitized)
    
    def test_is_recent_download_recent(self):
        """Test is_recent_download with recent timestamp"""
        recent_time = timezone.now() - timedelta(hours=12)
        self.assertTrue(is_recent_download(recent_time, hours=24))
        self.assertTrue(is_recent_download(recent_time, hours=48))
    
    def test_is_recent_download_old(self):
        """Test is_recent_download with old timestamp"""
        old_time = timezone.now() - timedelta(hours=48)
        self.assertFalse(is_recent_download(old_time, hours=24))
        self.assertFalse(is_recent_download(old_time, hours=36))
    
    def test_is_recent_download_none(self):
        """Test is_recent_download with None"""
        self.assertFalse(is_recent_download(None))
    
    def test_get_file_extension_basic(self):
        """Test get_file_extension with basic filenames"""
        self.assertEqual(get_file_extension("test.pdf"), "pdf")
        self.assertEqual(get_file_extension("document.docx"), "docx")
        self.assertEqual(get_file_extension("image.jpg"), "jpg")
    
    def test_get_file_extension_uppercase(self):
        """Test get_file_extension converts to lowercase"""
        self.assertEqual(get_file_extension("test.PDF"), "pdf")
        self.assertEqual(get_file_extension("document.DOCX"), "docx")
    
    def test_validate_file_extension_valid(self):
        """Test validate_file_extension with valid extensions"""
        allowed = ['.pdf', '.doc', '.docx', '.jpg']
        self.assertTrue(validate_file_extension("test.pdf", allowed))
        self.assertTrue(validate_file_extension("document.docx", allowed))
        self.assertTrue(validate_file_extension("image.JPG", allowed))  # Case insensitive
    
    def test_validate_file_extension_invalid(self):
        """Test validate_file_extension with invalid extensions"""
        allowed = ['.pdf', '.doc', '.docx']
        self.assertFalse(validate_file_extension("test.exe", allowed))
        self.assertFalse(validate_file_extension("script.php", allowed))
