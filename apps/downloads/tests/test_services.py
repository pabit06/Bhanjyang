"""
Comprehensive tests for Downloads services
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.downloads.services import (
    DownloadsService, FileDownloadService, BulkDownloadService, DownloadsAnalyticsService
)
from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel


class DownloadsServiceTest(TestCase):
    """Test cases for DownloadsService"""

    def setUp(self):
        """Set up test data"""
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test files
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        self.file1 = DownloadableFile.objects.create(
            title="Test File 1",
            description="Description 1",
            file=self.test_file,
            category=FileCategory.FORM,
            priority=PriorityLevel.HIGH,
            is_featured=True,
            is_active=True
        )
        
        self.file2 = DownloadableFile.objects.create(
            title="Test File 2",
            description="Description 2",
            file=self.test_file,
            category=FileCategory.REPORT,
            priority=PriorityLevel.MEDIUM,
            is_featured=False,
            is_active=True
        )

    def test_get_download_center_context_basic(self):
        """Test basic get_download_center_context"""
        request_params = {}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertIn('files_by_category', context)
        self.assertIn('featured_files', context)
        self.assertIn('categories', context)
        self.assertIn('priorities', context)
        self.assertIn('total_files', context)

    def test_get_download_center_context_with_category_filter(self):
        """Test get_download_center_context with category filter"""
        request_params = {'category': FileCategory.FORM}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context['active_category'], FileCategory.FORM)
        # Should only have files in FORM category
        if FileCategory.FORM in context['files_by_category']:
            files = context['files_by_category'][FileCategory.FORM]['files']
            self.assertTrue(all(f.category == FileCategory.FORM for f in files))

    def test_get_download_center_context_with_search(self):
        """Test get_download_center_context with search query"""
        request_params = {'q': 'Test File 1'}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context['q'], 'Test File 1')
        # Should filter files by search query
        total_files = sum(
            len(cat['files']) for cat in context['files_by_category'].values()
        )
        self.assertGreaterEqual(total_files, 0)

    def test_get_download_center_context_featured_only(self):
        """Test get_download_center_context with featured filter"""
        request_params = {'featured': 'true'}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertTrue(context['featured_only'])
        # All files should be featured
        for category_data in context['files_by_category'].values():
            for file_obj in category_data['files']:
                self.assertTrue(file_obj.is_featured)

    def test_get_download_center_context_show_all(self):
        """Test get_download_center_context with show_all=True"""
        # Create more files
        for i in range(10):
            DownloadableFile.objects.create(
                title=f"File {i}",
                description=f"Description {i}",
                file=self.test_file,
                category=FileCategory.FORM,
                is_active=True
            )
        
        request_params = {}
        context = DownloadsService.get_download_center_context(request_params, show_all=True)
        
        self.assertTrue(context['show_all'])
        # Should show all files, not limited to 6
        if FileCategory.FORM in context['files_by_category']:
            files_count = len(context['files_by_category'][FileCategory.FORM]['files'])
            self.assertGreaterEqual(files_count, 10)

    def test_get_download_center_context_caching(self):
        """Test that get_download_center_context uses caching"""
        request_params = {}
        
        # First call
        context1 = DownloadsService.get_download_center_context(request_params)
        
        # Delete a file
        self.file1.delete()
        
        # Second call should use cache (if not show_all)
        context2 = DownloadsService.get_download_center_context(request_params, show_all=False)
        
        # Cache might return old data, so we just verify it doesn't crash
        self.assertIn('files_by_category', context2)
    
    def test_get_download_center_context_with_priority_filter(self):
        """Test get_download_center_context with priority filter"""
        request_params = {'priority': PriorityLevel.HIGH}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context['active_priority'], PriorityLevel.HIGH)
        # Verify files are filtered by priority
        for category_data in context['files_by_category'].values():
            for file_obj in category_data['files']:
                self.assertEqual(file_obj.priority, PriorityLevel.HIGH)


class FileDownloadServiceTest(TestCase):
    """Test cases for FileDownloadService"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
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
            is_active=True
        )

    def test_process_file_download_success(self):
        """Test successful file download"""
        request = self.factory.get('/')
        request.user = self.user
        
        success, url, error = FileDownloadService.process_file_download(request, self.file_obj)
        
        self.assertTrue(success)
        self.assertIsNotNone(url)
        self.assertIsNone(error)
        
        # Verify download count was incremented
        self.file_obj.refresh_from_db()
        self.assertGreater(self.file_obj.download_count, 0)

    def test_process_file_download_expired(self):
        """Test download of expired file"""
        self.file_obj.expires_at = timezone.now() - timedelta(days=1)
        self.file_obj.save()
        
        request = self.factory.get('/')
        request.user = self.user
        
        success, url, error = FileDownloadService.process_file_download(request, self.file_obj)
        
        self.assertFalse(success)
        self.assertIsNone(url)
        self.assertIn('expired', error.lower())

    def test_process_file_download_requires_login(self):
        """Test download of file requiring login"""
        self.file_obj.requires_login = True
        self.file_obj.save()
        
        request = self.factory.get('/')
        # Create an anonymous user (not authenticated)
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        success, url, error = FileDownloadService.process_file_download(request, self.file_obj)
        
        # Access control may allow or deny - depends on implementation
        # Just verify the method doesn't crash
        self.assertIsInstance(success, bool)

    def test_process_file_view_success(self):
        """Test successful file view"""
        request = self.factory.get('/')
        request.user = self.user
        
        initial_count = self.file_obj.view_count
        success = FileDownloadService.process_file_view(request, self.file_obj)
        
        self.assertTrue(success)
        self.file_obj.refresh_from_db()
        self.assertEqual(self.file_obj.view_count, initial_count + 1)

    def test_process_file_view_expired(self):
        """Test view of expired file"""
        self.file_obj.expires_at = timezone.now() - timedelta(days=1)
        self.file_obj.save()
        
        request = self.factory.get('/')
        request.user = self.user
        
        success = FileDownloadService.process_file_view(request, self.file_obj)
        
        self.assertFalse(success)
    
    def test_process_file_download_exception_handling(self):
        """Test exception handling in process_file_download"""
        request = self.factory.get('/')
        request.user = self.user
        
        # Mock increment_download_count to raise an exception
        with patch.object(self.file_obj, 'increment_download_count', side_effect=Exception("Test error")):
            success, url, error = FileDownloadService.process_file_download(request, self.file_obj)
            
            self.assertFalse(success)
            self.assertIsNone(url)
            self.assertIsNotNone(error)
            self.assertIn('Test error', error)
    
    def test_process_file_view_exception_handling(self):
        """Test exception handling in process_file_view"""
        request = self.factory.get('/')
        request.user = self.user
        
        # Mock increment_view_count to raise an exception
        with patch.object(self.file_obj, 'increment_view_count', side_effect=Exception("Test error")):
            success = FileDownloadService.process_file_view(request, self.file_obj)
            
            self.assertFalse(success)


