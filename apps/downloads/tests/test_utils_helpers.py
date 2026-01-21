"""
Tests for downloads utils helpers module
"""
from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
import os

from apps.downloads.utils.helpers import (
    get_client_ip,
    format_file_size_display,
    sanitize_filename,
    is_recent_download,
    get_file_extension,
    validate_file_extension
)

class UtilsHelpersTest(TestCase):
    """Test utils/helpers.py functions"""
    
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_client_ip(self):
        # Test with request object
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 10.0.0.2'
        self.assertEqual(get_client_ip(request), '10.0.0.1')
        
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.assertEqual(get_client_ip(request), '127.0.0.1')
        
        # Test with META dict
        meta = {'REMOTE_ADDR': '192.168.1.1'}
        self.assertEqual(get_client_ip(meta), '192.168.1.1')

    def test_format_file_size_display(self):
        self.assertEqual(format_file_size_display(0), "0 B")
        self.assertEqual(format_file_size_display(100), "100.0 B")
        self.assertEqual(format_file_size_display(1024), "1.0 KB")
        self.assertEqual(format_file_size_display(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size_display(1024 * 1024 * 1024), "1.0 GB")
        self.assertEqual(format_file_size_display(1024 * 1024 * 1024 * 1024), "1.0 TB")

    def test_sanitize_filename(self):
        # Test basic sanitization
        name = sanitize_filename("test file.pdf")
        self.assertIn("test file.pdf", name)
        # Check UUID prefix (8 chars + underscore = 9 chars min prefix)
        self.assertTrue(len(name) >= 10)
        
        # Test dangerous characters
        name = sanitize_filename("../../../etc/passwd")
        self.assertNotIn("/", name)
        self.assertNotIn("..", name)
        
        # Test length limit
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        self.assertLessEqual(len(sanitized), 250) # Buffer for UUID
        self.assertTrue(sanitized.endswith(".txt"))

    def test_is_recent_download(self):
        now = timezone.now()
        
        # Test recent (1 hour ago)
        recent = now - timedelta(hours=1)
        self.assertTrue(is_recent_download(recent, hours=24))
        
        # Test old (25 hours ago)
        old = now - timedelta(hours=25)
        self.assertFalse(is_recent_download(old, hours=24))
        
        # Test None
        self.assertFalse(is_recent_download(None))

    def test_get_file_extension(self):
        self.assertEqual(get_file_extension("test.pdf"), "pdf")
        self.assertEqual(get_file_extension("archive.tar.gz"), "gz")
        self.assertEqual(get_file_extension("makefile"), "")
        self.assertEqual(get_file_extension("TEST.PDF"), "pdf")

    def test_validate_file_extension(self):
        allowed = ['pdf', 'doc', 'docx']
        
        self.assertTrue(validate_file_extension("test.pdf", allowed))
        self.assertTrue(validate_file_extension("test.DOC", allowed))
        self.assertTrue(validate_file_extension("test.docx", allowed))
        
        self.assertFalse(validate_file_extension("test.exe", allowed))
        self.assertFalse(validate_file_extension("test", allowed))
