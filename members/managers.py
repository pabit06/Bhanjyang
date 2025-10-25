"""
Enhanced Model Managers and QuerySets for Members App

This module provides custom managers and querysets that add
business logic and optimized queries to the Member models.
"""

from django.db import models
from django.db.models import Q, Prefetch, Count, Sum, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class MemberQuerySet(models.QuerySet):
    """Custom QuerySet for Member model with business logic methods."""
    
    def active(self):
        """Return only active members."""
        return self.filter(is_active=True, is_verified=True)
    
    def verified(self):
        """Return only verified members."""
        return self.filter(is_verified=True)
    
    def with_accounts(self):
        """Prefetch related accounts."""
        return self.prefetch_related(
            Prefetch(
                'accounts',
                queryset=MemberAccount.objects.filter(is_active=True)
            )
        )
    
    def with_loans(self):
        """Prefetch related loans."""
        return self.prefetch_related('loans')
    
    def with_kyc_documents(self):
        """Prefetch related KYC documents."""
        return self.prefetch_related('kyc_documents')
    
    def by_ward(self, ward_id):
        """Filter members by ward."""
        return self.filter(ward_id=ward_id)
    
    def by_membership_type(self, membership_type):
        """Filter members by membership type."""
        return self.filter(membership_type=membership_type)
    
    def with_cbs_sync(self):
        """Filter members with CBS sync."""
        return self.filter(cbs_member_id__isnull=False)
    
    def without_cbs_sync(self):
        """Filter members without CBS sync."""
        return self.filter(cbs_member_id__isnull=True)
    
    def recent_members(self, days=30):
        """Get members who joined in the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def with_balance_above(self, amount):
        """Get members with total balance above amount."""
        return self.annotate(
            total_balance=Sum('accounts__balance')
        ).filter(total_balance__gte=amount)
    
    def with_active_loans(self):
        """Get members with active loans."""
        return self.filter(loans__status__in=['active', 'disbursed']).distinct()
    
    def search(self, query):
        """Search members by name, email, phone, or citizenship number."""
        return self.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(citizenship_number__icontains=query)
        )


class MemberManager(models.Manager):
    """Custom Manager for Member model."""
    
    def get_queryset(self):
        return MemberQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def verified(self):
        return self.get_queryset().verified()
    
    def with_accounts(self):
        return self.get_queryset().with_accounts()
    
    def with_loans(self):
        return self.get_queryset().with_loans()
    
    def with_kyc_documents(self):
        return self.get_queryset().with_kyc_documents()
    
    def by_ward(self, ward_id):
        return self.get_queryset().by_ward(ward_id)
    
    def by_membership_type(self, membership_type):
        return self.get_queryset().by_membership_type(membership_type)
    
    def with_cbs_sync(self):
        return self.get_queryset().with_cbs_sync()
    
    def without_cbs_sync(self):
        return self.get_queryset().without_cbs_sync()
    
    def recent_members(self, days=30):
        return self.get_queryset().recent_members(days)
    
    def with_balance_above(self, amount):
        return self.get_queryset().with_balance_above(amount)
    
    def with_active_loans(self):
        return self.get_queryset().with_active_loans()
    
    def search(self, query):
        return self.get_queryset().search(query)
    
    def get_statistics(self):
        """Get comprehensive member statistics."""
        queryset = self.get_queryset()
        
        return {
            'total_members': queryset.count(),
            'active_members': queryset.active().count(),
            'verified_members': queryset.verified().count(),
            'recent_members': queryset.recent_members(30).count(),
            'members_with_cbs_sync': queryset.with_cbs_sync().count(),
            'members_without_cbs_sync': queryset.without_cbs_sync().count(),
            'members_with_active_loans': queryset.with_active_loans().count(),
        }


class MemberRegistrationQuerySet(models.QuerySet):
    """Custom QuerySet for MemberRegistration model."""
    
    def pending_location(self):
        """Return registrations pending location verification."""
        return self.filter(status='pending_location')
    
    def location_verified(self):
        """Return registrations with verified location."""
        return self.filter(status='location_verified')
    
    def kyc_pending(self):
        """Return registrations pending KYC verification."""
        return self.filter(status='kyc_pending')
    
    def kyc_approved(self):
        """Return approved registrations."""
        return self.filter(status='kyc_approved')
    
    def rejected(self):
        """Return rejected registrations."""
        return self.filter(status='rejected')
    
    def by_status(self, status):
        """Filter by registration status."""
        return self.filter(status=status)
    
    def by_ward(self, ward_id):
        """Filter by ward."""
        return self.filter(ward_id=ward_id)
    
    def by_verifier(self, verifier_id):
        """Filter by verifier."""
        return self.filter(verified_by_id=verifier_id)
    
    def recent(self, days=30):
        """Get recent registrations."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def requiring_attention(self, days=3):
        """Get registrations requiring admin attention."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            Q(status='pending_location', created_at__lt=cutoff_date) |
            Q(status='kyc_pending', updated_at__lt=cutoff_date)
        )
    
    def with_documents(self):
        """Filter registrations with uploaded documents."""
        return self.filter(
            Q(citizenship_document__isnull=False) |
            Q(address_proof__isnull=False)
        )
    
    def search(self, query):
        """Search registrations by name, email, phone, or citizenship number."""
        return self.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(citizenship_number__icontains=query)
        )


class MemberRegistrationManager(models.Manager):
    """Custom Manager for MemberRegistration model."""
    
    def get_queryset(self):
        return MemberRegistrationQuerySet(self.model, using=self._db)
    
    def pending_location(self):
        return self.get_queryset().pending_location()
    
    def location_verified(self):
        return self.get_queryset().location_verified()
    
    def kyc_pending(self):
        return self.get_queryset().kyc_pending()
    
    def kyc_approved(self):
        return self.get_queryset().kyc_approved()
    
    def rejected(self):
        return self.get_queryset().rejected()
    
    def by_status(self, status):
        return self.get_queryset().by_status(status)
    
    def by_ward(self, ward_id):
        return self.get_queryset().by_ward(ward_id)
    
    def by_verifier(self, verifier_id):
        return self.get_queryset().by_verifier(verifier_id)
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)
    
    def requiring_attention(self, days=3):
        return self.get_queryset().requiring_attention(days)
    
    def with_documents(self):
        return self.get_queryset().with_documents()
    
    def search(self, query):
        return self.get_queryset().search(query)
    
    def get_statistics(self):
        """Get comprehensive registration statistics."""
        queryset = self.get_queryset()
        
        return {
            'total_registrations': queryset.count(),
            'pending_location': queryset.pending_location().count(),
            'location_verified': queryset.location_verified().count(),
            'kyc_pending': queryset.kyc_pending().count(),
            'kyc_approved': queryset.kyc_approved().count(),
            'rejected': queryset.rejected().count(),
            'requiring_attention': queryset.requiring_attention().count(),
            'recent_registrations': queryset.recent(30).count(),
        }


class MemberAccountQuerySet(models.QuerySet):
    """Custom QuerySet for MemberAccount model."""
    
    def active(self):
        """Return only active accounts."""
        return self.filter(is_active=True)
    
    def primary(self):
        """Return primary accounts."""
        return self.filter(is_primary=True, is_active=True)
    
    def by_type(self, account_type):
        """Filter by account type."""
        return self.filter(account_type=account_type)
    
    def by_member(self, member_id):
        """Filter by member."""
        return self.filter(member_id=member_id)
    
    def with_balance_above(self, amount):
        """Filter accounts with balance above amount."""
        return self.filter(balance__gte=amount)
    
    def with_balance_below(self, amount):
        """Filter accounts with balance below amount."""
        return self.filter(balance__lt=amount)
    
    def with_cbs_sync(self):
        """Filter accounts with CBS sync."""
        return self.filter(cbs_account_id__isnull=False)
    
    def without_cbs_sync(self):
        """Filter accounts without CBS sync."""
        return self.filter(cbs_account_id__isnull=True)
    
    def recent(self, days=30):
        """Get recently created accounts."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def inactive_recent(self, days=90):
        """Get accounts with no recent transactions."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            is_active=True
        ).exclude(
            transactions__transaction_date__gte=cutoff_date
        ).distinct()
    
    def with_interest_rate_above(self, rate):
        """Filter accounts with interest rate above rate."""
        return self.filter(interest_rate__gte=rate)
    
    def search(self, query):
        """Search accounts by account number or member name."""
        return self.filter(
            Q(account_number__icontains=query) |
            Q(account_name__icontains=query) |
            Q(member__first_name__icontains=query) |
            Q(member__last_name__icontains=query)
        )


class MemberAccountManager(models.Manager):
    """Custom Manager for MemberAccount model."""
    
    def get_queryset(self):
        return MemberAccountQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def primary(self):
        return self.get_queryset().primary()
    
    def by_type(self, account_type):
        return self.get_queryset().by_type(account_type)
    
    def by_member(self, member_id):
        return self.get_queryset().by_member(member_id)
    
    def with_balance_above(self, amount):
        return self.get_queryset().with_balance_above(amount)
    
    def with_balance_below(self, amount):
        return self.get_queryset().with_balance_below(amount)
    
    def with_cbs_sync(self):
        return self.get_queryset().with_cbs_sync()
    
    def without_cbs_sync(self):
        return self.get_queryset().without_cbs_sync()
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)
    
    def inactive_recent(self, days=90):
        return self.get_queryset().inactive_recent(days)
    
    def with_interest_rate_above(self, rate):
        return self.get_queryset().with_interest_rate_above(rate)
    
    def search(self, query):
        return self.get_queryset().search(query)
    
    def get_statistics(self):
        """Get comprehensive account statistics."""
        queryset = self.get_queryset()
        
        return {
            'total_accounts': queryset.count(),
            'active_accounts': queryset.active().count(),
            'primary_accounts': queryset.primary().count(),
            'accounts_with_cbs_sync': queryset.with_cbs_sync().count(),
            'accounts_without_cbs_sync': queryset.without_cbs_sync().count(),
            'recent_accounts': queryset.recent(30).count(),
            'inactive_recent': queryset.inactive_recent(90).count(),
        }


class MemberTransactionQuerySet(models.QuerySet):
    """Custom QuerySet for MemberTransaction model."""
    
    def by_account(self, account_id):
        """Filter by account."""
        return self.filter(account_id=account_id)
    
    def by_type(self, transaction_type):
        """Filter by transaction type."""
        return self.filter(transaction_type=transaction_type)
    
    def deposits(self):
        """Filter deposit transactions."""
        return self.filter(transaction_type__in=['deposit', 'transfer_in', 'interest'])
    
    def withdrawals(self):
        """Filter withdrawal transactions."""
        return self.filter(transaction_type__in=['withdrawal', 'transfer_out', 'fee'])
    
    def transfers(self):
        """Filter transfer transactions."""
        return self.filter(transaction_type__in=['transfer_in', 'transfer_out'])
    
    def recent(self, days=30):
        """Get recent transactions."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(transaction_date__gte=cutoff_date)
    
    def by_date_range(self, start_date, end_date):
        """Filter by date range."""
        return self.filter(
            transaction_date__date__range=[start_date, end_date]
        )
    
    def by_amount_above(self, amount):
        """Filter transactions above amount."""
        return self.filter(amount__gte=amount)
    
    def by_amount_below(self, amount):
        """Filter transactions below amount."""
        return self.filter(amount__lt=amount)
    
    def with_cbs_sync(self):
        """Filter transactions with CBS sync."""
        return self.filter(is_cbs_synced=True)
    
    def without_cbs_sync(self):
        """Filter transactions without CBS sync."""
        return self.filter(is_cbs_synced=False)
    
    def search(self, query):
        """Search transactions by description or reference number."""
        return self.filter(
            Q(description__icontains=query) |
            Q(reference_number__icontains=query)
        )


