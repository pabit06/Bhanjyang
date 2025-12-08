"""
Member Repository

Handles data access operations for Member and MemberRegistration models.
This repository provides optimized queries and abstracts database
operations from the service layer.
"""

import logging
from typing import Optional, List, Dict, Any
from django.db.models import Q, Prefetch, Count, Sum
from django.contrib.auth.models import User
from django.utils import timezone

from ..models import Member, MemberRegistration, MemberAccount, MemberTransaction, MemberLoan, MemberNotification

logger = logging.getLogger('members.repositories')


class MemberRepository:
    """
    Repository class for member-related data operations.
    
    This repository handles:
    - Member queries with optimized joins
    - Registration data retrieval
    - Member statistics and analytics
    - Complex filtering and searching
    """
    
    def get_member_by_id(self, member_id: int) -> Member:
        """Get member by ID with related data."""
        try:
            return Member.objects.select_related(
                'user', 'ward'
            ).prefetch_related(
                'accounts', 'kyc_documents', 'loans'
            ).get(id=member_id)
        except Member.DoesNotExist:
            raise Member.DoesNotExist(f"Member with ID {member_id} not found")
    
    def get_member_by_user(self, user: User) -> Optional[Member]:
        """Get member by user instance."""
        try:
            return Member.objects.select_related(
                'user', 'ward'
            ).prefetch_related(
                'accounts', 'kyc_documents', 'loans'
            ).get(user=user)
        except Member.DoesNotExist:
            return None
    
    def get_member_with_accounts(self, member_id: int) -> Member:
        """Get member with all active accounts."""
        try:
            return Member.objects.select_related(
                'user', 'ward'
            ).prefetch_related(
                Prefetch(
                    'accounts',
                    queryset=MemberAccount.objects.filter(is_active=True).order_by('account_type')
                ),
                'kyc_documents',
                'loans'
            ).get(id=member_id)
        except Member.DoesNotExist:
            raise Member.DoesNotExist(f"Member with ID {member_id} not found")
    
    def get_registration_by_id(self, registration_id: int) -> MemberRegistration:
        """Get registration by ID."""
        try:
            return MemberRegistration.objects.select_related(
                'ward', 'verified_by'
            ).get(id=registration_id)
        except MemberRegistration.DoesNotExist:
            raise MemberRegistration.DoesNotExist(f"Registration with ID {registration_id} not found")
    
    def get_registrations_by_status(self, status: str, limit: int = 50) -> List[MemberRegistration]:
        """Get registrations by status."""
        return MemberRegistration.objects.filter(
            status=status
        ).select_related(
            'ward', 'verified_by'
        ).order_by('-created_at')[:limit]
    
    def get_pending_registrations(self, limit: int = 50) -> List[MemberRegistration]:
        """Get pending registrations."""
        return self.get_registrations_by_status('pending_location', limit)
    
    def get_kyc_pending_registrations(self, limit: int = 50) -> List[MemberRegistration]:
        """Get KYC pending registrations."""
        return self.get_registrations_by_status('kyc_pending', limit)
    
    def get_active_members(self, limit: int = 100) -> List[Member]:
        """Get active members with basic info."""
        return Member.objects.filter(
            is_active=True,
            is_verified=True
        ).select_related(
            'user', 'ward'
        ).order_by('-created_at')[:limit]
    
    def get_members_by_ward(self, ward_id: int) -> List[Member]:
        """Get members by ward."""
        return Member.objects.filter(
            ward_id=ward_id,
            is_active=True
        ).select_related(
            'user', 'ward'
        ).order_by('first_name', 'last_name')
    
    def search_members(self, query: str, limit: int = 50) -> List[Member]:
        """Search members by name, email, or phone."""
        return Member.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(citizenship_number__icontains=query)
        ).select_related(
            'user', 'ward'
        ).order_by('first_name', 'last_name')[:limit]
    
    def get_recent_transactions(self, member_id: int, limit: int = 10) -> List[MemberTransaction]:
        """Get recent transactions for a member."""
        return MemberTransaction.objects.filter(
            account__member_id=member_id
        ).select_related(
            'account'
        ).order_by('-transaction_date')[:limit]
    
    def get_unread_notifications(self, member_id: int, limit: int = 10) -> List[MemberNotification]:
        """Get unread notifications for a member."""
        return MemberNotification.objects.filter(
            member_id=member_id,
            is_read=False
        ).order_by('-created_at')[:limit]
    
    def get_member_statistics(self, member_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a member."""
        try:
            member = self.get_member_by_id(member_id)
            
            # Account statistics
            accounts = member.accounts.filter(is_active=True)
            total_balance = sum(account.balance for account in accounts)
            account_count = accounts.count()
            
            # Transaction statistics
            transactions = MemberTransaction.objects.filter(
                account__member=member
            )
            total_deposits = transactions.filter(
                transaction_type__in=['deposit', 'transfer_in', 'interest']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            total_withdrawals = transactions.filter(
                transaction_type__in=['withdrawal', 'transfer_out', 'fee']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Loan statistics
            loans = member.loans.all()
            active_loans = loans.filter(status__in=['active', 'disbursed'])
            total_loan_amount = sum(loan.loan_amount for loan in active_loans)
            
            # Notification statistics
            unread_notifications = MemberNotification.objects.filter(
                member=member,
                is_read=False
            ).count()
            
            return {
                'member': member,
                'total_balance': total_balance,
                'account_count': account_count,
                'total_deposits': total_deposits,
                'total_withdrawals': total_withdrawals,
                'active_loans_count': active_loans.count(),
                'total_loan_amount': total_loan_amount,
                'unread_notifications': unread_notifications,
                'membership_duration_days': (member.created_at.date() - member.membership_date).days if member.membership_date else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting member statistics: {e}")
            return {}
    
    def get_member_dashboard_data(self, member_id: int) -> Dict[str, Any]:
        """Get dashboard data for a member."""
        try:
            member = self.get_member_with_accounts(member_id)
            
            # Get recent transactions
            recent_transactions = self.get_recent_transactions(member_id, 10)
            
            # Get active loans
            active_loans = member.loans.filter(status__in=['active', 'disbursed'])
            
            # Get notifications
            notifications = self.get_unread_notifications(member_id, 5)
            
            # Calculate totals
            total_balance = sum(account.balance for account in member.accounts.filter(is_active=True))
            
            return {
                'member': member,
                'accounts': member.accounts.filter(is_active=True),
                'total_balance': total_balance,
                'recent_transactions': recent_transactions,
                'active_loans': active_loans,
                'notifications': notifications,
                'account_count': member.accounts.filter(is_active=True).count(),
                'loan_count': active_loans.count(),
                'unread_notifications': notifications.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting member dashboard data: {e}")
            return {}
    
    def get_registration_statistics(self) -> Dict[str, Any]:
        """Get registration statistics for admin dashboard."""
        try:
            total_registrations = MemberRegistration.objects.count()
            
            status_counts = {}
            for status, _ in MemberRegistration.STATUS_CHOICES:
                status_counts[status] = MemberRegistration.objects.filter(status=status).count()
            
            recent_registrations = MemberRegistration.objects.order_by('-created_at')[:10]
            
            return {
                'total_registrations': total_registrations,
                'status_counts': status_counts,
                'recent_registrations': recent_registrations
            }
            
        except Exception as e:
            logger.error(f"Error getting registration statistics: {e}")
            return {}
    
    def get_member_by_citizenship_number(self, citizenship_number: str) -> Optional[Member]:
        """Get member by citizenship number."""
        try:
            return Member.objects.select_related(
                'user', 'ward'
            ).get(citizenship_number=citizenship_number)
        except Member.DoesNotExist:
            return None
    
    def get_member_by_phone(self, phone: str) -> Optional[Member]:
        """Get member by phone number."""
        try:
            return Member.objects.select_related(
                'user', 'ward'
            ).get(phone=phone)
        except Member.DoesNotExist:
            return None
    
    def update_member_last_login(self, member: Member) -> None:
        """Update member's last login timestamp."""
        member.user.last_login = timezone.now()
        member.user.save()
        member.save()
