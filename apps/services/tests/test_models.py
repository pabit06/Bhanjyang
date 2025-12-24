"""
Comprehensive tests for services app models
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from apps.services.models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService,
    MemberRelief, ServiceApplication, ServiceAnalytics, ServiceRecommendation
)


class SavingsAccountModelTest(TestCase):
    """Test suite for SavingsAccount model"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name="General Savings",
            nepali_name="सामान्य बचत",
            account_type="general",
            interest_rate=Decimal("4.50"),
            minimum_balance=Decimal("1000.00")
        )
    
    def test_savings_creation(self):
        """Test basic savings account creation"""
        self.assertEqual(self.savings.english_name, "General Savings")
        self.assertEqual(self.savings.account_type, "general")
        self.assertEqual(self.savings.interest_rate, Decimal("4.50"))
        self.assertTrue(self.savings.is_active)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from english_name"""
        self.assertIsNotNone(self.savings.slug)
        self.assertEqual(self.savings.slug, "general-savings")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.savings), "General Savings (4.50%)")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.savings.get_absolute_url()
        self.assertIn(self.savings.slug, url)
        self.assertIn('savings', url)
    
    def test_account_type_choices(self):
        """Test account type choices"""
        types = ['general', 'daily', 'institutional', 'child', 
                 'senior_citizen', 'remit', 'insurance', 'monthly']
        for acc_type in types:
            savings = SavingsAccount.objects.create(
                english_name=f"Test {acc_type}",
                nepali_name="Test",
                account_type=acc_type,
                interest_rate=Decimal("4.00")
            )
            self.assertEqual(savings.account_type, acc_type)
    
    def test_unique_account_type(self):
        """Test that account_type must be unique"""
        with self.assertRaises(Exception):  # IntegrityError
            SavingsAccount.objects.create(
                english_name="Another General",
                nepali_name="Test",
                account_type="general",
                interest_rate=Decimal("5.00")
            )
    
    def test_ordering(self):
        """Test model ordering"""
        featured = SavingsAccount.objects.create(
            english_name="Featured Savings",
            nepali_name="Test",
            account_type="daily",
            interest_rate=Decimal("5.00"),
            is_featured=True
        )
        savings_list = list(SavingsAccount.objects.all())
        # Should be ordered by -is_featured, -interest_rate
        self.assertEqual(savings_list[0], featured)
    
    def test_default_color(self):
        """Test default color theme"""
        self.assertEqual(self.savings.color, "deuraligreen")


class FixedDepositModelTest(TestCase):
    """Test suite for FixedDeposit model"""
    
    def setUp(self):
        """Set up test data"""
        self.fd = FixedDeposit.objects.create(
            duration_months=12,
            payment_frequency="monthly",
            interest_rate=Decimal("8.50"),
            minimum_amount=Decimal("10000.00")
        )
    
    def test_fd_creation(self):
        """Test basic fixed deposit creation"""
        self.assertEqual(self.fd.duration_months, 12)
        self.assertEqual(self.fd.payment_frequency, "monthly")
        self.assertEqual(self.fd.interest_rate, Decimal("8.50"))
        self.assertTrue(self.fd.is_active)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn("1 Year", str(self.fd))
        self.assertIn("Monthly Payout", str(self.fd))
        self.assertIn("8.50%", str(self.fd))
    
    def test_duration_choices(self):
        """Test duration choices"""
        durations = [3, 6, 12, 24, 36]
        for duration in durations:
            fd = FixedDeposit.objects.create(
                duration_months=duration,
                payment_frequency="lump_sum",
                interest_rate=Decimal("8.00"),
                minimum_amount=Decimal("10000.00")
            )
            self.assertEqual(fd.duration_months, duration)
    
    def test_payment_frequency_choices(self):
        """Test payment frequency choices"""
        frequencies = ['monthly', 'quarterly', 'lump_sum']
        for freq in frequencies:
            fd = FixedDeposit.objects.create(
                duration_months=12,
                payment_frequency=freq,
                interest_rate=Decimal("8.00"),
                minimum_amount=Decimal("10000.00")
            )
            self.assertEqual(fd.payment_frequency, freq)
    
    def test_unique_together(self):
        """Test unique_together constraint"""
        # Same duration and payment_frequency should fail
        with self.assertRaises(Exception):  # IntegrityError
            FixedDeposit.objects.create(
                duration_months=12,
                payment_frequency="monthly",
                interest_rate=Decimal("9.00"),
                minimum_amount=Decimal("10000.00")
            )
    
    def test_ordering(self):
        """Test model ordering"""
        fd2 = FixedDeposit.objects.create(
            duration_months=6,
            payment_frequency="quarterly",
            interest_rate=Decimal("7.50"),
            minimum_amount=Decimal("10000.00")
        )
        fd_list = list(FixedDeposit.objects.all())
        # Should be ordered by duration_months, interest_rate
        self.assertEqual(fd_list[0], fd2)  # 6 < 12
        self.assertEqual(fd_list[1], self.fd)


class LoanTypeModelTest(TestCase):
    """Test suite for LoanType model"""
    
    def setUp(self):
        """Set up test data"""
        self.loan = LoanType.objects.create(
            english_name="Business Loan",
            nepali_name="व्यापार ऋण",
            loan_category="business",
            monthly_interest_rate=Decimal("1.25"),
            minimum_amount=Decimal("50000.00"),
            maximum_amount=Decimal("5000000.00")
        )
    
    def test_loan_creation(self):
        """Test basic loan creation"""
        self.assertEqual(self.loan.english_name, "Business Loan")
        self.assertEqual(self.loan.loan_category, "business")
        self.assertEqual(self.loan.monthly_interest_rate, Decimal("1.25"))
        self.assertTrue(self.loan.is_active)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated"""
        self.assertIsNotNone(self.loan.slug)
        self.assertEqual(self.loan.slug, "business-loan")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.loan), "Business Loan")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.loan.get_absolute_url()
        self.assertIn(self.loan.slug, url)
        self.assertIn('loan', url)
    
    def test_annual_interest_rate_property(self):
        """Test annual_interest_rate property"""
        annual_rate = self.loan.annual_interest_rate
        expected = Decimal("1.25") * 12
        self.assertEqual(annual_rate, expected)
    
    def test_loan_category_choices(self):
        """Test loan category choices"""
        categories = ['business', 'agricultural', 'vehicle', 'foreign_employment',
                     'household', 'house_construction', 'land_purchase', 'education', 'personal']
        for category in categories:
            loan = LoanType.objects.create(
                english_name=f"Test {category}",
                nepali_name="Test",
                loan_category=category,
                monthly_interest_rate=Decimal("1.00")
            )
            self.assertEqual(loan.loan_category, category)
    
    def test_unique_loan_category(self):
        """Test that loan_category must be unique"""
        with self.assertRaises(Exception):  # IntegrityError
            LoanType.objects.create(
                english_name="Another Business Loan",
                nepali_name="Test",
                loan_category="business",
                monthly_interest_rate=Decimal("1.50")
            )


