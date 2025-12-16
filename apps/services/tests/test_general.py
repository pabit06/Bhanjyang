from django.test import TestCase, Client
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from datetime import date

from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief,
    ServiceApplication, ServiceAnalytics, ServiceRecommendation
)
from apps.services.services import (
    ServiceAnalyticsService, ServiceRecommendationService,
    ServiceComparisonService, ServiceSearchService
)

# --- Core Service Model Tests ---

class SavingsAccountModelTest(TestCase):
    """Test suite for the SavingsAccount model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.savings_account = SavingsAccount.objects.create(
            account_type='general',
            nepali_name='साधारण बचत',
            english_name='General Savings',
            interest_rate=5.50,
            minimum_balance=1000.00,
            is_featured=True
        )

    def test_savings_account_creation(self):
        """Test the basic creation and field assignments for a SavingsAccount."""
        self.assertEqual(self.savings_account.english_name, 'General Savings')
        self.assertEqual(self.savings_account.interest_rate, 5.50)
        self.assertTrue(self.savings_account.is_featured)

    def test_slug_auto_generation(self):
        """Test that the slug is automatically generated from the english_name upon saving."""
        expected_slug = slugify(self.savings_account.english_name)
        self.assertEqual(self.savings_account.slug, expected_slug)

    def test_get_absolute_url(self):
        """Test that get_absolute_url returns the correct URL based on the slug."""
        expected_url = reverse('services:savings_detail', kwargs={'slug': self.savings_account.slug})
        self.assertEqual(self.savings_account.get_absolute_url(), expected_url)

    def test_str_representation(self):
        """Test the human-readable string representation of the model."""
        expected = f"{self.savings_account.english_name} ({self.savings_account.interest_rate}%)"
        self.assertEqual(str(self.savings_account), expected)

    def test_meta_ordering(self):
        """Test that the default ordering places featured accounts first."""
        SavingsAccount.objects.create(
            account_type='child',
            english_name='Child Savings',
            interest_rate=6.00,
            is_featured=False
        )
        accounts = SavingsAccount.objects.all()
        self.assertEqual(accounts.first(), self.savings_account, "Featured account should be first.")


class FixedDepositModelTest(TestCase):
    """Test suite for the FixedDeposit model."""

    @classmethod
    def setUpTestData(cls):
        cls.fixed_deposit = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='monthly',
            interest_rate=8.50,
            minimum_amount=50000.00
        )

    def test_fixed_deposit_creation(self):
        """Test basic field assignments."""
        self.assertEqual(self.fixed_deposit.duration_months, 12)
        self.assertEqual(self.fixed_deposit.interest_rate, 8.50)

    def test_str_representation(self):
        """Test the string representation, ensuring display names are used."""
        expected = f"{self.fixed_deposit.get_duration_months_display()} - {self.fixed_deposit.get_payment_frequency_display()} ({self.fixed_deposit.interest_rate}%)"
        self.assertEqual(str(self.fixed_deposit), expected)

    def test_unique_together_constraint(self):
        """Test that creating a duplicate duration/frequency pair raises an integrity error."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            FixedDeposit.objects.create(
                duration_months=12,
                payment_frequency='monthly',
                interest_rate=9.00,
                minimum_amount=50000.00
            )


class LoanTypeModelTest(TestCase):
    """Test suite for the LoanType model."""

    @classmethod
    def setUpTestData(cls):
        cls.loan_type = LoanType.objects.create(
            loan_category='business',
            nepali_name='व्यवसाय ऋण',
            english_name='Business Loan',
            monthly_interest_rate=1.25, # e.g., 15% annually
        )

    def test_slug_auto_generation(self):
        """Test slug auto-generation."""
        self.assertEqual(self.loan_type.slug, 'business-loan')

    def test_get_absolute_url(self):
        """Test the get_absolute_url method."""
        expected_url = reverse('services:loan_detail', kwargs={'slug': self.loan_type.slug})
        self.assertEqual(self.loan_type.get_absolute_url(), expected_url)

    def test_annual_interest_rate_property(self):
        """Test the calculated `annual_interest_rate` property."""
        expected_annual_rate = self.loan_type.monthly_interest_rate * 12
        self.assertEqual(self.loan_type.annual_interest_rate, expected_annual_rate)

    def test_str_representation(self):
        """Test the string representation."""
        self.assertEqual(str(self.loan_type), self.loan_type.english_name)


# --- Services Layer Tests ---

