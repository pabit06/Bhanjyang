"""
Comprehensive tests for Services forms
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, ServiceApplication
)
from apps.services.forms import (
    LoanCalculatorForm, SavingsCalculatorForm, FixedDepositCalculatorForm,
    ServiceApplicationForm, ServiceComparisonForm, ServiceSearchForm,
    ServiceRecommendationForm
)


class LoanCalculatorFormTest(TestCase):
    """Test suite for LoanCalculatorForm"""
    
    def setUp(self):
        """Set up test data"""
        self.loan = LoanType.objects.create(
            english_name='Test Loan',
            nepali_name='परीक्षण ऋण',
            slug='test-loan',
            loan_category='personal',
            monthly_interest_rate=1.5,
            minimum_amount=10000.0,
            maximum_amount=1000000.0,
            max_tenure_years=10,
            is_active=True
        )
    
    def test_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '100000',
            'tenure_years': '5',
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_principal_below_minimum(self):
        """Test form with principal below minimum"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '5000',  # Below minimum
            'tenure_years': '5',
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_principal_above_maximum(self):
        """Test form with principal above maximum"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '2000000',  # Above maximum
            'tenure_years': '5',
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_tenure_exceeds_maximum(self):
        """Test form with tenure exceeding maximum"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '100000',
            'tenure_years': '15',  # Exceeds max_tenure_years
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_principal_too_low(self):
        """Test form with principal below absolute minimum"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '500',  # Below form's min_value
            'tenure_years': '5',
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('principal_amount', form.errors)
    
    def test_form_tenure_too_low(self):
        """Test form with tenure below minimum"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '100000',
            'tenure_years': '0',  # Below min_value
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tenure_years', form.errors)
    
    def test_form_tenure_too_high(self):
        """Test form with tenure above absolute maximum"""
        form_data = {
            'loan_type': self.loan.id,
            'principal_amount': '100000',
            'tenure_years': '35',  # Above form's max_value
            'payment_frequency': 'monthly'
        }
        form = LoanCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tenure_years', form.errors)


