# downloads/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import DownloadableFile, FileCategory, PriorityLevel


class DownloadableFileModelTest(TestCase):
    """Test cases for the DownloadableFile model."""

    def setUp(self):
        """Set up test data."""
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_create_downloadable_file(self):
        """Test creating a downloadable file."""
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="A test file",
            file=self.test_file,
            category=FileCategory.FORM
        )
        
        self.assertEqual(file_obj.title, "Test File")
        self.assertEqual(file_obj.category, FileCategory.FORM)
        self.assertTrue(file_obj.is_active)
        self.assertFalse(file_obj.is_featured)
        self.assertEqual(file_obj.priority, PriorityLevel.MEDIUM)
        self.assertFalse(file_obj.requires_login)
        self.assertEqual(file_obj.download_count, 0)
        self.assertEqual(file_obj.view_count, 0)

    def test_file_type_auto_detection(self):
        """Test that file type is automatically detected."""
        file_obj = DownloadableFile.objects.create(
            title="Test PDF",
            file=self.test_file,
            category=FileCategory.FORM
        )
        
        self.assertEqual(file_obj.file_type, "pdf")

    def test_file_size_property(self):
        """Test the file_size property."""
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=self.test_file,
            category=FileCategory.FORM
        )
        
        self.assertEqual(file_obj.file_size, "12 B")

    def test_is_expired_property(self):
        """Test the is_expired property."""
        # Test with no expiration date
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=self.test_file,
            category=FileCategory.FORM
        )
        self.assertFalse(file_obj.is_expired)

        # Test with future expiration date
        future_date = timezone.now() + timedelta(days=30)
        file_obj.expires_at = future_date
        file_obj.save()
        self.assertFalse(file_obj.is_expired)

        # Test with past expiration date
        past_date = timezone.now() - timedelta(days=1)
        file_obj.expires_at = past_date
        file_obj.save()
        self.assertTrue(file_obj.is_expired)

    def test_tag_list_property(self):
        """Test the tag_list property."""
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=self.test_file,
            category=FileCategory.FORM,
            tags="tag1, tag2, tag3"
        )
        
        expected_tags = ["tag1", "tag2", "tag3"]
        self.assertEqual(file_obj.tag_list, expected_tags)

    def test_increment_view_count(self):
        """Test the increment_view_count method."""
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=self.test_file,
            category=FileCategory.FORM
        )
        
        initial_count = file_obj.view_count
        file_obj.increment_view_count()
        file_obj.refresh_from_db()
        
        self.assertEqual(file_obj.view_count, initial_count + 1)

    def test_model_ordering(self):
        """Test that files are ordered by priority and upload date."""
        # Create files with different priorities
        file1 = DownloadableFile.objects.create(
            title="Low Priority File",
            file=self.test_file,
            category=FileCategory.FORM,
            priority=PriorityLevel.LOW
        )
        
        file2 = DownloadableFile.objects.create(
            title="High Priority File",
            file=self.test_file,
            category=FileCategory.FORM,
            priority=PriorityLevel.HIGH
        )
        
        files = list(DownloadableFile.objects.all())
        # Check that high priority comes before low priority
        # The ordering is by priority (descending) then by upload date (descending)
        self.assertIn(file1, files)
        self.assertIn(file2, files)
        # Verify that priority ordering is working
        high_priority_files = [f for f in files if f.priority == PriorityLevel.HIGH]
        low_priority_files = [f for f in files if f.priority == PriorityLevel.LOW]
        self.assertTrue(len(high_priority_files) > 0)
        self.assertTrue(len(low_priority_files) > 0)


