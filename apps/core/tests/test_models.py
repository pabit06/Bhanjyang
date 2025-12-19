"""
Comprehensive tests for core models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.core.models import APIKey, SecurityLog

User = get_user_model()


class APIKeyModelTest(TestCase):
    """Test suite for APIKey model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_api_key_creation(self):
        """Test API key creation"""
        api_key = APIKey.objects.create(
            name='Test API Key',
            user=self.user
        )
        self.assertIsNotNone(api_key.key)
        self.assertEqual(len(api_key.key), 43)  # token_urlsafe(32) produces 43 chars
        self.assertTrue(api_key.is_active)
        self.assertEqual(api_key.user, self.user)
    
    def test_api_key_auto_generation(self):
        """Test that API key is auto-generated on save"""
        api_key = APIKey(name='Test', user=self.user)
        # Key may be empty string before save
        self.assertIn(api_key.key, ['', None])
        api_key.save()
        self.assertIsNotNone(api_key.key)
        self.assertGreater(len(api_key.key), 0)
    
    def test_api_key_str(self):
        """Test string representation"""
        api_key = APIKey.objects.create(
            name='Test API Key',
            user=self.user
        )
        self.assertEqual(str(api_key), f"Test API Key ({self.user.username})")
    
    def test_api_key_is_valid_active(self):
        """Test is_valid for active key without expiration"""
        api_key = APIKey.objects.create(
            name='Test',
            user=self.user,
            is_active=True
        )
        self.assertTrue(api_key.is_valid())
    
    def test_api_key_is_valid_inactive(self):
        """Test is_valid for inactive key"""
        api_key = APIKey.objects.create(
            name='Test',
            user=self.user,
            is_active=False
        )
        self.assertFalse(api_key.is_valid())
    
    def test_api_key_is_valid_expired(self):
        """Test is_valid for expired key"""
        api_key = APIKey.objects.create(
            name='Test',
            user=self.user,
            is_active=True,
            expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(api_key.is_valid())
    
    def test_api_key_is_valid_not_expired(self):
        """Test is_valid for key not yet expired"""
        api_key = APIKey.objects.create(
            name='Test',
            user=self.user,
            is_active=True,
            expires_at=timezone.now() + timedelta(days=1)
        )
        self.assertTrue(api_key.is_valid())
    
    def test_api_key_update_last_used(self):
        """Test update_last_used method"""
        api_key = APIKey.objects.create(
            name='Test',
            user=self.user
        )
        self.assertIsNone(api_key.last_used)
        api_key.update_last_used()
        api_key.refresh_from_db()
        self.assertIsNotNone(api_key.last_used)
        self.assertAlmostEqual(
            api_key.last_used,
            timezone.now(),
            delta=timedelta(seconds=5)
        )
    
    def test_api_key_unique_key(self):
        """Test that API keys are unique"""
        api_key1 = APIKey.objects.create(name='Test1', user=self.user)
        api_key2 = APIKey.objects.create(name='Test2', user=self.user)
        self.assertNotEqual(api_key1.key, api_key2.key)
    
    def test_api_key_default_rate_limits(self):
        """Test default rate limits"""
        api_key = APIKey.objects.create(name='Test', user=self.user)
        self.assertEqual(api_key.requests_per_hour, 1000)
        self.assertEqual(api_key.requests_per_day, 10000)
    
    def test_api_key_custom_rate_limits(self):
        """Test custom rate limits"""
        api_key = APIKey.objects.create(
            name='Test',
            user=self.user,
            requests_per_hour=500,
            requests_per_day=5000
        )
        self.assertEqual(api_key.requests_per_hour, 500)
        self.assertEqual(api_key.requests_per_day, 5000)
    
    def test_api_key_ordering(self):
        """Test that API keys are ordered by created_at descending"""
        api_key1 = APIKey.objects.create(name='Test1', user=self.user)
        api_key2 = APIKey.objects.create(name='Test2', user=self.user)
        api_keys = list(APIKey.objects.all())
        self.assertEqual(api_keys[0], api_key2)
        self.assertEqual(api_keys[1], api_key1)


class SecurityLogModelTest(TestCase):
    """Test suite for SecurityLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_security_log_creation(self):
        """Test security log creation"""
        log = SecurityLog.objects.create(
            event_type='login_success',
            ip_address='192.168.1.1',
            user=self.user,
            user_agent='Test Agent',
            details={'test': 'data'}
        )
        self.assertEqual(log.event_type, 'login_success')
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.details, {'test': 'data'})
    
    def test_security_log_str(self):
        """Test string representation"""
        log = SecurityLog.objects.create(
            event_type='login_failed',
            ip_address='192.168.1.1'
        )
        self.assertEqual(str(log), "Failed Login - 192.168.1.1")
    
    def test_security_log_event_types(self):
        """Test all event types"""
        event_types = [
            'login_success',
            'login_failed',
            'rate_limit_exceeded',
            'suspicious_input',
            'brute_force_blocked',
            'api_key_used',
            'api_key_invalid',
            'security_header_violation',
        ]
        for event_type in event_types:
            log = SecurityLog.objects.create(
                event_type=event_type,
                ip_address='192.168.1.1'
            )
            self.assertEqual(log.event_type, event_type)
    
    def test_security_log_without_user(self):
        """Test security log without user"""
        log = SecurityLog.objects.create(
            event_type='suspicious_input',
            ip_address='192.168.1.1'
        )
        self.assertIsNone(log.user)
    
    def test_security_log_default_details(self):
        """Test security log with default details"""
        log = SecurityLog.objects.create(
            event_type='rate_limit_exceeded',
            ip_address='192.168.1.1'
        )
        self.assertEqual(log.details, {})
    
    def test_security_log_ordering(self):
        """Test that security logs are ordered by timestamp descending"""
        log1 = SecurityLog.objects.create(
            event_type='login_success',
            ip_address='192.168.1.1'
        )
        log2 = SecurityLog.objects.create(
            event_type='login_failed',
            ip_address='192.168.1.2'
        )
        logs = list(SecurityLog.objects.all())
        self.assertEqual(logs[0], log2)
        self.assertEqual(logs[1], log1)
    
    def test_security_log_indexes(self):
        """Test that indexes are defined in model Meta"""
        # Check that indexes are defined in Meta class
        self.assertTrue(hasattr(SecurityLog._meta, 'indexes'))
        self.assertGreater(len(SecurityLog._meta.indexes), 0)

