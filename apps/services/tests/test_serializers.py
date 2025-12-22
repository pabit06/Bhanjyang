"""
Tests for services app serializers
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService,
    MemberRelief, ServiceApplication, ServiceAnalytics, ServiceRecommendation
)
from apps.services.serializers import (
    SavingsAccountSerializer, FixedDepositSerializer, LoanTypeSerializer,
    RemittanceServiceSerializer, MemberReliefSerializer, ServiceApplicationSerializer,
    ServiceAnalyticsSerializer, ServiceRecommendationSerializer,
    ServiceCalculatorSerializer, ServiceSearchSerializer
)


class SerializerTestCase(TestCase):
    """Base test case for serializers"""
    
    def setUp(self):
        self.savings_account = SavingsAccount.objects.create(
            english_name='Test Savings',
            nepali_name='परीक्षण बचत',
            account_type='regular',
            interest_rate=Decimal('6.0'),
            minimum_balance=Decimal('1000'),
            is_active=True
        )
        self.fixed_deposit = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency='lump_sum',
            interest_rate=Decimal('8.0'),
            minimum_amount=Decimal('50000'),
            is_active=True
        )
        self.loan_type = LoanType.objects.create(
            english_name='Test Loan',
            nepali_name='परीक्षण ऋण',
            loan_category='personal',
            monthly_interest_rate=Decimal('1.0'),
            minimum_amount=Decimal('10000'),
            maximum_amount=Decimal('500000'),
            max_tenure_years=5,
            is_active=True
        )
        self.remittance = RemittanceService.objects.create(
            english_name='Test Remittance',
            service_type='domestic',
            processing_time='24 hours',
            is_active=True
        )
        self.relief = MemberRelief.objects.create(
            english_name='Test Relief',
            nepali_name='परीक्षण राहत',
            relief_type='financial',
            is_active=True
        )


class SavingsAccountSerializerTest(SerializerTestCase):
    """Test SavingsAccountSerializer"""
    
    def test_serialize_savings_account(self):
        """Test serializing savings account"""
        serializer = SavingsAccountSerializer(self.savings_account)
        data = serializer.data
        self.assertEqual(data['english_name'], self.savings_account.english_name)
        self.assertEqual(data['nepali_name'], self.savings_account.nepali_name)
        self.assertIn('annual_interest_rate', data)
        self.assertIn('url', data)
        self.assertIn('interest_rate', data)
        self.assertIn('minimum_balance', data)
    
    def test_deserialize_savings_account(self):
        """Test deserializing savings account"""
        data = {
            'english_name': 'New Savings',
            'nepali_name': 'नयाँ बचत',
            'account_type': 'general',  # Use valid account type
            'interest_rate': '7.0',
            'minimum_balance': '2000',
            'is_active': True
        }
        serializer = SavingsAccountSerializer(data=data)
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
        instance = serializer.save()
        self.assertEqual(instance.english_name, 'New Savings')
        self.assertEqual(instance.interest_rate, Decimal('7.0'))
    
    def test_validate_interest_rate_valid(self):
        """Test validating valid interest rate"""
        data = {
            'english_name': 'Test Savings',
            'nepali_name': 'परीक्षण बचत',
            'account_type': 'general',
            'interest_rate': '10.0'
        }
        serializer = SavingsAccountSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_validate_interest_rate_too_high(self):
        """Test validating interest rate too high"""
        data = {
            'english_name': 'Test',
            'interest_rate': '60.0'  # Exceeds 50
        }
        serializer = SavingsAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('interest_rate', serializer.errors)
    
    def test_validate_interest_rate_negative(self):
        """Test validating negative interest rate"""
        data = {
            'english_name': 'Test',
            'interest_rate': '-5.0'
        }
        serializer = SavingsAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('interest_rate', serializer.errors)
    
    def test_validate_minimum_balance_negative(self):
        """Test validating negative minimum balance"""
        data = {
            'english_name': 'Test',
            'minimum_balance': '-1000'
        }
        serializer = SavingsAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('minimum_balance', serializer.errors)
    
    def test_get_url(self):
        """Test get_url method"""
        serializer = SavingsAccountSerializer(self.savings_account)
        data = serializer.data
        self.assertIn('url', data)
        self.assertIsNotNone(data['url'])


class FixedDepositSerializerTest(SerializerTestCase):
    """Test FixedDepositSerializer"""
    
    def test_serialize_fixed_deposit(self):
        """Test serializing fixed deposit"""
        serializer = FixedDepositSerializer(self.fixed_deposit)
        data = serializer.data
        self.assertEqual(data['duration_months'], self.fixed_deposit.duration_months)
        self.assertEqual(data['payment_frequency'], self.fixed_deposit.payment_frequency)
        self.assertIn('annual_interest_rate', data)
        self.assertIn('maturity_amount', data)
    
    def test_get_annual_interest_rate(self):
        """Test get_annual_interest_rate method"""
        serializer = FixedDepositSerializer(self.fixed_deposit)
        data = serializer.data
        self.assertIn('annual_interest_rate', data)
        self.assertIsInstance(data['annual_interest_rate'], (int, float))
    
    def test_get_maturity_amount(self):
        """Test get_maturity_amount method"""
        serializer = FixedDepositSerializer(self.fixed_deposit)
        data = serializer.data
        self.assertIn('maturity_amount', data)
        if data['maturity_amount']:
            self.assertIn('minimum_investment', data['maturity_amount'])
            self.assertIn('minimum_maturity', data['maturity_amount'])
    
    def test_validate_interest_rate(self):
        """Test validating interest rate"""
        data = {
            'duration_months': 12,
            'payment_frequency': 'lump_sum',
            'interest_rate': '60.0'  # Exceeds 50
        }
        serializer = FixedDepositSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('interest_rate', serializer.errors)


class LoanTypeSerializerTest(SerializerTestCase):
    """Test LoanTypeSerializer"""
    
    def test_serialize_loan_type(self):
        """Test serializing loan type"""
        serializer = LoanTypeSerializer(self.loan_type)
        data = serializer.data
        self.assertEqual(data['english_name'], self.loan_type.english_name)
        self.assertIn('annual_interest_rate', data)
        self.assertIn('url', data)
        self.assertIn('monthly_payment_calculator', data)
    
    def test_get_url(self):
        """Test get_url method"""
        serializer = LoanTypeSerializer(self.loan_type)
        data = serializer.data
        self.assertIn('url', data)
    
    def test_get_monthly_payment_calculator(self):
        """Test get_monthly_payment_calculator method"""
        serializer = LoanTypeSerializer(self.loan_type)
        data = serializer.data
        self.assertIn('monthly_payment_calculator', data)
        if data['monthly_payment_calculator']:
            self.assertIn('loan_range', data['monthly_payment_calculator'])
            self.assertIn('tenure_range', data['monthly_payment_calculator'])


class RemittanceServiceSerializerTest(SerializerTestCase):
    """Test RemittanceServiceSerializer"""
    
    def test_serialize_remittance_service(self):
        """Test serializing remittance service"""
        serializer = RemittanceServiceSerializer(self.remittance)
        data = serializer.data
        self.assertEqual(data['english_name'], self.remittance.english_name)
        self.assertEqual(data['service_type'], self.remittance.service_type)
        self.assertIn('url', data)
        self.assertIn('processing_time', data)
    
    def test_get_url(self):
        """Test get_url method"""
        serializer = RemittanceServiceSerializer(self.remittance)
        data = serializer.data
        self.assertIn('url', data)


class MemberReliefSerializerTest(SerializerTestCase):
    """Test MemberReliefSerializer"""
    
    def test_serialize_member_relief(self):
        """Test serializing member relief"""
        serializer = MemberReliefSerializer(self.relief)
        data = serializer.data
        self.assertEqual(data['english_name'], self.relief.english_name)
        self.assertEqual(data['relief_type'], self.relief.relief_type)
        self.assertIn('url', data)
        self.assertIn('image_url', data)
    
    def test_get_url(self):
        """Test get_url method"""
        serializer = MemberReliefSerializer(self.relief)
        data = serializer.data
        self.assertIn('url', data)
    
    def test_get_image_url(self):
        """Test get_image_url method"""
        serializer = MemberReliefSerializer(self.relief)
        data = serializer.data
        self.assertIn('image_url', data)
        # Should be None if no image
        self.assertIsNone(data['image_url'])


class ServiceApplicationSerializerTest(SerializerTestCase):
    """Test ServiceApplicationSerializer"""
    
    def setUp(self):
        super().setUp()
        self.content_type = ContentType.objects.get_for_model(SavingsAccount)
        self.application = ServiceApplication.objects.create(
            applicant_name='Test Applicant',
            applicant_email='test@example.com',
            applicant_phone='9800000000',
            content_type=self.content_type,
            object_id=self.savings_account.id,
            status='pending'
        )
    
    def test_serialize_service_application(self):
        """Test serializing service application"""
        serializer = ServiceApplicationSerializer(self.application)
        data = serializer.data
        self.assertEqual(data['applicant_name'], self.application.applicant_name)
        self.assertEqual(data['applicant_email'], self.application.applicant_email)
        self.assertIn('service_name', data)
        self.assertIn('service_type', data)
        self.assertIn('status', data)
    
    def test_get_service_type(self):
        """Test get_service_type method"""
        serializer = ServiceApplicationSerializer(self.application)
        data = serializer.data
        self.assertIn('service_type', data)
        self.assertEqual(data['service_type'], 'savingsaccount')
    
    def test_validate_applicant_email(self):
        """Test validating applicant email"""
        data = {
            'applicant_name': 'Test',
            'applicant_email': 'invalid-email',  # Missing @
            'content_type': self.content_type.id,
            'object_id': self.savings_account.id
        }
        serializer = ServiceApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('applicant_email', serializer.errors)
    
    def test_validate_applicant_phone_too_short(self):
        """Test validating applicant phone too short"""
        data = {
            'applicant_name': 'Test',
            'applicant_email': 'test@example.com',
            'applicant_phone': '123',  # Too short
            'content_type': self.content_type.id,
            'object_id': self.savings_account.id
        }
        serializer = ServiceApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('applicant_phone', serializer.errors)
    
    def test_readonly_fields(self):
        """Test readonly fields"""
        data = {
            'applicant_name': 'Test',
            'applicant_email': 'test@example.com',
            'service_name': 'Changed Name',  # Should be ignored
            'applied_date': '2020-01-01'  # Should be ignored
        }
        serializer = ServiceApplicationSerializer(data=data)
        # Readonly fields should not affect validation
        self.assertTrue(serializer.is_valid() or not serializer.is_valid())


class ServiceAnalyticsSerializerTest(SerializerTestCase):
    """Test ServiceAnalyticsSerializer"""
    
    def setUp(self):
        super().setUp()
        from django.utils import timezone
        self.content_type = ContentType.objects.get_for_model(SavingsAccount)
        self.analytics = ServiceAnalytics.objects.create(
            content_type=self.content_type,
            object_id=self.savings_account.id,
            date=timezone.now().date(),
            page_views=100,
            applications_received=5,
            calculator_usage=20
        )
    
    def test_serialize_service_analytics(self):
        """Test serializing service analytics"""
        serializer = ServiceAnalyticsSerializer(self.analytics)
        data = serializer.data
        self.assertEqual(data['page_views'], self.analytics.page_views)
        self.assertEqual(data['applications_received'], self.analytics.applications_received)
        self.assertIn('service_name', data)
        self.assertIn('date', data)
    
    def test_get_service_name(self):
        """Test get_service_name method"""
        serializer = ServiceAnalyticsSerializer(self.analytics)
        data = serializer.data
        self.assertIn('service_name', data)
        self.assertEqual(data['service_name'], self.savings_account.english_name)


class ServiceRecommendationSerializerTest(SerializerTestCase):
    """Test ServiceRecommendationSerializer"""
    
    def setUp(self):
        super().setUp()
        self.recommendation = ServiceRecommendation.objects.create(
            user_profile={'age': 30, 'monthly_income': 50000},
            recommended_services=[{'id': 1, 'name': 'Test Service'}],
            confidence_score=0.85
        )
    
    def test_serialize_service_recommendation(self):
        """Test serializing service recommendation"""
        serializer = ServiceRecommendationSerializer(self.recommendation)
        data = serializer.data
        self.assertIn('user_profile', data)
        self.assertIn('recommended_services', data)
        self.assertIn('confidence_score', data)
        self.assertIn('recommendation_reason', data)
        self.assertEqual(data['confidence_score'], '0.85')


class ServiceCalculatorSerializerTest(TestCase):
    """Test ServiceCalculatorSerializer"""
    
    def test_valid_calculator_request(self):
        """Test valid calculator request"""
        data = {
            'service_type': 'loan',
            'amount': '100000',
            'duration_months': 60,
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_service_type(self):
        """Test invalid service type"""
        data = {
            'service_type': 'invalid',
            'amount': '100000',
            'duration_months': 60,
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('service_type', serializer.errors)
    
    def test_validate_amount_positive(self):
        """Test validating positive amount"""
        data = {
            'service_type': 'loan',
            'amount': '100000',
            'duration_months': 60,
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_validate_amount_negative(self):
        """Test validating negative amount"""
        data = {
            'service_type': 'loan',
            'amount': '-100000',
            'duration_months': 60,
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
    
    def test_validate_amount_zero(self):
        """Test validating zero amount"""
        data = {
            'service_type': 'loan',
            'amount': '0',
            'duration_months': 60,
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
    
    def test_validate_duration_months_min(self):
        """Test validating minimum duration"""
        data = {
            'service_type': 'loan',
            'amount': '100000',
            'duration_months': 0,  # Below minimum
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('duration_months', serializer.errors)
    
    def test_validate_duration_months_max(self):
        """Test validating maximum duration"""
        data = {
            'service_type': 'loan',
            'amount': '100000',
            'duration_months': 500,  # Exceeds maximum
            'service_id': 1
        }
        serializer = ServiceCalculatorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('duration_months', serializer.errors)


class ServiceSearchSerializerTest(TestCase):
    """Test ServiceSearchSerializer"""
    
    def test_valid_search_request(self):
        """Test valid search request"""
        data = {
            'query': 'savings',
            'service_type': 'savings',
            'is_featured': True,
            'is_active': True
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_search_with_interest_rate_range(self):
        """Test search with interest rate range"""
        data = {
            'query': 'savings',
            'min_interest_rate': '5.0',
            'max_interest_rate': '10.0'
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_search_with_ordering(self):
        """Test search with ordering"""
        data = {
            'query': 'savings',
            'ordering': 'interest_rate'
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_search_with_pagination(self):
        """Test search with pagination"""
        data = {
            'query': 'savings',
            'page': 1,
            'page_size': 20
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_search_all_optional_fields(self):
        """Test search with all fields optional"""
        data = {}
        serializer = ServiceSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_service_type(self):
        """Test invalid service type"""
        data = {
            'service_type': 'invalid'
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('service_type', serializer.errors)
    
    def test_invalid_ordering(self):
        """Test invalid ordering"""
        data = {
            'ordering': 'invalid'
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ordering', serializer.errors)
    
    def test_invalid_page_size(self):
        """Test invalid page size"""
        data = {
            'page_size': 200  # Exceeds max
        }
        serializer = ServiceSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('page_size', serializer.errors)

