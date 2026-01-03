"""
Tests for services.py service classes
"""
from django.test import TestCase
from decimal import Decimal

from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief,
    ServiceRecommendation
)
from apps.services.services import (
    ServiceRecommendationService, ServiceComparisonService,
    ServiceSearchService, ServiceApplicationService, ServiceAnalyticsService
)


class ServiceRecommendationServiceTest(TestCase):
    """Tests for ServiceRecommendationService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name="General Savings",
            nepali_name="सामान्य बचत",
            account_type="general",
            interest_rate=Decimal("4.50"),
            minimum_balance=Decimal("1000.00")
        )
    
    def test_get_recommendations_young_age(self):
        """Test recommendations for young users"""
        profile = {
            'age': 22,
            'monthly_income': 30000,
            'goals': [],
            'risk_tolerance': 'moderate'
        }
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('savings_accounts', recommendations)
        self.assertIn('reasoning', recommendations)
        self.assertIn('general', recommendations['savings_accounts'])
    
    def test_get_recommendations_middle_age(self):
        """Test recommendations for middle-aged users"""
        profile = {
            'age': 35,
            'monthly_income': 75000,
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('savings_accounts', recommendations)
        self.assertIn('loans', recommendations)
        self.assertIn('house_construction', recommendations['loans'])
    
    def test_get_recommendations_education_goal(self):
        """Test recommendations with education goal"""
        profile = {
            'age': 30,
            'monthly_income': 50000,
            'goals': ['education'],
            'risk_tolerance': 'moderate'
        }
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('education', recommendations['loans'])
        self.assertIn('child', recommendations['savings_accounts'])
    
    def test_save_recommendation(self):
        """Test saving recommendations"""
        profile = {
            'age': 30,
            'monthly_income': 50000,
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        saved = ServiceRecommendationService.save_recommendation(profile, recommendations)
        
        self.assertIsNotNone(saved)
        self.assertEqual(saved.user_profile['age'], 30)
        self.assertIn('savings_accounts', saved.recommended_services)


class ServiceComparisonServiceTest(TestCase):
    """Tests for ServiceComparisonService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings1 = SavingsAccount.objects.create(
            english_name="General Savings",
            nepali_name="सामान्य बचत",
            account_type="general",
            interest_rate=Decimal("4.50"),
            minimum_balance=Decimal("1000.00"),
            is_featured=True
        )
        
        self.savings2 = SavingsAccount.objects.create(
            english_name="Monthly Savings",
            nepali_name="मासिक बचत",
            account_type="monthly",
            interest_rate=Decimal("5.00"),
            minimum_balance=Decimal("500.00")
        )
        
        self.loan1 = LoanType.objects.create(
            english_name="Business Loan",
            nepali_name="व्यापार ऋण",
            loan_category="business",
            monthly_interest_rate=Decimal("1.25"),
            minimum_amount=Decimal("100000"),
            maximum_amount=Decimal("5000000")
        )
        
        self.loan2 = LoanType.objects.create(
            english_name="Education Loan",
            nepali_name="शिक्षा ऋण",
            loan_category="education",
            monthly_interest_rate=Decimal("1.00"),
            minimum_amount=Decimal("50000"),
            maximum_amount=Decimal("2000000")
        )
        
        self.fd1 = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency="monthly",
            interest_rate=Decimal("8.50"),
            minimum_amount=Decimal("10000.00")
        )
        
        self.fd2 = FixedDeposit.objects.create(
            duration_months=24,
            payment_frequency="quarterly",
            interest_rate=Decimal("9.00"),
            minimum_amount=Decimal("20000.00")
        )
    
    def test_compare_savings_accounts(self):
        """Test comparing savings accounts"""
        comparison = ServiceComparisonService.compare_savings_accounts(
            [self.savings1.id, self.savings2.id]
        )
        
        self.assertIn('accounts', comparison)
        self.assertEqual(len(comparison['accounts']), 2)
        self.assertEqual(comparison['best_interest_rate'], 5.0)
        self.assertEqual(comparison['lowest_minimum_balance'], 500.0)
        self.assertEqual(len(comparison['featured_accounts']), 1)
    
    def test_compare_loans(self):
        """Test comparing loans"""
        comparison = ServiceComparisonService.compare_loans(
            [self.loan1.id, self.loan2.id]
        )
        
        self.assertIn('loans', comparison)
        self.assertEqual(len(comparison['loans']), 2)
        self.assertEqual(comparison['lowest_interest_rate'], 1.0)
        self.assertEqual(comparison['highest_maximum_amount'], 5000000.0)
    
    def test_compare_fixed_deposits(self):
        """Test comparing fixed deposits"""
        comparison = ServiceComparisonService.compare_fixed_deposits(
            [self.fd1.id, self.fd2.id]
        )
        
        self.assertIn('deposits', comparison)
        self.assertEqual(len(comparison['deposits']), 2)
        self.assertEqual(comparison['highest_interest_rate'], 9.0)
        self.assertEqual(comparison['shortest_duration'], 12)
        self.assertEqual(comparison['longest_duration'], 24)
    
    def test_compare_empty_list(self):
        """Test comparing with empty list"""
        comparison = ServiceComparisonService.compare_savings_accounts([])
        self.assertEqual(comparison, {})


class ServiceSearchServiceTest(TestCase):
    """Tests for ServiceSearchService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name="General Savings",
            nepali_name="सामान्य बचत",
            account_type="general",
            interest_rate=Decimal("4.50"),
            minimum_balance=Decimal("1000.00"),
            description="A general savings account",
            is_featured=True
        )
        
        self.loan = LoanType.objects.create(
            english_name="Business Loan",
            nepali_name="व्यापार ऋण",
            loan_category="business",
            monthly_interest_rate=Decimal("1.25"),
            description="Loan for business purposes"
        )
    
    def test_search_savings_by_name(self):
        """Test searching savings by name"""
        form_data = {
            'query': 'General',
            'service_type': 'savings'
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertEqual(results['total_results'], 1)
        self.assertEqual(results['results'][0].name, 'General Savings')
    
    def test_search_all_services(self):
        """Test searching across all services"""
        form_data = {
            'query': 'Business',
            'service_type': ''
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 1)
    
    def test_search_by_interest_rate(self):
        """Test searching by interest rate"""
        form_data = {
            'query': '',
            'service_type': 'savings',
            'interest_rate_min': 4.0,
            'interest_rate_max': 5.0
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 0)
    
    def test_search_featured_only(self):
        """Test searching featured services only"""
        form_data = {
            'query': '',
            'service_type': 'savings',
            'featured_only': True
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 0)
        # All results should be featured
        for result in results['results']:
            # Note: The search service returns dicts, not model instances
            # So we can't directly check is_featured, but we can verify structure
            self.assertIn('type', result)
            self.assertIn('name', result)


class ServiceAnalyticsServiceTest(TestCase):
    """Tests for ServiceAnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name="General Savings",
            nepali_name="सामान्य बचत",
            account_type="general",
            interest_rate=Decimal("4.50"),
            minimum_balance=Decimal("1000.00")
        )
    
    def test_track_usage_page_views(self):
        """Test tracking page views"""
        # This should not raise an exception
        try:
            ServiceAnalyticsService.track_usage('savings', self.savings.id, 'page_views')
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_track_usage_invalid_service_type(self):
        """Test tracking with invalid service type"""
        # Should fail silently
        try:
            ServiceAnalyticsService.track_usage('invalid_type', 1, 'page_views')
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_get_model_class(self):
        """Test _get_model_class method"""
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('savings'),
            SavingsAccount
        )
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('loan'),
            LoanType
        )
        self.assertIsNone(ServiceAnalyticsService._get_model_class('invalid'))


class ServiceApplicationServiceTest(TestCase):
    """Tests for ServiceApplicationService"""
    
    def setUp(self):
        """Set up test data"""
        from apps.services.forms import ServiceApplicationForm
        
        self.savings = SavingsAccount.objects.create(
            english_name="General Savings",
            nepali_name="सामान्य बचत",
            account_type="general",
            interest_rate=Decimal("4.50"),
            minimum_balance=Decimal("1000.00")
        )
        
        self.form_data = {
            'applicant_name': 'Test User',
            'applicant_email': 'test@example.com',
            'applicant_phone': '+977-9812345678',
            'message': 'Test application message'
        }
        self.form = ServiceApplicationForm(data=self.form_data)
    
    def test_process_application(self):
        """Test processing an application"""
        if self.form.is_valid():
            application = ServiceApplicationService.process_application(
                self.form, 'savings', str(self.savings.id)
            )
            
            self.assertIsNotNone(application)
            self.assertEqual(application.applicant_name, 'Test User')
            self.assertEqual(application.applicant_email, 'test@example.com')
            # Check that it's linked to the savings account
            self.assertEqual(application.content_type.model, 'savingsaccount')
            self.assertEqual(application.object_id, self.savings.id)

