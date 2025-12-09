"""
Member Admin Interface
Custom admin for member management and approvals
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import (
    MemberRegistration, Member, KYCDocument, 
    Ward, MemberAccount, MemberTransaction, MemberLoan, MemberNotification
)
from .integrations.cbs_models import CBSAccount, CBSTransaction, CBSLoan, CBSMember, CBSSyncLog

logger = logging.getLogger('members.admin')


# MemberUser admin temporarily disabled
# @admin.register(MemberUser)
# class MemberUserAdmin(UserAdmin):
#     """
#     Custom User Admin for Member Users
#     """
#     list_display = [
#         'username', 'email', 'first_name', 'last_name', 
#         'member_id', 'is_member', 'is_verified', 'is_active', 'date_joined'
#     ]
#     list_filter = [
#         'is_member', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined'
#     ]
#     search_fields = ['username', 'email', 'first_name', 'last_name', 'member_id']
#     ordering = ['-date_joined']
#     
#     fieldsets = UserAdmin.fieldsets + (
#         (_('Member Information'), {
#             'fields': ('member_id', 'is_member', 'is_verified', 'phone_number', 'member_since')
#         }),
#     )
#     
#     readonly_fields = ['member_id', 'member_since']
#     
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('member_profile')


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    """
    Ward Admin
    """
    list_display = ['ward_number', 'ward_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['ward_number', 'ward_name']
    ordering = ['ward_number']


class KYCDocumentInline(admin.TabularInline):
    """
    KYC Document Inline
    """
    model = KYCDocument
    extra = 0
    readonly_fields = ['created_at', 'verified_by', 'verification_date']
    fields = [
        'document_type', 'document_file', 'document_number', 
        'issue_date', 'expiry_date', 'is_verified', 'verification_notes'
    ]


@admin.register(MemberRegistration)
class MemberRegistrationAdmin(admin.ModelAdmin):
    """
    Member Registration Admin with Approval Actions
    """
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'phone', 
        'ward', 'status', 'location_verified', 'created_at'
    ]
    list_filter = [
        'status', 'location_verified', 'ward', 'created_at'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone', 'citizenship_number'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'middle_name', 'email', 'phone')
        }),
        (_('Location Information'), {
            'fields': ('permanent_address', 'ward', 'tole_name')
        }),
        (_('Verification Status'), {
            'fields': ('status', 'location_verified', 'verified_by', 'verification_date', 'verification_notes')
        }),
        (_('Documents'), {
            'fields': ('citizenship_document', 'address_proof')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_location', 'reject_location', 'approve_kyc', 'reject_kyc']
    
    def approve_location(self, request, queryset):
        """Approve location verification"""
        approved_count = 0
        for registration in queryset.filter(status='pending_location'):
            registration.status = 'location_verified'
            registration.location_verified = True
            registration.verified_by = request.user
            registration.verification_date = timezone.now()
            registration.save()
            
            # Send approval email
            self.send_location_approval_email(registration)
            approved_count += 1
        
        messages.success(
            request,
            f'{approved_count} स्थान प्रमाणीकरण स्वीकृत गरियो।'
        )
    approve_location.short_description = _('स्थान प्रमाणीकरण स्वीकृत गर्नुहोस्')
    
    def reject_location(self, request, queryset):
        """Reject location verification"""
        rejected_count = 0
        for registration in queryset.filter(status='pending_location'):
            registration.status = 'rejected'
            registration.location_verified = False
            registration.verified_by = request.user
            registration.verification_date = timezone.now()
            registration.save()
            
            # Send rejection email
            self.send_location_rejection_email(registration)
            rejected_count += 1
        
        messages.success(
            request,
            f'{rejected_count} स्थान प्रमाणीकरण अस्वीकृत गरियो।'
        )
    reject_location.short_description = _('स्थान प्रमाणीकरण अस्वीकृत गर्नुहोस्')
    
    def approve_kyc(self, request, queryset):
        """Approve KYC and create member"""
        approved_count = 0
        for registration in queryset.filter(status='kyc_pending'):
            try:
                # Create member
                member = self.create_member_from_registration(registration)
                
                # Update registration status
                registration.status = 'member_active'
                registration.save()
                
                # Send approval email
                self.send_kyc_approval_email(registration, member)
                approved_count += 1
                
            except Exception as e:
                logger.error(f"Error creating member from registration {registration.id}: {e}")
                messages.error(request, f'Registration {registration.id} को लागि समस्या भयो: {e}')
        
        messages.success(
            request,
            f'{approved_count} KYC स्वीकृत गरियो र सदस्य सिर्जना गरियो।'
        )
    approve_kyc.short_description = _('KYC स्वीकृत गर्नुहोस्')
    
    def reject_kyc(self, request, queryset):
        """Reject KYC"""
        rejected_count = 0
        for registration in queryset.filter(status='kyc_pending'):
            registration.status = 'rejected'
            registration.save()
            
            # Send rejection email
            self.send_kyc_rejection_email(registration)
            rejected_count += 1
        
        messages.success(
            request,
            f'{rejected_count} KYC अस्वीकृत गरियो।'
        )
    reject_kyc.short_description = _('KYC अस्वीकृत गर्नुहोस्')
    
    def create_member_from_registration(self, registration):
        """Create member from approved registration"""
        from django.utils import timezone
        
        # Get or create user
        user, created = MemberUser.objects.get_or_create(
            email=registration.email,
            defaults={
                'username': registration.email,
                'first_name': registration.first_name,
                'last_name': registration.last_name,
                'phone_number': registration.phone,
                'is_member': True,
                'is_verified': True,
                'member_since': timezone.now()
            }
        )
        
        if not created:
            user.is_member = True
            user.is_verified = True
            user.save()
        
        # Create member profile
        member = Member.objects.create(
            user=user,
            first_name=registration.first_name,
            last_name=registration.last_name,
            email=registration.email,
            phone=registration.phone,
            permanent_address=registration.permanent_address,
            ward=registration.ward,
            tole_name=registration.tole_name,
            membership_date=timezone.now().date(),
            citizenship_number=registration.citizenship_number or 'N/A',
            citizenship_issue_date=registration.citizenship_issue_date or timezone.now().date(),
            citizenship_issue_district=registration.citizenship_issue_district or 'Kaski',
            father_name=registration.father_name or 'N/A',
            mother_name=registration.mother_name or 'N/A',
            occupation=registration.occupation or 'N/A',
            is_active=True,
            is_verified=True,
            citizenship_document=registration.citizenship_document
        )
        
        return member
    
    def send_location_approval_email(self, registration):
        """Send location approval email"""
        try:
            subject = _('स्थान प्रमाणीकरण स्वीकृत')
            message = f"""
            नमस्कार {registration.first_name} {registration.last_name},
            
            तपाईंको स्थान प्रमाणीकरण स्वीकृत भयो।
            
            अब तपाईंले KYC दस्तावेज अपलोड गर्न सक्नुहुन्छ:
            {settings.SITE_URL}/members/kyc/{registration.id}/
            
            धन्यवाद,
            भन्ज्याङ सहकारी
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [registration.email],
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"Location approval email failed: {e}")
    
    def send_location_rejection_email(self, registration):
        """Send location rejection email"""
        try:
            subject = _('स्थान प्रमाणीकरण अस्वीकृत')
            message = f"""
            नमस्कार {registration.first_name} {registration.last_name},
            
            तपाईंको स्थान प्रमाणीकरण अस्वीकृत भयो।
            
            कृपया सम्पर्क गर्नुहोस्: {settings.CONTACT_EMAIL}
            
            धन्यवाद,
            भन्ज्याङ सहकारी
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [registration.email],
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"Location rejection email failed: {e}")
    
    def send_kyc_approval_email(self, registration, member):
        """Send KYC approval email"""
        try:
            subject = _('सदस्यता स्वीकृत')
            message = f"""
            नमस्कार {registration.first_name} {registration.last_name},
            
            तपाईंको सदस्यता स्वीकृत भयो।
            
            सदस्य नम्बर: {member.user.member_id}
            
            तपाईंले सदस्य ड्यासबोर्डमा लगइन गर्न सक्नुहुन्छ:
            {settings.SITE_URL}/members/login/
            
            धन्यवाद,
            भन्ज्याङ सहकारी
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [registration.email],
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"KYC approval email failed: {e}")
    
    def send_kyc_rejection_email(self, registration):
        """Send KYC rejection email"""
        try:
            subject = _('KYC अस्वीकृत')
            message = f"""
            नमस्कार {registration.first_name} {registration.last_name},
            
            तपाईंको KYC अस्वीकृत भयो।
            
            कृपया सम्पर्क गर्नुहोस्: {settings.CONTACT_EMAIL}
            
            धन्यवाद,
            भन्ज्याङ सहकारी
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [registration.email],
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"KYC rejection email failed: {e}")


