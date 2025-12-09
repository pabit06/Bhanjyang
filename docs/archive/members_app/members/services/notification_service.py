"""
Notification Service

Handles member notifications including email notifications, in-app notifications,
SMS notifications, and push notifications. This service provides a centralized
way to manage all communication with members.
"""

import logging
from typing import Optional, Dict, Any, List
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from ..models import Member, MemberNotification
from ..exceptions import NotificationServiceException
from ..dto import NotificationDTO

logger = logging.getLogger('members.services')


class NotificationService:
    """
    Service class for notification operations.
    
    This service handles:
    - Email notifications
    - In-app notifications
    - SMS notifications (future)
    - Push notifications (future)
    - Notification templates
    - Notification preferences
    """
    
    def __init__(self):
        self.email_enabled = getattr(settings, 'SEND_REAL_EMAILS', False)
    
    def send_registration_confirmation(self, registration) -> bool:
        """
        Send registration confirmation email.
        
        Args:
            registration: MemberRegistration instance
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = 'भन्ज्याङ सहकारीको सदस्यता दर्ता'
            
            context = {
                'registration': registration,
                'member_name': f"{registration.first_name} {registration.last_name}",
                'registration_id': registration.id,
                'status': registration.get_status_display(),
                'next_steps': self._get_next_steps(registration.status)
            }
            
            message = render_to_string('members/emails/registration_confirmation.txt', context)
            html_message = render_to_string('members/emails/registration_confirmation.html', context)
            
            return self._send_email(
                subject=subject,
                message=message,
                html_message=html_message,
                recipient_list=[registration.email]
            )
            
        except Exception as e:
            logger.error(f"Error sending registration confirmation: {e}")
            return False
    
    def send_kyc_submission_confirmation(self, registration) -> bool:
        """
        Send KYC submission confirmation email.
        
        Args:
            registration: MemberRegistration instance
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = 'KYC दस्तावेज पेश गरियो'
            
            context = {
                'registration': registration,
                'member_name': f"{registration.first_name} {registration.last_name}",
                'registration_id': registration.id,
                'status': registration.get_status_display()
            }
            
            message = render_to_string('members/emails/kyc_submission_confirmation.txt', context)
            html_message = render_to_string('members/emails/kyc_submission_confirmation.html', context)
            
            return self._send_email(
                subject=subject,
                message=message,
                html_message=html_message,
                recipient_list=[registration.email]
            )
            
        except Exception as e:
            logger.error(f"Error sending KYC submission confirmation: {e}")
            return False
    
    def send_membership_approval(self, member: Member) -> bool:
        """
        Send membership approval notification.
        
        Args:
            member: Member instance
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            # Send email notification
            subject = 'सदस्यता स्वीकृत भयो - भन्ज्याङ सहकारी'
            
            context = {
                'member': member,
                'member_name': member.get_full_name(),
                'member_id': member.user.username,
                'login_url': f"{settings.SITE_URL}/members/login/"
            }
            
            message = render_to_string('members/emails/membership_approval.txt', context)
            html_message = render_to_string('members/emails/membership_approval.html', context)
            
            email_sent = self._send_email(
                subject=subject,
                message=message,
                html_message=html_message,
                recipient_list=[member.email]
            )
            
            # Create in-app notification
            self.create_notification(
                member=member,
                notification_type='success',
                title='सदस्यता स्वीकृत भयो',
                message='तपाईंको सदस्यता सफलतापूर्वक स्वीकृत भयो। तपाईंले अब सदस्य ड्यासबोर्डमा लगइन गर्न सक्नुहुन्छ।'
            )
            
            return email_sent
            
        except Exception as e:
            logger.error(f"Error sending membership approval: {e}")
            return False
    
    def send_account_update_notification(self, member: Member, account_type: str, amount: Decimal) -> bool:
        """
        Send account update notification.
        
        Args:
            member: Member instance
            account_type: Type of account updated
            amount: Amount involved
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            # Create in-app notification
            self.create_notification(
                member=member,
                notification_type='info',
                title='खाता अपडेट',
                message=f'तपाईंको {account_type} खातामा रु. {amount:,.2f} को लेनदेन भयो।'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending account update notification: {e}")
            return False
    
    def send_loan_status_update(self, member: Member, loan, status: str) -> bool:
        """
        Send loan status update notification.
        
        Args:
            member: Member instance
            loan: MemberLoan instance
            status: New loan status
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            status_messages = {
                'approved': 'तपाईंको ऋण आवेदन स्वीकृत भयो।',
                'disbursed': 'तपाईंको ऋण रकम खातामा जम्मा गरियो।',
                'rejected': 'तपाईंको ऋण आवेदन अस्वीकृत भयो।'
            }
            
            message = status_messages.get(status, f'तपाईंको ऋणको स्थिति {status} मा परिवर्तन भयो।')
            
            # Create in-app notification
            self.create_notification(
                member=member,
                notification_type='info' if status in ['approved', 'disbursed'] else 'warning',
                title='ऋण स्थिति अपडेट',
                message=message
            )
            
            # Send email for important status changes
            if status in ['approved', 'disbursed', 'rejected']:
                subject = f'ऋण स्थिति अपडेट - {loan.loan_type}'
                
                context = {
                    'member': member,
                    'loan': loan,
                    'status': status,
                    'message': message
                }
                
                message_text = render_to_string('members/emails/loan_status_update.txt', context)
                html_message = render_to_string('members/emails/loan_status_update.html', context)
                
                return self._send_email(
                    subject=subject,
                    message=message_text,
                    html_message=html_message,
                    recipient_list=[member.email]
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending loan status update: {e}")
            return False
    
    def create_notification(self, member: Member, notification_type: str, title: str, message: str) -> MemberNotification:
        """
        Create an in-app notification for a member.
        
        Args:
            member: Member instance
            notification_type: Type of notification (info, warning, success, error)
            title: Notification title
            message: Notification message
            
        Returns:
            MemberNotification: Created notification instance
        """
        try:
            notification = MemberNotification.objects.create(
                member=member,
                notification_type=notification_type,
                title=title,
                message=message,
                is_read=False
            )
            
            logger.info(f"Notification created for member {member.id}: {title}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise NotificationServiceException(f"Failed to create notification: {str(e)}")
    
    def mark_notification_as_read(self, notification_id: int, member: Member) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification
            member: Member instance
            
        Returns:
            bool: True if notification marked as read
        """
        try:
            notification = MemberNotification.objects.get(
                id=notification_id,
                member=member
            )
            notification.is_read = True
            notification.save()
            
            logger.info(f"Notification {notification_id} marked as read for member {member.id}")
            return True
            
        except MemberNotification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for member {member.id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    def get_unread_notifications(self, member: Member, limit: int = 10) -> List[MemberNotification]:
        """
        Get unread notifications for a member.
        
        Args:
            member: Member instance
            limit: Maximum number of notifications to return
            
        Returns:
            List of unread notifications
        """
        try:
            return MemberNotification.objects.filter(
                member=member,
                is_read=False
            ).order_by('-created_at')[:limit]
            
        except Exception as e:
            logger.error(f"Error getting unread notifications: {e}")
            return []
    
    def _send_email(self, subject: str, message: str, html_message: Optional[str] = None, 
                   recipient_list: List[str] = None) -> bool:
        """Send email notification."""
        try:
            if not self.email_enabled:
                logger.info(f"Email not sent (development mode): {subject}")
                return True
            
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False
            )
            
            logger.info(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _get_next_steps(self, status: str) -> List[str]:
        """Get next steps based on registration status."""
        next_steps_map = {
            'pending_location': [
                'स्थान प्रमाणीकरणको लागि प्रतीक्षा गर्नुहोस्',
                'प्रशासकले तपाईंको ठेगाना जाँच गर्नेछन्',
                'प्रमाणीकरण पछि KYC दस्तावेज अपलोड गर्न सकिनेछ'
            ],
            'location_verified': [
                'KYC दस्तावेज अपलोड गर्नुहोस्',
                'नागरिकता प्रमाणपत्र र ठेगाना प्रमाणपत्र अपलोड गर्नुहोस्',
                'सबै जानकारी भरेर पेश गर्नुहोस्'
            ],
            'kyc_pending': [
                'KYC दस्तावेजहरूको जाँचको लागि प्रतीक्षा गर्नुहोस्',
                'प्रशासकले दस्तावेजहरू जाँच गर्नेछन्',
                'स्वीकृति पछि सदस्यता सक्रिय हुनेछ'
            ],
            'kyc_approved': [
                'सदस्यता सफलतापूर्वक स्वीकृत भयो',
                'तपाईंले सदस्य ड्यासबोर्डमा लगइन गर्न सक्नुहुन्छ',
                'सबै सेवाहरू प्रयोग गर्न सकिनेछ'
            ],
            'rejected': [
                'तपाईंको आवेदन अस्वीकृत भयो',
                'कृपया सम्पर्क गर्नुहोस्: info@bhanjyangcoop.com',
                'नयाँ आवेदन पेश गर्न सकिनेछ'
            ]
        }
        
        return next_steps_map.get(status, [])