class ServiceAnalyticsServiceTest(TestCase):
    def setUp(self):
        self.loan = LoanType.objects.create(
            loan_category='personal', 
            english_name='Test Analytics Loan', 
            monthly_interest_rate=1.0
        )

    def test_track_usage_creates_analytics_entry(self):
        ServiceAnalyticsService.track_usage('loan', self.loan.id, 'page_views')
        
        analytics = ServiceAnalytics.objects.filter(object_id=self.loan.id).first()
        self.assertIsNotNone(analytics)
        self.assertEqual(analytics.page_views, 1)
        self.assertEqual(analytics.service_object, self.loan)

    def test_track_usage_increments_count(self):
        ServiceAnalyticsService.track_usage('loan', self.loan.id, 'page_views')
        ServiceAnalyticsService.track_usage('loan', self.loan.id, 'page_views')
        
        analytics = ServiceAnalytics.objects.filter(object_id=self.loan.id).first()
        self.assertEqual(analytics.page_views, 2)


class ServiceRecommendationServiceTest(TestCase):
    def test_get_recommendations(self):
        profile = {
            'age': 22,
            'monthly_income': 20000,
            'goals': ['education'],
            'risk_tolerance': 'conservative'
        }
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('savings_accounts', recommendations)
        self.assertIn('loans', recommendations)
        self.assertIn('fixed_deposits', recommendations)
        # Check specific recommendation logic
        self.assertIn('general', recommendations['savings_accounts'])
        self.assertIn('education', recommendations['loans'])

    def test_save_recommendation(self):
        profile = {'age': 30, 'income': 50000}
        recs = {'reasoning': ['Test reason']}
        rec_obj = ServiceRecommendationService.save_recommendation(profile, recs)
        
        self.assertIsInstance(rec_obj, ServiceRecommendation)
        self.assertEqual(rec_obj.user_profile, profile)
        self.assertEqual(rec_obj.recommendation_reason, 'Test reason')


class ServiceComparisonServiceTest(TestCase):
    def setUp(self):
        self.s1 = SavingsAccount.objects.create(account_type='g1', english_name='S1', interest_rate=5.0, is_active=True)
        self.s2 = SavingsAccount.objects.create(account_type='g2', english_name='S2', interest_rate=6.0, is_active=True)

    def test_compare_savings_accounts(self):
        result = ServiceComparisonService.compare_savings_accounts([self.s1.id, self.s2.id])
        
        self.assertIn('accounts', result)
        self.assertEqual(len(result['accounts']), 2)
        self.assertEqual(result['best_interest_rate'], 6.0)


class ServiceSearchServiceTest(TestCase):
    def setUp(self):
        self.s1 = SavingsAccount.objects.create(english_name='Super Saver', interest_rate=5.0, is_active=True)
        self.l1 = LoanType.objects.create(english_name='Super Loan', monthly_interest_rate=1.0, is_active=True)

    def test_search_services_generic(self):
        # Search for "Super"
        results = ServiceSearchService.search_services({'query': 'Super'})
        self.assertEqual(results['total_results'], 2)
        
    def test_search_services_type_specific(self):
        results = ServiceSearchService.search_services({'query': 'Super', 'service_type': 'savings'})
        self.assertEqual(results['total_results'], 1)
        self.assertEqual(results['results'][0]['type'], 'savings')


# --- View Tests ---

class ServicesViewsTest(TestCase):
    """
    Test suite for the service-related views.
    """
    def setUp(self):
        self.client = Client()
        self.savings_account = SavingsAccount.objects.create(
            account_type='general',
            english_name='General Savings',
            interest_rate=5.50,
            is_featured=True
        )
        self.loan_type = LoanType.objects.create(
            loan_category='business',
            english_name='Business Loan',
            monthly_interest_rate=1.50,
            is_featured=True
        )

    def test_services_overview_view(self):
        """Test that the main services overview page loads and contains service names."""
        response = self.client.get(reverse('services:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'General Savings')
        self.assertContains(response, 'Business Loan')

    def test_savings_list_view(self):
        """Test the savings account list page."""
        response = self.client.get(reverse('services:savings_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'General Savings')

    def test_savings_detail_view(self):
        """Test the detail view for a specific savings account using its slug."""
        url = reverse('services:savings_detail', kwargs={'slug': self.savings_account.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'General Savings')
        
        # Verify analytics tracked
        # Only if we can rely on tracking working synchronously
        ct = ContentType.objects.get_for_model(SavingsAccount)
        self.assertTrue(ServiceAnalytics.objects.filter(content_type=ct, object_id=self.savings_account.id).exists())

    def test_loan_detail_view(self):
        """Test the detail view for a specific loan type using its slug."""
        url = reverse('services:loan_detail', kwargs={'slug': self.loan_type.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Business Loan')

    def test_loan_calculator_view(self):
        url = reverse('services:loan_calculator')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Post request
        data = {
            'loan_type': self.loan_type.id,
            'principal_amount': 100000,
            'tenure_years': 1,
            'payment_frequency': 'monthly'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly EMI') # Assuming template contains this text for results

