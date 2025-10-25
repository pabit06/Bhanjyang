"""
Member URL Configuration
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import test_views

app_name = 'members'

urlpatterns = [
    # Test routes for template viewing (temporary)
    path('test/login/', test_views.test_member_login, name='test_login'),
    path('test/dashboard/', test_views.test_member_dashboard, name='test_dashboard'),
    path('test/profile/', test_views.test_member_profile, name='test_profile'),
    path('test/accounts/', test_views.test_member_accounts, name='test_accounts'),
    path('test/transactions/', test_views.test_member_transactions, name='test_transactions'),
    path('test/loan-application/', test_views.test_member_loan_application, name='test_loan_application'),
    path('test/loan-status/', test_views.test_member_loan_status, name='test_loan_status'),
    path('test/landing/', test_views.test_member_landing, name='test_landing'),
    path('test/password-reset-form/', test_views.test_password_reset, name='test_password_reset'),
    path('test/password-reset-confirm-form/', test_views.test_password_reset_confirm, name='test_password_reset_confirm'),
    
    # Registration Flow
    path('register/', views.MemberRegistrationView.as_view(), name='member_register'),
    path('registration-success/', views.RegistrationStatusView.as_view(), name='registration_success'),
    path('kyc/<int:pk>/', views.KYCDocumentUploadView.as_view(), name='kyc_upload'),
    path('kyc-success/', views.RegistrationStatusView.as_view(), name='kyc_success'),
    path('status/<int:pk>/', views.RegistrationStatusView.as_view(), name='registration_status'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='members/login.html',
        form_class=views.MemberLoginForm,
        redirect_authenticated_user=True,
        next_page='members:member_dashboard'
    ), name='member_login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='members:member_login'
    ), name='member_logout'),
    
    # Password Management
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='members/password_reset.html',
        email_template_name='members/password_reset_email.html',
        subject_template_name='members/password_reset_subject.txt',
        success_url='/members/password-reset-done/'
    ), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='members/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='members/password_reset_confirm.html',
        success_url='/members/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='members/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Member Dashboard & Profile
    path('dashboard/', views.MemberDashboardView.as_view(), name='member_dashboard'),
    path('profile/', views.MemberProfileView.as_view(), name='member_profile'),
    
    # Accounts & Transactions
    path('accounts/', views.MemberAccountsView.as_view(), name='member_accounts'),
    path('transactions/', views.MemberTransactionsView.as_view(), name='member_transactions'),
    
    # Loan Services
    path('loan-apply/', views.LoanApplicationView.as_view(), name='loan_application'),
    path('loan-status/<int:pk>/', views.LoanStatusView.as_view(), name='loan_status'),
    path('loan-success/', views.LoanStatusView.as_view(), name='loan_success'),
    
    # Notifications
    path('notifications/', views.MemberNotificationsView.as_view(), name='member_notifications'),
    
    # Support
    path('contact-support/', views.ContactSupportView.as_view(), name='contact_support'),
    
    # AJAX Endpoints
    path('ajax/sync-cbs/', views.sync_cbs_data, name='sync_cbs_data'),
    path('ajax/notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
