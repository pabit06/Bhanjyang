import math
from decimal import Decimal
from typing import Dict, Any
from django.utils.translation import gettext_lazy as _


class FinancialCalculator:
    """Utility class for financial calculations"""
    
    @staticmethod
    def calculate_loan_emi(principal: Decimal, annual_rate: Decimal, tenure_months: int, 
                          payment_frequency: str = 'monthly') -> Dict[str, Any]:
        """
        Calculate EMI for loans
        
        Args:
            principal: Loan amount
            annual_rate: Annual interest rate (as percentage)
            tenure_months: Loan tenure in months
            payment_frequency: 'monthly' or 'quarterly'
        
        Returns:
            Dictionary with EMI calculation results
        """
        if payment_frequency == 'quarterly':
            # Convert to quarterly payments
            tenure_periods = tenure_months // 3
            rate_per_period = annual_rate / 400  # Quarterly rate
        else:
            tenure_periods = tenure_months
            rate_per_period = annual_rate / 1200  # Monthly rate
        
        if rate_per_period == 0:
            emi = principal / tenure_periods
        else:
            emi = principal * rate_per_period * ((1 + rate_per_period) ** tenure_periods) / \
                  (((1 + rate_per_period) ** tenure_periods) - 1)
        
        total_amount = emi * tenure_periods
        total_interest = total_amount - principal
        
        return {
            'emi': round(emi, 2),
            'total_amount': round(total_amount, 2),
            'total_interest': round(total_interest, 2),
            'principal': principal,
            'tenure_periods': tenure_periods,
            'rate_per_period': rate_per_period * 100,
            'payment_frequency': payment_frequency
        }
    
    @staticmethod
    def calculate_savings_maturity(monthly_deposit: Decimal, annual_rate: Decimal, 
                                 tenure_years: int) -> Dict[str, Any]:
        """
        Calculate savings maturity amount
        
        Args:
            monthly_deposit: Monthly deposit amount
            annual_rate: Annual interest rate (as percentage)
            tenure_years: Savings tenure in years
        
        Returns:
            Dictionary with savings calculation results
        """
        monthly_rate = annual_rate / 1200
        total_months = tenure_years * 12
        total_deposits = monthly_deposit * total_months
        
        if monthly_rate == 0:
            maturity_amount = total_deposits
        else:
            maturity_amount = monthly_deposit * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
        
        interest_earned = maturity_amount - total_deposits
        
        return {
            'maturity_amount': round(maturity_amount, 2),
            'total_deposits': round(total_deposits, 2),
            'interest_earned': round(interest_earned, 2),
            'monthly_deposit': monthly_deposit,
            'tenure_years': tenure_years,
            'annual_rate': annual_rate
        }
    
    @staticmethod
    def calculate_fixed_deposit_maturity(principal: Decimal, annual_rate: Decimal, 
                                       tenure_months: int, payment_frequency: str) -> Dict[str, Any]:
        """
        Calculate fixed deposit maturity amount
        
        Args:
            principal: Deposit amount
            annual_rate: Annual interest rate (as percentage)
            tenure_months: Deposit tenure in months
            payment_frequency: 'monthly', 'quarterly', or 'lump_sum'
        
        Returns:
            Dictionary with FD calculation results
        """
        monthly_rate = annual_rate / 1200
        
        if payment_frequency == 'lump_sum':
            # Compound interest calculation
            maturity_amount = principal * ((1 + monthly_rate) ** tenure_months)
        elif payment_frequency == 'quarterly':
            # Quarterly interest payments
            quarterly_rate = annual_rate / 400
            quarters = tenure_months // 3
            quarterly_interest = principal * quarterly_rate
            total_interest = quarterly_interest * quarters
            maturity_amount = principal + total_interest
        else:  # monthly
            # Monthly interest payments
            monthly_interest = principal * monthly_rate
            total_interest = monthly_interest * tenure_months
            maturity_amount = principal + total_interest
        
        interest_earned = maturity_amount - principal
        
        return {
            'maturity_amount': round(maturity_amount, 2),
            'principal': principal,
            'interest_earned': round(interest_earned, 2),
            'tenure_months': tenure_months,
            'annual_rate': annual_rate,
            'payment_frequency': payment_frequency
        }


