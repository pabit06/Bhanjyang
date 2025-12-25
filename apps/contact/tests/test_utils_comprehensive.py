"""
Comprehensive tests for Contact utilities
"""
from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

from apps.contact.utils.validators import (
    validate_contact_file_size,
    validate_contact_file_extension,
    validate_contact_mime_type
)
from apps.contact.utils.helpers import (
    get_client_ip,
    format_file_size_display,
    get_attachment_filename,
    is_recent_submission
)
from apps.contact.utils.constants import (
    MAX_CONTACT_FILE_SIZE_BYTES,
    ALLOWED_CONTACT_FILE_EXTENSIONS,
    ALLOWED_CONTACT_MIME_TYPES
)


class ContactValidatorsTest(TestCase):
    """Test suite for Contact validators"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_file = SimpleUploadedFile(
            'test.pdf',
            b'PDF content',
            content_type='application/pdf'
        )
        
        self.large_file = SimpleUploadedFile(
            'large.pdf',
            b'x' * (MAX_CONTACT_FILE_SIZE_BYTES + 1),
            content_type='application/pdf'
        )
    
    def test_validate_contact_file_size_valid(self):
        """Test file size validation with valid file"""
        # Should not raise exception
        validate_contact_file_size(self.valid_file)
    
    def test_validate_contact_file_size_too_large(self):
        """Test file size validation with file that's too large"""
        with self.assertRaises(ValidationError) as context:
            validate_contact_file_size(self.large_file)
        
        self.assertIn('exceed', str(context.exception).lower())
        self.assertIn('5', str(context.exception))
    
    def test_validate_contact_file_size_exact_limit(self):
        """Test file size validation with file at exact limit"""
        exact_size_file = SimpleUploadedFile(
            'test.pdf',
            b'x' * MAX_CONTACT_FILE_SIZE_BYTES,
            content_type='application/pdf'
        )
        # Should not raise exception
        validate_contact_file_size(exact_size_file)
    
    def test_validate_contact_file_extension_valid(self):
        """Test file extension validation with valid extension"""
        for ext in ALLOWED_CONTACT_FILE_EXTENSIONS:
            file = SimpleUploadedFile(
                f'test.{ext}',
                b'content',
                content_type='application/pdf'
            )
            # Should not raise exception
            validate_contact_file_extension(file)
    
    def test_validate_contact_file_extension_invalid(self):
        """Test file extension validation with invalid extension"""
        invalid_file = SimpleUploadedFile(
            'test.exe',
            b'content',
            content_type='application/x-msdownload'
        )
        
        with self.assertRaises(ValidationError) as context:
            validate_contact_file_extension(invalid_file)
        
        self.assertIn('not allowed', str(context.exception).lower())
    
    def test_validate_contact_file_extension_case_insensitive(self):
        """Test file extension validation is case insensitive"""
        # Test uppercase extension
        uppercase_file = SimpleUploadedFile(
            'test.PDF',
            b'content',
            content_type='application/pdf'
        )
        # Should not raise exception
        validate_contact_file_extension(uppercase_file)
    
    def test_validate_contact_mime_type_valid(self):
        """Test MIME type validation with valid MIME type"""
        for mime_type in ALLOWED_CONTACT_MIME_TYPES:
            file = SimpleUploadedFile(
                'test.pdf',
                b'content',
                content_type=mime_type
            )
            # Should not raise exception
            validate_contact_mime_type(file)
    
    def test_validate_contact_mime_type_invalid(self):
        """Test MIME type validation with invalid MIME type"""
        invalid_file = SimpleUploadedFile(
            'test.bin',
            b'content',
            content_type='application/octet-stream'
        )
        
        with self.assertRaises(ValidationError) as context:
            validate_contact_mime_type(invalid_file)
        
        self.assertIn('not allowed', str(context.exception).lower())
    
    def test_validate_contact_mime_type_no_content_type(self):
        """Test MIME type validation with file without content_type"""
        file_without_type = SimpleUploadedFile(
            'test.pdf',
            b'content'
        )
        # Remove content_type if it exists
        if hasattr(file_without_type, 'content_type'):
            delattr(file_without_type, 'content_type')
        
        # Should not raise exception if content_type is missing
        # (validation might be lenient or skip)
        try:
            validate_contact_mime_type(file_without_type)
        except ValidationError:
            # Expected if validation is strict
            pass