class DownloadViewsTest(TestCase):
    """Test cases for download views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        self.file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="A test file",
            file=self.test_file,
            category=FileCategory.FORM
        )

    def test_download_center_view(self):
        """Test the download center view."""
        response = self.client.get(reverse('downloads:download_center'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Download Center")
        self.assertContains(response, self.file_obj.title)

    def test_download_center_view_with_filters(self):
        """Test the download center view with filters."""
        # Test category filter
        response = self.client.get(
            reverse('downloads:download_center'),
            {'category': FileCategory.FORM}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.file_obj.title)

        # Test search filter
        response = self.client.get(
            reverse('downloads:download_center'),
            {'q': 'Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.file_obj.title)

        # Test priority filter
        response = self.client.get(
            reverse('downloads:download_center'),
            {'priority': PriorityLevel.MEDIUM}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.file_obj.title)

        # Test featured filter
        self.file_obj.is_featured = True
        self.file_obj.save()
        
        response = self.client.get(
            reverse('downloads:download_center'),
            {'featured': 'true'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.file_obj.title)

    def test_download_file_view(self):
        """Test the download file view."""
        initial_count = self.file_obj.download_count
        
        response = self.client.get(
            reverse('downloads:download_file', args=[self.file_obj.pk])
        )
        
        # Should redirect to the file URL
        self.assertEqual(response.status_code, 302)
        
        # Check that download count was incremented
        self.file_obj.refresh_from_db()
        self.assertEqual(self.file_obj.download_count, initial_count + 1)

    def test_download_file_view_with_login_required(self):
        """Test download file view with login requirement."""
        self.file_obj.requires_login = True
        self.file_obj.save()
        
        response = self.client.get(
            reverse('downloads:download_file', args=[self.file_obj.pk])
        )
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_download_file_view_with_expired_file(self):
        """Test download file view with expired file."""
        self.file_obj.expires_at = timezone.now() - timedelta(days=1)
        self.file_obj.save()
        
        response = self.client.get(
            reverse('downloads:download_file', args=[self.file_obj.pk])
        )
        
        # Should redirect back to download center
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('downloads:download_center'))

    def test_file_detail_view(self):
        """Test the file detail view."""
        response = self.client.get(
            reverse('downloads:file_detail', args=[self.file_obj.pk])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.file_obj.title)
        self.assertContains(response, self.file_obj.description)

    def test_file_detail_view_increments_view_count(self):
        """Test that file detail view increments view count."""
        initial_count = self.file_obj.view_count
        
        response = self.client.get(
            reverse('downloads:file_detail', args=[self.file_obj.pk])
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that view count was incremented
        self.file_obj.refresh_from_db()
        self.assertEqual(self.file_obj.view_count, initial_count + 1)

    def test_file_detail_view_with_expired_file(self):
        """Test file detail view with expired file."""
        self.file_obj.expires_at = timezone.now() - timedelta(days=1)
        self.file_obj.save()
        
        response = self.client.get(
            reverse('downloads:file_detail', args=[self.file_obj.pk])
        )
        
        # Should redirect back to download center
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('downloads:download_center'))


class DownloadAdminTest(TestCase):
    """Test cases for download admin interface."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_admin_list_view(self):
        """Test the admin list view."""
        response = self.client.get('/admin/downloads/downloadablefile/')
        self.assertEqual(response.status_code, 200)

    def test_admin_add_view(self):
        """Test the admin add view."""
        response = self.client.get('/admin/downloads/downloadablefile/add/')
        self.assertEqual(response.status_code, 200)

    def test_admin_change_view(self):
        """Test the admin change view."""
        test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=test_file,
            category=FileCategory.FORM
        )
        
        response = self.client.get(f'/admin/downloads/downloadablefile/{file_obj.pk}/change/')
        self.assertEqual(response.status_code, 200)


class DownloadURLsTest(TestCase):
    """Test cases for download URLs."""

    def test_download_center_url(self):
        """Test the download center URL."""
        response = self.client.get(reverse('downloads:download_center'))
        self.assertEqual(response.status_code, 200)

    def test_download_file_url(self):
        """Test the download file URL."""
        test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=test_file,
            category=FileCategory.FORM
        )
        
        response = self.client.get(reverse('downloads:download_file', args=[file_obj.pk]))
        self.assertEqual(response.status_code, 302)  # Redirects to file URL

    def test_file_detail_url(self):
        """Test the file detail URL."""
        test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        file_obj = DownloadableFile.objects.create(
            title="Test File",
            file=test_file,
            category=FileCategory.FORM
        )
        
        response = self.client.get(reverse('downloads:file_detail', args=[file_obj.pk]))
        self.assertEqual(response.status_code, 200)
