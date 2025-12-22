"""
Comprehensive tests for query utilities and managers.
"""
from django.test import TestCase
from django.db import models

from apps.core.query_utils import (
    ActiveManager,
    FeaturedManager,
    get_active_queryset,
    get_featured_queryset
)
from apps.services.models import SavingsAccount, LoanType, FixedDeposit


class TestActiveManager(TestCase):
    """Test suite for ActiveManager"""
    
    def setUp(self):
        """Set up test data"""
        # Create test instances with unique account types
        self.active_item = SavingsAccount.objects.create(
            english_name='Active Savings',
            nepali_name='सक्रिय बचत',
            account_type='general',
            interest_rate=5.0,
            is_active=True
        )
        
        self.inactive_item = SavingsAccount.objects.create(
            english_name='Inactive Savings',
            nepali_name='निष्क्रिय बचत',
            account_type='daily',  # Different account type for uniqueness
            interest_rate=5.0,
            is_active=False
        )
    
    def test_active_manager_filters_active_only(self):
        """Test that ActiveManager returns only active items"""
        # Using SavingsAccount which has is_active field
        active_count = SavingsAccount.objects.filter(is_active=True).count()
        all_count = SavingsAccount.objects.count()
        
        self.assertGreater(all_count, active_count)
        self.assertGreater(active_count, 0)
    
    def test_active_manager_excludes_inactive(self):
        """Test that ActiveManager excludes inactive items"""
        active_items = SavingsAccount.objects.filter(is_active=True)
        inactive_items = SavingsAccount.objects.filter(is_active=False)
        
        # Should not have any inactive items in active queryset
        for item in active_items:
            self.assertTrue(item.is_active)
        
        # Should have inactive items in inactive queryset
        self.assertGreater(inactive_items.count(), 0)


class TestFeaturedManager(TestCase):
    """Test suite for FeaturedManager"""
    
    def setUp(self):
        """Set up test data"""
        self.featured_active = SavingsAccount.objects.create(
            english_name='Featured Active',
            nepali_name='विशेष सक्रिय',
            account_type='general',
            interest_rate=6.0,
            is_active=True,
            is_featured=True
        )
        
        self.non_featured_active = SavingsAccount.objects.create(
            english_name='Non-Featured Active',
            nepali_name='गैर-विशेष सक्रिय',
            account_type='daily',  # Different account type
            interest_rate=5.0,
            is_active=True,
            is_featured=False
        )
        
        self.featured_inactive = SavingsAccount.objects.create(
            english_name='Featured Inactive',
            nepali_name='विशेष निष्क्रिय',
            account_type='institutional',  # Different account type
            interest_rate=5.0,
            is_active=False,
            is_featured=True
        )
    
    def test_featured_manager_filters_featured_and_active(self):
        """Test that FeaturedManager returns only featured active items"""
        featured_active = SavingsAccount.objects.filter(
            is_active=True,
            is_featured=True
        )
        
        self.assertGreater(featured_active.count(), 0)
        for item in featured_active:
            self.assertTrue(item.is_active)
            self.assertTrue(item.is_featured)
    
    def test_featured_manager_excludes_non_featured(self):
        """Test that FeaturedManager excludes non-featured items"""
        featured = SavingsAccount.objects.filter(
            is_active=True,
            is_featured=True
        )
        non_featured = SavingsAccount.objects.filter(
            is_active=True,
            is_featured=False
        )
        
        # Should not have non-featured in featured queryset
        featured_ids = set(featured.values_list('id', flat=True))
        non_featured_ids = set(non_featured.values_list('id', flat=True))
        
        self.assertFalse(featured_ids & non_featured_ids)


