from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, ServiceCategory, MemberRelief
)


def services_overview(request):
    """Main services overview page"""
    context = {
        'savings_accounts': SavingsAccount.objects.filter(is_active=True),
        'fixed_deposits': FixedDeposit.objects.filter(is_active=True),
        'loan_types': LoanType.objects.filter(is_active=True),
        'remittance_services': RemittanceService.objects.filter(is_active=True),
        'member_reliefs': MemberRelief.objects.filter(is_active=True),
        'service_categories': ServiceCategory.objects.filter(is_active=True),
        'featured_savings': SavingsAccount.objects.filter(is_active=True, is_featured=True)[:3],
        'featured_loans': LoanType.objects.filter(is_active=True, is_featured=True)[:3],
    }
    return render(request, 'services/services_overview.html', context)


class SavingsAccountsView(ListView):
    """Display all savings account types"""
    model = SavingsAccount
    template_name = 'services/savings_accounts.html'
    context_object_name = 'savings_accounts'
    
    def get_queryset(self):
        return SavingsAccount.objects.filter(is_active=True).order_by('-is_featured', 'interest_rate', 'account_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Savings Accounts'
        context['page_description'] = 'Choose from our range of savings accounts with competitive interest rates'
        context['featured_accounts'] = SavingsAccount.objects.filter(is_active=True, is_featured=True)
        return context


class FixedDepositsView(ListView):
    """Display all fixed deposit options"""
    model = FixedDeposit
    template_name = 'services/fixed_deposits.html'
    context_object_name = 'fixed_deposits'
    
    def get_queryset(self):
        return FixedDeposit.objects.filter(is_active=True).order_by('duration_months', 'payment_frequency')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fixed Deposits'
        context['page_description'] = 'Secure your future with our fixed deposit schemes'
        
        # Group by duration for better display
        deposits_by_duration = {}
        for deposit in context['fixed_deposits']:
            duration = deposit.get_duration_months_display()
            if duration not in deposits_by_duration:
                deposits_by_duration[duration] = []
            deposits_by_duration[duration].append(deposit)
        
        context['deposits_by_duration'] = deposits_by_duration
        return context


class LoanServicesView(ListView):
    """Display all loan services"""
    model = LoanType
    template_name = 'services/loan_services.html'
    context_object_name = 'loan_types'
    
    def get_queryset(self):
        return LoanType.objects.filter(is_active=True).order_by('-is_featured', 'loan_category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Loan Services'
        context['page_description'] = 'Flexible loan options for all your financial needs'
        context['featured_loans'] = LoanType.objects.filter(is_active=True, is_featured=True)
        return context


class RemittanceServicesView(ListView):
    """Display remittance services"""
    model = RemittanceService
    template_name = 'services/remittance_services.html'
    context_object_name = 'remittance_services'
    
    def get_queryset(self):
        return RemittanceService.objects.filter(is_active=True).order_by('service_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remittance Services'
        context['page_description'] = 'Fast and secure money transfer services'
        return context


class MemberReliefView(ListView):
    """Display member relief programs"""
    model = MemberRelief
    template_name = 'services/member_relief.html'
    context_object_name = 'member_reliefs'
    
    def get_queryset(self):
        return MemberRelief.objects.filter(is_active=True).order_by('relief_type', 'title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Member Relief Programs'
        context['page_description'] = 'Support and assistance programs for our valued members'
        
        # Group by relief type
        reliefs_by_type = {}
        for relief in context['member_reliefs']:
            relief_type = relief.get_relief_type_display()
            if relief_type not in reliefs_by_type:
                reliefs_by_type[relief_type] = []
            reliefs_by_type[relief_type].append(relief)
        
        context['reliefs_by_type'] = reliefs_by_type
        return context


def service_detail(request, service_type, service_id):
    """Generic service detail view"""
    context = {}
    
    if service_type == 'savings':
        service = SavingsAccount.objects.get(id=service_id, is_active=True)
        template = 'services/savings_detail.html'
    elif service_type == 'fixed_deposit':
        service = FixedDeposit.objects.get(id=service_id, is_active=True)
        template = 'services/fixed_deposit_detail.html'
    elif service_type == 'loan':
        service = LoanType.objects.get(id=service_id, is_active=True)
        template = 'services/loan_detail.html'
    elif service_type == 'remittance':
        service = RemittanceService.objects.get(id=service_id, is_active=True)
        template = 'services/remittance_detail.html'
    elif service_type == 'relief':
        service = MemberRelief.objects.get(id=service_id, is_active=True)
        template = 'services/relief_detail.html'
    else:
        return render(request, 'services/404.html', status=404)
    
    context['service'] = service
    context['service_type'] = service_type
    return render(request, template, context)
