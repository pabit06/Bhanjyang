"""
KYC Repository

Handles data access operations for KYC-related models including
MemberRegistration and KYCDocument. This repository provides optimized
queries for KYC workflow operations.
"""

import logging
from typing import Optional, List, Dict, Any
from django.db.models import Q, Count
from django.utils import timezone

from ..models import MemberRegistration, KYCDocument, Member

logger = logging.getLogger('members.repositories')


class KYCRepository:
    """
    Repository class for KYC-related data operations.
    
    This repository handles:
    - Registration queries with optimized joins
    - KYC document management
    - Verification workflow data
    - Compliance and audit queries
    """
    
    def get_registration_by_id(self, registration_id: int) -> MemberRegistration:
        """Get registration by ID with related data."""
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
    
    def get_pending_location_verifications(self, limit: int = 50) -> List[MemberRegistration]:
        """Get registrations pending location verification."""
        return self.get_registrations_by_status('pending_location', limit)
    
    def get_kyc_pending_registrations(self, limit: int = 50) -> List[MemberRegistration]:
        """Get registrations pending KYC verification."""
        return self.get_registrations_by_status('kyc_pending', limit)
    
    def get_approved_registrations(self, limit: int = 50) -> List[MemberRegistration]:
        """Get approved registrations ready for member creation."""
        return self.get_registrations_by_status('kyc_approved', limit)
    
    def get_rejected_registrations(self, limit: int = 50) -> List[MemberRegistration]:
        """Get rejected registrations."""
        return self.get_registrations_by_status('rejected', limit)
    
    def search_registrations(self, query: str, limit: int = 50) -> List[MemberRegistration]:
        """Search registrations by name, email, phone, or citizenship number."""
        return MemberRegistration.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(citizenship_number__icontains=query)
        ).select_related(
            'ward', 'verified_by'
        ).order_by('-created_at')[:limit]
    
    def get_registrations_by_ward(self, ward_id: int, limit: int = 50) -> List[MemberRegistration]:
        """Get registrations by ward."""
        return MemberRegistration.objects.filter(
            ward_id=ward_id
        ).select_related(
            'ward', 'verified_by'
        ).order_by('-created_at')[:limit]
    
    def get_registrations_by_verifier(self, verifier_id: int, limit: int = 50) -> List[MemberRegistration]:
        """Get registrations verified by a specific user."""
        return MemberRegistration.objects.filter(
            verified_by_id=verifier_id
        ).select_related(
            'ward', 'verified_by'
        ).order_by('-verification_date')[:limit]
    
    def get_registration_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registration statistics."""
        try:
            total_registrations = MemberRegistration.objects.count()
            
            # Status breakdown
            status_counts = {}
            for status, _ in MemberRegistration.STATUS_CHOICES:
                status_counts[status] = MemberRegistration.objects.filter(status=status).count()
            
            # Ward breakdown
            ward_counts = MemberRegistration.objects.values(
                'ward__ward_number', 'ward__ward_name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Recent registrations
            recent_registrations = MemberRegistration.objects.order_by('-created_at')[:10]
            
            # Verification statistics
            verification_stats = MemberRegistration.objects.filter(
                verified_by__isnull=False
            ).values(
                'verified_by__username'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'total_registrations': total_registrations,
                'status_counts': status_counts,
                'ward_counts': list(ward_counts),
                'recent_registrations': recent_registrations,
                'verification_stats': list(verification_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting registration statistics: {e}")
            return {}
    
    def get_registration_timeline(self, registration_id: int) -> List[Dict[str, Any]]:
        """Get timeline of events for a registration."""
        try:
            registration = self.get_registration_by_id(registration_id)
            
            timeline = []
            
            # Registration created
            timeline.append({
                'date': registration.created_at,
                'event': 'Registration Created',
                'description': 'Member registration submitted',
                'status': 'completed'
            })
            
            # Location verification
            if registration.location_verified and registration.verification_date:
                timeline.append({
                    'date': registration.verification_date,
                    'event': 'Location Verified',
                    'description': f'Verified by {registration.verified_by.username if registration.verified_by else "System"}',
                    'status': 'completed'
                })
            
            # KYC submission
            if registration.status in ['kyc_pending', 'kyc_approved', 'member_active']:
                timeline.append({
                    'date': registration.updated_at,
                    'event': 'KYC Documents Submitted',
                    'description': 'KYC documents uploaded and submitted',
                    'status': 'completed'
                })
            
            # KYC approval/rejection
            if registration.status in ['kyc_approved', 'member_active']:
                timeline.append({
                    'date': registration.updated_at,
                    'event': 'KYC Approved',
                    'description': 'KYC verification completed successfully',
                    'status': 'completed'
                })
            elif registration.status == 'rejected':
                timeline.append({
                    'date': registration.updated_at,
                    'event': 'KYC Rejected',
                    'description': 'KYC verification failed',
                    'status': 'failed'
                })
            
            # Member creation
            if registration.status == 'member_active':
                timeline.append({
                    'date': registration.updated_at,
                    'event': 'Member Created',
                    'description': 'Active member account created',
                    'status': 'completed'
                })
            
            return sorted(timeline, key=lambda x: x['date'])
            
        except Exception as e:
            logger.error(f"Error getting registration timeline: {e}")
            return []
    
    def get_kyc_documents_by_registration(self, registration_id: int) -> List[Dict[str, Any]]:
        """Get KYC documents for a registration."""
        try:
            registration = self.get_registration_by_id(registration_id)
            
            documents = []
            
            if registration.citizenship_document:
                documents.append({
                    'type': 'citizenship',
                    'name': 'Citizenship Certificate',
                    'file': registration.citizenship_document,
                    'uploaded_at': registration.updated_at
                })
            
            if registration.address_proof:
                documents.append({
                    'type': 'address_proof',
                    'name': 'Address Proof',
                    'file': registration.address_proof,
                    'uploaded_at': registration.updated_at
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting KYC documents: {e}")
            return []
    
    def get_registration_by_email(self, email: str) -> Optional[MemberRegistration]:
        """Get registration by email address."""
        try:
            return MemberRegistration.objects.select_related(
                'ward', 'verified_by'
            ).get(email=email)
        except MemberRegistration.DoesNotExist:
            return None
    
    def get_registration_by_phone(self, phone: str) -> Optional[MemberRegistration]:
        """Get registration by phone number."""
        try:
            return MemberRegistration.objects.select_related(
                'ward', 'verified_by'
            ).get(phone=phone)
        except MemberRegistration.DoesNotExist:
            return None
    
    def get_registration_by_citizenship_number(self, citizenship_number: str) -> Optional[MemberRegistration]:
        """Get registration by citizenship number."""
        try:
            return MemberRegistration.objects.select_related(
                'ward', 'verified_by'
            ).get(citizenship_number=citizenship_number)
        except MemberRegistration.DoesNotExist:
            return None
    
    def get_registrations_requiring_attention(self, limit: int = 20) -> List[MemberRegistration]:
        """Get registrations that require admin attention."""
        # Get registrations that have been pending for more than 3 days
        cutoff_date = timezone.now() - timezone.timedelta(days=3)
        
        return MemberRegistration.objects.filter(
            Q(status='pending_location', created_at__lt=cutoff_date) |
            Q(status='kyc_pending', updated_at__lt=cutoff_date)
        ).select_related(
            'ward', 'verified_by'
        ).order_by('created_at')[:limit]
    
    def get_verification_performance_stats(self) -> Dict[str, Any]:
        """Get verification performance statistics."""
        try:
            # Average verification time
            verified_registrations = MemberRegistration.objects.filter(
                verification_date__isnull=False
            )
            
            verification_times = []
            for reg in verified_registrations:
                if reg.verification_date and reg.created_at:
                    time_diff = reg.verification_date - reg.created_at
                    verification_times.append(time_diff.total_seconds() / 3600)  # Convert to hours
            
            avg_verification_time = sum(verification_times) / len(verification_times) if verification_times else 0
            
            # Verification success rate
            total_verifications = MemberRegistration.objects.filter(
                verification_date__isnull=False
            ).count()
            
            successful_verifications = MemberRegistration.objects.filter(
                status__in=['kyc_approved', 'member_active']
            ).count()
            
            success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
            
            return {
                'average_verification_time_hours': avg_verification_time,
                'total_verifications': total_verifications,
                'successful_verifications': successful_verifications,
                'success_rate_percentage': success_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting verification performance stats: {e}")
            return {}
    
    def get_duplicate_registrations(self) -> List[Dict[str, Any]]:
        """Get potential duplicate registrations."""
        try:
            # Find registrations with same email, phone, or citizenship number
            duplicates = []
            
            # Email duplicates
            email_duplicates = MemberRegistration.objects.values('email').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            for dup in email_duplicates:
                registrations = MemberRegistration.objects.filter(
                    email=dup['email']
                ).select_related('ward')
                duplicates.append({
                    'type': 'email',
                    'value': dup['email'],
                    'count': dup['count'],
                    'registrations': list(registrations)
                })
            
            # Phone duplicates
            phone_duplicates = MemberRegistration.objects.values('phone').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            for dup in phone_duplicates:
                registrations = MemberRegistration.objects.filter(
                    phone=dup['phone']
                ).select_related('ward')
                duplicates.append({
                    'type': 'phone',
                    'value': dup['phone'],
                    'count': dup['count'],
                    'registrations': list(registrations)
                })
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Error getting duplicate registrations: {e}")
            return []
