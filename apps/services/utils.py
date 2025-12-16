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



