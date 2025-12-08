"""
Member API Serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    MemberUser, MemberRegistration, Member, KYCDocument, 
    Ward, MemberAccount, MemberTransaction, MemberLoan, MemberNotification
)
from .integrations.cbs_models import CBSAccount, CBSTransaction, CBSLoan, CBSMember

User = get_user_model()


class WardSerializer(serializers.ModelSerializer):
    """Ward serializer"""
    
    class Meta:
        model = Ward
        fields = ['id', 'ward_number', 'ward_name', 'description', 'is_active']


class MemberUserSerializer(serializers.ModelSerializer):
    """Member User serializer"""
    
    class Meta:
        model = MemberUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'member_id', 'is_member', 'is_verified', 'phone_number',
            'member_since', 'last_login_ip', 'date_joined'
        ]
        read_only_fields = [
            'id', 'member_id', 'member_since', 'last_login_ip', 'date_joined'
        ]


class MemberRegistrationSerializer(serializers.ModelSerializer):
    """Member Registration serializer"""
    
    ward_name = serializers.CharField(source='ward.ward_name', read_only=True)
    
    class Meta:
        model = MemberRegistration
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'email', 'phone',
            'permanent_address', 'ward', 'ward_name', 'tole_name',
            'status', 'location_verified', 'verified_by', 'verification_date',
            'verification_notes', 'citizenship_document', 'address_proof',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'location_verified', 'verified_by', 
            'verification_date', 'created_at', 'updated_at'
        ]


class KYCDocumentSerializer(serializers.ModelSerializer):
    """KYC Document serializer"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = KYCDocument
        fields = [
            'id', 'member', 'member_name', 'document_type', 'document_file',
            'document_number', 'issue_date', 'expiry_date', 'is_verified',
            'verified_by', 'verification_date', 'verification_notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'is_verified', 'verified_by', 'verification_date', 'created_at'
        ]


