"""
Member Views for Registration, Dashboard, and Management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import (
    TemplateView, CreateView, UpdateView, ListView, DetailView
)
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .models import (
    MemberRegistration, Member, KYCDocument, 
    Ward, MemberAccount, MemberTransaction, MemberLoan, MemberNotification
)
from .forms import (
    MemberRegistrationForm, KYCDocumentForm, MemberLoginForm,
    MemberProfileForm, LoanApplicationForm, PasswordChangeForm, ContactForm
)
from .integrations.cbs_api import CBSAPIClient, CBSSyncService

logger = logging.getLogger('members')


class MemberRegistrationView(CreateView):
    """
    Member Registration View (Step 1: Location Verification)
    """
    model = MemberRegistration
    form_class = MemberRegistrationForm
    template_name = 'members/registration/register.html'
    success_url = reverse_lazy('members:registration_success')
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                registration = form.save()
                
                # Send confirmation email
                self.send_registration_email(registration)
                
                messages.success(
                    self.request,
                    _('Registration successful! Please proceed to KYC document upload.')
                )
                
                return redirect('members:kyc_upload', pk=registration.pk)
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            messages.error(
                self.request,
                _('दर्तामा समस्या भयो। कृपया पुनः प्रयास गर्नुहोस्।')
            )
            return self.form_invalid(form)
    
    def send_registration_email(self, registration):
        """Send registration confirmation email"""
        try:
            subject = _('भन्ज्याङ सहकारीको सदस्यता दर्ता')
            message = f"""
            नमस्कार {registration.first_name} {registration.last_name},
            
            तपाईंको सदस्यता दर्ता सफलतापूर्वक पेश गरियो।
            
            दर्ता नम्बर: {registration.id}
            स्थिति: स्थान प्रमाणीकरणको लागि प्रतीक्षा
            
            तपाईंको दर्ता स्थिति जाँच गर्न यहाँ क्लिक गर्नुहोस्:
            {self.request.build_absolute_uri(reverse('members:registration_status', kwargs={'pk': registration.pk}))}
            
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
            logger.error(f"Email sending failed: {e}")


class RegistrationStatusView(DetailView):
    """
    Registration Status View
    Shows current status of member registration
    """
    model = MemberRegistration
    template_name = 'members/registration/status.html'
    context_object_name = 'registration'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = self.get_object()
        
        # Determine next steps based on status
        next_steps = []
        if registration.status == 'pending_location':
            next_steps = [
                'स्थान प्रमाणीकरणको लागि प्रतीक्षा गर्नुहोस्',
                'प्रशासकले तपाईंको ठेगाना जाँच गर्नेछन्',
                'प्रमाणीकरण पछि KYC दस्तावेज अपलोड गर्न सकिनेछ'
            ]
        elif registration.status == 'location_verified':
            next_steps = [
                'KYC दस्तावेज अपलोड गर्नुहोस्',
                'नागरिकता प्रमाणपत्र र ठेगाना प्रमाणपत्र अपलोड गर्नुहोस्',
                'सबै जानकारी भरेर पेश गर्नुहोस्'
            ]
        elif registration.status == 'kyc_pending':
            next_steps = [
                'KYC दस्तावेजहरूको जाँचको लागि प्रतीक्षा गर्नुहोस्',
                'प्रशासकले दस्तावेजहरू जाँच गर्नेछन्',
                'स्वीकृति पछि सदस्यता सक्रिय हुनेछ'
            ]
        elif registration.status == 'kyc_approved':
            next_steps = [
                'सदस्यता सफलतापूर्वक स्वीकृत भयो',
                'तपाईंले सदस्य ड्यासबोर्डमा लगइन गर्न सक्नुहुन्छ',
                'सबै सेवाहरू प्रयोग गर्न सकिनेछ'
            ]
        elif registration.status == 'rejected':
            next_steps = [
                'तपाईंको आवेदन अस्वीकृत भयो',
                'कृपया सम्पर्क गर्नुहोस्: info@bhanjyangcoop.com',
                'नयाँ आवेदन पेश गर्न सकिनेछ'
            ]
        
        context['next_steps'] = next_steps
        context['can_proceed'] = registration.status == 'location_verified'
        
        return context


