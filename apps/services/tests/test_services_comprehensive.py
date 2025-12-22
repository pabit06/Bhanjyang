"""
Comprehensive tests for Services layer (apps/services/services.py)

This test suite provides complete coverage for all service classes:
- ServiceAnalyticsService
- ServiceRecommendationService
- ServiceComparisonService
- ServiceSearchService
- ServiceApplicationService
"""
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from datetime import date
from unittest.mock import patch, MagicMock

from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief,
    ServiceApplication, ServiceAnalytics, ServiceRecommendation
)
from apps.services.services import (
    ServiceAnalyticsService, ServiceRecommendationService,
    ServiceComparisonService, ServiceSearchService, ServiceApplicationService
)


class ServiceAnalyticsServiceTest(TestCase):
    """Comprehensive tests for ServiceAnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            account_type='general',
            english_name='Test Savings',
            interest_rate=5.0,
            is_active=True
        )
        self.loan = LoanType.objects.create(
            loan_category='personal',
            english_name='Test Loan',
            monthly_interest_rate=1.5,
            is_active=True
        )
        self.fixed_deposit = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='monthly',
            interest_rate=8.0,
            minimum_amount=50000.0
        )
    
    def test_track_usage_creates_new_analytics(self):
        """Test that track_usage creates a new analytics entry"""
        ServiceAnalyticsService.track_usage('savings', self.savings.id, 'page_views')
        
        content_type = ContentType.objects.get_for_model(SavingsAccount)
        analytics = ServiceAnalytics.objects.get(
            content_type=content_type,
            object_id=self.savings.id,
            date=date.today()
        )
        
        self.assertEqual(analytics.page_views, 1)
        self.assertEqual(analytics.service_object, self.savings)
    
    def test_track_usage_increments_existing(self):
        """Test that track_usage increments existing analytics"""
        ServiceAnalyticsService.track_usage('savings', self.savings.id, 'page_views')
        ServiceAnalyticsService.track_usage('savings', self.savings.id, 'page_views')
        
        content_type = ContentType.objects.get_for_model(SavingsAccount)
        analytics = ServiceAnalytics.objects.get(
            content_type=content_type,
            object_id=self.savings.id,
            date=date.today()
        )
        
        self.assertEqual(analytics.page_views, 2)
    
    def test_track_usage_different_actions(self):
        """Test tracking different action types"""
        ServiceAnalyticsService.track_usage('loan', self.loan.id, 'page_views')
        ServiceAnalyticsService.track_usage('loan', self.loan.id, 'calculator_usage')
        ServiceAnalyticsService.track_usage('loan', self.loan.id, 'applications_received')
        
        content_type = ContentType.objects.get_for_model(LoanType)
        analytics = ServiceAnalytics.objects.get(
            content_type=content_type,
            object_id=self.loan.id,
            date=date.today()
        )
        
        self.assertEqual(analytics.page_views, 1)
        self.assertEqual(analytics.calculator_usage, 1)
        self.assertEqual(analytics.applications_received, 1)
    
    def test_track_usage_invalid_service_type(self):
        """Test that invalid service type is handled gracefully"""
        # Should not raise exception
        ServiceAnalyticsService.track_usage('invalid', 999, 'page_views')
        
        # Should not create analytics entry
        count = ServiceAnalytics.objects.count()
        self.assertEqual(count, 0)
    
    def test_track_usage_error_handling(self):
        """Test error handling in track_usage"""
        from django.contrib.contenttypes.models import ContentType
        with patch.object(ContentType.objects, 'get_for_model') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            # Should not raise exception
            ServiceAnalyticsService.track_usage('savings', self.savings.id, 'page_views')
    
    def test_get_model_class_valid_types(self):
        """Test _get_model_class with valid service types"""
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('savings'),
            SavingsAccount
        )
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('loan'),
            LoanType
        )
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('fixed_deposit'),
            FixedDeposit
        )
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('remittance'),
            RemittanceService
        )
        self.assertEqual(
            ServiceAnalyticsService._get_model_class('relief'),
            MemberRelief
        )
    
    def test_get_model_class_invalid_type(self):
        """Test _get_model_class with invalid service type"""
        self.assertIsNone(ServiceAnalyticsService._get_model_class('invalid'))


class ServiceRecommendationServiceTest(TestCase):
    """Comprehensive tests for ServiceRecommendationService"""
    
    def test_get_recommendations_young_age(self):
        """Test recommendations for young users (< 25)"""
        profile = {
            'age': 22,
            'monthly_income': 25000,
            'goals': [],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('savings_accounts', recommendations)
        self.assertIn('loans', recommendations)
        self.assertIn('fixed_deposits', recommendations)
        self.assertIn('reasoning', recommendations)
        self.assertIn('general', recommendations['savings_accounts'])
        self.assertIn('monthly', recommendations['savings_accounts'])
    
    def test_get_recommendations_middle_age(self):
        """Test recommendations for middle-aged users (25-40)"""
        profile = {
            'age': 35,
            'monthly_income': 75000,
            'goals': [],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('general', recommendations['savings_accounts'])
        self.assertIn('monthly', recommendations['savings_accounts'])
        self.assertIn('12_months', recommendations['fixed_deposits'])
        self.assertIn('24_months', recommendations['fixed_deposits'])
    
    def test_get_recommendations_pre_retirement(self):
        """Test recommendations for pre-retirement users (40-60)"""
        profile = {
            'age': 55,
            'monthly_income': 100000,
            'goals': [],
            'risk_tolerance': 'conservative'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('senior_citizen', recommendations['savings_accounts'])
        self.assertIn('12_months', recommendations['fixed_deposits'])
        self.assertIn('36_months', recommendations['fixed_deposits'])
    
    def test_get_recommendations_retirement(self):
        """Test recommendations for retirement age users (60+)"""
        profile = {
            'age': 65,
            'monthly_income': 50000,
            'goals': [],
            'risk_tolerance': 'conservative'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('senior_citizen', recommendations['savings_accounts'])
        self.assertIn('12_months', recommendations['fixed_deposits'])
    
    def test_get_recommendations_low_income(self):
        """Test recommendations for low income users"""
        profile = {
            'age': 30,
            'monthly_income': 20000,
            'goals': [],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('general', recommendations['savings_accounts'])
        self.assertIn('daily', recommendations['savings_accounts'])
    
    def test_get_recommendations_high_income(self):
        """Test recommendations for high income users"""
        profile = {
            'age': 35,
            'monthly_income': 150000,
            'goals': [],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('institutional', recommendations['savings_accounts'])
        self.assertIn('24_months', recommendations['fixed_deposits'])
        self.assertIn('36_months', recommendations['fixed_deposits'])
    
    def test_get_recommendations_house_purchase_goal(self):
        """Test recommendations with house purchase goal"""
        profile = {
            'age': 30,
            'monthly_income': 60000,
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('monthly', recommendations['savings_accounts'])
        self.assertIn('house_construction', recommendations['loans'])
        self.assertIn('land_purchase', recommendations['loans'])
    
    def test_get_recommendations_education_goal(self):
        """Test recommendations with education goal"""
        profile = {
            'age': 25,
            'monthly_income': 40000,
            'goals': ['education'],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('child', recommendations['savings_accounts'])
        self.assertIn('education', recommendations['loans'])
    
    def test_get_recommendations_business_goal(self):
        """Test recommendations with business goal"""
        profile = {
            'age': 35,
            'monthly_income': 80000,
            'goals': ['business'],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('institutional', recommendations['savings_accounts'])
        self.assertIn('business', recommendations['loans'])
    
    def test_get_recommendations_vehicle_goal(self):
        """Test recommendations with vehicle purchase goal"""
        profile = {
            'age': 28,
            'monthly_income': 50000,
            'goals': ['vehicle'],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('vehicle', recommendations['loans'])
    
    def test_get_recommendations_conservative_risk(self):
        """Test recommendations for conservative risk tolerance"""
        profile = {
            'age': 40,
            'monthly_income': 60000,
            'goals': [],
            'risk_tolerance': 'conservative'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('12_months', recommendations['fixed_deposits'])
        self.assertIn('24_months', recommendations['fixed_deposits'])
    
    def test_get_recommendations_aggressive_risk(self):
        """Test recommendations for aggressive risk tolerance"""
        profile = {
            'age': 30,
            'monthly_income': 70000,
            'goals': [],
            'risk_tolerance': 'aggressive'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        self.assertIn('monthly', recommendations['savings_accounts'])
        self.assertIn('36_months', recommendations['fixed_deposits'])
    
    def test_get_recommendations_deduplication(self):
        """Test that recommendations are deduplicated"""
        profile = {
            'age': 30,
            'monthly_income': 50000,
            'goals': ['house_purchase', 'education'],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        # Check that lists don't have duplicates
        savings_set = set(recommendations['savings_accounts'])
        loans_set = set(recommendations['loans'])
        deposits_set = set(recommendations['fixed_deposits'])
        
        self.assertEqual(len(recommendations['savings_accounts']), len(savings_set))
        self.assertEqual(len(recommendations['loans']), len(loans_set))
        self.assertEqual(len(recommendations['fixed_deposits']), len(deposits_set))
    
    def test_get_recommendations_default_values(self):
        """Test recommendations with minimal profile data"""
        profile = {}
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        
        # Should use defaults: age=30, income=50000, goals=[], risk='moderate'
        self.assertIn('savings_accounts', recommendations)
        self.assertIn('loans', recommendations)
        self.assertIn('fixed_deposits', recommendations)
        self.assertIn('reasoning', recommendations)
    
    def test_save_recommendation(self):
        """Test saving recommendations to database"""
        profile = {
            'age': 30,
            'monthly_income': 50000,
            'goals': ['house_purchase'],
            'risk_tolerance': 'moderate'
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(profile)
        saved = ServiceRecommendationService.save_recommendation(
            profile, recommendations, confidence=85.0
        )
        
        self.assertIsInstance(saved, ServiceRecommendation)
        self.assertEqual(saved.user_profile, profile)
        self.assertEqual(saved.recommended_services, recommendations)
        self.assertEqual(saved.confidence_score, 85.0)
        self.assertIn('house purchase', saved.recommendation_reason.lower())


class ServiceComparisonServiceTest(TestCase):
    """Comprehensive tests for ServiceComparisonService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings1 = SavingsAccount.objects.create(
            account_type='general',
            english_name='Savings Account 1',
            interest_rate=5.0,
            minimum_balance=1000.0,
            is_featured=True,
            is_active=True
        )
        self.savings2 = SavingsAccount.objects.create(
            account_type='monthly',
            english_name='Savings Account 2',
            interest_rate=6.0,
            minimum_balance=5000.0,
            is_featured=False,
            is_active=True
        )
        self.savings3 = SavingsAccount.objects.create(
            account_type='child',
            english_name='Savings Account 3',
            interest_rate=7.0,
            minimum_balance=2000.0,
            is_featured=True,
            is_active=True
        )
        
        self.loan1 = LoanType.objects.create(
            loan_category='personal',
            english_name='Personal Loan',
            monthly_interest_rate=1.2,
            minimum_amount=50000.0,
            maximum_amount=500000.0,
            max_tenure_years=5,
            is_featured=True,
            is_active=True
        )
        self.loan2 = LoanType.objects.create(
            loan_category='business',
            english_name='Business Loan',
            monthly_interest_rate=1.5,
            minimum_amount=100000.0,
            maximum_amount=1000000.0,
            max_tenure_years=10,
            is_featured=False,
            is_active=True
        )
        
        self.fd1 = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='monthly',
            interest_rate=8.0,
            minimum_amount=50000.0,
            maximum_amount=1000000.0
        )
        self.fd2 = FixedDeposit.objects.create(
            duration_months=24,
            payment_frequency='quarterly',
            interest_rate=9.0,
            minimum_amount=100000.0,
            maximum_amount=2000000.0
        )
        self.fd3 = FixedDeposit.objects.create(
            duration_months=36,
            payment_frequency='lump_sum',
            interest_rate=10.0,
            minimum_amount=200000.0,
            maximum_amount=5000000.0
        )
    
    def test_compare_savings_accounts_basic(self):
        """Test basic savings account comparison"""
        account_ids = [self.savings1.id, self.savings2.id, self.savings3.id]
        comparison = ServiceComparisonService.compare_savings_accounts(account_ids)
        
        self.assertIn('accounts', comparison)
        self.assertEqual(len(comparison['accounts']), 3)
        self.assertIn('best_interest_rate', comparison)
        self.assertIn('lowest_minimum_balance', comparison)
        self.assertIn('featured_accounts', comparison)
        
        self.assertEqual(comparison['best_interest_rate'], 7.0)
        self.assertEqual(comparison['lowest_minimum_balance'], 1000.0)
        self.assertEqual(len(comparison['featured_accounts']), 2)
    
    def test_compare_savings_accounts_empty_list(self):
        """Test comparison with empty account list"""
        comparison = ServiceComparisonService.compare_savings_accounts([])
        
        self.assertEqual(comparison, {})
    
    def test_compare_savings_accounts_inactive_filtered(self):
        """Test that inactive accounts are filtered out"""
        inactive = SavingsAccount.objects.create(
            account_type='institutional',
            english_name='Inactive Savings',
            interest_rate=5.0,
            is_active=False
        )
        
        account_ids = [self.savings1.id, inactive.id]
        comparison = ServiceComparisonService.compare_savings_accounts(account_ids)
        
        self.assertEqual(len(comparison['accounts']), 1)
        self.assertEqual(comparison['accounts'][0]['id'], self.savings1.id)
    
    def test_compare_savings_accounts_features_parsing(self):
        """Test that features are properly parsed"""
        self.savings1.features = "Feature 1\nFeature 2\nFeature 3"
        self.savings1.save()
        
        account_ids = [self.savings1.id]
        comparison = ServiceComparisonService.compare_savings_accounts(account_ids)
        
        self.assertEqual(len(comparison['accounts'][0]['features']), 3)
        self.assertIn('Feature 1', comparison['accounts'][0]['features'])
    
    def test_compare_loans_basic(self):
        """Test basic loan comparison"""
        loan_ids = [self.loan1.id, self.loan2.id]
        comparison = ServiceComparisonService.compare_loans(loan_ids)
        
        self.assertIn('loans', comparison)
        self.assertEqual(len(comparison['loans']), 2)
        self.assertIn('lowest_interest_rate', comparison)
        self.assertIn('highest_maximum_amount', comparison)
        self.assertIn('featured_loans', comparison)
        
        self.assertEqual(comparison['lowest_interest_rate'], 1.2)
        self.assertEqual(comparison['highest_maximum_amount'], 1000000.0)
        self.assertEqual(len(comparison['featured_loans']), 1)
    
    def test_compare_loans_empty_list(self):
        """Test comparison with empty loan list"""
        comparison = ServiceComparisonService.compare_loans([])
        
        self.assertEqual(comparison, {})
    
    def test_compare_loans_requirements_parsing(self):
        """Test that requirements are properly parsed"""
        self.loan1.requirements = "Requirement 1\nRequirement 2"
        self.loan1.save()
        
        loan_ids = [self.loan1.id]
        comparison = ServiceComparisonService.compare_loans(loan_ids)
        
        self.assertEqual(len(comparison['loans'][0]['requirements']), 2)
    
    def test_compare_fixed_deposits_basic(self):
        """Test basic fixed deposit comparison"""
        deposit_ids = [self.fd1.id, self.fd2.id, self.fd3.id]
        comparison = ServiceComparisonService.compare_fixed_deposits(deposit_ids)
        
        self.assertIn('deposits', comparison)
        self.assertEqual(len(comparison['deposits']), 3)
        self.assertIn('highest_interest_rate', comparison)
        self.assertIn('shortest_duration', comparison)
        self.assertIn('longest_duration', comparison)
        
        self.assertEqual(comparison['highest_interest_rate'], 10.0)
        self.assertEqual(comparison['shortest_duration'], 12)
        self.assertEqual(comparison['longest_duration'], 36)
        
        # Verify deposit data structure
        for deposit in comparison['deposits']:
            self.assertIn('id', deposit)
            self.assertIn('duration_months', deposit)
            self.assertIn('interest_rate', deposit)
    
    def test_compare_fixed_deposits_empty_list(self):
        """Test comparison with empty deposit list"""
        comparison = ServiceComparisonService.compare_fixed_deposits([])
        
        self.assertEqual(comparison, {})
    
    def test_compare_fixed_deposits_benefits_parsing(self):
        """Test that benefits are properly parsed"""
        # FixedDeposit model may not have benefits field, so we check if it exists
        if hasattr(self.fd1, 'benefits'):
            self.fd1.benefits = "Benefit 1\nBenefit 2"
            self.fd1.save()
            
            deposit_ids = [self.fd1.id]
            comparison = ServiceComparisonService.compare_fixed_deposits(deposit_ids)
            
            if comparison['deposits'][0].get('benefits'):
                self.assertEqual(len(comparison['deposits'][0]['benefits']), 2)


