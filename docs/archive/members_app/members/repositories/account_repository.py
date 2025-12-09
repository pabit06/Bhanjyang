"""
Account Repository

Handles data access operations for MemberAccount and MemberTransaction models.
This repository provides optimized queries for account-related operations.
"""

import logging
from typing import Optional, List, Dict, Any
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from decimal import Decimal

from ..models import MemberAccount, MemberTransaction, Member

logger = logging.getLogger('members.repositories')


class AccountRepository:
    """
    Repository class for account-related data operations.
    
    This repository handles:
    - Account queries with optimized joins
    - Transaction data retrieval
    - Account analytics and reporting
    - Complex filtering and searching
    """
    
    def get_account_by_id(self, account_id: int) -> MemberAccount:
        """Get account by ID with related data."""
        try:
            return MemberAccount.objects.select_related(
                'member', 'member__user', 'member__ward'
            ).get(id=account_id)
        except MemberAccount.DoesNotExist:
            raise MemberAccount.DoesNotExist(f"Account with ID {account_id} not found")
    
    def get_account_by_number(self, account_number: str) -> Optional[MemberAccount]:
        """Get account by account number."""
        try:
            return MemberAccount.objects.select_related(
                'member', 'member__user', 'member__ward'
            ).get(account_number=account_number)
        except MemberAccount.DoesNotExist:
            return None
    
    def get_member_accounts(self, member_id: int, active_only: bool = True) -> List[MemberAccount]:
        """Get all accounts for a member."""
        queryset = MemberAccount.objects.filter(member_id=member_id)
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.select_related(
            'member', 'member__user'
        ).order_by('account_type', 'account_number')
    
    def get_primary_account(self, member_id: int) -> Optional[MemberAccount]:
        """Get primary account for a member."""
        try:
            return MemberAccount.objects.filter(
                member_id=member_id,
                is_primary=True,
                is_active=True
            ).select_related(
                'member', 'member__user'
            ).first()
        except MemberAccount.DoesNotExist:
            return None
    
    def get_accounts_by_type(self, member_id: int, account_type: str) -> List[MemberAccount]:
        """Get accounts by type for a member."""
        return MemberAccount.objects.filter(
            member_id=member_id,
            account_type=account_type,
            is_active=True
        ).select_related(
            'member', 'member__user'
        ).order_by('account_number')
    
    def get_transactions_in_range(self, account: MemberAccount, from_date: timezone.datetime, 
                                to_date: timezone.datetime, limit: int = 100) -> List[MemberTransaction]:
        """Get transactions for an account within date range."""
        return MemberTransaction.objects.filter(
            account=account,
            transaction_date__date__range=[from_date.date(), to_date.date()]
        ).order_by('-transaction_date')[:limit]
    
    def get_recent_transactions_for_member(self, member: Member, limit: int = 10) -> List[MemberTransaction]:
        """Get recent transactions for all member accounts."""
        return MemberTransaction.objects.filter(
            account__member=member
        ).select_related(
            'account'
        ).order_by('-transaction_date')[:limit]
    
    def get_transactions_by_type(self, account: MemberAccount, transaction_type: str, 
                               limit: int = 50) -> List[MemberTransaction]:
        """Get transactions by type for an account."""
        return MemberTransaction.objects.filter(
            account=account,
            transaction_type=transaction_type
        ).order_by('-transaction_date')[:limit]
    
    def get_account_balance_history(self, account: MemberAccount, days: int = 30) -> List[Dict[str, Any]]:
        """Get account balance history for the last N days."""
        from django.db.models import F
        
        # Get daily balance snapshots
        transactions = MemberTransaction.objects.filter(
            account=account,
            transaction_date__gte=timezone.now() - timezone.timedelta(days=days)
        ).order_by('transaction_date')
        
        balance_history = []
        current_balance = account.balance
        
        for transaction in reversed(transactions):
            balance_history.append({
                'date': transaction.transaction_date.date(),
                'balance': current_balance,
                'transaction_type': transaction.transaction_type,
                'amount': transaction.amount
            })
            
            # Reverse calculate balance
            if transaction.transaction_type in ['deposit', 'transfer_in', 'interest']:
                current_balance -= transaction.amount
            elif transaction.transaction_type in ['withdrawal', 'transfer_out', 'fee']:
                current_balance += transaction.amount
        
        return list(reversed(balance_history))
    
    def get_account_statistics(self, account: MemberAccount) -> Dict[str, Any]:
        """Get comprehensive statistics for an account."""
        try:
            # Transaction counts by type
            transaction_counts = MemberTransaction.objects.filter(
                account=account
            ).values('transaction_type').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
            
            # Monthly transaction summary
            monthly_summary = MemberTransaction.objects.filter(
                account=account,
                transaction_date__gte=timezone.now() - timezone.timedelta(days=30)
            ).aggregate(
                total_deposits=Sum('amount', filter=Q(transaction_type__in=['deposit', 'transfer_in', 'interest'])),
                total_withdrawals=Sum('amount', filter=Q(transaction_type__in=['withdrawal', 'transfer_out', 'fee'])),
                transaction_count=Count('id')
            )
            
            # Average transaction amount
            avg_transaction = MemberTransaction.objects.filter(
                account=account
            ).aggregate(
                avg_amount=Avg('amount')
            )
            
            return {
                'account': account,
                'current_balance': account.balance,
                'transaction_counts': list(transaction_counts),
                'monthly_summary': monthly_summary,
                'average_transaction': avg_transaction['avg_amount'] or Decimal('0.00'),
                'account_age_days': (timezone.now().date() - account.created_at.date()).days
            }
            
        except Exception as e:
            logger.error(f"Error getting account statistics: {e}")
            return {}
    
    def get_member_account_summary(self, member_id: int) -> Dict[str, Any]:
        """Get account summary for a member."""
        try:
            accounts = self.get_member_accounts(member_id)
            
            total_balance = sum(account.balance for account in accounts)
            account_count = accounts.count()
            
            # Account types breakdown
            account_types = {}
            for account in accounts:
                account_type = account.get_account_type_display()
                if account_type not in account_types:
                    account_types[account_type] = {
                        'count': 0,
                        'total_balance': Decimal('0.00')
                    }
                account_types[account_type]['count'] += 1
                account_types[account_type]['total_balance'] += account.balance
            
            # Recent transactions
            recent_transactions = self.get_recent_transactions_for_member(
                Member.objects.get(id=member_id), limit=5
            )
            
            return {
                'total_balance': total_balance,
                'account_count': account_count,
                'account_types': account_types,
                'recent_transactions': recent_transactions,
                'primary_account': self.get_primary_account(member_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting member account summary: {e}")
            return {}
    
    def search_transactions(self, account: MemberAccount, query: str, limit: int = 50) -> List[MemberTransaction]:
        """Search transactions by description or reference number."""
        return MemberTransaction.objects.filter(
            account=account
        ).filter(
            Q(description__icontains=query) |
            Q(reference_number__icontains=query)
        ).order_by('-transaction_date')[:limit]
    
    def get_transaction_by_id(self, transaction_id: int) -> MemberTransaction:
        """Get transaction by ID."""
        try:
            return MemberTransaction.objects.select_related(
                'account', 'account__member'
            ).get(id=transaction_id)
        except MemberTransaction.DoesNotExist:
            raise MemberTransaction.DoesNotExist(f"Transaction with ID {transaction_id} not found")
    
    def get_accounts_with_low_balance(self, threshold: Decimal = Decimal('1000.00')) -> List[MemberAccount]:
        """Get accounts with balance below threshold."""
        return MemberAccount.objects.filter(
            balance__lt=threshold,
            is_active=True
        ).select_related(
            'member', 'member__user'
        ).order_by('balance')
    
    def get_accounts_by_interest_rate(self, min_rate: Decimal = Decimal('0.00')) -> List[MemberAccount]:
        """Get accounts with interest rate above minimum."""
        return MemberAccount.objects.filter(
            interest_rate__gte=min_rate,
            is_active=True
        ).select_related(
            'member', 'member__user'
        ).order_by('-interest_rate')
    
    def get_inactive_accounts(self, days_threshold: int = 90) -> List[MemberAccount]:
        """Get accounts with no transactions in the last N days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_threshold)
        
        return MemberAccount.objects.filter(
            is_active=True
        ).exclude(
            transactions__transaction_date__gte=cutoff_date
        ).select_related(
            'member', 'member__user'
        ).distinct()
    
    def get_account_performance_metrics(self, account: MemberAccount) -> Dict[str, Any]:
        """Get performance metrics for an account."""
        try:
            # Get transaction frequency
            total_transactions = MemberTransaction.objects.filter(account=account).count()
            account_age_days = (timezone.now().date() - account.created_at.date()).days
            
            if account_age_days > 0:
                transaction_frequency = total_transactions / account_age_days
            else:
                transaction_frequency = 0
            
            # Get balance growth rate
            first_transaction = MemberTransaction.objects.filter(
                account=account
            ).order_by('transaction_date').first()
            
            if first_transaction:
                balance_growth = account.balance - first_transaction.balance_after
                growth_rate = (balance_growth / first_transaction.balance_after * 100) if first_transaction.balance_after > 0 else 0
            else:
                growth_rate = 0
            
            return {
                'account': account,
                'total_transactions': total_transactions,
                'transaction_frequency': transaction_frequency,
                'balance_growth_rate': growth_rate,
                'account_age_days': account_age_days,
                'is_active': account.is_active,
                'is_primary': account.is_primary
            }
            
        except Exception as e:
            logger.error(f"Error getting account performance metrics: {e}")
            return {}