class MemberAccountInline(admin.TabularInline):
    """
    Member Account Inline
    """
    model = MemberAccount
    extra = 0
    readonly_fields = ['created_at', 'last_sync_date']
    fields = [
        'account_type', 'account_number', 'account_name', 
        'balance', 'interest_rate', 'is_active', 'is_primary'
    ]


class MemberLoanInline(admin.TabularInline):
    """
    Member Loan Inline
    """
    model = MemberLoan
    extra = 0
    readonly_fields = ['applied_date', 'approved_date', 'disbursed_date']
    fields = [
        'loan_type', 'loan_amount', 'interest_rate', 
        'tenure_months', 'status', 'purpose'
    ]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """
    Member Admin
    """
    list_display = [
        'user', 'first_name', 'last_name', 'email', 'phone', 
        'ward', 'membership_type', 'is_active', 'is_verified', 'membership_date'
    ]
    list_filter = [
        'is_active', 'is_verified', 'membership_type', 'ward', 'membership_date'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone', 'citizenship_number'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('user', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'alternate_phone')
        }),
        (_('Address Information'), {
            'fields': ('permanent_address', 'ward', 'tole_name')
        }),
        (_('Membership Information'), {
            'fields': ('membership_type', 'membership_date', 'membership_fee_paid', 'membership_fee_amount')
        }),
        (_('KYC Information'), {
            'fields': ('citizenship_number', 'citizenship_issue_date', 'citizenship_issue_district')
        }),
        (_('Family Information'), {
            'fields': ('father_name', 'mother_name', 'spouse_name')
        }),
        (_('Professional Information'), {
            'fields': ('occupation', 'workplace', 'monthly_income')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_verified')
        }),
        (_('Documents'), {
            'fields': ('profile_photo', 'citizenship_document')
        }),
        (_('CBS Integration'), {
            'fields': ('cbs_member_id', 'cbs_sync_status', 'last_sync_date'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_sync_date']
    inlines = [MemberAccountInline, MemberLoanInline]
    
    actions = ['sync_cbs_data', 'activate_members', 'deactivate_members']
    
    def sync_cbs_data(self, request, queryset):
        """Sync CBS data for selected members"""
        from .integrations.cbs_sync import CBSSyncManager
        
        sync_manager = CBSSyncManager()
        synced_count = 0
        
        for member in queryset.filter(cbs_member_id__isnull=False):
            try:
                result = sync_manager.sync_member_accounts(member.cbs_member_id)
                if result['status'] == 'success':
                    synced_count += 1
            except Exception as e:
                logger.error(f"CBS sync error for member {member.id}: {e}")
        
        messages.success(
            request,
            f'{synced_count} सदस्यहरूको CBS डाटा सिन्क गरियो।'
        )
    sync_cbs_data.short_description = _('CBS डाटा सिन्क गर्नुहोस्')
    
    def activate_members(self, request, queryset):
        """Activate selected members"""
        activated_count = queryset.filter(is_active=False).update(is_active=True)
        messages.success(
            request,
            f'{activated_count} सदस्यहरू सक्रिय गरियो।'
        )
    activate_members.short_description = _('सदस्यहरू सक्रिय गर्नुहोस्')
    
    def deactivate_members(self, request, queryset):
        """Deactivate selected members"""
        deactivated_count = queryset.filter(is_active=True).update(is_active=False)
        messages.success(
            request,
            f'{deactivated_count} सदस्यहरू निष्क्रिय गरियो।'
        )
    deactivate_members.short_description = _('सदस्यहरू निष्क्रिय गर्नुहोस्')


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    """
    KYC Document Admin
    """
    list_display = [
        'member', 'document_type', 'document_number', 
        'is_verified', 'verified_by', 'created_at'
    ]
    list_filter = [
        'document_type', 'is_verified', 'created_at'
    ]
    search_fields = [
        'member__first_name', 'member__last_name', 'document_number'
    ]
    ordering = ['-created_at']
    
    actions = ['verify_documents', 'reject_documents']
    
    def verify_documents(self, request, queryset):
        """Verify selected documents"""
        verified_count = queryset.filter(is_verified=False).update(
            is_verified=True,
            verified_by=request.user,
            verification_date=timezone.now()
        )
        messages.success(
            request,
            f'{verified_count} दस्तावेजहरू प्रमाणित गरियो।'
        )
    verify_documents.short_description = _('दस्तावेजहरू प्रमाणित गर्नुहोस्')
    
    def reject_documents(self, request, queryset):
        """Reject selected documents"""
        rejected_count = queryset.filter(is_verified=True).update(
            is_verified=False,
            verified_by=request.user,
            verification_date=timezone.now()
        )
        messages.success(
            request,
            f'{rejected_count} दस्तावेजहरू अस्वीकृत गरियो।'
        )
    reject_documents.short_description = _('दस्तावेजहरू अस्वीकृत गर्नुहोस्')


@admin.register(MemberAccount)
class MemberAccountAdmin(admin.ModelAdmin):
    """
    Member Account Admin
    """
    list_display = [
        'member', 'account_type', 'account_number', 
        'balance', 'is_active', 'is_primary'
    ]
    list_filter = [
        'account_type', 'is_active', 'is_primary'
    ]
    search_fields = [
        'member__first_name', 'member__last_name', 'account_number'
    ]
    ordering = ['-created_at']


@admin.register(MemberTransaction)
class MemberTransactionAdmin(admin.ModelAdmin):
    """
    Member Transaction Admin
    """
    list_display = [
        'account', 'transaction_type', 'amount', 
        'transaction_date', 'description'
    ]
    list_filter = [
        'transaction_type', 'transaction_date', 'is_cbs_synced'
    ]
    search_fields = [
        'account__member__first_name', 'account__member__last_name', 
        'account__account_number', 'reference_number'
    ]
    ordering = ['-transaction_date']
    date_hierarchy = 'transaction_date'


@admin.register(MemberLoan)
class MemberLoanAdmin(admin.ModelAdmin):
    """
    Member Loan Admin
    """
    list_display = [
        'member', 'loan_type', 'loan_amount', 
        'status', 'applied_date', 'tenure_months'
    ]
    list_filter = [
        'loan_type', 'status', 'applied_date'
    ]
    search_fields = [
        'member__first_name', 'member__last_name', 'loan_type'
    ]
    ordering = ['-applied_date']
    
    actions = ['approve_loans', 'reject_loans']
    
    def approve_loans(self, request, queryset):
        """Approve selected loans"""
        approved_count = queryset.filter(status='under_review').update(
            status='approved',
            approved_date=timezone.now()
        )
        messages.success(
            request,
            f'{approved_count} ऋणहरू स्वीकृत गरियो।'
        )
    approve_loans.short_description = _('ऋणहरू स्वीकृत गर्नुहोस्')
    
    def reject_loans(self, request, queryset):
        """Reject selected loans"""
        rejected_count = queryset.filter(status='under_review').update(
            status='rejected'
        )
        messages.success(
            request,
            f'{rejected_count} ऋणहरू अस्वीकृत गरियो।'
        )
    reject_loans.short_description = _('ऋणहरू अस्वीकृत गर्नुहोस्')


@admin.register(MemberNotification)
class MemberNotificationAdmin(admin.ModelAdmin):
    """
    Member Notification Admin
    """
    list_display = [
        'member', 'notification_type', 'title', 
        'is_read', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'created_at'
    ]
    search_fields = [
        'member__first_name', 'member__last_name', 'title'
    ]
    ordering = ['-created_at']


# CBS Integration Admin
@admin.register(CBSAccount)
class CBSAccountAdmin(admin.ModelAdmin):
    """
    CBS Account Admin
    """
    list_display = [
        'account_number', 'account_type', 'account_name', 
        'balance', 'status', 'last_sync_date'
    ]
    list_filter = [
        'account_type', 'status', 'last_sync_date'
    ]
    search_fields = [
        'account_number', 'account_name', 'cbs_member_id'
    ]
    ordering = ['-last_sync_date']


@admin.register(CBSTransaction)
class CBSTransactionAdmin(admin.ModelAdmin):
    """
    CBS Transaction Admin
    """
    list_display = [
        'cbs_transaction_id', 'transaction_type', 'amount', 
        'transaction_date', 'description'
    ]
    list_filter = [
        'transaction_type', 'transaction_date', 'sync_status'
    ]
    search_fields = [
        'cbs_transaction_id', 'description', 'reference_number'
    ]
    ordering = ['-transaction_date']
    date_hierarchy = 'transaction_date'


@admin.register(CBSLoan)
class CBSLoanAdmin(admin.ModelAdmin):
    """
    CBS Loan Admin
    """
    list_display = [
        'cbs_loan_id', 'loan_type', 'loan_amount', 
        'status', 'cbs_applied_date', 'tenure_months'
    ]
    list_filter = [
        'loan_type', 'status', 'cbs_applied_date'
    ]
    search_fields = [
        'cbs_loan_id', 'loan_type', 'cbs_member_id'
    ]
    ordering = ['-cbs_applied_date']


@admin.register(CBSMember)
class CBSMemberAdmin(admin.ModelAdmin):
    """
    CBS Member Admin
    """
    list_display = [
        'member_id', 'first_name', 'last_name', 
        'email', 'is_active', 'last_sync_date'
    ]
    list_filter = [
        'is_active', 'is_verified', 'last_sync_date'
    ]
    search_fields = [
        'member_id', 'first_name', 'last_name', 'email'
    ]
    ordering = ['-last_sync_date']


@admin.register(CBSSyncLog)
class CBSSyncLogAdmin(admin.ModelAdmin):
    """
    CBS Sync Log Admin
    """
    list_display = [
        'sync_type', 'sync_status', 'records_processed', 
        'records_successful', 'records_failed', 'started_at', 'duration_seconds'
    ]
    list_filter = [
        'sync_type', 'sync_status', 'started_at'
    ]
    search_fields = [
        'error_message'
    ]
    ordering = ['-started_at']
    date_hierarchy = 'started_at'
    
    readonly_fields = [
        'sync_type', 'sync_status', 'records_processed', 
        'records_successful', 'records_failed', 'error_message', 
        'error_details', 'started_at', 'completed_at', 'duration_seconds'
    ]