class ServiceRecommendationEngine:
    """Service recommendation engine based on user profile"""
    
    @staticmethod
    def get_recommendations(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get service recommendations based on user profile
        
        Args:
            user_profile: Dictionary containing user information
        
        Returns:
            Dictionary with recommended services and reasoning
        """
        age = user_profile.get('age', 30)
        income = user_profile.get('monthly_income', 50000)
        goals = user_profile.get('goals', [])
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        
        recommendations = {
            'savings_accounts': [],
            'loans': [],
            'fixed_deposits': [],
            'reasoning': []
        }
        
        # Age-based recommendations
        if age < 25:
            recommendations['reasoning'].append("Young professionals should focus on building emergency funds and starting long-term savings.")
            recommendations['savings_accounts'].extend(['general', 'monthly'])
        elif age < 40:
            recommendations['reasoning'].append("Prime earning years - consider growth-oriented savings and investment options.")
            recommendations['savings_accounts'].extend(['general', 'monthly'])
            recommendations['fixed_deposits'].extend(['12_months', '24_months'])
        elif age < 60:
            recommendations['reasoning'].append("Pre-retirement phase - focus on stable returns and capital preservation.")
            recommendations['savings_accounts'].extend(['senior_citizen'])
            recommendations['fixed_deposits'].extend(['12_months', '36_months'])
        else:
            recommendations['reasoning'].append("Retirement phase - prioritize income generation and capital preservation.")
            recommendations['savings_accounts'].extend(['senior_citizen'])
            recommendations['fixed_deposits'].extend(['12_months'])
        
        # Income-based recommendations
        if income < 30000:
            recommendations['reasoning'].append("Lower income - focus on basic savings and emergency funds.")
            recommendations['savings_accounts'] = ['general', 'daily']
        elif income < 100000:
            recommendations['reasoning'].append("Moderate income - consider diversified savings and medium-term deposits.")
            recommendations['fixed_deposits'].extend(['6_months', '12_months'])
        else:
            recommendations['reasoning'].append("Higher income - explore premium savings and long-term investment options.")
            recommendations['savings_accounts'].extend(['institutional'])
            recommendations['fixed_deposits'].extend(['24_months', '36_months'])
        
        # Goal-based recommendations
        if 'house_purchase' in goals:
            recommendations['reasoning'].append("House purchase goal - consider long-term savings and home loans.")
            recommendations['savings_accounts'].extend(['monthly'])
            recommendations['loans'].extend(['house_construction', 'land_purchase'])
        
        if 'education' in goals:
            recommendations['reasoning'].append("Education goal - consider education loans and child savings.")
            recommendations['savings_accounts'].extend(['child'])
            recommendations['loans'].extend(['education'])
        
        if 'business' in goals:
            recommendations['reasoning'].append("Business goal - consider business loans and institutional savings.")
            recommendations['savings_accounts'].extend(['institutional'])
            recommendations['loans'].extend(['business'])
        
        if 'vehicle' in goals:
            recommendations['reasoning'].append("Vehicle purchase goal - consider vehicle loans.")
            recommendations['loans'].extend(['vehicle'])
        
        # Risk tolerance adjustments
        if risk_tolerance == 'conservative':
            recommendations['reasoning'].append("Conservative approach - focus on guaranteed returns.")
            recommendations['fixed_deposits'] = ['12_months', '24_months']
        elif risk_tolerance == 'aggressive':
            recommendations['reasoning'].append("Aggressive approach - consider higher-yield options.")
            recommendations['savings_accounts'].extend(['monthly'])
            recommendations['fixed_deposits'].extend(['36_months'])
        
        return recommendations


class ServiceComparison:
    """Service comparison utility"""
    
    @staticmethod
    def compare_savings_accounts(account_ids: list) -> Dict[str, Any]:
        """Compare multiple savings accounts"""
        from .models import SavingsAccount
        
        accounts = SavingsAccount.objects.filter(id__in=account_ids, is_active=True)
        comparison_data = []
        
        for account in accounts:
            comparison_data.append({
                'id': account.id,
                'name': account.english_name,
                'nepali_name': account.nepali_name,
                'interest_rate': float(account.interest_rate),
                'minimum_balance': float(account.minimum_balance) if account.minimum_balance else 0,
                'features': account.features.split('\n') if account.features else [],
                'description': account.description,
                'is_featured': account.is_featured,
                'icon': account.icon,
                'color': account.color
            })
        
        return {
            'accounts': comparison_data,
            'best_interest_rate': max([acc['interest_rate'] for acc in comparison_data]),
            'lowest_minimum_balance': min([acc['minimum_balance'] for acc in comparison_data]),
            'featured_accounts': [acc for acc in comparison_data if acc['is_featured']]
        }
    
    @staticmethod
    def compare_loans(loan_ids: list) -> Dict[str, Any]:
        """Compare multiple loan types"""
        from .models import LoanType
        
        loans = LoanType.objects.filter(id__in=loan_ids, is_active=True)
        comparison_data = []
        
        for loan in loans:
            comparison_data.append({
                'id': loan.id,
                'name': loan.english_name,
                'nepali_name': loan.nepali_name,
                'monthly_interest_rate': float(loan.monthly_interest_rate),
                'monthly_installment_rate': float(loan.monthly_installment_rate),
                'minimum_amount': float(loan.minimum_amount) if loan.minimum_amount else 0,
                'maximum_amount': float(loan.maximum_amount) if loan.maximum_amount else 0,
                'max_tenure_years': loan.max_tenure_years,
                'requirements': loan.requirements.split('\n') if loan.requirements else [],
                'benefits': loan.benefits.split('\n') if loan.benefits else [],
                'is_featured': loan.is_featured,
                'icon': loan.icon,
                'color': loan.color
            })
        
        return {
            'loans': comparison_data,
            'lowest_interest_rate': min([loan['monthly_interest_rate'] for loan in comparison_data]),
            'highest_maximum_amount': max([loan['maximum_amount'] for loan in comparison_data]),
            'featured_loans': [loan for loan in comparison_data if loan['is_featured']]
        }
    
    @staticmethod
    def compare_fixed_deposits(deposit_ids: list) -> Dict[str, Any]:
        """Compare multiple fixed deposits"""
        from .models import FixedDeposit
        
        deposits = FixedDeposit.objects.filter(id__in=deposit_ids, is_active=True)
        comparison_data = []
        
        for deposit in deposits:
            comparison_data.append({
                'id': deposit.id,
                'duration_months': deposit.duration_months,
                'duration_display': deposit.get_duration_months_display(),
                'payment_frequency': deposit.payment_frequency,
                'payment_frequency_display': deposit.get_payment_frequency_display(),
                'interest_rate': float(deposit.interest_rate),
                'minimum_amount': float(deposit.minimum_amount) if deposit.minimum_amount else 0,
                'maximum_amount': float(deposit.maximum_amount) if deposit.maximum_amount else 0,
                'benefits': deposit.benefits.split('\n') if deposit.benefits else [],
                'description': deposit.description
            })
        
        return {
            'deposits': comparison_data,
            'highest_interest_rate': max([dep['interest_rate'] for dep in comparison_data]),
            'shortest_duration': min([dep['duration_months'] for dep in comparison_data]),
            'longest_duration': max([dep['duration_months'] for dep in comparison_data])
        }