class RemittanceServiceModelTest(TestCase):
    """Test suite for RemittanceService model"""
    
    def setUp(self):
        """Set up test data"""
        self.remittance = RemittanceService.objects.create(
            english_name="Domestic Transfer",
            nepali_name="घरेलु स्थानान्तरण",
            service_type="domestic",
            processing_time="Instant"
        )
    
    def test_remittance_creation(self):
        """Test basic remittance service creation"""
        self.assertEqual(self.remittance.english_name, "Domestic Transfer")
        self.assertEqual(self.remittance.service_type, "domestic")
        self.assertTrue(self.remittance.is_active)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated"""
        self.assertIsNotNone(self.remittance.slug)
        self.assertEqual(self.remittance.slug, "domestic-transfer")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.remittance), "Domestic Transfer")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.remittance.get_absolute_url()
        self.assertIn(self.remittance.slug, url)
        self.assertIn('remittance', url)
    
    def test_service_type_choices(self):
        """Test service type choices"""
        types = ['domestic', 'international', 'mobile_banking']
        for svc_type in types:
            remittance = RemittanceService.objects.create(
                english_name=f"Test {svc_type}",
                nepali_name="Test",
                service_type=svc_type
            )
            self.assertEqual(remittance.service_type, svc_type)


class MemberReliefModelTest(TestCase):
    """Test suite for MemberRelief model"""
    
    def setUp(self):
        """Set up test data"""
        self.relief = MemberRelief.objects.create(
            english_name="Medical Relief",
            nepali_name="चिकित्सा राहत",
            relief_type="medical",
            eligibility="Members with medical emergencies",
            benefits="Financial support for medical expenses"
        )
    
    def test_relief_creation(self):
        """Test basic member relief creation"""
        self.assertEqual(self.relief.english_name, "Medical Relief")
        self.assertEqual(self.relief.relief_type, "medical")
        self.assertTrue(self.relief.is_active)
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated"""
        self.assertIsNotNone(self.relief.slug)
        self.assertEqual(self.relief.slug, "medical-relief")
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.relief), "Medical Relief")
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.relief.get_absolute_url()
        self.assertIn(self.relief.slug, url)
        self.assertIn('relief', url)
    
    def test_relief_type_choices(self):
        """Test relief type choices"""
        types = ['medical', 'education', 'disaster', 'welfare']
        for rel_type in types:
            relief = MemberRelief.objects.create(
                english_name=f"Test {rel_type}",
                nepali_name="Test",
                relief_type=rel_type,
                eligibility="Test",
                benefits="Test"
            )
            self.assertEqual(relief.relief_type, rel_type)


