"""
Tests for virus scanning functionality.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import os

from apps.downloads.security import VirusScanManager
from apps.downloads.utils.error_codes import DownloadsErrorCodes


class VirusScanManagerTest(TestCase):
    """Test cases for VirusScanManager"""
    
    def setUp(self):
        """Set up test data"""
        # Ensure pyclamd is mocked in sys.modules
        import sys
        if 'pyclamd' not in sys.modules:
            sys.modules['pyclamd'] = MagicMock()
        
        # Reset mock state
        sys.modules['pyclamd'].reset_mock()
        sys.modules['pyclamd'].ClamdUnixSocket.side_effect = None
        sys.modules['pyclamd'].ClamdNetworkSocket.side_effect = None
            
        self.test_file_content = b"This is a test file for virus scanning"
        self.test_file = SimpleUploadedFile(
            "test_file.pdf",
            self.test_file_content,
            content_type="application/pdf"
        )
    
    def test_is_clamav_available_success(self):
        """Test checking if ClamAV is available when it is"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        
        mock_cd = MagicMock()
        mock_cd.ping.return_value = True
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd
        
        result = VirusScanManager.is_clamav_available()
        
        self.assertTrue(result)
        mock_cd.ping.assert_called_once()
    
    def test_is_clamav_available_not_running(self):
        """Test checking if ClamAV is available when daemon is not running"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        mock_pyclamd.ClamdUnixSocket.side_effect = Exception("Connection refused")
        mock_pyclamd.ClamdNetworkSocket.side_effect = Exception("Connection refused")
        
        result = VirusScanManager.is_clamav_available()
        
        self.assertFalse(result)
    
    def test_is_clamav_available_not_installed(self):
        """Test checking if ClamAV is available when pyclamd is not installed"""
        import sys
        # Temporarily remove pyclamd from sys.modules
        with patch.dict(sys.modules):
            if 'pyclamd' in sys.modules:
                del sys.modules['pyclamd']
            
            result = VirusScanManager.is_clamav_available()
            self.assertFalse(result)
    
    @patch('django.conf.settings')
    def test_scan_file_clean(self, mock_settings):
        """Test scanning a clean file"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        
        # Setup mocks
        mock_settings.DOWNLOADS_SETTINGS = {'ENABLE_VIRUS_SCAN': True}
        mock_cd = MagicMock()
        mock_cd.scan_file.return_value = None  # None means clean
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(self.test_file_content)
            temp_path = f.name
        
        try:
            is_clean, result = VirusScanManager.scan_file(temp_path)
            
            self.assertTrue(is_clean)
            self.assertIn("clean", result.lower())
            mock_cd.scan_file.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('django.conf.settings')
    def test_scan_file_virus_detected(self, mock_settings):
        """Test scanning a file with virus detected"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        
        # Setup mocks
        mock_settings.DOWNLOADS_SETTINGS = {'ENABLE_VIRUS_SCAN': True}
        mock_cd = MagicMock()
        # Simulate virus detection
        mock_cd.scan_file.return_value = {
            '/path/to/file.pdf': ('EICAR-Test-File', 'FOUND')
        }
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(self.test_file_content)
            temp_path = f.name
        
        try:
            is_clean, result = VirusScanManager.scan_file(temp_path)
            
            self.assertFalse(is_clean)
            self.assertIn("virus", result.lower())
            mock_cd.scan_file.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('django.conf.settings')
    def test_scan_file_disabled(self, mock_settings):
        """Test scanning when virus scanning is disabled"""
        mock_settings.DOWNLOADS_SETTINGS = {'ENABLE_VIRUS_SCAN': False}
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(self.test_file_content)
            temp_path = f.name
        
        try:
            is_clean, result = VirusScanManager.scan_file(temp_path)
            
            self.assertTrue(is_clean)
            self.assertIn("disabled", result.lower())
        finally:
            os.unlink(temp_path)
    
    @patch('django.conf.settings')
    def test_scan_file_not_found(self, mock_settings):
        """Test scanning a file that doesn't exist"""
        mock_settings.DOWNLOADS_SETTINGS = {'ENABLE_VIRUS_SCAN': True}
        
        is_clean, result = VirusScanManager.scan_file('/nonexistent/file.pdf')
        
        self.assertFalse(is_clean)
        self.assertIn("not found", result.lower())
    
    @patch('django.conf.settings')
    def test_scan_file_tcp_fallback(self, mock_settings):
        """Test scanning with TCP fallback when Unix socket fails"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        
        mock_settings.DOWNLOADS_SETTINGS = {
            'ENABLE_VIRUS_SCAN': True,
            'CLAMAV_HOST': '127.0.0.1',
            'CLAMAV_PORT': 3310
        }
        mock_cd_tcp = MagicMock()
        mock_cd_tcp.scan_file.return_value = None
        mock_pyclamd.ClamdUnixSocket.side_effect = Exception("Socket error")
        mock_pyclamd.ClamdNetworkSocket.return_value = mock_cd_tcp
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(self.test_file_content)
            temp_path = f.name
        
        try:
            is_clean, result = VirusScanManager.scan_file(temp_path)
            
            self.assertTrue(is_clean)
            # Called twice: once in has_clamav_available, once in scan_file
            mock_pyclamd.ClamdNetworkSocket.assert_called_with('127.0.0.1', 3310)
            mock_cd_tcp.scan_file.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('django.conf.settings')
    def test_scan_file_content_clean(self, mock_settings):
        """Test scanning file content in memory"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        
        mock_settings.DOWNLOADS_SETTINGS = {'ENABLE_VIRUS_SCAN': True}
        mock_cd = MagicMock()
        mock_cd.scan_stream.return_value = None
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd
        
        is_clean, result = VirusScanManager.scan_file_content(self.test_file_content)
        
        self.assertTrue(is_clean)
        self.assertIn("clean", result.lower())
        mock_cd.scan_stream.assert_called_once_with(self.test_file_content)
    
    @patch('django.conf.settings')
    def test_scan_file_content_virus_detected(self, mock_settings):
        """Test scanning file content with virus detected"""
        import sys
        mock_pyclamd = sys.modules['pyclamd']
        
        mock_settings.DOWNLOADS_SETTINGS = {'ENABLE_VIRUS_SCAN': True}
        mock_cd = MagicMock()
        mock_cd.scan_stream.return_value = {
            'stream': ('EICAR-Test-File', 'FOUND')
        }
        mock_pyclamd.ClamdUnixSocket.return_value = mock_cd
        
        is_clean, result = VirusScanManager.scan_file_content(self.test_file_content)
        
        self.assertFalse(is_clean)
        self.assertIn("virus", result.lower())
        mock_cd.scan_stream.assert_called_once_with(self.test_file_content)
