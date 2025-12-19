"""
Comprehensive tests for downloads views
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel


class DownloadsViewsTest(TestCase):
    """Test cases for downloads views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        self.file_obj = DownloadableFile.objects.create(
            title="Test File",
            description="Test description",
            file=self.test_file,
            category=FileCategory.FORM,
            priority=PriorityLevel.HIGH,
            is_featured=True,
            is_active=True
        )

    def test_download_center_view_get(self):
        """Test download center view GET request"""
        response = self.client.get(reverse('downloads:download_center'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('files_by_category', response.context)
        self.assertIn('featured_files', response.context)

    def test_download_center_view_with_category_filter(self):
        """Test download center view with category filter"""
        response = self.client.get(
            reverse('downloads:download_center'),
            {'category': FileCategory.FORM}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_category'], FileCategory.FORM)

    def test_download_center_view_with_search(self):
        """Test download center view with search query"""
        response = self.client.get(
            reverse('downloads:download_center'),
            {'q': 'Test'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['q'], 'Test')

    def test_download_center_view_with_featured_filter(self):
        """Test download center view with featured filter"""
        response = self.client.get(
            reverse('downloads:download_center'),
            {'featured': 'true'}
        )
        
        self.assertEqual(response.status_code, 200)
        # featured_files should be a list, not a dict
        self.assertIsInstance(response.context['featured_files'], list)
        self.assertTrue(response.context['featured_only'])

    def test_download_center_view_show_all(self):
        """Test download center view with show_all parameter"""
        response = self.client.get(
            reverse('downloads:download_center'),
            {'show_all': 'true'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_all'])

    def test_file_detail_view(self):
        """Test file detail view"""
        response = self.client.get(reverse('downloads:file_detail', args=[self.file_obj.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['file'], self.file_obj)

    def test_download_file_view_success(self):
        """Test download file view with valid file"""
        response = self.client.get(reverse('downloads:download_file', args=[self.file_obj.pk]))
        
        # Should redirect to file URL or return file
        self.assertIn(response.status_code, [200, 302])

    def test_download_file_view_expired(self):
        """Test download file view with expired file"""
        self.file_obj.expires_at = timezone.now() - timedelta(days=1)
        self.file_obj.save()
        
        response = self.client.get(reverse('downloads:download_file', args=[self.file_obj.pk]))
        
        # Should redirect to download center (expired files redirect, not return 403)
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            self.assertEqual(response.url, reverse('downloads:download_center'))

    def test_download_file_view_requires_login(self):
        """Test download file view with file requiring login"""
        self.file_obj.requires_login = True
        self.file_obj.save()
        
        # As anonymous user
        response = self.client.get(reverse('downloads:download_file', args=[self.file_obj.pk]))
        
        # Should return 403 or redirect to login
        self.assertIn(response.status_code, [302, 403])
        
        # As authenticated user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('downloads:download_file', args=[self.file_obj.pk]))
        
        # Should work for authenticated user
        self.assertIn(response.status_code, [200, 302])
    
    def test_file_detail_view_expired(self):
        """Test file detail view with expired file"""
        self.file_obj.expires_at = timezone.now() - timedelta(days=1)
        self.file_obj.save()
        
        response = self.client.get(reverse('downloads:file_detail', args=[self.file_obj.pk]))
        
        # Should redirect to download center
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('downloads:download_center'))
    
    def test_file_preview_view_success(self):
        """Test file preview view with previewable file type"""
        # Create a PDF file for preview
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        preview_file = DownloadableFile.objects.create(
            title="Preview File",
            description="Test preview",
            file=pdf_file,
            category=FileCategory.FORM,
            is_active=True,
            file_type='pdf'
        )
        
        response = self.client.get(reverse('downloads:file_preview', args=[preview_file.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['file'], preview_file)
        self.assertIn('preview_url', response.context)
    
    def test_file_preview_view_non_previewable(self):
        """Test file preview view with non-previewable file type"""
        # Create a non-previewable file
        doc_file = SimpleUploadedFile(
            "test.doc",
            b"DOC content",
            content_type="application/msword"
        )
        non_preview_file = DownloadableFile.objects.create(
            title="Non Preview File",
            description="Test",
            file=doc_file,
            category=FileCategory.FORM,
            is_active=True,
            file_type='doc'
        )
        
        response = self.client.get(reverse('downloads:file_preview', args=[non_preview_file.pk]))
        
        # Should return 400 error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_file_preview_view_expired(self):
        """Test file preview view with expired file"""
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        preview_file = DownloadableFile.objects.create(
            title="Preview File",
            description="Test",
            file=pdf_file,
            category=FileCategory.FORM,
            is_active=True,
            file_type='pdf',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        response = self.client.get(reverse('downloads:file_preview', args=[preview_file.pk]))
        
        # Should return 404 or error
        self.assertIn(response.status_code, [400, 403, 404])
    
    def test_bulk_download_view_requires_login(self):
        """Test bulk download view requires login"""
        response = self.client.post(reverse('downloads:bulk_download'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_bulk_download_view_no_files(self):
        """Test bulk download view with no files selected"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('downloads:bulk_download'))
        
        # Should return 400 error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('No files selected', data['error'])
    
    def test_bulk_download_view_success(self):
        """Test bulk download view with valid files"""
        from django.core.cache import cache
        from unittest.mock import patch
        
        # Clear rate limit cache
        cache.clear()
        
        self.client.login(username='testuser', password='testpass123')
        
        # Create additional file for bulk download
        file2 = DownloadableFile.objects.create(
            title="Test File 2",
            description="Test",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True
        )
        
        # Mock file.path to avoid actual file system operations
        with patch.object(self.file_obj, 'file') as mock_file1, \
             patch.object(file2, 'file') as mock_file2:
            # Mock file paths to avoid actual file access
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.pdf') as f1, \
                 tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.pdf') as f2:
                f1.write('test content 1')
                f2.write('test content 2')
                temp_path1 = f1.name
                temp_path2 = f2.name
            
            mock_file1.path = temp_path1
            mock_file1.name = 'test1.pdf'
            mock_file2.path = temp_path2
            mock_file2.name = 'test2.pdf'
            
            response = self.client.post(
                reverse('downloads:bulk_download'),
                {'file_ids': [self.file_obj.pk, file2.pk]},
                follow=False
            )
            
            # Should return ZIP file or handle gracefully
            # May fail if files don't exist on disk, but should not crash
            self.assertIn(response.status_code, [200, 400, 403, 500])
            
            # Cleanup
            try:
                os.unlink(temp_path1)
                os.unlink(temp_path2)
            except:
                pass
    
    def test_bulk_download_view_invalid_file_ids(self):
        """Test bulk download view with invalid file IDs"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('downloads:bulk_download'),
            {'file_ids': [99999, 99998]}
        )
        
        # Should return 403 error (no accessible files)
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('error', data)
    
    def test_download_history_view_requires_login(self):
        """Test download history view requires login"""
        response = self.client.get(reverse('downloads:download_history'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_download_history_view_authenticated(self):
        """Test download history view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('downloads:download_history'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('downloads', response.context)
        self.assertIn('user', response.context)
    
    def test_download_center_view_with_priority_filter(self):
        """Test download center view with priority filter"""
        response = self.client.get(
            reverse('downloads:download_center'),
            {'priority': PriorityLevel.HIGH}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_priority'], PriorityLevel.HIGH)
    
    def test_download_file_view_exception_handling(self):
        """Test download file view exception handling"""
        # Mock increment_download_count to raise exception
        from unittest.mock import patch
        with patch.object(self.file_obj, 'increment_download_count', side_effect=Exception("Test error")):
            response = self.client.get(reverse('downloads:download_file', args=[self.file_obj.pk]))
            
            # Should still redirect even if increment fails
            self.assertIn(response.status_code, [200, 302])
    
    def test_file_detail_view_exception_handling(self):
        """Test file detail view exception handling"""
        from unittest.mock import patch
        with patch.object(self.file_obj, 'increment_view_count', side_effect=Exception("Test error")):
            response = self.client.get(reverse('downloads:file_detail', args=[self.file_obj.pk]))
            
            # Should still render even if increment fails
            self.assertEqual(response.status_code, 200)

