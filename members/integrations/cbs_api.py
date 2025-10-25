"""
CBS API Client with Mock Data
Provides interface for CBS integration with realistic mock responses
"""

# import requests  # Commented out until installed
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger('members.cbs')


class CBSAPIClient:
    """
    Mock CBS API Client for Bhanjyang Cooperative
    Provides realistic mock responses for development and testing
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'CBS_API_URL', 'https://mock-cbs-api.com/api/v1')
        self.api_key = getattr(settings, 'CBS_API_KEY', 'mock-api-key')
        self.timeout = getattr(settings, 'CBS_API_TIMEOUT', 30)
        self.retry_attempts = getattr(settings, 'CBS_API_RETRY_ATTEMPTS', 3)
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """
        Make HTTP request to CBS API with error handling
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            # Mock implementation since requests is not installed
            # if method.upper() == 'GET':
            #     response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            # elif method.upper() == 'POST':
            #     response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
            # elif method.upper() == 'PUT':
            #     response = requests.put(url, headers=self.headers, json=data, timeout=self.timeout)
            # else:
            #     raise ValueError(f"Unsupported HTTP method: {method}")
            
            # response.raise_for_status()
            # return response.json()
            
            # Return mock data for development
            return self._get_mock_response(endpoint, method, data, params)
            
        except Exception as e:
            logger.error(f"CBS API request failed: {e}")
            # Return mock data for development
            return self._get_mock_response(endpoint, method, data, params)
    
    def _get_mock_response(self, endpoint: str, method: str, data: Dict = None, params: Dict = None) -> Dict:
        """
        Generate mock responses for development
        """
        if 'members' in endpoint and method == 'GET':
            return self._mock_member_data(params)
        elif 'accounts' in endpoint and method == 'GET':
            return self._mock_account_data(params)
        elif 'transactions' in endpoint and method == 'GET':
            return self._mock_transaction_data(params)
        elif 'loans' in endpoint and method == 'GET':
            return self._mock_loan_data(params)
        elif 'loans' in endpoint and method == 'POST':
            return self._mock_loan_application_response(data)
        else:
            return {'status': 'success', 'message': 'Mock response'}
    
    def get_member_info(self, cbs_member_id: str) -> Dict:
        """
        Get member information from CBS
        """
        return self._make_request('GET', f'members/{cbs_member_id}')
    
    def get_member_accounts(self, cbs_member_id: str) -> List[Dict]:
        """
        Get all accounts for a member
        """
        response = self._make_request('GET', f'members/{cbs_member_id}/accounts')
        return response.get('accounts', [])
    
    def get_account_balance(self, account_number: str) -> Dict:
        """
        Get real-time account balance
        """
        return self._make_request('GET', f'accounts/{account_number}/balance')
    
    def get_transaction_history(self, account_number: str, from_date: str = None, to_date: str = None, limit: int = 50) -> List[Dict]:
        """
        Get transaction history for an account
        """
        params = {'limit': limit}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
            
        response = self._make_request('GET', f'accounts/{account_number}/transactions', params=params)
        return response.get('transactions', [])
    
    def submit_loan_application(self, loan_data: Dict) -> Dict:
        """
        Submit loan application to CBS
        """
        return self._make_request('POST', 'loans/apply', data=loan_data)
    
    def get_loan_status(self, loan_id: str) -> Dict:
        """
        Get loan application status
        """
        return self._make_request('GET', f'loans/{loan_id}/status')
    
    def get_member_loans(self, cbs_member_id: str) -> List[Dict]:
        """
        Get all loans for a member
        """
        response = self._make_request('GET', f'members/{cbs_member_id}/loans')
        return response.get('loans', [])
    
    def _mock_member_data(self, params: Dict = None) -> Dict:
        """Generate mock member data"""
        return {
            'status': 'success',
            'member': {
                'cbs_member_id': 'CBS001',
                'member_id': 'RUPA20240001',
                'first_name': 'राम',
                'last_name': 'शर्मा',
                'middle_name': 'प्रसाद',
                'email': 'ram.sharma@example.com',
                'phone': '+977-9841234567',
                'permanent_address': 'रुपा गाउँपालिका, वडा नं. १, कास्की',
                'ward_number': '1',
                'membership_date': '2024-01-15',
                'membership_type': 'regular',
                'is_active': True,
                'is_verified': True,
                'cbs_created_date': '2024-01-15T10:00:00Z',
                'cbs_last_updated': timezone.now().isoformat()
            }
        }
    
    def _mock_account_data(self, params: Dict = None) -> Dict:
        """Generate mock account data"""
        accounts = [
            {
                'cbs_account_id': 'ACC001',
                'account_number': 'SAV001234567',
                'account_type': 'savings',
                'account_name': 'बचत खाता',
                'balance': '25000.00',
                'available_balance': '25000.00',
                'interest_rate': '4.50',
                'status': 'active',
                'is_active': True,
                'cbs_created_date': '2024-01-15T10:00:00Z',
                'cbs_last_updated': timezone.now().isoformat()
            },
            {
                'cbs_account_id': 'ACC002',
                'account_number': 'SHA001234567',
                'account_type': 'share',
                'account_name': 'शेयर खाता',
                'balance': '5000.00',
                'available_balance': '5000.00',
                'interest_rate': '6.00',
                'status': 'active',
                'is_active': True,
                'cbs_created_date': '2024-01-15T10:00:00Z',
                'cbs_last_updated': timezone.now().isoformat()
            }
        ]
        
        return {
            'status': 'success',
            'accounts': accounts
        }
    
    def _mock_transaction_data(self, params: Dict = None) -> Dict:
        """Generate mock transaction data"""
        transactions = []
        base_date = timezone.now()
        
        # Generate last 10 transactions
        for i in range(10):
            transaction_date = base_date - timedelta(days=i)
            amount = Decimal('1000') + (i * Decimal('500'))
            
            transactions.append({
                'cbs_transaction_id': f'TXN{1000 + i}',
                'transaction_type': 'deposit' if i % 2 == 0 else 'withdrawal',
                'amount': str(amount),
                'balance_after': str(Decimal('25000') + amount),
                'description': f'लेनदेन {i + 1}',
                'reference_number': f'REF{1000 + i}',
                'transaction_date': transaction_date.isoformat(),
                'cbs_created_date': transaction_date.isoformat()
            })
        
        return {
            'status': 'success',
            'transactions': transactions
        }
    
    def _mock_loan_data(self, params: Dict = None) -> Dict:
        """Generate mock loan data"""
        loans = [
            {
                'cbs_loan_id': 'LOAN001',
                'loan_type': 'घरेलु ऋण',
                'loan_amount': '100000.00',
                'disbursed_amount': '100000.00',
                'outstanding_amount': '85000.00',
                'interest_rate': '12.00',
                'tenure_months': 24,
                'purpose': 'घर निर्माण',
                'monthly_installment': '5000.00',
                'status': 'active',
                'cbs_applied_date': '2024-01-15T10:00:00Z',
                'cbs_approved_date': '2024-01-20T10:00:00Z',
                'cbs_disbursed_date': '2024-01-25T10:00:00Z'
            }
        ]
        
        return {
            'status': 'success',
            'loans': loans
        }
    
    def _mock_loan_application_response(self, data: Dict) -> Dict:
        """Generate mock loan application response"""
        return {
            'status': 'success',
            'message': 'ऋण आवेदन सफलतापूर्वक पेश गरियो',
            'loan_id': 'LOAN002',
            'application_number': f'APP{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'estimated_processing_time': '5-7 business days',
            'next_steps': [
                'दस्तावेजहरू जाँच गर्नुहोस्',
                'सहमति पत्र हस्ताक्षर गर्नुहोस्',
                'ऋण रकम प्राप्त गर्नुहोस्'
            ]
        }