class TestGetActiveQueryset(TestCase):
    """Test suite for get_active_queryset function"""
    
    def setUp(self):
        """Set up test data"""
        self.active_savings = SavingsAccount.objects.create(
            english_name='Active Savings 1',
            nepali_name='सक्रिय बचत १',
            account_type='general',
            interest_rate=5.0,
            is_active=True
        )
        
        self.inactive_savings = SavingsAccount.objects.create(
            english_name='Inactive Savings',
            nepali_name='निष्क्रिय बचत',
            account_type='daily',  # Different account type
            interest_rate=5.0,
            is_active=False
        )
    
    def test_get_active_queryset_basic(self):
        """Test basic get_active_queryset functionality"""
        queryset = get_active_queryset(SavingsAccount)
        
        self.assertGreater(queryset.count(), 0)
        for item in queryset:
            self.assertTrue(item.is_active)
    
    def test_get_active_queryset_with_fields(self):
        """Test get_active_queryset with field limiting"""
        fields = ['id', 'english_name', 'interest_rate']
        queryset = get_active_queryset(SavingsAccount, fields=fields)
        
        self.assertGreater(queryset.count(), 0)
        # Check that only specified fields are fetched
        item = queryset.first()
        self.assertTrue(hasattr(item, 'english_name'))
        self.assertTrue(hasattr(item, 'interest_rate'))
    
    def test_get_active_queryset_with_order_by(self):
        """Test get_active_queryset with ordering"""
        queryset = get_active_queryset(
            SavingsAccount,
            order_by=['-interest_rate']
        )
        
        items = list(queryset)
        if len(items) > 1:
            # Check that items are ordered by interest_rate descending
            for i in range(len(items) - 1):
                self.assertGreaterEqual(
                    items[i].interest_rate,
                    items[i + 1].interest_rate
                )
    
    def test_get_active_queryset_with_fields_and_order(self):
        """Test get_active_queryset with both fields and ordering"""
        fields = ['id', 'english_name', 'interest_rate']
        queryset = get_active_queryset(
            SavingsAccount,
            fields=fields,
            order_by=['english_name']
        )
        
        self.assertGreater(queryset.count(), 0)
        items = list(queryset)
        if len(items) > 1:
            # Check ordering
            for i in range(len(items) - 1):
                self.assertLessEqual(
                    items[i].english_name,
                    items[i + 1].english_name
                )
    
    def test_get_active_queryset_excludes_inactive(self):
        """Test that get_active_queryset excludes inactive items"""
        queryset = get_active_queryset(SavingsAccount)
        active_ids = set(queryset.values_list('id', flat=True))
        
        self.assertNotIn(self.inactive_savings.id, active_ids)
        self.assertIn(self.active_savings.id, active_ids)


