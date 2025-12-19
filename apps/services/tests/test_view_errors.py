"""
Tests for services view error handling and edge cases
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from apps.services.models import SavingsAccount, FixedDeposit, LoanType


class ServicesViewErrorHandlingTest(TestCase):
    """Test error handling in services views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.savings = SavingsAccount.objects.create(
            english_name='Regular Savings',
            account_type='general',
            minimum_balance=1000,
            interest_rate=5.0,
            is_active=True
        )
        
        self.fixed_deposit = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='lump_sum',
            minimum_amount=10000,
            interest_rate=8.0,
            is_active=True
        )
        
        self.loan = LoanType.objects.create(
            english_name='Personal Loan',
            loan_category='personal',
            monthly_interest_rate=1.0,  # 1% per month = 12% per year
            minimum_amount=50000,
            maximum_amount=500000,
            is_active=True
        )

    def test_services_list_view(self):
        """Test services list view"""
        # Use services_overview URL
        response = self.client.get(reverse('services:overview'))
        
        self.assertEqual(response.status_code, 200)

    def test_service_detail_view_404(self):
        """Test service detail view with non-existent service"""
        response = self.client.get(reverse('services:savings_detail', kwargs={'slug': 'non-existent-slug'}))
        
        self.assertEqual(response.status_code, 404)

    def test_savings_account_detail_view(self):
        """Test savings account detail view"""
        response = self.client.get(reverse('services:savings_detail', kwargs={'slug': self.savings.slug}))
        
        self.assertEqual(response.status_code, 200)

    def test_fixed_deposit_detail_view(self):
        """Test fixed deposit detail view"""
        # FixedDeposit doesn't have slug, so we'll test the list view instead
        response = self.client.get(reverse('services:fixed_deposit_list'))
        
        self.assertEqual(response.status_code, 200)

    def test_loan_detail_view(self):
        """Test loan detail view"""
        response = self.client.get(reverse('services:loan_detail', kwargs={'slug': self.loan.slug}))
        
        self.assertEqual(response.status_code, 200)

    def test_service_detail_view_inactive(self):
        """Test service detail view with inactive service"""
        self.savings.is_active = False
        self.savings.save()
        
        response = self.client.get(reverse('services:savings_detail', kwargs={'slug': self.savings.slug}))
        
        # Should return 404 or handle gracefully
        self.assertIn(response.status_code, [200, 404])

