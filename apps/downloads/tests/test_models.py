"""
Comprehensive tests for downloads app models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel

User = get_user_model()


class DownloadableFileModelTest(TestCase):
    """Test suite for DownloadableFile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file content",
            content_type="application/pdf"
        )
        self.downloadable_file = DownloadableFile.objects.create(
            title="Test File",
            description="Test Description",
            file=test_file,
            category=FileCategory.FORM,
            priority=PriorityLevel.MEDIUM,
            uploaded_by=self.user
        )
    
    def test_file_creation(self):
        """Test basic file creation"""
        self.assertEqual(self.downloadable_file.title, "Test File")
        self.assertEqual(self.downloadable_file.category, FileCategory.FORM)
        self.assertEqual(self.downloadable_file.priority, PriorityLevel.MEDIUM)
        self.assertTrue(self.downloadable_file.is_active)
        self.assertEqual(self.downloadable_file.download_count, 0)
        self.assertEqual(self.downloadable_file.view_count, 0)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.downloadable_file), "Test File")
    
    def test_file_type_auto_detection(self):
        """Test that file_type is auto-detected from file extension"""
        self.assertEqual(self.downloadable_file.file_type, "pdf")
    
    def test_category_choices(self):
        """Test category choices"""
        categories = [
            FileCategory.FORM,
            FileCategory.REPORT,
            FileCategory.POLICY,
            FileCategory.PUBLICATION,
            FileCategory.MANUAL,
            FileCategory.CERTIFICATE,
            FileCategory.BROCHURE,
            FileCategory.OTHER
        ]
        for category in categories:
            test_file = SimpleUploadedFile(
                f"test_{category}.pdf",
                b"file content",
                content_type="application/pdf"
            )
            file_obj = DownloadableFile.objects.create(
                title=f"Test {category}",
                file=test_file,
                category=category
            )
            self.assertEqual(file_obj.category, category)
    
    def test_priority_choices(self):
        """Test priority choices"""
        priorities = [
            PriorityLevel.LOW,
            PriorityLevel.MEDIUM,
            PriorityLevel.HIGH,
            PriorityLevel.URGENT
        ]
        for priority in priorities:
            test_file = SimpleUploadedFile(
                f"test_{priority}.pdf",
                b"file content",
                content_type="application/pdf"
            )
            file_obj = DownloadableFile.objects.create(
                title=f"Test {priority}",
                file=test_file,
                priority=priority
            )
            self.assertEqual(file_obj.priority, priority)
    
    def test_is_expired_property(self):
        """Test is_expired property"""
        # No expiry date
        self.assertFalse(self.downloadable_file.is_expired)
        
        # Future expiry date
        self.downloadable_file.expires_at = timezone.now() + timedelta(days=7)
        self.downloadable_file.save()
        self.assertFalse(self.downloadable_file.is_expired)
        
        # Past expiry date
        self.downloadable_file.expires_at = timezone.now() - timedelta(days=7)
        self.downloadable_file.save()
        self.assertTrue(self.downloadable_file.is_expired)
    
    def test_tag_list_property(self):
        """Test tag_list property"""
        # No tags
        self.assertEqual(self.downloadable_file.tag_list, [])
        
        # With tags
        self.downloadable_file.tags = "form, application, document"
        self.downloadable_file.save()
        tag_list = self.downloadable_file.tag_list
        self.assertEqual(len(tag_list), 3)
        self.assertIn("form", tag_list)
        self.assertIn("application", tag_list)
        self.assertIn("document", tag_list)
        
        # With spaces
        self.downloadable_file.tags = "form , application , document"
        self.downloadable_file.save()
        tag_list = self.downloadable_file.tag_list
        self.assertEqual(len(tag_list), 3)
    
    def test_increment_view_count(self):
        """Test increment_view_count method"""
        initial_count = self.downloadable_file.view_count
        self.downloadable_file.increment_view_count()
        self.downloadable_file.refresh_from_db()
        self.assertEqual(self.downloadable_file.view_count, initial_count + 1)
        self.assertIsNotNone(self.downloadable_file.last_accessed)
        self.assertEqual(self.downloadable_file.access_count, 1)
    
    def test_increment_download_count(self):
        """Test increment_download_count method"""
        initial_count = self.downloadable_file.download_count
        self.downloadable_file.increment_download_count()
        self.downloadable_file.refresh_from_db()
        self.assertEqual(self.downloadable_file.download_count, initial_count + 1)
        self.assertIsNotNone(self.downloadable_file.last_accessed)
        self.assertEqual(self.downloadable_file.access_count, 1)
    
    def test_file_size_property(self):
        """Test file_size property"""
        # File size should be calculated
        size = self.downloadable_file.file_size
        self.assertIsNotNone(size)
        self.assertIn("B", size)  # Should contain unit
    
    def test_ordering(self):
        """Test model ordering"""
        test_file = SimpleUploadedFile(
            "test2.pdf",
            b"file content",
            content_type="application/pdf"
        )
        file2 = DownloadableFile.objects.create(
            title="Test File 2",
            file=test_file,
            priority=PriorityLevel.HIGH
        )
        files = list(DownloadableFile.objects.all())
        # Should be ordered by -priority, -uploaded_at
        # HIGH comes before MEDIUM
        self.assertEqual(files[0], file2)
        self.assertEqual(files[1], self.downloadable_file)
    
    def test_default_values(self):
        """Test default field values"""
        test_file = SimpleUploadedFile(
            "test_default.pdf",
            b"file content",
            content_type="application/pdf"
        )
        file_obj = DownloadableFile.objects.create(
            title="Test Default",
            file=test_file
        )
        self.assertEqual(file_obj.category, FileCategory.OTHER)
        self.assertEqual(file_obj.priority, PriorityLevel.MEDIUM)
        self.assertTrue(file_obj.is_active)
        self.assertFalse(file_obj.is_featured)
        self.assertFalse(file_obj.requires_login)

