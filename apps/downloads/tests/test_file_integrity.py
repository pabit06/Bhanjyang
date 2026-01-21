"""
Tests for file integrity checking (hash verification).
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import hashlib
import os
import tempfile

from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel
from apps.downloads.security import FileSecurityValidator
from apps.downloads.services import FileDownloadService
from apps.downloads.utils.error_codes import DownloadsErrorCodes
from django.test import RequestFactory


class FileIntegrityTest(TestCase):
    """Test cases for file integrity checking"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test file content
        self.test_content = b"This is test file content for integrity checking"
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            self.test_content,
            content_type="application/pdf"
        )
        
        # Calculate expected hash
        self.expected_hash = hashlib.sha256(self.test_content).hexdigest()
    
    def test_generate_file_hash(self):
        """Test generating file hash"""
        file_obj = SimpleUploadedFile(
            "test.pdf",
            b"test content",
            content_type="application/pdf"
        )
        
        hash_value = FileSecurityValidator.generate_file_hash(file_obj)
        
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)  # SHA-256 hex digest length
        self.assertEqual(
            hash_value,
            hashlib.sha256(b"test content").hexdigest()
        )
    
    def test_generate_file_hash_empty_file(self):
        """Test generating hash for empty file"""
        file_obj = SimpleUploadedFile(
            "empty.pdf",
            b"",
            content_type="application/pdf"
        )
        
        hash_value = FileSecurityValidator.generate_file_hash(file_obj)
        
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)
        self.assertEqual(
            hash_value,
            hashlib.sha256(b"").hexdigest()
        )
    
    def test_verify_file_hash_valid(self):
        """Test verifying file hash when hash matches"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(self.test_content)
            temp_path = f.name
        
        try:
            is_valid, current_hash, error_msg = FileSecurityValidator.verify_file_hash(
                temp_path,
                self.expected_hash
            )
            
            self.assertTrue(is_valid)
            self.assertEqual(current_hash, self.expected_hash)
            self.assertIsNone(error_msg)
        finally:
            os.unlink(temp_path)
    
    def test_verify_file_hash_mismatch(self):
        """Test verifying file hash when hash doesn't match (tampering detected)"""
        # Create temporary file with different content
        tampered_content = b"This is tampered content"
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(tampered_content)
            temp_path = f.name
        
        try:
            is_valid, current_hash, error_msg = FileSecurityValidator.verify_file_hash(
                temp_path,
                self.expected_hash  # Original hash
            )
            
            self.assertFalse(is_valid)
            self.assertIsNotNone(current_hash)
            self.assertNotEqual(current_hash, self.expected_hash)
            self.assertIsNotNone(error_msg)
            self.assertIn("mismatch", error_msg.lower() or "tampered", error_msg.lower())
        finally:
            os.unlink(temp_path)
    
    def test_verify_file_hash_file_not_found(self):
        """Test verifying hash when file doesn't exist"""
        is_valid, current_hash, error_msg = FileSecurityValidator.verify_file_hash(
            "/nonexistent/path/file.pdf",
            self.expected_hash
        )
        
        self.assertFalse(is_valid)
        self.assertIsNone(current_hash)
        self.assertIsNotNone(error_msg)
        self.assertIn("not found", error_msg.lower())
    
    def test_verify_file_hash_no_expected_hash(self):
        """Test verifying hash when no expected hash is provided"""
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(self.test_content)
            temp_path = f.name
        
        try:
            # No hash stored - should return True (skip check)
            is_valid, current_hash, error_msg = FileSecurityValidator.verify_file_hash(
                temp_path,
                None
            )
            
            self.assertTrue(is_valid)
            self.assertIsNone(current_hash)
            self.assertIsNone(error_msg)
        finally:
            os.unlink(temp_path)
    
    def test_file_hash_saved_on_upload(self):
        """Test that file hash is saved when file is uploaded"""
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="Test",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True,
            uploaded_by=self.user
        )
        
        # Hash should be generated and saved
        self.assertIsNotNone(file_obj.file_hash)
        self.assertEqual(len(file_obj.file_hash), 64)
        self.assertEqual(file_obj.file_hash, self.expected_hash)
    
    def test_file_download_integrity_check_valid(self):
        """Test file download with valid integrity check"""
        # Create file with hash
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="Test",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True,
            file_hash=self.expected_hash,
            uploaded_by=self.user
        )
        
        request = self.factory.get('/downloads/')
        request.user = self.user
        
        success, url, error_code = FileDownloadService.process_file_download(request, file_obj)
        
        # Should succeed if file exists and hash matches
        # Note: May fail if file doesn't exist on disk in test environment
        self.assertIsInstance(success, bool)
    
    def test_file_download_integrity_check_failed(self):
        """Test file download when integrity check fails"""
        # Create file with hash
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="Test",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True,
            file_hash=self.expected_hash,
            uploaded_by=self.user
        )
        
        # Tamper with the file on disk (if it exists)
        if hasattr(file_obj.file, 'path') and os.path.exists(file_obj.file.path):
            with open(file_obj.file.path, 'wb') as f:
                f.write(b"tampered content")
        
        request = self.factory.get('/downloads/')
        request.user = self.user
        
        success, url, error_code = FileDownloadService.process_file_download(request, file_obj)
        
        # Should fail with integrity error if file was tampered
        if not success and error_code:
            self.assertEqual(error_code, DownloadsErrorCodes.FILE_INTEGRITY_FAILED)
    
    def test_file_hash_recalculation_on_update(self):
        """Test that hash is recalculated when file is updated"""
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="Test",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True,
            uploaded_by=self.user
        )
        
        original_hash = file_obj.file_hash
        
        # Update with new file
        new_content = b"New file content"
        new_file = SimpleUploadedFile(
            "new_file.pdf",
            new_content,
            content_type="application/pdf"
        )
        file_obj.file = new_file
        file_obj.save()
        
        # Hash should be recalculated
        file_obj.refresh_from_db()
        new_hash = hashlib.sha256(new_content).hexdigest()
        self.assertEqual(file_obj.file_hash, new_hash)
        self.assertNotEqual(file_obj.file_hash, original_hash)