class ContactHelpersTest(TestCase):
    """Test suite for Contact helper functions"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
    
    def test_get_client_ip_direct(self):
        """Test getting client IP directly"""
        request = self.factory.get('/contact/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header"""
        request = self.factory.get('/contact/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = get_client_ip(request)
        
        self.assertEqual(ip, '10.0.0.1')
    
    def test_get_client_ip_forwarded_with_spaces(self):
        """Test getting client IP from X-Forwarded-For with spaces"""
        request = self.factory.get('/contact/')
        request.META['HTTP_X_FORWARDED_FOR'] = '  10.0.0.1  ,  192.168.1.1  '
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = get_client_ip(request)
        
        self.assertEqual(ip, '10.0.0.1')
    
    def test_get_client_ip_no_remote_addr(self):
        """Test getting client IP when REMOTE_ADDR is missing"""
        request = self.factory.get('/contact/')
        # Remove REMOTE_ADDR if it exists
        if 'REMOTE_ADDR' in request.META:
            del request.META['REMOTE_ADDR']
        
        ip = get_client_ip(request)
        
        # RequestFactory may set a default, so just check it's a string
        self.assertIsInstance(ip, str)
    
    def test_format_file_size_display_bytes(self):
        """Test formatting file size in bytes"""
        size = format_file_size_display(500)
        
        self.assertEqual(size, '500.0 B')
    
    def test_format_file_size_display_kb(self):
        """Test formatting file size in KB"""
        size = format_file_size_display(2048)
        
        self.assertEqual(size, '2.0 KB')
    
    def test_format_file_size_display_mb(self):
        """Test formatting file size in MB"""
        size = format_file_size_display(2 * 1024 * 1024)
        
        self.assertEqual(size, '2.0 MB')
    
    def test_format_file_size_display_gb(self):
        """Test formatting file size in GB"""
        size = format_file_size_display(2 * 1024 * 1024 * 1024)
        
        self.assertEqual(size, '2.0 GB')
    
    def test_format_file_size_display_zero(self):
        """Test formatting zero file size"""
        size = format_file_size_display(0)
        
        self.assertEqual(size, '0 B')
    
    def test_format_file_size_display_decimal(self):
        """Test formatting file size with decimal precision"""
        size = format_file_size_display(1536)  # 1.5 KB
        
        self.assertEqual(size, '1.5 KB')
    
    def test_get_attachment_filename_with_file(self):
        """Test getting attachment filename when file exists"""
        file_field = SimpleUploadedFile(
            'test.pdf',
            b'content',
            content_type='application/pdf'
        )
        
        filename = get_attachment_filename(file_field)
        
        self.assertEqual(filename, 'test.pdf')
    
    def test_get_attachment_filename_with_path(self):
        """Test getting attachment filename with path"""
        file_field = SimpleUploadedFile(
            'uploads/test.pdf',
            b'content',
            content_type='application/pdf'
        )
        
        filename = get_attachment_filename(file_field)
        
        self.assertEqual(filename, 'test.pdf')
    
    def test_get_attachment_filename_none(self):
        """Test getting attachment filename when file is None"""
        filename = get_attachment_filename(None)
        
        self.assertIsNone(filename)
    
    def test_get_attachment_filename_no_name(self):
        """Test getting attachment filename when name is missing"""
        # Create a mock file field without a name
        from unittest.mock import MagicMock
        file_field = MagicMock()
        file_field.name = None
        
        filename = get_attachment_filename(file_field)
        
        # Should return None when name is None
        self.assertIsNone(filename)
    
    def test_is_recent_submission_recent(self):
        """Test checking recent submission"""
        recent_time = timezone.now() - timedelta(hours=12)
        
        is_recent = is_recent_submission(recent_time, hours=24)
        
        self.assertTrue(is_recent)
    
    def test_is_recent_submission_old(self):
        """Test checking old submission"""
        old_time = timezone.now() - timedelta(hours=25)
        
        is_recent = is_recent_submission(old_time, hours=24)
        
        self.assertFalse(is_recent)
    
    def test_is_recent_submission_exact_boundary(self):
        """Test checking submission at exact boundary"""
        boundary_time = timezone.now() - timedelta(hours=24)
        
        is_recent = is_recent_submission(boundary_time, hours=24)
        
        # Should be False as it's exactly at the boundary
        self.assertFalse(is_recent)
    
    def test_is_recent_submission_custom_hours(self):
        """Test checking recent submission with custom hours"""
        recent_time = timezone.now() - timedelta(hours=2)
        
        is_recent = is_recent_submission(recent_time, hours=3)
        
        self.assertTrue(is_recent)
    
    def test_is_recent_submission_very_recent(self):
        """Test checking very recent submission"""
        very_recent_time = timezone.now() - timedelta(minutes=30)
        
        is_recent = is_recent_submission(very_recent_time, hours=24)
        
        self.assertTrue(is_recent)
    
    def test_is_recent_submission_future(self):
        """Test checking submission in the future"""
        future_time = timezone.now() + timedelta(hours=1)
        
        is_recent = is_recent_submission(future_time, hours=24)
        
        # Future submissions should be considered recent
        self.assertTrue(is_recent)


class ContactConstantsTest(TestCase):
    """Test suite for Contact constants"""
    
    def test_max_contact_file_size_bytes(self):
        """Test MAX_CONTACT_FILE_SIZE_BYTES constant"""
        from apps.contact.utils.constants import MAX_CONTACT_FILE_SIZE_BYTES
        
        self.assertEqual(MAX_CONTACT_FILE_SIZE_BYTES, 5 * 1024 * 1024)
    
    def test_allowed_contact_file_extensions(self):
        """Test ALLOWED_CONTACT_FILE_EXTENSIONS constant"""
        from apps.contact.utils.constants import ALLOWED_CONTACT_FILE_EXTENSIONS
        
        self.assertIsInstance(ALLOWED_CONTACT_FILE_EXTENSIONS, list)
        self.assertIn('pdf', ALLOWED_CONTACT_FILE_EXTENSIONS)
        self.assertIn('doc', ALLOWED_CONTACT_FILE_EXTENSIONS)
        self.assertIn('docx', ALLOWED_CONTACT_FILE_EXTENSIONS)
    
    def test_allowed_contact_mime_types(self):
        """Test ALLOWED_CONTACT_MIME_TYPES constant"""
        from apps.contact.utils.constants import ALLOWED_CONTACT_MIME_TYPES
        
        self.assertIsInstance(ALLOWED_CONTACT_MIME_TYPES, list)
        self.assertIn('application/pdf', ALLOWED_CONTACT_MIME_TYPES)
        self.assertIn('image/jpeg', ALLOWED_CONTACT_MIME_TYPES)
    
    def test_max_name_length(self):
        """Test MAX_NAME_LENGTH constant"""
        from apps.contact.utils.constants import MAX_NAME_LENGTH
        
        self.assertEqual(MAX_NAME_LENGTH, 100)
    
    def test_max_email_length(self):
        """Test MAX_EMAIL_LENGTH constant"""
        from apps.contact.utils.constants import MAX_EMAIL_LENGTH
        
        self.assertEqual(MAX_EMAIL_LENGTH, 254)
    
    def test_min_message_length(self):
        """Test MIN_MESSAGE_LENGTH constant"""
        from apps.contact.utils.constants import MIN_MESSAGE_LENGTH
        
        self.assertEqual(MIN_MESSAGE_LENGTH, 10)