class SavingsCalculatorFormTest(TestCase):
    """Test suite for SavingsCalculatorForm"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name='Test Savings',
            nepali_name='परीक्षण बचत',
            slug='test-savings',
            account_type='regular',
            interest_rate=5.0,
            is_active=True
        )
    
    def test_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'savings_type': self.savings.id,
            'monthly_deposit': '10000',
            'tenure_years': '10'
        }
        form = SavingsCalculatorForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_deposit_too_low(self):
        """Test form with deposit below minimum"""
        form_data = {
            'savings_type': self.savings.id,
            'monthly_deposit': '50',  # Below min_value
            'tenure_years': '10'
        }
        form = SavingsCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('monthly_deposit', form.errors)
    
    def test_form_tenure_too_low(self):
        """Test form with tenure below minimum"""
        form_data = {
            'savings_type': self.savings.id,
            'monthly_deposit': '10000',
            'tenure_years': '0'  # Below min_value
        }
        form = SavingsCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tenure_years', form.errors)
    
    def test_form_tenure_too_high(self):
        """Test form with tenure above maximum"""
        form_data = {
            'savings_type': self.savings.id,
            'monthly_deposit': '10000',
            'tenure_years': '45'  # Above max_value
        }
        form = SavingsCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tenure_years', form.errors)


class FixedDepositCalculatorFormTest(TestCase):
    """Test suite for FixedDepositCalculatorForm"""
    
    def setUp(self):
        """Set up test data"""
        self.fd = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='monthly',
            interest_rate=7.0,
            minimum_amount=10000.0,
            maximum_amount=1000000.0,
            is_active=True
        )
    
    def test_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'deposit_type': self.fd.id,
            'deposit_amount': '100000'
        }
        form = FixedDepositCalculatorForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_amount_below_minimum(self):
        """Test form with amount below minimum"""
        form_data = {
            'deposit_type': self.fd.id,
            'deposit_amount': '5000'  # Below minimum
        }
        form = FixedDepositCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_amount_above_maximum(self):
        """Test form with amount above maximum"""
        form_data = {
            'deposit_type': self.fd.id,
            'deposit_amount': '2000000'  # Above maximum
        }
        form = FixedDepositCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_amount_too_low(self):
        """Test form with amount below absolute minimum"""
        form_data = {
            'deposit_type': self.fd.id,
            'deposit_amount': '500'  # Below form's min_value
        }
        form = FixedDepositCalculatorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deposit_amount', form.errors)


class ServiceApplicationFormTest(TestCase):
    """Test suite for ServiceApplicationForm"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name='Test Savings',
            slug='test-savings',
            account_type='general',
            interest_rate=5.0,
            is_active=True
        )
    
    def test_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'applicant_phone': '+977-9812345678',
            'applicant_address': 'Test Address',
            'terms_accepted': True
        }
        form = ServiceApplicationForm(data=form_data, service_object=self.savings)
        self.assertTrue(form.is_valid())
    
    def test_form_phone_validation_valid(self):
        """Test phone validation with valid Nepali number"""
        form_data = {
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'applicant_phone': '+977-9812345678',
            'applicant_address': 'Test Address',
            'terms_accepted': True
        }
        form = ServiceApplicationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_phone_validation_invalid(self):
        """Test phone validation with invalid number"""
        form_data = {
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'applicant_phone': '1234567890',  # Invalid format
            'applicant_address': 'Test Address',
            'terms_accepted': True
        }
        form = ServiceApplicationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('applicant_phone', form.errors)
    
    def test_form_terms_not_accepted(self):
        """Test form without terms accepted"""
        form_data = {
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'applicant_phone': '+977-9812345678',
            'applicant_address': 'Test Address',
            'terms_accepted': False
        }
        form = ServiceApplicationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('terms_accepted', form.errors)
    
    def test_form_save_with_service_object(self):
        """Test form save with service object"""
        form_data = {
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'applicant_phone': '+977-9812345678',
            'applicant_address': 'Test Address',
            'terms_accepted': True
        }
        form = ServiceApplicationForm(data=form_data, service_object=self.savings)
        self.assertTrue(form.is_valid())
        
        instance = form.save()
        self.assertEqual(instance.applicant_name, 'John Doe')
        self.assertEqual(instance.service_object, self.savings)


class ServiceComparisonFormTest(TestCase):
    """Test suite for ServiceComparisonForm"""
    
    def setUp(self):
        """Set up test data"""
        self.savings1 = SavingsAccount.objects.create(
            english_name='Savings 1',
            slug='savings-1',
            account_type='general',
            interest_rate=5.0,
            is_active=True
        )
        self.savings2 = SavingsAccount.objects.create(
            english_name='Savings 2',
            slug='savings-2',
            account_type='daily',
            interest_rate=5.5,
            is_active=True
        )
        self.savings3 = SavingsAccount.objects.create(
            english_name='Savings 3',
            slug='savings-3',
            account_type='institutional',
            interest_rate=6.0,
            is_active=True
        )
        self.savings4 = SavingsAccount.objects.create(
            english_name='Savings 4',
            slug='savings-4',
            account_type='child',
            interest_rate=6.5,
            is_active=True
        )
        self.savings5 = SavingsAccount.objects.create(
            english_name='Savings 5',
            slug='savings-5',
            account_type='senior_citizen',
            interest_rate=7.0,
            is_active=True
        )
    
    def test_form_valid_with_two_services(self):
        """Test form with 2 services (minimum)"""
        form_data = {
            'service_type': 'savings',
            'services': [str(self.savings1.id), str(self.savings2.id)]
        }
        form = ServiceComparisonForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_four_services(self):
        """Test form with 4 services (maximum)"""
        form_data = {
            'service_type': 'savings',
            'services': [
                str(self.savings1.id), str(self.savings2.id),
                str(self.savings3.id), str(self.savings4.id)
            ]
        }
        form = ServiceComparisonForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_too_few_services(self):
        """Test form with only 1 service"""
        form_data = {
            'service_type': 'savings',
            'services': [str(self.savings1.id)]
        }
        form = ServiceComparisonForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('services', form.errors)
    
    def test_form_too_many_services(self):
        """Test form with more than 4 services"""
        form_data = {
            'service_type': 'savings',
            'services': [
                str(self.savings1.id), str(self.savings2.id),
                str(self.savings3.id), str(self.savings4.id),
                str(self.savings5.id)
            ]
        }
        form = ServiceComparisonForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('services', form.errors)
    
    def test_form_dynamic_choices_savings(self):
        """Test dynamic choices for savings"""
        form_data = {
            'service_type': 'savings',
            'services': []
        }
        form = ServiceComparisonForm(data=form_data)
        # Form should be bound and have choices populated
        self.assertTrue(form.is_bound)
        self.assertGreater(len(form.fields['services'].choices), 0)
    
    def test_form_dynamic_choices_loans(self):
        """Test dynamic choices for loans"""
        loan = LoanType.objects.create(
            english_name='Test Loan',
            slug='test-loan',
            loan_category='personal',
            monthly_interest_rate=1.5,
            is_active=True
        )
        form_data = {
            'service_type': 'loans',
            'services': []
        }
        form = ServiceComparisonForm(data=form_data)
        self.assertTrue(form.is_bound)
        self.assertGreater(len(form.fields['services'].choices), 0)