class ServiceApplicationModelTest(TestCase):
    """Test suite for ServiceApplication model"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name="Test Savings",
            nepali_name="Test",
            account_type="general",
            interest_rate=Decimal("4.00")
        )
        self.content_type = ContentType.objects.get_for_model(SavingsAccount)
        
        self.application = ServiceApplication.objects.create(
            content_type=self.content_type,
            object_id=self.savings.id,
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="1234567890",
            applicant_address="Test Address",
            status="pending"
        )
    
    def test_application_creation(self):
        """Test basic application creation"""
        self.assertEqual(self.application.applicant_name, "John Doe")
        self.assertEqual(self.application.status, "pending")
        self.assertIsNotNone(self.application.applied_date)
    
    def test_str_representation(self):
        """Test string representation"""
        expected = f"Application from John Doe for {self.savings.english_name}"
        self.assertEqual(str(self.application), expected)
    
    def test_service_name_property(self):
        """Test service_name property"""
        self.assertEqual(self.application.service_name, "Test Savings")
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = ['pending', 'under_review', 'approved', 'rejected']
        for status in statuses:
            app = ServiceApplication.objects.create(
                content_type=self.content_type,
                object_id=self.savings.id,
                applicant_name=f"Test {status}",
                applicant_email=f"test{status}@example.com",
                applicant_phone="1234567890",
                applicant_address="Test",
                status=status
            )
            self.assertEqual(app.status, status)
    
    def test_ordering(self):
        """Test model ordering"""
        app2 = ServiceApplication.objects.create(
            content_type=self.content_type,
            object_id=self.savings.id,
            applicant_name="Second Applicant",
            applicant_email="second@example.com",
            applicant_phone="1234567890",
            applicant_address="Test"
        )
        apps = list(ServiceApplication.objects.all())
        # Should be ordered by -applied_date (newest first)
        self.assertEqual(apps[0], app2)
        self.assertEqual(apps[1], self.application)


class ServiceAnalyticsModelTest(TestCase):
    """Test suite for ServiceAnalytics model"""
    
    def setUp(self):
        """Set up test data"""
        self.savings = SavingsAccount.objects.create(
            english_name="Test Savings",
            nepali_name="Test",
            account_type="general",
            interest_rate=Decimal("4.00")
        )
        self.content_type = ContentType.objects.get_for_model(SavingsAccount)
        
        from datetime import date
        self.analytics = ServiceAnalytics.objects.create(
            content_type=self.content_type,
            object_id=self.savings.id,
            date=date.today(),
            page_views=100,
            applications_received=5,
            calculator_usage=20
        )
    
    def test_analytics_creation(self):
        """Test basic analytics creation"""
        self.assertEqual(self.analytics.page_views, 100)
        self.assertEqual(self.analytics.applications_received, 5)
        self.assertEqual(self.analytics.calculator_usage, 20)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn("Test Savings", str(self.analytics))
        self.assertIn(str(self.analytics.date), str(self.analytics))
    
    def test_unique_together(self):
        """Test unique_together constraint"""
        from datetime import date
        # Same content_type, object_id, and date should fail
        with self.assertRaises(Exception):  # IntegrityError
            ServiceAnalytics.objects.create(
                content_type=self.content_type,
                object_id=self.savings.id,
                date=date.today(),
                page_views=200
            )


class ServiceRecommendationModelTest(TestCase):
    """Test suite for ServiceRecommendation model"""
    
    def setUp(self):
        """Set up test data"""
        self.recommendation = ServiceRecommendation.objects.create(
            user_profile={"age": 30, "income": 50000},
            recommended_services=["savings", "loan"],
            recommendation_reason="Based on user profile",
            confidence_score=Decimal("85.50")
        )
    
    def test_recommendation_creation(self):
        """Test basic recommendation creation"""
        self.assertEqual(self.recommendation.confidence_score, Decimal("85.50"))
        self.assertEqual(self.recommendation.user_profile, {"age": 30, "income": 50000})
        self.assertEqual(self.recommendation.recommended_services, ["savings", "loan"])
        self.assertIsNotNone(self.recommendation.created_at)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertIn("85.50", str(self.recommendation))
        self.assertIn("confidence", str(self.recommendation))
    
    def test_ordering(self):
        """Test model ordering"""
        rec2 = ServiceRecommendation.objects.create(
            user_profile={},
            recommended_services=[],
            recommendation_reason="Test",
            confidence_score=Decimal("90.00")
        )
        recommendations = list(ServiceRecommendation.objects.all())
        # Should be ordered by -confidence_score, -created_at
        self.assertEqual(recommendations[0], rec2)  # 90.00 > 85.50
        self.assertEqual(recommendations[1], self.recommendation)

