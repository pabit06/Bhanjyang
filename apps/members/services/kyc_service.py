"""
KYC Service

Handles Know Your Customer (KYC) workflow including document validation,
verification processes, and compliance checks. This service manages the
complete KYC lifecycle from document upload to approval.
"""

import logging
import hashlib
from typing import Optional, Dict, Any, List
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction

from ..models import MemberRegistration, KYCDocument, Member
from ..repositories import KYCRepository
from ..exceptions import KYCServiceException, ValidationException
from ..dto import KYCDocumentDTO, KYCVerificationDTO

logger = logging.getLogger('members.services')


class KYCService:
    """
    Service class for KYC-related operations.
    
    This service handles:
    - Document upload and validation
    - KYC verification workflow
    - Compliance checks
    - Document security and integrity
    """
    
    def __init__(self):
        self.kyc_repository = KYCRepository()
    
    def upload_kyc_documents(self, registration_id: int, document_data: KYCDocumentDTO) -> MemberRegistration:
        """
        Upload KYC documents for a member registration.
        
        Args:
            registration_id: ID of the registration
            document_data: KYCDocumentDTO containing document information
            
        Returns:
            MemberRegistration: Updated registration instance
        """
        try:
            with transaction.atomic():
                registration = self.kyc_repository.get_registration_by_id(registration_id)
                
                if registration.status != 'location_verified':
                    raise ValidationException("Location must be verified before KYC upload")
                
                # Validate documents
                self._validate_documents(document_data)
                
                # Update registration with KYC information
                registration.citizenship_number = document_data.citizenship_number
                registration.citizenship_issue_date = document_data.citizenship_issue_date
                registration.citizenship_issue_district = document_data.citizenship_issue_district
                registration.father_name = document_data.father_name
                registration.mother_name = document_data.mother_name
                registration.spouse_name = document_data.spouse_name
                registration.occupation = document_data.occupation
                registration.workplace = document_data.workplace
                registration.monthly_income = document_data.monthly_income
                
                # Save documents
                if document_data.citizenship_document:
                    registration.citizenship_document = document_data.citizenship_document
                if document_data.address_proof:
                    registration.address_proof = document_data.address_proof
                
                registration.status = 'kyc_pending'
                registration.save()
                
                logger.info(f"KYC documents uploaded for registration: {registration_id}")
                return registration
                
        except ValidationError as e:
            logger.error(f"Validation error in KYC upload: {e}")
            raise ValidationException(str(e))
        except Exception as e:
            logger.error(f"Error uploading KYC documents: {e}")
            raise KYCServiceException(f"Failed to upload KYC documents: {str(e)}")
    
    def verify_kyc_documents(self, registration_id: int, verification_data: KYCVerificationDTO) -> MemberRegistration:
        """
        Verify KYC documents and approve/reject registration.
        
        Args:
            registration_id: ID of the registration
            verification_data: KYCVerificationDTO containing verification information
            
        Returns:
            MemberRegistration: Updated registration instance
        """
        try:
            with transaction.atomic():
                registration = self.kyc_repository.get_registration_by_id(registration_id)
                
                if registration.status != 'kyc_pending':
                    raise ValidationException("Registration is not in KYC pending status")
                
                # Perform verification checks
                verification_result = self._perform_verification_checks(registration, verification_data)
                
                if verification_result['approved']:
                    registration.status = 'kyc_approved'
                    logger.info(f"KYC approved for registration: {registration_id}")
                else:
                    registration.status = 'rejected'
                    logger.info(f"KYC rejected for registration: {registration_id}")
                
                registration.save()
                
                return registration
                
        except Exception as e:
            logger.error(f"Error verifying KYC documents: {e}")
            raise KYCServiceException(f"Failed to verify KYC documents: {str(e)}")
    
    def get_kyc_status(self, registration_id: int) -> Dict[str, Any]:
        """
        Get KYC status and document information for a registration.
        
        Args:
            registration_id: ID of the registration
            
        Returns:
            Dict containing KYC status information
        """
        try:
            registration = self.kyc_repository.get_registration_by_id(registration_id)
            
            return {
                'status': registration.status,
                'citizenship_number': registration.citizenship_number,
                'citizenship_issue_date': registration.citizenship_issue_date,
                'citizenship_issue_district': registration.citizenship_issue_district,
                'father_name': registration.father_name,
                'mother_name': registration.mother_name,
                'spouse_name': registration.spouse_name,
                'occupation': registration.occupation,
                'workplace': registration.workplace,
                'monthly_income': registration.monthly_income,
                'has_citizenship_document': bool(registration.citizenship_document),
                'has_address_proof': bool(registration.address_proof),
                'verification_notes': registration.verification_notes,
                'verified_by': registration.verified_by,
                'verification_date': registration.verification_date
            }
            
        except Exception as e:
            logger.error(f"Error getting KYC status: {e}")
            raise KYCServiceException(f"Failed to get KYC status: {str(e)}")
    
    def validate_document_integrity(self, document_file: UploadedFile) -> Dict[str, Any]:
        """
        Validate document integrity and security.
        
        Args:
            document_file: Uploaded file to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if document_file.size > max_size:
                return {
                    'valid': False,
                    'error': 'File size exceeds 5MB limit'
                }
            
            # Check file type
            allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if document_file.content_type not in allowed_types:
                return {
                    'valid': False,
                    'error': 'Only PDF, JPG, JPEG, and PNG files are allowed'
                }
            
            # Calculate file hash for integrity
            document_file.seek(0)
            file_hash = hashlib.sha256(document_file.read()).hexdigest()
            document_file.seek(0)  # Reset file pointer
            
            return {
                'valid': True,
                'file_hash': file_hash,
                'file_size': document_file.size,
                'content_type': document_file.content_type
            }
            
        except Exception as e:
            logger.error(f"Error validating document integrity: {e}")
            return {
                'valid': False,
                'error': 'Document validation failed'
            }
    
    def _validate_documents(self, document_data: KYCDocumentDTO) -> None:
        """Validate KYC document data."""
        # Validate citizenship number format (Nepali format)
        if document_data.citizenship_number:
            if not self._is_valid_citizenship_number(document_data.citizenship_number):
                raise ValidationException("Invalid citizenship number format")
        
        # Validate required fields
        required_fields = [
            'citizenship_number', 'citizenship_issue_date', 'citizenship_issue_district',
            'father_name', 'mother_name', 'occupation'
        ]
        
        for field in required_fields:
            if not getattr(document_data, field):
                raise ValidationException(f"{field.replace('_', ' ').title()} is required")
        
        # Validate documents
        if document_data.citizenship_document:
            validation_result = self.validate_document_integrity(document_data.citizenship_document)
            if not validation_result['valid']:
                raise ValidationException(validation_result['error'])
        
        if document_data.address_proof:
            validation_result = self.validate_document_integrity(document_data.address_proof)
            if not validation_result['valid']:
                raise ValidationException(validation_result['error'])
    
    def _perform_verification_checks(self, registration: MemberRegistration, verification_data: KYCVerificationDTO) -> Dict[str, Any]:
        """Perform comprehensive KYC verification checks."""
        checks = {
            'document_quality': True,
            'data_consistency': True,
            'compliance': True,
            'approved': True
        }
        
        # Document quality checks
        if not registration.citizenship_document or not registration.address_proof:
            checks['document_quality'] = False
            checks['approved'] = False
        
        # Data consistency checks
        if not registration.citizenship_number or not registration.father_name:
            checks['data_consistency'] = False
            checks['approved'] = False
        
        # Compliance checks (can be extended with external API calls)
        if verification_data.compliance_notes and 'reject' in verification_data.compliance_notes.lower():
            checks['compliance'] = False
            checks['approved'] = False
        
        return checks
    
    def _is_valid_citizenship_number(self, citizenship_number: str) -> bool:
        """Validate Nepali citizenship number format."""
        # Basic format validation for Nepali citizenship numbers
        # This can be enhanced with more specific rules
        import re
        pattern = r'^[0-9]{1,2}-[0-9]{2}-[0-9]{5}$'
        return bool(re.match(pattern, citizenship_number))
