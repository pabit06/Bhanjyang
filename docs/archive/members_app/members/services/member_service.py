"""
Member Service

Handles core member business logic including registration, profile management,
and member lifecycle operations. This service abstracts complex member
operations from views and provides a clean interface for member management.
"""

import logging
from typing import Optional, Dict, Any, List
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from ..models import Member, MemberRegistration, Ward
from ..repositories import MemberRepository
from ..exceptions import MemberServiceException, ValidationException
from ..dto import MemberRegistrationDTO, MemberProfileDTO

logger = logging.getLogger('members.services')


class MemberService:
    """
    Service class for member-related business operations.
    
    This service handles:
    - Member registration workflow
    - Profile management
    - Member status updates
    - Data validation and business rules
    """
    
    def __init__(self):
        self.member_repository = MemberRepository()
    
    def register_member(self, registration_data: MemberRegistrationDTO) -> MemberRegistration:
        """
        Register a new member with location verification.
        
        Args:
            registration_data: MemberRegistrationDTO containing registration information
            
        Returns:
            MemberRegistration: Created registration instance
            
        Raises:
            ValidationException: If validation fails
            MemberServiceException: If registration fails
        """
        try:
            with transaction.atomic():
                # Validate ward exists and is active
                ward = self._validate_ward(registration_data.ward_id)
                
                # Create registration
                registration = MemberRegistration.objects.create(
                    first_name=registration_data.first_name,
                    last_name=registration_data.last_name,
                    middle_name=registration_data.middle_name or '',
                    email=registration_data.email,
                    phone=registration_data.phone,
                    permanent_address=registration_data.permanent_address,
                    ward=ward,
                    tole_name=registration_data.tole_name,
                    status='pending_location'
                )
                
                logger.info(f"Member registration created: {registration.id}")
                return registration
                
        except ValidationError as e:
            logger.error(f"Validation error in member registration: {e}")
            raise ValidationException(str(e))
        except Exception as e:
            logger.error(f"Error creating member registration: {e}")
            raise MemberServiceException(f"Failed to create member registration: {str(e)}")
    
    def approve_location_verification(self, registration_id: int, verified_by: User, notes: str = '') -> MemberRegistration:
        """
        Approve location verification for a member registration.
        
        Args:
            registration_id: ID of the registration to approve
            verified_by: User who verified the location
            notes: Optional verification notes
            
        Returns:
            MemberRegistration: Updated registration instance
        """
        try:
            with transaction.atomic():
                registration = self.member_repository.get_registration_by_id(registration_id)
                
                if registration.status != 'pending_location':
                    raise ValidationException("Registration is not in pending location status")
                
                registration.location_verified = True
                registration.verified_by = verified_by
                registration.verification_date = timezone.now()
                registration.verification_notes = notes
                registration.status = 'location_verified'
                registration.save()
                
                logger.info(f"Location verification approved for registration: {registration_id}")
                return registration
                
        except Exception as e:
            logger.error(f"Error approving location verification: {e}")
            raise MemberServiceException(f"Failed to approve location verification: {str(e)}")
    
    def create_member_from_registration(self, registration_id: int) -> Member:
        """
        Create an active member from an approved registration.
        
        Args:
            registration_id: ID of the approved registration
            
        Returns:
            Member: Created member instance
        """
        try:
            with transaction.atomic():
                registration = self.member_repository.get_registration_by_id(registration_id)
                
                if registration.status != 'kyc_approved':
                    raise ValidationException("Registration must be KYC approved to create member")
                
                # Create user account
                user = User.objects.create_user(
                    username=registration.email,
                    email=registration.email,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    is_active=True
                )
                
                # Create member profile
                member = Member.objects.create(
                    user=user,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    middle_name=registration.middle_name,
                    email=registration.email,
                    phone=registration.phone,
                    permanent_address=registration.permanent_address,
                    ward=registration.ward,
                    tole_name=registration.tole_name,
                    membership_date=timezone.now().date(),
                    membership_fee_paid=True,
                    membership_fee_amount=Decimal('1000.00'),  # Default membership fee
                    citizenship_number=registration.citizenship_number or '',
                    citizenship_issue_date=registration.citizenship_issue_date or timezone.now().date(),
                    citizenship_issue_district=registration.citizenship_issue_district or '',
                    father_name=registration.father_name or '',
                    mother_name=registration.mother_name or '',
                    occupation=registration.occupation or '',
                    is_active=True,
                    is_verified=True
                )
                
                # Update registration status
                registration.status = 'member_active'
                registration.save()
                
                logger.info(f"Member created from registration: {member.id}")
                return member
                
        except Exception as e:
            logger.error(f"Error creating member from registration: {e}")
            raise MemberServiceException(f"Failed to create member: {str(e)}")
    
    def update_member_profile(self, member_id: int, profile_data: MemberProfileDTO) -> Member:
        """
        Update member profile information.
        
        Args:
            member_id: ID of the member to update
            profile_data: MemberProfileDTO containing updated information
            
        Returns:
            Member: Updated member instance
        """
        try:
            member = self.member_repository.get_member_by_id(member_id)
            
            # Update member fields
            member.first_name = profile_data.first_name
            member.last_name = profile_data.last_name
            member.middle_name = profile_data.middle_name or ''
            member.phone = profile_data.phone
            member.alternate_phone = profile_data.alternate_phone or ''
            member.permanent_address = profile_data.permanent_address
            member.tole_name = profile_data.tole_name
            member.father_name = profile_data.father_name or ''
            member.mother_name = profile_data.mother_name or ''
            member.spouse_name = profile_data.spouse_name or ''
            member.occupation = profile_data.occupation or ''
            member.workplace = profile_data.workplace or ''
            member.monthly_income = profile_data.monthly_income
            
            if profile_data.profile_photo:
                member.profile_photo = profile_data.profile_photo
            
            member.save()
            
            logger.info(f"Member profile updated: {member_id}")
            return member
            
        except Exception as e:
            logger.error(f"Error updating member profile: {e}")
            raise MemberServiceException(f"Failed to update member profile: {str(e)}")
    
    def get_member_dashboard_data(self, member_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a member.
        
        Args:
            member_id: ID of the member
            
        Returns:
            Dict containing dashboard data
        """
        try:
            member = self.member_repository.get_member_with_accounts(member_id)
            
            # Get account summaries
            accounts = member.accounts.filter(is_active=True)
            total_balance = sum(account.balance for account in accounts)
            
            # Get recent transactions
            recent_transactions = self.member_repository.get_recent_transactions(member_id, limit=10)
            
            # Get active loans
            active_loans = member.loans.filter(status__in=['active', 'disbursed'])
            
            # Get notifications
            notifications = self.member_repository.get_unread_notifications(member_id, limit=5)
            
            return {
                'member': member,
                'accounts': accounts,
                'total_balance': total_balance,
                'recent_transactions': recent_transactions,
                'active_loans': active_loans,
                'notifications': notifications,
                'account_count': accounts.count(),
                'loan_count': active_loans.count(),
                'unread_notifications': notifications.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting member dashboard data: {e}")
            raise MemberServiceException(f"Failed to get dashboard data: {str(e)}")
    
    def deactivate_member(self, member_id: int, reason: str, deactivated_by: User) -> Member:
        """
        Deactivate a member account.
        
        Args:
            member_id: ID of the member to deactivate
            reason: Reason for deactivation
            deactivated_by: User who performed the deactivation
            
        Returns:
            Member: Updated member instance
        """
        try:
            with transaction.atomic():
                member = self.member_repository.get_member_by_id(member_id)
                
                member.is_active = False
                member.save()
                
                # Deactivate user account
                member.user.is_active = False
                member.user.save()
                
                logger.info(f"Member deactivated: {member_id} by {deactivated_by.username}")
                return member
                
        except Exception as e:
            logger.error(f"Error deactivating member: {e}")
            raise MemberServiceException(f"Failed to deactivate member: {str(e)}")
    
    def _validate_ward(self, ward_id: int) -> Ward:
        """Validate that ward exists and is active."""
        try:
            ward = Ward.objects.get(id=ward_id, is_active=True)
            return ward
        except Ward.DoesNotExist:
            raise ValidationException("Selected ward is not available")
