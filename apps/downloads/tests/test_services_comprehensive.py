"""
Comprehensive tests for Downloads services
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel
from apps.downloads.services import (
    DownloadsService, FileDownloadService, BulkDownloadService,
    DownloadsAnalyticsService
)
from apps.downloads.utils.error_codes import DownloadsErrorCodes

User = get_user_model()


class DownloadsServiceTest(TestCase):
    """Test suite for DownloadsService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test files
        self.file1 = DownloadableFile.objects.create(
            title='Test File 1',
            description='Test description',
            category=FileCategory.FORM,
            priority=PriorityLevel.HIGH,
            is_active=True,
            is_featured=True,
            file=SimpleUploadedFile("test1.pdf", b"content")
        )
        
        self.file2 = DownloadableFile.objects.create(
            title='Test File 2',
            description='Another test',
            category=FileCategory.FORM,
            priority=PriorityLevel.MEDIUM,
            is_active=True,
            file=SimpleUploadedFile("test2.pdf", b"content")
        )
    
    def test_get_download_center_context_basic(self):
        """Test getting download center context"""
        request_params = {}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertIn('files_by_category', context)
        self.assertIn('featured_files', context)
        self.assertIn('categories', context)
        self.assertIn('priorities', context)
        self.assertIn('total_files', context)
    
    def test_get_download_center_context_with_category(self):
        """Test getting context with category filter"""
        request_params = {'category': FileCategory.FORM}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context['active_category'], FileCategory.FORM)
        self.assertGreaterEqual(context['total_files'], 0)
    
    def test_get_download_center_context_with_priority(self):
        """Test getting context with priority filter"""
        request_params = {'priority': PriorityLevel.HIGH}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context['active_priority'], PriorityLevel.HIGH)
    
    def test_get_download_center_context_with_search(self):
        """Test getting context with search query"""
        request_params = {'q': 'Test'}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context['q'], 'Test')
    
    @patch('apps.downloads.services.DownloadsPerformanceMonitor.get_cached_file_list')
    def test_get_download_center_context_featured_only(self, mock_cache):
        """Test getting context with featured filter"""
        mock_cache.return_value = None  # Don't use cache
        request_params = {'featured': 'true'}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertTrue(context['featured_only'])
    
    def test_get_download_center_context_show_all(self):
        """Test getting context with show_all flag"""
        request_params = {}
        context = DownloadsService.get_download_center_context(request_params, show_all=True)
        
        self.assertTrue(context['show_all'])
    
    @patch('apps.downloads.services.DownloadsPerformanceMonitor.get_cached_file_list')
    def test_get_download_center_context_uses_cache(self, mock_cache):
        """Test that context uses cached data when available"""
        mock_cache.return_value = {'cached': True}
        
        request_params = {}
        context = DownloadsService.get_download_center_context(request_params)
        
        self.assertEqual(context, {'cached': True})
        mock_cache.assert_called_once()
    
    def test_get_filtered_files_by_category(self):
        """Test filtering files by category"""
        files = DownloadsService._get_filtered_files(
            category_code=FileCategory.FORM,
            priority_code=None,
            featured_only=False,
            query=''
        )
        
        self.assertGreaterEqual(files.count(), 2)
        for file in files:
            self.assertEqual(file.category, FileCategory.FORM)
    
    def test_get_filtered_files_by_priority(self):
        """Test filtering files by priority"""
        files = DownloadsService._get_filtered_files(
            category_code=None,
            priority_code=PriorityLevel.HIGH,
            featured_only=False,
            query=''
        )
        
        for file in files:
            self.assertEqual(file.priority, PriorityLevel.HIGH)
    
    def test_get_filtered_files_featured_only(self):
        """Test filtering featured files only"""
        files = DownloadsService._get_filtered_files(
            category_code=None,
            priority_code=None,
            featured_only=True,
            query=''
        )
        
        for file in files:
            self.assertTrue(file.is_featured)
    
    def test_get_filtered_files_with_search(self):
        """Test filtering files with search query"""
        files = DownloadsService._get_filtered_files(
            category_code=None,
            priority_code=None,
            featured_only=False,
            query='Test File 1'
        )
        
        self.assertGreaterEqual(files.count(), 1)
        self.assertIn(self.file1, files)
    
    def test_get_filtered_files_excludes_expired(self):
        """Test that expired files are excluded"""
        expired_file = DownloadableFile.objects.create(
            title='Expired File',
            description='Test',
            category=FileCategory.FORM,
            is_active=True,
            expires_at=timezone.now() - timedelta(days=1),
            file=SimpleUploadedFile("expired.pdf", b"content")
        )
        
        files = DownloadsService._get_filtered_files(
            category_code=None,
            priority_code=None,
            featured_only=False,
            query=''
        )
        
        self.assertNotIn(expired_file, files)
    
    def test_group_files_by_category(self):
        """Test grouping files by category"""
        files = DownloadableFile.objects.filter(is_active=True)
        grouped = DownloadsService._group_files_by_category(files, show_all=False)
        
        self.assertIsInstance(grouped, dict)
        if FileCategory.FORM in grouped:
            self.assertIn('files', grouped[FileCategory.FORM])
            self.assertIn('total_count', grouped[FileCategory.FORM])
            self.assertIn('has_more', grouped[FileCategory.FORM])
    
    def test_group_files_by_category_show_all(self):
        """Test grouping files with show_all flag"""
        files = DownloadableFile.objects.filter(is_active=True)
        grouped = DownloadsService._group_files_by_category(files, show_all=True)
        
        if FileCategory.FORM in grouped:
            self.assertFalse(grouped[FileCategory.FORM]['has_more'])
    
    @patch('apps.downloads.services.DownloadsPerformanceMonitor.get_cached_file_list')
    def test_get_featured_files(self, mock_cache):
        """Test getting featured files"""
        mock_cache.return_value = None  # Don't use cache
        featured = DownloadsService._get_featured_files()
        
        self.assertIsInstance(featured, list)
        for file in featured:
            self.assertTrue(file.is_featured)
            self.assertTrue(file.is_active)