class KYCDocumentUploadView(UpdateView):
    """
    KYC Document Upload View (Step 2: After Location Approval)
    """
    model = MemberRegistration
    form_class = KYCDocumentForm
    template_name = 'members/registration/kyc.html'
    success_url = reverse_lazy('members:kyc_success')
    
    def get_queryset(self):
        return MemberRegistration.objects.filter(
            status__in=['pending_location', 'location_verified']
        )
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                registration = form.save(commit=False)
                registration.status = 'kyc_pending'
                registration.save()
                
                # Send KYC submission email
                self.send_kyc_email(registration)
                
                messages.success(
                    self.request,
                    _('KYC दस्तावेज सफलतापूर्वक अपलोड गरियो। जाँचको लागि प्रतीक्षा गर्नुहोस्।')
                )
                
                return redirect('members:registration_status', pk=registration.pk)
                
        except Exception as e:
            logger.error(f"KYC upload error: {e}")
            messages.error(
                self.request,
                _('KYC अपलोडमा समस्या भयो। कृपया पुनः प्रयास गर्नुहोस्।')
            )
            return self.form_invalid(form)
    
    def send_kyc_email(self, registration):
        """Send KYC submission email"""
        try:
            subject = _('KYC दस्तावेज पेश गरियो')
            message = f"""
            नमस्कार {registration.first_name} {registration.last_name},
            
            तपाईंको KYC दस्तावेज सफलतापूर्वक पेश गरियो।
            
            दर्ता नम्बर: {registration.id}
            स्थिति: KYC जाँचको लागि प्रतीक्षा
            
            तपाईंको दर्ता स्थिति जाँच गर्न यहाँ क्लिक गर्नुहोस्:
            {self.request.build_absolute_uri(reverse('members:registration_status', kwargs={'pk': registration.pk}))}
            
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
            logger.error(f"Email sending failed: {e}")


class MemberDashboardView(LoginRequiredMixin, TemplateView):
    """
    Member Dashboard View
    Main dashboard with CBS data integration
    """
    template_name = 'members/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get member profile
            member = Member.objects.get(user=self.request.user)
            context['member'] = member
            
            # Get CBS data
            cbs_client = CBSAPIClient()
            cbs_data = self.get_cbs_data(member, cbs_client)
            context.update(cbs_data)
            
            # Get recent notifications
            notifications = MemberNotification.objects.filter(
                member=member,
                is_read=False
            ).order_by('-created_at')[:5]
            context['notifications'] = notifications
            
            # Get recent transactions
            recent_transactions = MemberTransaction.objects.filter(
                account__member=member
            ).order_by('-transaction_date')[:10]
            context['recent_transactions'] = recent_transactions
            
            # Get active loans
            active_loans = MemberLoan.objects.filter(
                member=member,
                status__in=['active', 'disbursed']
            )
            context['active_loans'] = active_loans
            
        except Member.DoesNotExist:
            context['member'] = None
            context['error'] = _('सदस्य प्रोफाइल फेला परेन।')
            context['needs_registration'] = True
        
        return context
    
    def get_cbs_data(self, member, cbs_client):
        """Get CBS data for member"""
        cbs_data = {
            'cbs_accounts': [],
            'cbs_transactions': [],
            'cbs_loans': [],
            'cbs_error': None
        }
        
        try:
            if member.cbs_member_id:
                # Get accounts
                accounts_data = cbs_client.get_member_accounts(member.cbs_member_id)
                cbs_data['cbs_accounts'] = accounts_data
                
                # Get recent transactions for primary account
                if accounts_data:
                    primary_account = accounts_data[0]
                    transactions_data = cbs_client.get_transaction_history(
                        primary_account['account_number'],
                        limit=10
                    )
                    cbs_data['cbs_transactions'] = transactions_data
                
                # Get loans
                loans_data = cbs_client.get_member_loans(member.cbs_member_id)
                cbs_data['cbs_loans'] = loans_data
                
        except Exception as e:
            logger.error(f"CBS data fetch error: {e}")
            cbs_data['cbs_error'] = str(e)
        
        return cbs_data


class MemberProfileView(LoginRequiredMixin, UpdateView):
    """
    Member Profile View
    Profile management and updates
    """
    model = Member
    form_class = MemberProfileForm
    template_name = 'members/profile.html'
    success_url = reverse_lazy('members:member_profile')
    
    def get_object(self):
        return get_object_or_404(Member, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(
            self.request,
            _('प्रोफाइल सफलतापूर्वक अपडेट गरियो।')
        )
        return super().form_valid(form)


class MemberAccountsView(LoginRequiredMixin, ListView):
    """
    Member Accounts View
    Display all member accounts with balances
    """
    model = MemberAccount
    template_name = 'members/accounts.html'
    context_object_name = 'accounts'
    paginate_by = 10
    
    def get_queryset(self):
        member = get_object_or_404(Member, user=self.request.user)
        return MemberAccount.objects.filter(
            member=member,
            is_active=True
        ).order_by('account_type', 'account_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = get_object_or_404(Member, user=self.request.user)
        
        # Get CBS data for accounts
        cbs_client = CBSAPIClient()
        cbs_accounts = []
        
        try:
            if member.cbs_member_id:
                cbs_accounts = cbs_client.get_member_accounts(member.cbs_member_id)
        except Exception as e:
            logger.error(f"CBS accounts fetch error: {e}")
        
        context['cbs_accounts'] = cbs_accounts
        context['member'] = member
        
        return context


class MemberTransactionsView(LoginRequiredMixin, ListView):
    """
    Member Transactions View
    Display transaction history
    """
    model = MemberTransaction
    template_name = 'members/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        member = get_object_or_404(Member, user=self.request.user)
        return MemberTransaction.objects.filter(
            account__member=member
        ).order_by('-transaction_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = get_object_or_404(Member, user=self.request.user)
        
        # Get date range from request
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        
        if from_date and to_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                
                context['transactions'] = context['transactions'].filter(
                    transaction_date__date__range=[from_date_obj, to_date_obj]
                )
                context['from_date'] = from_date
                context['to_date'] = to_date
            except ValueError:
                pass
        
        context['member'] = member
        return context


class LoanApplicationView(LoginRequiredMixin, CreateView):
    """
    Loan Application View
    Submit loan applications
    """
    model = MemberLoan
    form_class = LoanApplicationForm
    template_name = 'members/loan_application.html'
    success_url = reverse_lazy('members:loan_success')
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.member = get_object_or_404(Member, user=self.request.user)
                loan.status = 'applied'
                loan.applied_date = timezone.now()
                loan.save()
                
                # Submit to CBS
                self.submit_to_cbs(loan)
                
                messages.success(
                    self.request,
                    _('ऋण आवेदन सफलतापूर्वक पेश गरियो।')
                )
                
                return redirect('members:loan_status', pk=loan.pk)
                
        except Exception as e:
            logger.error(f"Loan application error: {e}")
            messages.error(
                self.request,
                _('ऋण आवेदनमा समस्या भयो। कृपया पुनः प्रयास गर्नुहोस्।')
            )
            return self.form_invalid(form)
    
    def submit_to_cbs(self, loan):
        """Submit loan application to CBS"""
        try:
            cbs_client = CBSAPIClient()
            
            loan_data = {
                'member_id': loan.member.cbs_member_id,
                'loan_type': loan.loan_type,
                'loan_amount': str(loan.loan_amount),
                'purpose': loan.purpose,
                'tenure_months': loan.tenure_months
            }
            
            response = cbs_client.submit_loan_application(loan_data)
            
            if response.get('status') == 'success':
                loan.cbs_loan_id = response.get('loan_id')
                loan.cbs_sync_status = 'synced'
                loan.save()
                
        except Exception as e:
            logger.error(f"CBS loan submission error: {e}")


class LoanStatusView(LoginRequiredMixin, DetailView):
    """
    Loan Status View
    Check loan application status
    """
    model = MemberLoan
    template_name = 'members/loan_status.html'
    context_object_name = 'loan'
    
    def get_queryset(self):
        return MemberLoan.objects.filter(member__user=self.request.user)


class MemberNotificationsView(LoginRequiredMixin, ListView):
    """
    Member Notifications View
    Display member notifications
    """
    model = MemberNotification
    template_name = 'members/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        member = get_object_or_404(Member, user=self.request.user)
        return MemberNotification.objects.filter(
            member=member
        ).order_by('-created_at')


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    """
    Password Change View
    """
    template_name = 'members/password_change.html'
    
    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(
                request,
                _('पासवर्ड सफलतापूर्वक परिवर्तन गरियो।')
            )
            return redirect('members:member_profile')
        else:
            return render(request, self.template_name, {'form': form})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PasswordChangeForm(self.request.user)
        return context


class ContactSupportView(LoginRequiredMixin, TemplateView):
    """
    Contact Support View
    """
    template_name = 'members/contact_support.html'
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Send support email
            self.send_support_email(form.cleaned_data, request.user)
            
            messages.success(
                request,
                _('तपाईंको सन्देश सफलतापूर्वक पठाइयो।')
            )
            return redirect('members:member_dashboard')
        else:
            return render(request, self.template_name, {'form': form})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def send_support_email(self, data, user):
        """Send support email"""
        try:
            subject = f"Support Request: {data['subject']}"
            message = f"""
            Member: {user.get_full_name()} ({user.email})
            Priority: {data['priority']}
            
            Message:
            {data['message']}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"Support email sending failed: {e}")


# AJAX Views for dynamic content
def sync_cbs_data(request):
    """Sync CBS data for member"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        member = get_object_or_404(Member, user=request.user)
        sync_service = CBSSyncService()
        
        if member.cbs_member_id:
            result = sync_service.full_sync_member(member.cbs_member_id)
            
            return JsonResponse({
                'status': 'success',
                'message': 'CBS data synced successfully',
                'result': result
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'CBS member ID not found'
            })
            
    except Exception as e:
        logger.error(f"CBS sync error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        member = get_object_or_404(Member, user=request.user)
        notification = get_object_or_404(
            MemberNotification,
            id=notification_id,
            member=member
        )
        
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Notification mark read error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })