from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Main Service Pages
    path('', views.ServicesOverviewView.as_view(), name='overview'),
    path('savings/', views.SavingsAccountsView.as_view(), name='savings_list'),
    path('loans/', views.LoanServicesView.as_view(), name='loan_list'),
    path('fixed-deposits/', views.FixedDepositsView.as_view(), name='fixed_deposit_list'),
    path('remittance/', views.RemittanceServicesView.as_view(), name='remittance_list'),
    path('digital-services/', views.DigitalServicesView.as_view(), name='digital_list'),
    path('member-relief/', views.MemberReliefView.as_view(), name='member_relief_list'),

    # Detail Pages using Slugs
    path('savings/<slug:slug>/', views.SavingsDetailView.as_view(), name='savings_detail'),
    path('loans/<slug:slug>/', views.LoanDetailView.as_view(), name='loan_detail'),
    path('fixed-deposits/<int:pk>/', views.FixedDepositDetailView.as_view(), name='fixed_deposit_detail'),
    path('remittance/<slug:slug>/', views.RemittanceDetailView.as_view(), name='remittance_detail'),
    path('digital-services/<slug:slug>/', views.DigitalServiceDetailView.as_view(), name='digital_detail'),
    path('member-relief/<slug:slug>/', views.MemberReliefDetailView.as_view(), name='relief_detail'),

    # Shared/Utility Pages
    path('calculators/loan/', views.loan_calculator, name='loan_calculator'),
    path('calculators/savings/', views.savings_calculator, name='savings_calculator'),
    path('calculators/fixed-deposit/', views.fixed_deposit_calculator, name='fixed_deposit_calculator'),
    path('api/calculator/', views.calculator_api, name='calculator_api'),
    path('apply/', views.service_application, name='service_application'),
    path('compare/', views.service_comparison, name='service_comparison'),
    path('search/', views.service_search, name='service_search'),
]
