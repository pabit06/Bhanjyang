"""
Comprehensive API serializers for the Bhanjyang Cooperative services.
"""
from typing import Dict, Any, List
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import QuerySet
from .models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService, 
    MemberRelief, ServiceApplication, ServiceAnalytics, ServiceRecommendation
)


class SavingsAccountSerializer(serializers.ModelSerializer):
    """Serializer for Savings Account model with enhanced fields."""
    
    annual_interest_rate = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = SavingsAccount
        fields = [
            'id', 'english_name', 'nepali_name', 'slug', 'description',
            'icon', 'color', 'is_featured', 'is_active', 'account_type',
            'interest_rate', 'minimum_balance', 'features', 'created_at',
            'updated_at', 'annual_interest_rate', 'url'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_annual_interest_rate(self, obj: SavingsAccount) -> float:
        """Get annual interest rate (same as interest_rate for savings accounts)."""
        return float(obj.interest_rate)
    
    def get_url(self, obj: SavingsAccount) -> str:
        """Get the absolute URL for the savings account."""
        return obj.get_absolute_url()
    
    def validate_interest_rate(self, value: float) -> float:
        """Validate interest rate is within reasonable bounds."""
        if value < 0 or value > 50:
            raise serializers.ValidationError(
                "Interest rate must be between 0 and 50 percent."
            )
        return value
    
    def validate_minimum_balance(self, value: float) -> float:
        """Validate minimum balance is positive."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Minimum balance must be positive."
            )
        return value


class FixedDepositSerializer(serializers.ModelSerializer):
    """Serializer for Fixed Deposit model."""
    
    annual_interest_rate = serializers.SerializerMethodField()
    maturity_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = FixedDeposit
        fields = [
            'id', 'duration_months', 'payment_frequency', 'interest_rate',
            'minimum_amount', 'maximum_amount', 'benefits', 'is_active',
            'created_at', 'updated_at', 'annual_interest_rate', 'maturity_amount'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_annual_interest_rate(self, obj: FixedDeposit) -> float:
        """Calculate annual interest rate."""
        return float(obj.interest_rate)
    
    def get_maturity_amount(self, obj: FixedDeposit) -> Dict[str, Any]:
        """Calculate maturity amount for different investment amounts."""
        if obj.minimum_amount:
            return {
                'minimum_investment': float(obj.minimum_amount),
                'minimum_maturity': float(obj.minimum_amount * (1 + obj.interest_rate / 100 * obj.duration_months / 12)),
                'calculation_note': f"Based on {obj.duration_months} months at {obj.interest_rate}%"
            }
        return {}
    
    def validate_interest_rate(self, value: float) -> float:
        """Validate interest rate."""
        if value < 0 or value > 50:
            raise serializers.ValidationError(
                "Interest rate must be between 0 and 50 percent."
            )
        return value


class LoanTypeSerializer(serializers.ModelSerializer):
    """Serializer for Loan Type model."""
    
    annual_interest_rate = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    monthly_payment_calculator = serializers.SerializerMethodField()
    
    class Meta:
        model = LoanType
        fields = [
            'id', 'english_name', 'nepali_name', 'slug', 'description',
            'icon', 'color', 'is_featured', 'is_active', 'loan_category',
            'monthly_interest_rate', 'repayment_type', 'minimum_amount', 'maximum_amount',
            'max_tenure_years', 'requirements', 'benefits', 'created_at',
            'updated_at', 'annual_interest_rate', 'url', 'monthly_payment_calculator'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_url(self, obj: LoanType) -> str:
        """Get the absolute URL for the loan type."""
        return obj.get_absolute_url()
    
    def get_monthly_payment_calculator(self, obj: LoanType) -> Dict[str, Any]:
        """Provide loan calculation information."""
        if obj.minimum_amount and obj.maximum_amount and obj.max_tenure_years:
            return {
                'loan_range': {
                    'minimum': float(obj.minimum_amount),
                    'maximum': float(obj.maximum_amount)
                },
                'tenure_range': {
                    'maximum_years': obj.max_tenure_years,
                    'maximum_months': obj.max_tenure_years * 12
                },
                'interest_rate': {
                    'monthly': float(obj.monthly_interest_rate),
                    'annual': float(obj.annual_interest_rate)
                },
                'note': 'Use loan calculator for exact monthly payment calculations'
            }
        return {}


class RemittanceServiceSerializer(serializers.ModelSerializer):
    """Serializer for Remittance Service model."""
    
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = RemittanceService
        fields = [
            'id', 'english_name', 'nepali_name', 'slug', 'description',
            'icon', 'color', 'is_featured', 'is_active', 'service_type',
            'processing_time', 'fees', 'created_at', 'updated_at', 'url'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_url(self, obj: RemittanceService) -> str:
        """Get the absolute URL for the remittance service."""
        return obj.get_absolute_url()


class MemberReliefSerializer(serializers.ModelSerializer):
    """Serializer for Member Relief model."""
    
    url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberRelief
        fields = [
            'id', 'english_name', 'nepali_name', 'slug', 'description',
            'icon', 'color', 'is_featured', 'is_active', 'relief_type',
            'eligibility', 'benefits', 'application_process', 'image',
            'created_at', 'updated_at', 'url', 'image_url'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_url(self, obj: MemberRelief) -> str:
        """Get the absolute URL for the member relief program."""
        return obj.get_absolute_url()
    
    def get_image_url(self, obj: MemberRelief) -> str:
        """Get the full URL for the relief program image."""
        if obj.image:
            return obj.image.url
        return None


class ServiceApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Service Application model."""
    
    service_name = serializers.ReadOnlyField()
    service_type = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceApplication
        fields = [
            'id', 'content_type', 'object_id', 'service_object', 'service_name',
            'service_type', 'applicant_name', 'applicant_email', 'applicant_phone',
            'applicant_address', 'additional_info', 'status', 'applied_date',
            'reviewed_date', 'reviewed_by', 'notes'
        ]
        read_only_fields = [
            'id', 'service_name', 'service_type', 'applied_date', 
            'reviewed_date', 'reviewed_by'
        ]
    
    def get_service_type(self, obj: ServiceApplication) -> str:
        """Get the service type name."""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def validate_applicant_email(self, value: str) -> str:
        """Validate email format."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid email address.")
        return value
    
    def validate_applicant_phone(self, value: str) -> str:
        """Validate phone number format."""
        if value and len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value


class ServiceAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for Service Analytics model."""
    
    service_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceAnalytics
        fields = [
            'id', 'content_type', 'object_id', 'service_object', 'service_name',
            'date', 'page_views', 'applications_received', 'calculator_usage'
        ]
        read_only_fields = ['id']
    
    def get_service_name(self, obj: ServiceAnalytics) -> str:
        """Get the service name."""
        if obj.service_object:
            return obj.service_object.english_name
        return None


class ServiceRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for Service Recommendation model."""
    
    class Meta:
        model = ServiceRecommendation
        fields = [
            'id', 'user_profile', 'recommended_services', 'recommendation_reason',
            'confidence_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ServiceCalculatorSerializer(serializers.Serializer):
    """Serializer for service calculation requests."""
    
    service_type = serializers.ChoiceField(choices=[
        'savings', 'fixed_deposit', 'loan', 'remittance'
    ])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    duration_months = serializers.IntegerField(min_value=1, max_value=360)
    service_id = serializers.IntegerField()
    
    def validate_amount(self, value: float) -> float:
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class ServiceSearchSerializer(serializers.Serializer):
    """Serializer for service search requests."""
    
    query = serializers.CharField(max_length=200, required=False)
    service_type = serializers.ChoiceField(choices=[
        'savings', 'fixed_deposit', 'loan', 'remittance', 'relief'
    ], required=False)
    is_featured = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    min_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    max_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    ordering = serializers.ChoiceField(choices=[
        'name', '-name', 'interest_rate', '-interest_rate', 'created_at', '-created_at'
    ], required=False)
    page = serializers.IntegerField(min_value=1, required=False)
    page_size = serializers.IntegerField(min_value=1, max_value=100, required=False)