class FileDownloadServiceTest(TestCase):
    """Test suite for FileDownloadService"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.file = DownloadableFile.objects.create(
            title='Test File',
            description='Test',
            category=FileCategory.FORM,
            is_active=True,
            file=SimpleUploadedFile("test.pdf", b"content")
        )
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    @patch('apps.downloads.services.SecurityAuditLogger.log_download_attempt')
    def test_process_file_download_success(self, mock_log, mock_access):
        """Test successful file download"""
        mock_access.return_value = (True, None)
        request = self.factory.get('/download/')
        request.user = self.user
        
        success, response, error = FileDownloadService.process_file_download(request, self.file)
        
        self.assertTrue(success)
        self.assertIsNotNone(response)
        self.assertIsNone(error)
        mock_log.assert_called_once()
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    @patch('apps.downloads.services.SecurityAuditLogger.log_download_attempt')
    def test_process_file_download_expired(self, mock_log, mock_access):
        """Test download of expired file"""
        self.file.expires_at = timezone.now() - timedelta(days=1)
        self.file.save()
        
        request = self.factory.get('/download/')
        request.user = self.user
        
        success, response, error = FileDownloadService.process_file_download(request, self.file)
        
        self.assertFalse(success)
        self.assertIn('expired', error.lower())
        mock_log.assert_called_once()
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    @patch('apps.downloads.services.SecurityAuditLogger.log_download_attempt')
    def test_process_file_download_no_permission(self, mock_log, mock_access):
        """Test download without permission"""
        mock_access.return_value = (False, 'Permission denied')
        request = self.factory.get('/download/')
        request.user = self.user
        
        success, response, error = FileDownloadService.process_file_download(request, self.file)
        
        self.assertFalse(success)
        self.assertEqual(error, DownloadsErrorCodes.ACCESS_DENIED)
        mock_log.assert_called_once()
    
    def test_process_file_view_success(self):
        """Test successful file view"""
        initial_count = self.file.view_count
        success = FileDownloadService.process_file_view(self.factory.get('/'), self.file)
        
        self.assertTrue(success)
        self.file.refresh_from_db()
        self.assertEqual(self.file.view_count, initial_count + 1)
    
    def test_process_file_view_expired(self):
        """Test view of expired file"""
        self.file.expires_at = timezone.now() - timedelta(days=1)
        self.file.save()
        
        success = FileDownloadService.process_file_view(self.factory.get('/'), self.file)
        
        self.assertFalse(success)


class BulkDownloadServiceTest(TestCase):
    """Test suite for BulkDownloadService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.file1 = DownloadableFile.objects.create(
            title='File 1',
            category=FileCategory.FORM,
            is_active=True,
            file=SimpleUploadedFile("file1.pdf", b"content")
        )
        
        self.file2 = DownloadableFile.objects.create(
            title='File 2',
            category=FileCategory.FORM,
            is_active=True,
            file=SimpleUploadedFile("file2.pdf", b"content")
        )
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    def test_get_accessible_files(self, mock_access):
        """Test getting accessible files"""
        mock_access.return_value = (True, None)
        
        file_ids = [self.file1.id, self.file2.id]
        accessible = BulkDownloadService.get_accessible_files(self.user, file_ids)
        
        self.assertEqual(len(accessible), 2)
        self.assertIn(self.file1, accessible)
        self.assertIn(self.file2, accessible)
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    def test_get_accessible_files_with_invalid_id(self, mock_access):
        """Test getting accessible files with invalid ID"""
        mock_access.return_value = (True, None)
        
        file_ids = [self.file1.id, 99999]  # Invalid ID
        accessible = BulkDownloadService.get_accessible_files(self.user, file_ids)
        
        self.assertEqual(len(accessible), 1)
        self.assertIn(self.file1, accessible)
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    def test_get_accessible_files_with_no_permission(self, mock_access):
        """Test getting accessible files when user has no permission"""
        mock_access.return_value = (False, 'No permission')
        
        file_ids = [self.file1.id]
        accessible = BulkDownloadService.get_accessible_files(self.user, file_ids)
        
        self.assertEqual(len(accessible), 0)
    
    @patch('apps.downloads.services.AccessControlManager.can_download_file')
    def test_get_accessible_files_excludes_expired(self, mock_access):
        """Test that expired files are excluded"""
        mock_access.return_value = (True, None)
        self.file1.expires_at = timezone.now() - timedelta(days=1)
        self.file1.save()
        
        file_ids = [self.file1.id, self.file2.id]
        accessible = BulkDownloadService.get_accessible_files(self.user, file_ids)
        
        self.assertEqual(len(accessible), 1)
        self.assertIn(self.file2, accessible)
        self.assertNotIn(self.file1, accessible)
    
    @patch('zipfile.ZipFile')
    @patch('tempfile.NamedTemporaryFile')
    def test_create_zip_file(self, mock_temp, mock_zip):
        """Test creating ZIP file"""
        mock_temp_file = MagicMock()
        mock_temp_file.name = '/tmp/test.zip'
        mock_temp.return_value = mock_temp_file
        
        mock_zip_file = MagicMock()
        mock_zip.return_value.__enter__.return_value = mock_zip_file
        
        file_objects = [self.file1, self.file2]
        temp_path, success_count, failed = BulkDownloadService.create_zip_file(file_objects)
        
        self.assertIsNotNone(temp_path)
        self.assertGreater(success_count, 0)
        self.assertIsInstance(failed, list)


