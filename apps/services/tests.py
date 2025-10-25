from django.test import TestCase, Client
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType

from .models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief,
    ServiceApplication, ServiceAnalytics
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


# --- Tracking & Analytics Model Tests (UPGRADED) ---

class ServiceApplicationModelTest(TestCase):
    """
    Test suite for the ServiceApplication model, focusing on the GenericForeignKey relationship.
    """
    @classmethod
    def setUpTestData(cls):
        cls.savings = SavingsAccount.objects.create(account_type='general', english_name='Test Savings', interest_rate=5.0)
        cls.loan = LoanType.objects.create(loan_category='personal', english_name='Test Loan', monthly_interest_rate=1.0)

        # Create an application linked to the SavingsAccount
        cls.app_for_savings = ServiceApplication.objects.create(
            service_object=cls.savings,
            applicant_name='Jane Doe',
            applicant_email='jane@example.com',
            applicant_phone='9800000001'
        )
        
        # Create an application linked to the LoanType
        cls.app_for_loan = ServiceApplication.objects.create(
            service_object=cls.loan,
            applicant_name='John Smith',
            applicant_email='john@example.com',
            applicant_phone='9800000002'
        )

    def test_generic_foreign_key_linking(self):
        """Test that the service_object correctly links to different service models."""
        self.assertEqual(self.app_for_savings.service_object, self.savings)
        self.assertEqual(self.app_for_loan.service_object, self.loan)
        self.assertIsInstance(self.app_for_savings.service_object, SavingsAccount)
        self.assertIsInstance(self.app_for_loan.service_object, LoanType)

    def test_service_name_property(self):
        """Test the `service_name` property returns the correct name from the linked object."""
        self.assertEqual(self.app_for_savings.service_name, 'Test Savings')
        self.assertEqual(self.app_for_loan.service_name, 'Test Loan')

    def test_str_representation(self):
        """Test the application's string representation."""
        expected_str = f"Application from {self.app_for_savings.applicant_name} for {self.savings.english_name}"
        self.assertEqual(str(self.app_for_savings), expected_str)

class ServiceAnalyticsModelTest(TestCase):
    """
    Test suite for the ServiceAnalytics model, focusing on the GenericForeignKey.
    """
    def test_analytics_linking(self):
        """Test creating an analytics entry linked to a service."""
        from datetime import date
        loan = LoanType.objects.create(loan_category='education', english_name='Edu Loan', monthly_interest_rate=1.0)
        
        analytics_entry = ServiceAnalytics.objects.create(
            service_object=loan,
            date=date.today(),
            page_views=150,
            calculator_usage=25
        )
        
        self.assertEqual(analytics_entry.service_object, loan)
        self.assertEqual(analytics_entry.page_views, 150)
        self.assertEqual(str(analytics_entry), f"Analytics for {loan} on {date.today()}")

# --- View Tests (Placeholder for future update) ---

# TODO: Update these view tests to use slug-based lookups instead of IDs.
# This requires updating the urls.py and views.py files first to handle slugs.
class ServicesViewsTest(TestCase):
    """
    Test suite for the service-related views.
    NOTE: These tests assume URLs have been updated to use slugs.
    """
    def setUp(self):
        self.client = Client()
        self.savings_account = SavingsAccount.objects.create(
            account_type='general',
            english_name='General Savings',
            interest_rate=5.50
        )
        self.loan_type = LoanType.objects.create(
            loan_category='business',
            english_name='Business Loan',
            monthly_interest_rate=1.50
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

    def test_loan_detail_view(self):
        """Test the detail view for a specific loan type using its slug."""
        url = reverse('services:loan_detail', kwargs={'slug': self.loan_type.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Business Loan')
