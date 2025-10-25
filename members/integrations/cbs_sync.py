"""
CBS Synchronization Service
Handles automated data synchronization between local database and CBS
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from typing import Dict, List, Optional
from .cbs_api import CBSSyncService
from .cbs_models import CBSSyncLog


logger = logging.getLogger('members.cbs.sync')


class CBSSyncManager:
    """
    CBS Synchronization Manager
    Handles batch synchronization operations
    """
    
    def __init__(self):
        self.sync_service = CBSSyncService()
        self.logger = logger
    
    def sync_all_active_members(self) -> Dict:
        """
        Sync all active members with CBS
        """
        from members.models import Member
        
        sync_log = CBSSyncLog.objects.create(
            sync_type='full',
            sync_status='started'
        )
        
        try:
            active_members = Member.objects.filter(
                is_active=True,
                cbs_member_id__isnull=False
            )
            
            total_members = active_members.count()
            successful_syncs = 0
            failed_syncs = 0
            
            self.logger.info(f"Starting full sync for {total_members} active members")
            
            for member in active_members:
                try:
                    sync_results = self.sync_service.full_sync_member(member.cbs_member_id)
                    
                    if all(sync_results.values()):
                        successful_syncs += 1
                    else:
                        failed_syncs += 1
                        
                except Exception as e:
                    failed_syncs += 1
                    self.logger.error(f"Failed to sync member {member.cbs_member_id}: {e}")
            
            # Update sync log
            sync_log.sync_status = 'completed' if failed_syncs == 0 else 'partial'
            sync_log.records_processed = total_members
            sync_log.records_successful = successful_syncs
            sync_log.records_failed = failed_syncs
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
            sync_log.save()
            
            self.logger.info(f"Full sync completed: {successful_syncs}/{total_members} successful")
            
            return {
                'status': 'success',
                'total_members': total_members,
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'sync_log_id': sync_log.id
            }
            
        except Exception as e:
            sync_log.sync_status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            self.logger.error(f"Full sync failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'sync_log_id': sync_log.id
            }
    
    def sync_member_accounts(self, member_id: str) -> Dict:
        """
        Sync accounts for a specific member
        """
        sync_log = CBSSyncLog.objects.create(
            sync_type='account',
            sync_status='started'
        )
        
        try:
            success = self.sync_service.sync_account_data(member_id)
            
            sync_log.sync_status = 'completed' if success else 'failed'
            sync_log.records_processed = 1
            sync_log.records_successful = 1 if success else 0
            sync_log.records_failed = 0 if success else 1
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
            sync_log.save()
            
            return {
                'status': 'success' if success else 'error',
                'member_id': member_id,
                'sync_log_id': sync_log.id
            }
            
        except Exception as e:
            sync_log.sync_status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            return {
                'status': 'error',
                'error': str(e),
                'member_id': member_id,
                'sync_log_id': sync_log.id
            }
    
    def sync_account_transactions(self, account_number: str, days: int = 30) -> Dict:
        """
        Sync transactions for a specific account
        """
        sync_log = CBSSyncLog.objects.create(
            sync_type='transaction',
            sync_status='started'
        )
        
        try:
            success = self.sync_service.sync_transaction_data(account_number, days)
            
            sync_log.sync_status = 'completed' if success else 'failed'
            sync_log.records_processed = 1
            sync_log.records_successful = 1 if success else 0
            sync_log.records_failed = 0 if success else 1
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
            sync_log.save()
            
            return {
                'status': 'success' if success else 'error',
                'account_number': account_number,
                'sync_log_id': sync_log.id
            }
            
        except Exception as e:
            sync_log.sync_status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            return {
                'status': 'error',
                'error': str(e),
                'account_number': account_number,
                'sync_log_id': sync_log.id
            }
    
    def sync_member_loans(self, member_id: str) -> Dict:
        """
        Sync loans for a specific member
        """
        sync_log = CBSSyncLog.objects.create(
            sync_type='loan',
            sync_status='started'
        )
        
        try:
            success = self.sync_service.sync_loan_data(member_id)
            
            sync_log.sync_status = 'completed' if success else 'failed'
            sync_log.records_processed = 1
            sync_log.records_successful = 1 if success else 0
            sync_log.records_failed = 0 if success else 1
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
            sync_log.save()
            
            return {
                'status': 'success' if success else 'error',
                'member_id': member_id,
                'sync_log_id': sync_log.id
            }
            
        except Exception as e:
            sync_log.sync_status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            return {
                'status': 'error',
                'error': str(e),
                'member_id': member_id,
                'sync_log_id': sync_log.id
            }
    
    def get_sync_status(self, sync_log_id: int) -> Dict:
        """
        Get status of a specific sync operation
        """
        try:
            sync_log = CBSSyncLog.objects.get(id=sync_log_id)
            
            return {
                'status': 'success',
                'sync_log': {
                    'id': sync_log.id,
                    'sync_type': sync_log.get_sync_type_display(),
                    'sync_status': sync_log.get_sync_status_display(),
                    'records_processed': sync_log.records_processed,
                    'records_successful': sync_log.records_successful,
                    'records_failed': sync_log.records_failed,
                    'started_at': sync_log.started_at,
                    'completed_at': sync_log.completed_at,
                    'duration_seconds': sync_log.duration_seconds,
                    'error_message': sync_log.error_message
                }
            }
            
        except CBSSyncLog.DoesNotExist:
            return {
                'status': 'error',
                'error': 'Sync log not found'
            }
    
    def get_recent_sync_logs(self, limit: int = 10) -> List[Dict]:
        """
        Get recent sync logs
        """
        sync_logs = CBSSyncLog.objects.order_by('-started_at')[:limit]
        
        return [
            {
                'id': log.id,
                'sync_type': log.get_sync_type_display(),
                'sync_status': log.get_sync_status_display(),
                'records_processed': log.records_processed,
                'records_successful': log.records_successful,
                'records_failed': log.records_failed,
                'started_at': log.started_at,
                'completed_at': log.completed_at,
                'duration_seconds': log.duration_seconds,
                'error_message': log.error_message
            }
            for log in sync_logs
        ]


class CBSDataValidator:
    """
    CBS Data Validation Service
    Validates data integrity between local and CBS
    """
    
    def __init__(self):
        self.logger = logger
    
    def validate_member_data(self, member_id: str) -> Dict:
        """
        Validate member data consistency
        """
        from members.models import Member
        
        try:
            member = Member.objects.get(cbs_member_id=member_id)
            
            # Check if CBS data exists
            cbs_data = self.sync_service.api_client.get_member_info(member_id)
            
            if cbs_data.get('status') != 'success':
                return {
                    'status': 'error',
                    'message': 'CBS data not available',
                    'member_id': member_id
                }
            
            # Compare key fields
            cbs_member = cbs_data['member']
            discrepancies = []
            
            if member.first_name != cbs_member['first_name']:
                discrepancies.append('first_name')
            
            if member.last_name != cbs_member['last_name']:
                discrepancies.append('last_name')
            
            if member.email != cbs_member['email']:
                discrepancies.append('email')
            
            if member.phone != cbs_member['phone']:
                discrepancies.append('phone')
            
            return {
                'status': 'success',
                'member_id': member_id,
                'discrepancies': discrepancies,
                'is_valid': len(discrepancies) == 0
            }
            
        except Member.DoesNotExist:
            return {
                'status': 'error',
                'message': 'Member not found',
                'member_id': member_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'member_id': member_id
            }
    
    def validate_account_data(self, account_number: str) -> Dict:
        """
        Validate account data consistency
        """
        from members.models import MemberAccount
        
        try:
            account = MemberAccount.objects.get(account_number=account_number)
            
            # Check if CBS data exists
            cbs_data = self.sync_service.api_client.get_account_balance(account_number)
            
            if cbs_data.get('status') != 'success':
                return {
                    'status': 'error',
                    'message': 'CBS account data not available',
                    'account_number': account_number
                }
            
            # Compare balance
            cbs_balance = Decimal(cbs_data['balance'])
            local_balance = account.balance
            
            balance_difference = abs(cbs_balance - local_balance)
            
            return {
                'status': 'success',
                'account_number': account_number,
                'local_balance': str(local_balance),
                'cbs_balance': str(cbs_balance),
                'balance_difference': str(balance_difference),
                'is_valid': balance_difference < Decimal('0.01')  # Allow 1 paisa difference
            }
            
        except MemberAccount.DoesNotExist:
            return {
                'status': 'error',
                'message': 'Account not found',
                'account_number': account_number
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'account_number': account_number
            }


# Management Command for CBS Sync
class Command(BaseCommand):
    """
    Django management command for CBS synchronization
    Usage: python manage.py sync_cbs_data [--member-id MEMBER_ID] [--full]
    """
    
    help = 'Synchronize data with CBS'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--member-id',
            type=str,
            help='Sync specific member by CBS member ID'
        )
        parser.add_argument(
            '--account-number',
            type=str,
            help='Sync specific account by account number'
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full sync for all active members'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to sync transactions (default: 30)'
        )
    
    def handle(self, *args, **options):
        sync_manager = CBSSyncManager()
        
        if options['full']:
            self.stdout.write('Starting full CBS sync...')
            result = sync_manager.sync_all_active_members()
            
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Full sync completed: {result['successful_syncs']}/{result['total_members']} successful"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Full sync failed: {result['error']}")
                )
        
        elif options['member_id']:
            self.stdout.write(f'Syncing member: {options["member_id"]}')
            result = sync_manager.sync_member_accounts(options['member_id'])
            
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(f"Member sync completed: {options['member_id']}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Member sync failed: {result['error']}")
                )
        
        elif options['account_number']:
            self.stdout.write(f'Syncing account: {options["account_number"]}')
            result = sync_manager.sync_account_transactions(
                options['account_number'], 
                options['days']
            )
            
            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(f"Account sync completed: {options['account_number']}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Account sync failed: {result['error']}")
                )
        
        else:
            self.stdout.write(
                self.style.WARNING('Please specify --member-id, --account-number, or --full')
            )