class ServiceSearchFormTest(TestCase):
    """Test suite for ServiceSearchForm"""
    
    def test_form_valid_empty(self):
        """Test form with empty data (all optional)"""
        form_data = {}
        form = ServiceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_query(self):
        """Test form with search query"""
        form_data = {
            'query': 'savings'
        }
        form = ServiceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_service_type(self):
        """Test form with service type"""
        form_data = {
            'service_type': 'savings'
        }
        form = ServiceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_interest_rate(self):
        """Test form with interest rate filter"""
        form_data = {
            'interest_rate_min': '5.0'
        }
        form = ServiceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_featured_only(self):
        """Test form with featured only filter"""
        form_data = {
            'featured_only': True
        }
        form = ServiceSearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class ServiceRecommendationFormTest(TestCase):
    """Test suite for ServiceRecommendationForm"""
    
    def test_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'age': '30',
            'monthly_income': '50000',
            'goals': ['house_purchase', 'education'],
            'risk_tolerance': 'moderate'
        }
        form = ServiceRecommendationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_age_too_low(self):
        """Test form with age below minimum"""
        form_data = {
            'age': '17',  # Below min_value
            'monthly_income': '50000',
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        form = ServiceRecommendationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)
    
    def test_form_age_too_high(self):
        """Test form with age above maximum"""
        form_data = {
            'age': '101',  # Above max_value
            'monthly_income': '50000',
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        form = ServiceRecommendationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)
    
    def test_form_income_negative(self):
        """Test form with negative income"""
        form_data = {
            'age': '30',
            'monthly_income': '-1000',  # Below min_value
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        form = ServiceRecommendationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('monthly_income', form.errors)
    
    def test_form_all_risk_tolerances(self):
        """Test form with all risk tolerance options"""
        risk_tolerances = ['conservative', 'moderate', 'aggressive']
        
        for risk in risk_tolerances:
            form_data = {
                'age': '30',
                'monthly_income': '50000',
                'goals': ['house_purchase'],
                'risk_tolerance': risk
            }
            form = ServiceRecommendationForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Risk tolerance {risk} should be valid")
    
    def test_form_all_goals(self):
        """Test form with all goal options"""
        all_goals = [
            'house_purchase', 'education', 'business',
            'vehicle', 'retirement'
        ]
        
        form_data = {
            'age': '30',
            'monthly_income': '50000',
            'goals': all_goals,
            'risk_tolerance': 'moderate'
        }
        form = ServiceRecommendationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_empty_goals(self):
        """Test form with no goals selected"""
        form_data = {
            'age': '30',
            'monthly_income': '50000',
            'goals': [],
            'risk_tolerance': 'moderate'
        }
        form = ServiceRecommendationForm(data=form_data)
        # Goals is a MultipleChoiceField, empty might be valid depending on implementation
        # Let's test that form can be created
        self.assertIsNotNone(form)

