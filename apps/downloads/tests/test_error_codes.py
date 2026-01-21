"""
Tests for Downloads app error codes.
"""
from django.test import TestCase

from apps.downloads.utils.error_codes import (
    DownloadsErrorCodes,
    ERROR_STATUS_MAP,
    get_status_code_for_error,
    get_user_friendly_message
)


class DownloadsErrorCodesTest(TestCase):
    """Test cases for DownloadsErrorCodes"""
    
    def test_error_codes_exist(self):
        """Test that all error codes are defined"""
        self.assertTrue(hasattr(DownloadsErrorCodes, 'DOWNLOAD_ERROR'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'FILE_NOT_FOUND'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'ACCESS_DENIED'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'RATE_LIMIT_EXCEEDED'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'FILE_EXPIRED'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'INVALID_FILE_TYPE'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'BULK_DOWNLOAD_ERROR'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'VIRUS_DETECTED'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'IP_BLACKLISTED'))
        self.assertTrue(hasattr(DownloadsErrorCodes, 'DATABASE_ERROR'))
    
    def test_error_code_values(self):
        """Test that error codes have proper string values"""
        self.assertEqual(DownloadsErrorCodes.DOWNLOAD_ERROR, 'DOWNLOAD_ERROR')
        self.assertEqual(DownloadsErrorCodes.FILE_NOT_FOUND, 'DOWNLOAD_FILE_NOT_FOUND')
        self.assertEqual(DownloadsErrorCodes.ACCESS_DENIED, 'DOWNLOAD_ACCESS_DENIED')
        self.assertEqual(DownloadsErrorCodes.RATE_LIMIT_EXCEEDED, 'DOWNLOAD_RATE_LIMIT_EXCEEDED')
    
    def test_error_status_map_exists(self):
        """Test that ERROR_STATUS_MAP contains all error codes"""
        self.assertIn(DownloadsErrorCodes.DOWNLOAD_ERROR, ERROR_STATUS_MAP)
        self.assertIn(DownloadsErrorCodes.FILE_NOT_FOUND, ERROR_STATUS_MAP)
        self.assertIn(DownloadsErrorCodes.ACCESS_DENIED, ERROR_STATUS_MAP)
        self.assertIn(DownloadsErrorCodes.RATE_LIMIT_EXCEEDED, ERROR_STATUS_MAP)
        self.assertIn(DownloadsErrorCodes.FILE_EXPIRED, ERROR_STATUS_MAP)
    
    def test_get_status_code_for_error(self):
        """Test get_status_code_for_error function"""
        # Test known error codes
        self.assertEqual(get_status_code_for_error(DownloadsErrorCodes.FILE_NOT_FOUND), 404)
        self.assertEqual(get_status_code_for_error(DownloadsErrorCodes.ACCESS_DENIED), 403)
        self.assertEqual(get_status_code_for_error(DownloadsErrorCodes.RATE_LIMIT_EXCEEDED), 429)
        self.assertEqual(get_status_code_for_error(DownloadsErrorCodes.FILE_EXPIRED), 410)
        self.assertEqual(get_status_code_for_error(DownloadsErrorCodes.DOWNLOAD_ERROR), 500)
        
        # Test unknown error code (should default to 500)
        self.assertEqual(get_status_code_for_error('UNKNOWN_ERROR'), 500)
    
    def test_get_user_friendly_message(self):
        """Test get_user_friendly_message function"""
        # Test known error codes
        message = get_user_friendly_message(DownloadsErrorCodes.FILE_NOT_FOUND)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        
        message = get_user_friendly_message(DownloadsErrorCodes.RATE_LIMIT_EXCEEDED)
        self.assertIn('too many', message.lower() or 'wait', message.lower())
        
        message = get_user_friendly_message(DownloadsErrorCodes.ACCESS_DENIED)
        self.assertIsInstance(message, str)
        
        # Test unknown error code (should return default message)
        message = get_user_friendly_message('UNKNOWN_ERROR')
        self.assertIn('unexpected error', message.lower())
    
    def test_error_status_map_completeness(self):
        """Test that all error codes have status mappings"""
        error_codes = [
            DownloadsErrorCodes.DOWNLOAD_ERROR,
            DownloadsErrorCodes.FILE_NOT_FOUND,
            DownloadsErrorCodes.ACCESS_DENIED,
            DownloadsErrorCodes.RATE_LIMIT_EXCEEDED,
            DownloadsErrorCodes.FILE_EXPIRED,
            DownloadsErrorCodes.INVALID_FILE_TYPE,
            DownloadsErrorCodes.BULK_DOWNLOAD_ERROR,
            DownloadsErrorCodes.VIRUS_DETECTED,
            DownloadsErrorCodes.IP_BLACKLISTED,
            DownloadsErrorCodes.DATABASE_ERROR,
        ]
        
        for error_code in error_codes:
            self.assertIn(error_code, ERROR_STATUS_MAP, f"{error_code} missing from ERROR_STATUS_MAP")
            status_code = ERROR_STATUS_MAP[error_code]
            self.assertIsInstance(status_code, int)
            self.assertGreaterEqual(status_code, 400)
            self.assertLessEqual(status_code, 599)
    
    def test_user_friendly_messages_completeness(self):
        """Test that all error codes have user-friendly messages"""
        error_codes = [
            DownloadsErrorCodes.DOWNLOAD_ERROR,
            DownloadsErrorCodes.FILE_NOT_FOUND,
            DownloadsErrorCodes.ACCESS_DENIED,
            DownloadsErrorCodes.RATE_LIMIT_EXCEEDED,
            DownloadsErrorCodes.FILE_EXPIRED,
            DownloadsErrorCodes.INVALID_FILE_TYPE,
            DownloadsErrorCodes.BULK_DOWNLOAD_ERROR,
            DownloadsErrorCodes.VIRUS_DETECTED,
            DownloadsErrorCodes.IP_BLACKLISTED,
            DownloadsErrorCodes.DATABASE_ERROR,
        ]
        
        for error_code in error_codes:
            message = get_user_friendly_message(error_code)
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0, f"No message for {error_code}")