class DownloadsAnalyticsServiceTest(TestCase):
    """Test suite for DownloadsAnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        self.file1 = DownloadableFile.objects.create(
            title='File 1',
            category=FileCategory.FORM,
            is_active=True,
            is_featured=True,
            download_count=10,
            view_count=20,
            file=SimpleUploadedFile("file1.pdf", b"content")
        )
        
        self.file2 = DownloadableFile.objects.create(
            title='File 2',
            category=FileCategory.REPORT,
            is_active=True,
            download_count=5,
            view_count=15,
            file=SimpleUploadedFile("file2.pdf", b"content")
        )
    
    def test_get_download_stats(self):
        """Test getting download statistics"""
        stats = DownloadsAnalyticsService.get_download_stats()
        
        self.assertIn('total_files', stats)
        self.assertIn('featured_files', stats)
        self.assertIn('total_downloads', stats)
        self.assertIn('total_views', stats)
        self.assertIn('files_by_category', stats)
        
        self.assertGreaterEqual(stats['total_files'], 2)
        self.assertGreaterEqual(stats['featured_files'], 1)
        self.assertGreaterEqual(stats['total_downloads'], 15)
        self.assertGreaterEqual(stats['total_views'], 35)
    
    def test_get_download_stats_files_by_category(self):
        """Test files by category in stats"""
        stats = DownloadsAnalyticsService.get_download_stats()
        
        self.assertIn('files_by_category', stats)
        if FileCategory.FORM in stats['files_by_category']:
            self.assertIn('label', stats['files_by_category'][FileCategory.FORM])
            self.assertIn('count', stats['files_by_category'][FileCategory.FORM])

