"""
CBS Service

Handles integration with Core Banking System (CBS) including member
synchronization, account management, transaction processing, and loan
operations. This service provides a robust abstraction layer for CBS
integration with retry logic, circuit breaker pattern, and error handling.
"""

import logging
import requests
import time
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal

from ..models import Member, MemberAccount, MemberTransaction, MemberLoan
from ..exceptions import CBSServiceException, CBSConnectionException
from ..dto import CBSMemberDTO, CBSAccountDTO, CBSTransactionDTO, CBSLoanDTO

logger = logging.getLogger('members.services')


class CBSService:
    """
    Service class for CBS integration operations.
    
    This service handles:
    - Member synchronization with CBS
    - Account balance and transaction sync
    - Loan application and management
    - Error handling and retry logic
    - Circuit breaker pattern implementation
    """
    
    def __init__(self):
        self.api_url = getattr(settings, 'CBS_API_URL', 'https://mock-cbs-api.com/api/v1')
        self.api_key = getattr(settings, 'CBS_API_KEY', 'mock-api-key')
        self.api_secret = getattr(settings, 'CBS_API_SECRET', 'mock-api-secret')
        self.timeout = getattr(settings, 'CBS_API_TIMEOUT', 30)
        self.retry_attempts = getattr(settings, 'CBS_API_RETRY_ATTEMPTS', 3)
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
    
    def sync_member_to_cbs(self, member: Member) -> Dict[str, Any]:
        """
        Synchronize member data with CBS.
        
        Args:
            member: Member instance to sync
            
        Returns:
            Dict containing sync results
        """
        try:
            # Check circuit breaker
            if self._is_circuit_breaker_open():
                raise CBSConnectionException("CBS circuit breaker is open")
            
            member_data = self._prepare_member_data(member)
            
            response = self._make_cbs_request(
                'POST',
                '/members',
                data=member_data,
                retry=True
            )
            
            if response.get('status') == 'success':
                # Update member with CBS ID
                member.cbs_member_id = response.get('member_id')
                member.cbs_sync_status = 'synced'
                member.last_sync_date = timezone.now()
                member.save()
                
                logger.info(f"Member synced to CBS: {member.id}")
                return {
                    'success': True,
                    'cbs_member_id': response.get('member_id'),
                    'message': 'Member successfully synced to CBS'
                }
            else:
                raise CBSServiceException(f"CBS sync failed: {response.get('message')}")
                
        except Exception as e:
            logger.error(f"Error syncing member to CBS: {e}")
            self._record_cbs_failure()
            raise CBSServiceException(f"Failed to sync member to CBS: {str(e)}")
    
    def get_member_accounts_from_cbs(self, cbs_member_id: str) -> List[Dict[str, Any]]:
        """
        Get member accounts from CBS.
        
        Args:
            cbs_member_id: CBS member ID
            
        Returns:
            List of account data from CBS
        """
        try:
            if self._is_circuit_breaker_open():
                raise CBSConnectionException("CBS circuit breaker is open")
            
            response = self._make_cbs_request(
                'GET',
                f'/members/{cbs_member_id}/accounts',
                retry=True
            )
            
            if response.get('status') == 'success':
                return response.get('accounts', [])
            else:
                raise CBSServiceException(f"Failed to get accounts from CBS: {response.get('message')}")
                
        except Exception as e:
            logger.error(f"Error getting accounts from CBS: {e}")
            self._record_cbs_failure()
            raise CBSServiceException(f"Failed to get accounts from CBS: {str(e)}")
    
    def sync_account_balances(self, member: Member) -> Dict[str, Any]:
        """
        Synchronize account balances from CBS.
        
        Args:
            member: Member instance
            
        Returns:
            Dict containing sync results
        """
        try:
            if not member.cbs_member_id:
                raise CBSServiceException("Member does not have CBS ID")
            
            accounts_data = self.get_member_accounts_from_cbs(member.cbs_member_id)
            
            updated_accounts = []
            for account_data in accounts_data:
                try:
                    account = member.accounts.get(cbs_account_id=account_data['account_id'])
                    account.balance = Decimal(str(account_data['balance']))
                    account.cbs_sync_status = 'synced'
                    account.last_sync_date = timezone.now()
                    account.save()
                    updated_accounts.append(account)
                except MemberAccount.DoesNotExist:
                    # Create new account if it doesn't exist
                    account = MemberAccount.objects.create(
                        member=member,
                        account_type=account_data.get('account_type', 'savings'),
                        account_number=account_data['account_number'],
                        account_name=account_data.get('account_name', ''),
                        balance=Decimal(str(account_data['balance'])),
                        cbs_account_id=account_data['account_id'],
                        cbs_sync_status='synced',
                        last_sync_date=timezone.now()
                    )
                    updated_accounts.append(account)
            
            logger.info(f"Account balances synced for member: {member.id}")
            return {
                'success': True,
                'updated_accounts': len(updated_accounts),
                'message': 'Account balances successfully synced'
            }
            
        except Exception as e:
            logger.error(f"Error syncing account balances: {e}")
            raise CBSServiceException(f"Failed to sync account balances: {str(e)}")
    
    def get_transaction_history(self, account_number: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get transaction history from CBS.
        
        Args:
            account_number: Account number
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of transaction data from CBS
        """
        try:
            if self._is_circuit_breaker_open():
                raise CBSConnectionException("CBS circuit breaker is open")
            
            response = self._make_cbs_request(
                'GET',
                f'/accounts/{account_number}/transactions',
                params={'limit': limit},
                retry=True
            )
            
            if response.get('status') == 'success':
                return response.get('transactions', [])
            else:
                raise CBSServiceException(f"Failed to get transactions from CBS: {response.get('message')}")
                
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            self._record_cbs_failure()
            raise CBSServiceException(f"Failed to get transaction history: {str(e)}")
    
    def submit_loan_application(self, loan_data: CBSLoanDTO) -> Dict[str, Any]:
        """
        Submit loan application to CBS.
        
        Args:
            loan_data: CBSLoanDTO containing loan information
            
        Returns:
            Dict containing submission results
        """
        try:
            if self._is_circuit_breaker_open():
                raise CBSConnectionException("CBS circuit breaker is open")
            
            loan_payload = self._prepare_loan_data(loan_data)
            
            response = self._make_cbs_request(
                'POST',
                '/loans',
                data=loan_payload,
                retry=True
            )
            
            if response.get('status') == 'success':
                logger.info(f"Loan application submitted to CBS: {loan_data.member_id}")
                return {
                    'success': True,
                    'cbs_loan_id': response.get('loan_id'),
                    'message': 'Loan application successfully submitted'
                }
            else:
                raise CBSServiceException(f"Loan submission failed: {response.get('message')}")
                
        except Exception as e:
            logger.error(f"Error submitting loan application: {e}")
            self._record_cbs_failure()
            raise CBSServiceException(f"Failed to submit loan application: {str(e)}")
    
    def _make_cbs_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                         params: Optional[Dict] = None, retry: bool = False) -> Dict[str, Any]:
        """Make HTTP request to CBS API with retry logic."""
        url = f"{self.api_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-API-Secret': self.api_secret
        }
        
        attempts = 0
        last_exception = None
        
        while attempts < (self.retry_attempts if retry else 1):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
                else:
                    raise CBSServiceException(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                attempts += 1
                if attempts < self.retry_attempts:
                    time.sleep(2 ** attempts)  # Exponential backoff
                    logger.warning(f"CBS request failed, retrying ({attempts}/{self.retry_attempts}): {e}")
                else:
                    logger.error(f"CBS request failed after {self.retry_attempts} attempts: {e}")
        
        raise CBSConnectionException(f"CBS request failed: {str(last_exception)}")
    
    def _prepare_member_data(self, member: Member) -> Dict[str, Any]:
        """Prepare member data for CBS submission."""
        return {
            'first_name': member.first_name,
            'last_name': member.last_name,
            'middle_name': member.middle_name,
            'email': member.email,
            'phone': member.phone,
            'citizenship_number': member.citizenship_number,
            'citizenship_issue_date': member.citizenship_issue_date.isoformat() if member.citizenship_issue_date else None,
            'citizenship_issue_district': member.citizenship_issue_district,
            'father_name': member.father_name,
            'mother_name': member.mother_name,
            'occupation': member.occupation,
            'permanent_address': member.permanent_address,
            'ward_number': member.ward.ward_number,
            'tole_name': member.tole_name,
            'membership_date': member.membership_date.isoformat() if member.membership_date else None,
            'membership_type': member.membership_type
        }
    
    def _prepare_loan_data(self, loan_data: CBSLoanDTO) -> Dict[str, Any]:
        """Prepare loan data for CBS submission."""
        return {
            'member_id': loan_data.member_id,
            'loan_type': loan_data.loan_type,
            'loan_amount': str(loan_data.loan_amount),
            'purpose': loan_data.purpose,
            'tenure_months': loan_data.tenure_months,
            'interest_rate': str(loan_data.interest_rate) if loan_data.interest_rate else None
        }
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        circuit_breaker_key = 'cbs_circuit_breaker'
        circuit_breaker_data = cache.get(circuit_breaker_key)
        
        if circuit_breaker_data and circuit_breaker_data.get('open'):
            # Check if timeout has passed
            if timezone.now().timestamp() - circuit_breaker_data.get('opened_at', 0) > self.circuit_breaker_timeout:
                # Reset circuit breaker
                cache.delete(circuit_breaker_key)
                return False
            return True
        
        return False
    
    def _record_cbs_failure(self) -> None:
        """Record CBS failure for circuit breaker."""
        circuit_breaker_key = 'cbs_circuit_breaker'
        circuit_breaker_data = cache.get(circuit_breaker_key, {'failures': 0})
        
        circuit_breaker_data['failures'] += 1
        
        if circuit_breaker_data['failures'] >= self.circuit_breaker_threshold:
            circuit_breaker_data['open'] = True
            circuit_breaker_data['opened_at'] = timezone.now().timestamp()
            logger.warning("CBS circuit breaker opened due to repeated failures")
        
        cache.set(circuit_breaker_key, circuit_breaker_data, self.circuit_breaker_timeout)