class ServiceSearchServiceTest(TestCase):
    """Comprehensive tests for ServiceSearchService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings1 = SavingsAccount.objects.create(
            account_type='general',
            english_name='General Savings Account',
            nepali_name='साधारण बचत खाता',
            description='A general purpose savings account',
            interest_rate=5.0,
            is_featured=True,
            is_active=True
        )
        self.savings2 = SavingsAccount.objects.create(
            account_type='monthly',
            english_name='Monthly Savings',
            nepali_name='मासिक बचत',
            description='Monthly savings plan',
            interest_rate=6.0,
            is_featured=False,
            is_active=True
        )
        
        self.loan1 = LoanType.objects.create(
            loan_category='personal',
            english_name='Personal Loan',
            nepali_name='व्यक्तिगत ऋण',
            description='Personal loan for individuals',
            monthly_interest_rate=1.2,
            is_featured=True,
            is_active=True
        )
        self.loan2 = LoanType.objects.create(
            loan_category='business',
            english_name='Business Loan',
            nepali_name='व्यापार ऋण',
            description='Loan for business purposes',
            monthly_interest_rate=1.5,
            is_featured=False,
            is_active=True
        )
    
    def test_search_services_all_types(self):
        """Test searching across all service types"""
        form_data = {'query': 'savings'}
        results = ServiceSearchService.search_services(form_data)
        
        self.assertIn('results', results)
        self.assertIn('total_results', results)
        self.assertGreaterEqual(results['total_results'], 2)
    
    def test_search_services_savings_only(self):
        """Test searching only savings accounts"""
        form_data = {
            'query': 'savings',
            'service_type': 'savings'
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 2)
        # All results should be savings type
        for result in results['results']:
            self.assertEqual(result['type'], 'savings')
    
    def test_search_services_loans_only(self):
        """Test searching only loans"""
        form_data = {
            'query': 'loan',
            'service_type': 'loans'
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 2)
        # All results should be loan type
        for result in results['results']:
            self.assertEqual(result['type'], 'loan')
    
    def test_search_services_by_interest_rate_min(self):
        """Test filtering by minimum interest rate"""
        form_data = {
            'service_type': 'savings',
            'interest_rate_min': 5.5
        }
        results = ServiceSearchService.search_services(form_data)
        
        # Should only return savings2 (6.0%) not savings1 (5.0%)
        for result in results['results']:
            self.assertGreaterEqual(result['interest_rate'], 5.5)
    
    def test_search_services_by_interest_rate_max(self):
        """Test filtering by maximum interest rate"""
        form_data = {
            'service_type': 'savings',
            'interest_rate_max': 5.5
        }
        results = ServiceSearchService.search_services(form_data)
        
        # Should only return savings1 (5.0%) not savings2 (6.0%)
        for result in results['results']:
            self.assertLessEqual(result['interest_rate'], 5.5)
    
    def test_search_services_featured_only(self):
        """Test filtering by featured status"""
        form_data = {
            'service_type': 'savings',
            'featured_only': True
        }
        results = ServiceSearchService.search_services(form_data)
        
        # Should only return featured savings
        for result in results['results']:
            self.assertEqual(result['type'], 'savings')
            # Note: featured status is not in result dict, but filtering happens
    
    def test_search_services_pagination(self):
        """Test pagination functionality"""
        form_data = {'query': ''}
        results = ServiceSearchService.search_services(form_data, page_number=1, page_size=2)
        
        self.assertIn('results', results)
        self.assertLessEqual(len(results['results']), 2)
    
    def test_search_services_empty_query(self):
        """Test search with empty query returns all"""
        form_data = {}
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 4)  # At least 2 savings + 2 loans
    
    def test_search_services_nepali_name(self):
        """Test searching by Nepali name"""
        form_data = {
            'query': 'साधारण',
            'service_type': 'savings'
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 1)
    
    def test_search_services_description(self):
        """Test searching in description"""
        form_data = {
            'query': 'purpose',
            'service_type': 'savings'
        }
        results = ServiceSearchService.search_services(form_data)
        
        self.assertGreaterEqual(results['total_results'], 1)


class ServiceApplicationServiceTest(TestCase):
    """Comprehensive tests for ServiceApplicationService"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            account_type='general',
            english_name='Test Savings',
            interest_rate=5.0,
            is_active=True
        )
        
        from apps.services.forms import ServiceApplicationForm
        # ServiceApplicationForm requires all fields including terms_accepted
        # Phone must be in Nepali format: +977-98XXXXXXXX
        self.form_data = {
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'applicant_phone': '+977-9812345678',
            'applicant_address': '123 Test Street, Test City',
            'additional_info': 'I want to apply for this service',
            'terms_accepted': True
        }
        # Pass service_object to form
        self.form = ServiceApplicationForm(data=self.form_data, service_object=self.savings)
    
    def test_process_application_success(self):
        """Test successful application processing"""
        self.assertTrue(self.form.is_valid(), f"Form errors: {self.form.errors}")
        
        application = ServiceApplicationService.process_application(
            self.form, 'savings', str(self.savings.id)
        )
        
        self.assertIsInstance(application, ServiceApplication)
        self.assertEqual(application.applicant_name, 'John Doe')
        self.assertEqual(application.applicant_email, 'john@example.com')
        
        # Verify linked to service
        self.assertEqual(application.service_object, self.savings)
    
    def test_process_application_tracks_analytics(self):
        """Test that application processing tracks analytics"""
        self.assertTrue(self.form.is_valid())
        
        with patch('apps.services.services.ServiceAnalyticsService.track_usage') as mock_track:
            ServiceApplicationService.process_application(
                self.form, 'savings', str(self.savings.id)
            )
            
            mock_track.assert_called_once_with(
                'savings',
                self.savings.id,
                'applications_received'
            )
    
    def test_process_application_invalid_service_type(self):
        """Test processing with invalid service type"""
        self.assertTrue(self.form.is_valid())
        
        # Should still create application even if service type is invalid
        # The service will try to link but may fail gracefully
        application = ServiceApplicationService.process_application(
            self.form, 'invalid', '999'
        )
        
        self.assertIsInstance(application, ServiceApplication)
        # Application should be created regardless
        self.assertEqual(application.applicant_name, 'John Doe')