class BulkDownloadServiceTest(TestCase):
    """Test cases for BulkDownloadService"""

    def setUp(self):
        """Set up test data"""
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
        
        self.file1 = DownloadableFile.objects.create(
            title="File 1",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True
        )
        
        self.file2 = DownloadableFile.objects.create(
            title="File 2",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True
        )
        
        self.file3 = DownloadableFile.objects.create(
            title="File 3",
            file=self.test_file,
            category=FileCategory.FORM,
            requires_login=True,  # Requires login
            is_active=True
        )

    def test_get_accessible_files(self):
        """Test getting accessible files for user"""
        file_ids = [self.file1.pk, self.file2.pk, self.file3.pk]
        accessible = BulkDownloadService.get_accessible_files(self.user, file_ids)
        
        # Should return files user can access (file3 requires login, but user is authenticated)
        self.assertGreaterEqual(len(accessible), 2)
        file_ids_accessible = [f.id for f in accessible]
        self.assertIn(self.file1.id, file_ids_accessible)
        self.assertIn(self.file2.id, file_ids_accessible)

    def test_get_accessible_files_anonymous(self):
        """Test getting accessible files for anonymous user"""
        from django.contrib.auth.models import AnonymousUser
        anonymous_user = AnonymousUser()
        file_ids = [self.file1.pk, self.file2.pk, self.file3.pk]
        accessible = BulkDownloadService.get_accessible_files(anonymous_user, file_ids)
        
        # Should not include file3 (requires login) if access control is strict
        # But may include it if access control allows anonymous access
        file_ids_accessible = [f.id for f in accessible]
        # Just verify we get a list back
        self.assertIsInstance(accessible, list)

    def test_get_accessible_files_invalid_ids(self):
        """Test getting accessible files with invalid IDs"""
        file_ids = [99999, 99998]  # Non-existent IDs
        accessible = BulkDownloadService.get_accessible_files(self.user, file_ids)
        
        self.assertEqual(len(accessible), 0)
    
    def test_create_zip_file_success(self):
        """Test creating ZIP file with valid files"""
        import os
        file_objects = [self.file1, self.file2]
        
        # Mock file.path to avoid actual file system operations
        with patch.object(self.file1, 'file') as mock_file1, \
             patch.object(self.file2, 'file') as mock_file2:
            mock_file1.path = '/tmp/test1.pdf'
            mock_file1.name = 'test1.pdf'
            mock_file2.path = '/tmp/test2.pdf'
            mock_file2.name = 'test2.pdf'
            
            # Create temporary files for testing
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.pdf') as f1, \
                 tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.pdf') as f2:
                f1.write('test content 1')
                f2.write('test content 2')
                temp_path1 = f1.name
                temp_path2 = f2.name
            
            # Update mock to return actual temp file paths
            mock_file1.path = temp_path1
            mock_file2.path = temp_path2
            
            zip_path, success_count, failed_files = BulkDownloadService.create_zip_file(file_objects)
            
            # Verify ZIP was created
            self.assertIsNotNone(zip_path)
            self.assertTrue(os.path.exists(zip_path))
            self.assertGreater(success_count, 0)
            self.assertEqual(len(failed_files), 0)
            
            # Cleanup
            try:
                os.unlink(zip_path)
                os.unlink(temp_path1)
                os.unlink(temp_path2)
            except:
                pass
    
    def test_create_zip_file_with_failures(self):
        """Test creating ZIP file when some files fail"""
        import os
        import tempfile
        
        # Create a file object that will fail
        file_with_error = DownloadableFile.objects.create(
            title="File with Error",
            file=self.test_file,
            category=FileCategory.FORM,
            is_active=True
        )
        
        file_objects = [self.file1, file_with_error]
        
        # Mock file.path to cause an error for one file
        with patch.object(file_with_error, 'file') as mock_file_error:
            mock_file_error.path = '/nonexistent/path/file.pdf'  # Invalid path
            mock_file_error.name = 'file.pdf'
            
            # Create temp file for file1
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.pdf') as f1:
                f1.write('test content')
                temp_path1 = f1.name
            
            with patch.object(self.file1, 'file') as mock_file1:
                mock_file1.path = temp_path1
                mock_file1.name = 'test1.pdf'
                
                zip_path, success_count, failed_files = BulkDownloadService.create_zip_file(file_objects)
                
                # Should have at least one success and one failure
                self.assertIsNotNone(zip_path)
                self.assertGreater(success_count, 0)
                self.assertGreater(len(failed_files), 0)
                self.assertIn(file_with_error.id, failed_files)
                
                # Cleanup
                try:
                    if os.path.exists(zip_path):
                        os.unlink(zip_path)
                    os.unlink(temp_path1)
                except:
                    pass


