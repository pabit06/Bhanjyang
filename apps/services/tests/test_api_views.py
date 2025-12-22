"""
Comprehensive tests for services API views
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService,
    MemberRelief, ServiceApplication, ServiceAnalytics, ServiceRecommendation
)

User = get_user_model()


class SavingsAccountViewSetTest(TestCase):
    """Test cases for SavingsAccountViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test savings account
        self.savings_account = SavingsAccount.objects.create(
            english_name='Regular Savings',
            nepali_name='नियमित बचत',
            account_type='general',
            interest_rate=Decimal('5.5'),
            minimum_balance=Decimal('1000'),
            is_active=True,
            is_featured=True
        )

    def test_list_savings_accounts(self):
        """Test listing savings accounts"""
        response = self.client.get('/api/v1/savings-accounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_retrieve_savings_account(self):
        """Test retrieving a single savings account"""
        response = self.client.get(f'/api/v1/savings-accounts/{self.savings_account.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['english_name'], 'Regular Savings')

    def test_featured_savings_accounts(self):
        """Test getting featured savings accounts"""
        response = self.client.get('/api/v1/savings-accounts/featured/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertTrue(response.data[0]['is_featured'])

    def test_calculate_interest_valid(self):
        """Test calculating interest with valid parameters"""
        url = f'/api/v1/savings-accounts/{self.savings_account.id}/calculate_interest/'
        # Use GET with query parameters properly formatted
        response = self.client.get(url, {'amount': '10000', 'months': '12'})
        
        # The endpoint might be failing due to account not found or parameter parsing
        # Check if account exists and is active
        self.assertTrue(SavingsAccount.objects.filter(id=self.savings_account.id, is_active=True).exists())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                        f"Response status: {response.status_code}, data: {response.data}")
        if response.status_code == status.HTTP_200_OK:
            self.assertIn('principal', response.data)
            self.assertIn('interest_amount', response.data)
            self.assertIn('total_amount', response.data)
            self.assertEqual(float(response.data['principal']), 10000.0)

    def test_calculate_interest_missing_params(self):
        """Test calculating interest with missing parameters"""
        url = f'/api/v1/savings-accounts/{self.savings_account.id}/calculate_interest/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_calculate_interest_invalid_amount(self):
        """Test calculating interest with invalid amount"""
        url = f'/api/v1/savings-accounts/{self.savings_account.id}/calculate_interest/'
        response = self.client.get(url, {'amount': '-1000', 'months': '12'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_calculate_interest_invalid_months(self):
        """Test calculating interest with invalid months"""
        url = f'/api/v1/savings-accounts/{self.savings_account.id}/calculate_interest/'
        response = self.client.get(url, {'amount': '10000', 'months': '0'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filter_by_account_type(self):
        """Test filtering by account type"""
        response = self.client.get('/api/v1/savings-accounts/', {'account_type': 'general'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_savings_accounts(self):
        """Test searching savings accounts"""
        response = self.client.get('/api/v1/savings-accounts/', {'search': 'Regular'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FixedDepositViewSetTest(TestCase):
    """Test cases for FixedDepositViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test fixed deposit
        self.fixed_deposit = FixedDeposit.objects.create(
            duration_months=12,
            interest_rate=Decimal('7.5'),
            minimum_amount=Decimal('50000'),
            payment_frequency='monthly',
            benefits='High returns',
            is_active=True
        )

    def test_list_fixed_deposits(self):
        """Test listing fixed deposits"""
        response = self.client.get('/api/v1/fixed-deposits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_retrieve_fixed_deposit(self):
        """Test retrieving a single fixed deposit"""
        response = self.client.get(f'/api/v1/fixed-deposits/{self.fixed_deposit.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration_months'], 12)

    def test_by_duration_valid(self):
        """Test getting fixed deposits by duration"""
        response = self.client.get('/api/v1/fixed-deposits/by_duration/', {'duration': '12'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_by_duration_missing_param(self):
        """Test by_duration without duration parameter"""
        response = self.client.get('/api/v1/fixed-deposits/by_duration/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_by_duration_invalid(self):
        """Test by_duration with invalid duration"""
        response = self.client.get('/api/v1/fixed-deposits/by_duration/', {'duration': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filter_by_duration(self):
        """Test filtering by duration"""
        response = self.client.get('/api/v1/fixed-deposits/', {'duration_months': '12'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LoanTypeViewSetTest(TestCase):
    """Test cases for LoanTypeViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test loan type
        self.loan_type = LoanType.objects.create(
            english_name='Personal Loan',
            nepali_name='व्यक्तिगत ऋण',
            loan_category='personal',
            monthly_interest_rate=Decimal('1.5'),
            minimum_amount=Decimal('50000'),
            maximum_amount=Decimal('5000000'),
            is_active=True,
            is_featured=True
        )

    def test_list_loan_types(self):
        """Test listing loan types"""
        response = self.client.get('/api/v1/loan-types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_retrieve_loan_type(self):
        """Test retrieving a single loan type"""
        response = self.client.get(f'/api/v1/loan-types/{self.loan_type.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['english_name'], 'Personal Loan')

    def test_calculate_payment_valid(self):
        """Test calculating payment with valid parameters"""
        url = f'/api/v1/loan-types/{self.loan_type.id}/calculate_payment/'
        response = self.client.get(url, {'amount': '100000', 'months': '12'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('loan_amount', response.data)
        self.assertIn('monthly_payment', response.data)
        self.assertIn('total_payment', response.data)
        self.assertIn('total_interest', response.data)

    def test_calculate_payment_missing_params(self):
        """Test calculating payment with missing parameters"""
        url = f'/api/v1/loan-types/{self.loan_type.id}/calculate_payment/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_calculate_payment_below_minimum(self):
        """Test calculating payment with amount below minimum"""
        url = f'/api/v1/loan-types/{self.loan_type.id}/calculate_payment/'
        response = self.client.get(url, {'amount': '10000', 'months': '12'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_calculate_payment_above_maximum(self):
        """Test calculating payment with amount above maximum"""
        url = f'/api/v1/loan-types/{self.loan_type.id}/calculate_payment/'
        response = self.client.get(url, {'amount': '10000000', 'months': '12'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_calculate_payment_invalid_amount(self):
        """Test calculating payment with invalid amount"""
        url = f'/api/v1/loan-types/{self.loan_type.id}/calculate_payment/'
        response = self.client.get(url, {'amount': '-1000', 'months': '12'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_search_loan_types(self):
        """Test searching loan types"""
        response = self.client.get('/api/v1/loan-types/', {'search': 'Personal'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RemittanceServiceViewSetTest(TestCase):
    """Test cases for RemittanceServiceViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test remittance service
        self.remittance = RemittanceService.objects.create(
            english_name='Money Transfer',
            nepali_name='धन हस्तान्तरण',
            service_type='domestic',
            is_active=True,
            is_featured=True
        )

    def test_list_remittance_services(self):
        """Test listing remittance services"""
        response = self.client.get('/api/v1/remittance-services/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_retrieve_remittance_service(self):
        """Test retrieving a single remittance service"""
        response = self.client.get(f'/api/v1/remittance-services/{self.remittance.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['english_name'], 'Money Transfer')

    def test_filter_by_service_type(self):
        """Test filtering by service type"""
        response = self.client.get('/api/v1/remittance-services/', {'service_type': 'domestic'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MemberReliefViewSetTest(TestCase):
    """Test cases for MemberReliefViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test member relief
        self.relief = MemberRelief.objects.create(
            english_name='Emergency Relief',
            nepali_name='आपतकालीन राहत',
            relief_type='emergency',
            is_active=True,
            is_featured=True
        )

    def test_list_member_relief(self):
        """Test listing member relief services"""
        response = self.client.get('/api/v1/member-relief/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_retrieve_member_relief(self):
        """Test retrieving a single member relief"""
        response = self.client.get(f'/api/v1/member-relief/{self.relief.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['english_name'], 'Emergency Relief')

    def test_search_member_relief(self):
        """Test searching member relief"""
        response = self.client.get('/api/v1/member-relief/', {'search': 'Emergency'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ServiceApplicationViewSetTest(TestCase):
    """Test cases for ServiceApplicationViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test application
        self.application = ServiceApplication.objects.create(
            applicant_name='Test User',
            applicant_email='test@example.com',
            service_name='Test Service',
            status='pending'
        )

    def test_list_applications_authenticated(self):
        """Test listing applications when authenticated"""
        response = self.client.get('/api/v1/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_list_applications_unauthenticated(self):
        """Test listing applications when not authenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/applications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_application(self):
        """Test creating a new application"""
        data = {
            'applicant_name': 'New User',
            'applicant_email': 'new@example.com',
            'service_name': 'New Service',
            'status': 'pending'
        }
        response = self.client.post('/api/v1/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_by_status_valid(self):
        """Test getting applications by status"""
        response = self.client.get('/api/v1/applications/by_status/', {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_by_status_missing_param(self):
        """Test by_status without status parameter"""
        response = self.client.get('/api/v1/applications/by_status/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ServiceAnalyticsViewSetTest(TestCase):
    """Test cases for ServiceAnalyticsViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_analytics_authenticated(self):
        """Test listing analytics when authenticated"""
        response = self.client.get('/api/v1/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_list_analytics_unauthenticated(self):
        """Test listing analytics when not authenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/analytics/')
        # DRF's IsAuthenticated returns 403, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ServiceRecommendationViewSetTest(TestCase):
    """Test cases for ServiceRecommendationViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_recommendations_authenticated(self):
        """Test listing recommendations when authenticated"""
        response = self.client.get('/api/v1/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_list_recommendations_unauthenticated(self):
        """Test listing recommendations when not authenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/recommendations/')
        # DRF's IsAuthenticated returns 403, not 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ServiceSearchViewSetTest(TestCase):
    """Test cases for ServiceSearchViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test data
        SavingsAccount.objects.create(
            english_name='Test Savings',
            nepali_name='परीक्षण बचत',
            account_type='regular',
            interest_rate=Decimal('5.0'),
            is_active=True
        )
        
        LoanType.objects.create(
            english_name='Test Loan',
            nepali_name='परीक्षण ऋण',
            loan_category='personal',
            monthly_interest_rate=Decimal('1.5'),
            is_active=True
        )

    def test_search_all_services(self):
        """Test searching across all services"""
        response = self.client.get('/api/v1/search/', {'query': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('savings_accounts', response.data)
        self.assertIn('loan_types', response.data)

    def test_search_savings_only(self):
        """Test searching savings accounts only"""
        response = self.client.get('/api/v1/search/', {
            'query': 'Test',
            'service_type': 'savings'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('savings_accounts', response.data)

    def test_search_loans_only(self):
        """Test searching loans only"""
        response = self.client.get('/api/v1/search/', {
            'query': 'Test',
            'service_type': 'loan'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('loan_types', response.data)

    def test_search_with_filters(self):
        """Test searching with filters"""
        response = self.client.get('/api/v1/search/', {
            'query': 'Test',
            'is_featured': 'true',
            'min_interest_rate': '4.0'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_invalid_params(self):
        """Test searching with invalid parameters"""
        response = self.client.get('/api/v1/search/', {'invalid': 'param'})
        # Should handle gracefully
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

