from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Main services overview
    path('', views.services_overview, name='overview'),
    
    # Savings accounts
    path('savings/', views.SavingsAccountsView.as_view(), name='savings'),
    path('savings/<int:service_id>/', views.service_detail, {'service_type': 'savings'}, name='savings_detail'),
    
    # Fixed deposits
    path('fixed-deposits/', views.FixedDepositsView.as_view(), name='fixed_deposits'),
    path('fixed-deposits/<int:service_id>/', views.service_detail, {'service_type': 'fixed_deposit'}, name='fixed_deposit_detail'),
    
    # Loan services
    path('loans/', views.LoanServicesView.as_view(), name='loans'),
    path('loans/<int:service_id>/', views.service_detail, {'service_type': 'loan'}, name='loan_detail'),
    
    # Remittance services
    path('remittance/', views.RemittanceServicesView.as_view(), name='remittance'),
    path('remittance/<int:service_id>/', views.service_detail, {'service_type': 'remittance'}, name='remittance_detail'),
    
    # Member relief programs
    path('member-relief/', views.MemberReliefView.as_view(), name='member_relief'),
    path('member-relief/<int:service_id>/', views.service_detail, {'service_type': 'relief'}, name='relief_detail'),
]