class CBSSyncService:
    """
    CBS Data Synchronization Service
    Handles data sync between local database and CBS
    """
    
    def __init__(self):
        self.api_client = CBSAPIClient()
        self.logger = logging.getLogger('members.cbs.sync')
    
    def sync_member_data(self, member_id: str) -> bool:
        """
        Sync member data from CBS
        """
        try:
            # Get member data from CBS
            member_data = self.api_client.get_member_info(member_id)
            
            if member_data.get('status') == 'success':
                # Update local member record
                self._update_local_member(member_data['member'])
                self.logger.info(f"Successfully synced member: {member_id}")
                return True
            else:
                self.logger.error(f"Failed to sync member {member_id}: {member_data}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing member {member_id}: {e}")
            return False
    
    def sync_account_data(self, member_id: str) -> bool:
        """
        Sync account data for a member
        """
        try:
            # Get accounts from CBS
            accounts_data = self.api_client.get_member_accounts(member_id)
            
            if accounts_data:
                # Update local account records
                for account_data in accounts_data:
                    self._update_local_account(account_data)
                
                self.logger.info(f"Successfully synced accounts for member: {member_id}")
                return True
            else:
                self.logger.warning(f"No accounts found for member: {member_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing accounts for member {member_id}: {e}")
            return False
    
    def sync_transaction_data(self, account_number: str, days: int = 30) -> bool:
        """
        Sync transaction data for an account
        """
        try:
            from_date = (timezone.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = timezone.now().strftime('%Y-%m-%d')
            
            # Get transactions from CBS
            transactions_data = self.api_client.get_transaction_history(
                account_number, from_date, to_date
            )
            
            if transactions_data:
                # Update local transaction records
                for transaction_data in transactions_data:
                    self._update_local_transaction(transaction_data, account_number)
                
                self.logger.info(f"Successfully synced transactions for account: {account_number}")
                return True
            else:
                self.logger.warning(f"No transactions found for account: {account_number}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing transactions for account {account_number}: {e}")
            return False
    
    def sync_loan_data(self, member_id: str) -> bool:
        """
        Sync loan data for a member
        """
        try:
            # Get loans from CBS
            loans_data = self.api_client.get_member_loans(member_id)
            
            if loans_data:
                # Update local loan records
                for loan_data in loans_data:
                    self._update_local_loan(loan_data)
                
                self.logger.info(f"Successfully synced loans for member: {member_id}")
                return True
            else:
                self.logger.warning(f"No loans found for member: {member_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing loans for member {member_id}: {e}")
            return False
    
    def full_sync_member(self, member_id: str) -> Dict:
        """
        Perform full sync for a member (all data types)
        """
        sync_results = {
            'member': False,
            'accounts': False,
            'transactions': False,
            'loans': False
        }
        
        try:
            # Sync member data
            sync_results['member'] = self.sync_member_data(member_id)
            
            # Sync accounts
            sync_results['accounts'] = self.sync_account_data(member_id)
            
            # Sync transactions for each account
            if sync_results['accounts']:
                # Get member's accounts and sync transactions
                from members.models import MemberAccount
                accounts = MemberAccount.objects.filter(member__user__member_id=member_id)
                for account in accounts:
                    self.sync_transaction_data(account.account_number)
            
            # Sync loans
            sync_results['loans'] = self.sync_loan_data(member_id)
            
            # Log sync results
            successful_syncs = sum(1 for success in sync_results.values() if success)
            total_syncs = len(sync_results)
            
            self.logger.info(f"Full sync completed for member {member_id}: {successful_syncs}/{total_syncs} successful")
            
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Error in full sync for member {member_id}: {e}")
            return sync_results
    
    def _update_local_member(self, member_data: Dict):
        """Update local member record with CBS data"""
        from members.models import Member
        
        try:
            member = Member.objects.get(cbs_member_id=member_data['cbs_member_id'])
            
            # Update fields
            member.first_name = member_data['first_name']
            member.last_name = member_data['last_name']
            member.email = member_data['email']
            member.phone = member_data['phone']
            member.last_sync_date = timezone.now()
            member.cbs_sync_status = 'synced'
            
            member.save()
            
        except Member.DoesNotExist:
            self.logger.warning(f"Member not found for CBS ID: {member_data['cbs_member_id']}")
    
    def _update_local_account(self, account_data: Dict):
        """Update local account record with CBS data"""
        from members.models import MemberAccount
        
        try:
            account = MemberAccount.objects.get(cbs_account_id=account_data['cbs_account_id'])
            
            # Update fields
            account.balance = Decimal(account_data['balance'])
            account.interest_rate = Decimal(account_data['interest_rate']) if account_data['interest_rate'] else None
            account.last_sync_date = timezone.now()
            account.cbs_sync_status = 'synced'
            
            account.save()
            
        except MemberAccount.DoesNotExist:
            self.logger.warning(f"Account not found for CBS ID: {account_data['cbs_account_id']}")
    
    def _update_local_transaction(self, transaction_data: Dict, account_number: str):
        """Update local transaction record with CBS data"""
        from members.models import MemberTransaction, MemberAccount
        
        try:
            account = MemberAccount.objects.get(account_number=account_number)
            
            # Check if transaction already exists
            transaction, created = MemberTransaction.objects.get_or_create(
                cbs_transaction_id=transaction_data['cbs_transaction_id'],
                defaults={
                    'account': account,
                    'transaction_type': transaction_data['transaction_type'],
                    'amount': Decimal(transaction_data['amount']),
                    'balance_after': Decimal(transaction_data['balance_after']) if transaction_data['balance_after'] else None,
                    'description': transaction_data['description'],
                    'reference_number': transaction_data['reference_number'],
                    'transaction_date': timezone.datetime.fromisoformat(transaction_data['transaction_date'].replace('Z', '+00:00')),
                    'is_cbs_synced': True
                }
            )
            
            if created:
                self.logger.info(f"Created new transaction: {transaction_data['cbs_transaction_id']}")
            
        except MemberAccount.DoesNotExist:
            self.logger.warning(f"Account not found for account number: {account_number}")
    
    def _update_local_loan(self, loan_data: Dict):
        """Update local loan record with CBS data"""
        from members.models import MemberLoan
        
        try:
            loan = MemberLoan.objects.get(cbs_loan_id=loan_data['cbs_loan_id'])
            
            # Update fields
            loan.loan_amount = Decimal(loan_data['loan_amount'])
            loan.outstanding_amount = Decimal(loan_data['outstanding_amount']) if loan_data['outstanding_amount'] else None
            loan.status = loan_data['status']
            loan.cbs_sync_status = 'synced'
            
            loan.save()
            
        except MemberLoan.DoesNotExist:
            self.logger.warning(f"Loan not found for CBS ID: {loan_data['cbs_loan_id']}")