class MemberTransactionManager(models.Manager):
    """Custom Manager for MemberTransaction model."""
    
    def get_queryset(self):
        return MemberTransactionQuerySet(self.model, using=self._db)
    
    def by_account(self, account_id):
        return self.get_queryset().by_account(account_id)
    
    def by_type(self, transaction_type):
        return self.get_queryset().by_type(transaction_type)
    
    def deposits(self):
        return self.get_queryset().deposits()
    
    def withdrawals(self):
        return self.get_queryset().withdrawals()
    
    def transfers(self):
        return self.get_queryset().transfers()
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)
    
    def by_date_range(self, start_date, end_date):
        return self.get_queryset().by_date_range(start_date, end_date)
    
    def by_amount_above(self, amount):
        return self.get_queryset().by_amount_above(amount)
    
    def by_amount_below(self, amount):
        return self.get_queryset().by_amount_below(amount)
    
    def with_cbs_sync(self):
        return self.get_queryset().with_cbs_sync()
    
    def without_cbs_sync(self):
        return self.get_queryset().without_cbs_sync()
    
    def search(self, query):
        return self.get_queryset().search(query)
    
    def get_statistics(self):
        """Get comprehensive transaction statistics."""
        queryset = self.get_queryset()
        
        return {
            'total_transactions': queryset.count(),
            'total_deposits': queryset.deposits().aggregate(total=Sum('amount'))['total'] or 0,
            'total_withdrawals': queryset.withdrawals().aggregate(total=Sum('amount'))['total'] or 0,
            'recent_transactions': queryset.recent(30).count(),
            'transactions_with_cbs_sync': queryset.with_cbs_sync().count(),
            'transactions_without_cbs_sync': queryset.without_cbs_sync().count(),
        }