class MemberSerializer(serializers.ModelSerializer):
    """Member serializer"""
    
    user = MemberUserSerializer(read_only=True)
    ward_name = serializers.CharField(source='ward.ward_name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Member
        fields = [
            'id', 'user', 'first_name', 'last_name', 'middle_name', 'full_name',
            'email', 'phone', 'alternate_phone', 'permanent_address', 'ward',
            'ward_name', 'tole_name', 'membership_type', 'membership_date',
            'membership_fee_paid', 'membership_fee_amount', 'citizenship_number',
            'citizenship_issue_date', 'citizenship_issue_district', 'father_name',
            'mother_name', 'spouse_name', 'occupation', 'workplace', 'monthly_income',
            'is_active', 'is_verified', 'profile_photo', 'citizenship_document',
            'cbs_member_id', 'cbs_sync_status', 'last_sync_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'full_name', 'cbs_sync_status', 'last_sync_date',
            'created_at', 'updated_at'
        ]


class MemberAccountSerializer(serializers.ModelSerializer):
    """Member Account serializer"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = MemberAccount
        fields = [
            'id', 'member', 'member_name', 'account_type', 'account_number',
            'account_name', 'balance', 'interest_rate', 'is_active', 'is_primary',
            'cbs_account_id', 'cbs_sync_status', 'last_sync_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'member_name', 'cbs_sync_status', 'last_sync_date',
            'created_at', 'updated_at'
        ]


class MemberTransactionSerializer(serializers.ModelSerializer):
    """Member Transaction serializer"""
    
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    member_name = serializers.CharField(source='account.member.user.get_full_name', read_only=True)
    
    class Meta:
        model = MemberTransaction
        fields = [
            'id', 'account', 'account_number', 'member_name', 'transaction_type',
            'amount', 'balance_after', 'description', 'reference_number',
            'transaction_date', 'cbs_transaction_id', 'is_cbs_synced', 'created_at'
        ]
        read_only_fields = [
            'id', 'account_number', 'member_name', 'cbs_transaction_id',
            'is_cbs_synced', 'created_at'
        ]


class MemberLoanSerializer(serializers.ModelSerializer):
    """Member Loan serializer"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = MemberLoan
        fields = [
            'id', 'member', 'member_name', 'loan_type', 'loan_amount',
            'interest_rate', 'tenure_months', 'purpose', 'monthly_installment',
            'status', 'cbs_loan_id', 'cbs_sync_status', 'applied_date',
            'approved_date', 'disbursed_date'
        ]
        read_only_fields = [
            'id', 'member_name', 'cbs_loan_id', 'cbs_sync_status',
            'applied_date', 'approved_date', 'disbursed_date'
        ]


class MemberNotificationSerializer(serializers.ModelSerializer):
    """Member Notification serializer"""
    
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = MemberNotification
        fields = [
            'id', 'member', 'member_name', 'notification_type', 'title',
            'message', 'is_read', 'created_at'
        ]
        read_only_fields = [
            'id', 'member_name', 'created_at'
        ]


# CBS Integration Serializers
class CBSAccountSerializer(serializers.ModelSerializer):
    """CBS Account serializer"""
    
    class Meta:
        model = CBSAccount
        fields = [
            'id', 'cbs_account_id', 'cbs_member_id', 'account_number',
            'account_type', 'account_name', 'balance', 'available_balance',
            'interest_rate', 'status', 'is_active', 'cbs_created_date',
            'cbs_last_updated', 'last_sync_date', 'sync_status'
        ]
        read_only_fields = [
            'id', 'cbs_created_date', 'cbs_last_updated', 'last_sync_date', 'sync_status'
        ]


class CBSTransactionSerializer(serializers.ModelSerializer):
    """CBS Transaction serializer"""
    
    class Meta:
        model = CBSTransaction
        fields = [
            'id', 'cbs_transaction_id', 'cbs_account_id', 'transaction_type',
            'amount', 'balance_after', 'description', 'reference_number',
            'transaction_date', 'cbs_created_date', 'last_sync_date', 'sync_status'
        ]
        read_only_fields = [
            'id', 'cbs_created_date', 'last_sync_date', 'sync_status'
        ]


class CBSLoanSerializer(serializers.ModelSerializer):
    """CBS Loan serializer"""
    
    class Meta:
        model = CBSLoan
        fields = [
            'id', 'cbs_loan_id', 'cbs_member_id', 'loan_type', 'loan_amount',
            'disbursed_amount', 'outstanding_amount', 'interest_rate', 'tenure_months',
            'purpose', 'monthly_installment', 'status', 'cbs_applied_date',
            'cbs_approved_date', 'cbs_disbursed_date', 'last_sync_date', 'sync_status'
        ]
        read_only_fields = [
            'id', 'cbs_applied_date', 'cbs_approved_date', 'cbs_disbursed_date',
            'last_sync_date', 'sync_status'
        ]


class CBSMemberSerializer(serializers.ModelSerializer):
    """CBS Member serializer"""
    
    class Meta:
        model = CBSMember
        fields = [
            'id', 'cbs_member_id', 'member_id', 'first_name', 'last_name',
            'middle_name', 'email', 'phone', 'permanent_address', 'ward_number',
            'membership_date', 'membership_type', 'is_active', 'is_verified',
            'cbs_created_date', 'cbs_last_updated', 'last_sync_date', 'sync_status'
        ]
        read_only_fields = [
            'id', 'cbs_created_date', 'cbs_last_updated', 'last_sync_date', 'sync_status'
        ]


# Dashboard Serializers
class MemberDashboardSerializer(serializers.Serializer):
    """Member Dashboard serializer"""
    
    member = MemberSerializer(read_only=True)
    accounts = MemberAccountSerializer(many=True, read_only=True)
    recent_transactions = MemberTransactionSerializer(many=True, read_only=True)
    active_loans = MemberLoanSerializer(many=True, read_only=True)
    notifications = MemberNotificationSerializer(many=True, read_only=True)
    cbs_accounts = CBSAccountSerializer(many=True, read_only=True)
    cbs_transactions = CBSTransactionSerializer(many=True, read_only=True)
    cbs_loans = CBSLoanSerializer(many=True, read_only=True)
    cbs_error = serializers.CharField(read_only=True)


class LoanApplicationSerializer(serializers.Serializer):
    """Loan Application serializer"""
    
    loan_type = serializers.CharField(max_length=100)
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    purpose = serializers.CharField()
    tenure_months = serializers.IntegerField(min_value=1, max_value=60)
    
    def validate_loan_amount(self, value):
        if value < 1000:
            raise serializers.ValidationError("ऋण रकम कम्तिमा १,००० रुपैयाँ हुनुपर्छ।")
        return value
    
    def validate_tenure_months(self, value):
        if value < 1 or value > 60:
            raise serializers.ValidationError("ऋण अवधि १ देखि ६० महिना सम्म हुनुपर्छ।")
        return value


class ContactSupportSerializer(serializers.Serializer):
    """Contact Support serializer"""
    
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    priority = serializers.ChoiceField(choices=[
        ('low', 'कम'),
        ('medium', 'मध्यम'),
        ('high', 'उच्च'),
    ])


class PasswordChangeSerializer(serializers.Serializer):
    """Password Change serializer"""
    
    current_password = serializers.CharField()
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()
    
    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("नयाँ पासवर्डहरू मेल खाँदैन।")
        return data


# Statistics Serializers
class MemberStatsSerializer(serializers.Serializer):
    """Member Statistics serializer"""
    
    total_members = serializers.IntegerField(read_only=True)
    active_members = serializers.IntegerField(read_only=True)
    pending_registrations = serializers.IntegerField(read_only=True)
    total_accounts = serializers.IntegerField(read_only=True)
    total_loans = serializers.IntegerField(read_only=True)
    active_loans = serializers.IntegerField(read_only=True)
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)


class WardStatsSerializer(serializers.Serializer):
    """Ward Statistics serializer"""
    
    ward = WardSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    active_member_count = serializers.IntegerField(read_only=True)
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_loans = serializers.IntegerField(read_only=True)