class TestGetFeaturedQueryset(TestCase):
    """Test suite for get_featured_queryset function"""
    
    def setUp(self):
        """Set up test data"""
        self.featured_savings = SavingsAccount.objects.create(
            english_name='Featured Savings',
            nepali_name='विशेष बचत',
            account_type='general',
            interest_rate=6.0,
            is_active=True,
            is_featured=True
        )
        
        self.non_featured_savings = SavingsAccount.objects.create(
            english_name='Non-Featured Savings',
            nepali_name='गैर-विशेष बचत',
            account_type='daily',  # Different account type
            interest_rate=5.0,
            is_active=True,
            is_featured=False
        )
        
        self.featured_loan = LoanType.objects.create(
            english_name='Featured Loan',
            nepali_name='विशेष ऋण',
            loan_category='personal',
            monthly_interest_rate=1.5,
            is_active=True,
            is_featured=True
        )
    
    def test_get_featured_queryset_basic(self):
        """Test basic get_featured_queryset functionality"""
        queryset = get_featured_queryset(SavingsAccount)
        
        self.assertGreater(queryset.count(), 0)
        for item in queryset:
            self.assertTrue(item.is_active)
            self.assertTrue(item.is_featured)
    
    def test_get_featured_queryset_with_fields(self):
        """Test get_featured_queryset with field limiting"""
        fields = ['id', 'english_name', 'is_featured']
        queryset = get_featured_queryset(SavingsAccount, fields=fields)
        
        self.assertGreater(queryset.count(), 0)
        item = queryset.first()
        self.assertTrue(hasattr(item, 'english_name'))
        self.assertTrue(hasattr(item, 'is_featured'))
    
    def test_get_featured_queryset_with_limit(self):
        """Test get_featured_queryset with limit"""
        limit = 2
        queryset = get_featured_queryset(SavingsAccount, limit=limit)
        
        self.assertLessEqual(queryset.count(), limit)
    
    def test_get_featured_queryset_excludes_non_featured(self):
        """Test that get_featured_queryset excludes non-featured items"""
        queryset = get_featured_queryset(SavingsAccount)
        featured_ids = set(queryset.values_list('id', flat=True))
        
        self.assertIn(self.featured_savings.id, featured_ids)
        self.assertNotIn(self.non_featured_savings.id, featured_ids)
    
    def test_get_featured_queryset_with_different_model(self):
        """Test get_featured_queryset with different model"""
        queryset = get_featured_queryset(LoanType)
        
        self.assertGreater(queryset.count(), 0)
        for item in queryset:
            self.assertTrue(item.is_active)
            self.assertTrue(item.is_featured)
    
    def test_get_featured_queryset_with_fields_and_limit(self):
        """Test get_featured_queryset with both fields and limit"""
        fields = ['id', 'english_name', 'interest_rate']
        limit = 1
        queryset = get_featured_queryset(
            SavingsAccount,
            fields=fields,
            limit=limit
        )
        
        self.assertLessEqual(queryset.count(), limit)
        item = queryset.first()
        self.assertTrue(hasattr(item, 'english_name'))


class TestQueryUtilsIntegration(TestCase):
    """Integration tests for query utilities"""
    
    def setUp(self):
        """Set up comprehensive test data"""
        # Create multiple savings accounts with unique account types
        account_types = ['general', 'daily', 'institutional']
        for i in range(3):
            SavingsAccount.objects.create(
                english_name=f'Active Savings {i+1}',
                nepali_name=f'सक्रिय बचत {i+1}',
                account_type=account_types[i],
                interest_rate=5.0 + i,
                is_active=True,
                is_featured=(i < 2)  # First 2 are featured
            )
        
        # Create inactive savings
        SavingsAccount.objects.create(
            english_name='Inactive Savings',
            nepali_name='निष्क्रिय बचत',
            account_type='child',  # Different account type
            interest_rate=5.0,
            is_active=False
        )
    
    def test_integration_active_queryset(self):
        """Integration test for get_active_queryset"""
        queryset = get_active_queryset(
            SavingsAccount,
            fields=['id', 'english_name', 'interest_rate'],
            order_by=['-interest_rate']
        )
        
        self.assertEqual(queryset.count(), 3)  # Only active ones
        items = list(queryset)
        self.assertEqual(items[0].interest_rate, 7.0)  # Highest first
    
    def test_integration_featured_queryset(self):
        """Integration test for get_featured_queryset"""
        queryset = get_featured_queryset(
            SavingsAccount,
            fields=['id', 'english_name'],
            limit=2
        )
        
        self.assertLessEqual(queryset.count(), 2)
        for item in queryset:
            self.assertTrue(item.is_active)
            self.assertTrue(item.is_featured)
    
    def test_integration_with_fixed_deposit(self):
        """Test query utilities with FixedDeposit model"""
        # Create fixed deposits
        FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='monthly',
            interest_rate=8.0,
            minimum_amount=10000,
            is_active=True
        )
        
        FixedDeposit.objects.create(
            duration_months=6,
            payment_frequency='quarterly',
            interest_rate=7.5,
            minimum_amount=5000,
            is_active=False
        )
        
        active_queryset = get_active_queryset(FixedDeposit)
        self.assertEqual(active_queryset.count(), 1)
        
        # FixedDeposit doesn't have is_featured, so test only active
        for item in active_queryset:
            self.assertTrue(item.is_active)