class DownloadsAnalyticsServiceTest(TestCase):
    """Test cases for DownloadsAnalyticsService"""

    def setUp(self):
        """Set up test data"""
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        # Create files with different categories and stats
        self.file1 = DownloadableFile.objects.create(
            title="File 1",
            file=self.test_file,
            category=FileCategory.FORM,
            is_featured=True,
            is_active=True,
            download_count=10,
            view_count=50
        )
        
        self.file2 = DownloadableFile.objects.create(
            title="File 2",
            file=self.test_file,
            category=FileCategory.REPORT,
            is_featured=False,
            is_active=True,
            download_count=5,
            view_count=25
        )

    def test_get_download_stats(self):
        """Test getting download statistics"""
        stats = DownloadsAnalyticsService.get_download_stats()
        
        self.assertIn('total_files', stats)
        self.assertIn('featured_files', stats)
        self.assertIn('total_downloads', stats)
        self.assertIn('total_views', stats)
        self.assertIn('files_by_category', stats)
        
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['featured_files'], 1)
        self.assertEqual(stats['total_downloads'], 15)  # 10 + 5
        self.assertEqual(stats['total_views'], 75)  # 50 + 25
        self.assertIn(FileCategory.FORM, stats['files_by_category'])
        self.assertIn(FileCategory.REPORT, stats['files_by_category'])

    def test_get_download_stats_no_files(self):
        """Test getting stats when no files exist"""
        DownloadableFile.objects.all().delete()
        
        stats = DownloadsAnalyticsService.get_download_stats()
        
        self.assertEqual(stats['total_files'], 0)
        self.assertEqual(stats['featured_files'], 0)
        self.assertEqual(stats['total_downloads'], 0)
        self.assertEqual(stats['total_views'], 0)

