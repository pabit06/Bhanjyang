"""
Notification DTO

Data Transfer Object for notification operations.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class NotificationDTO:
    """DTO for notification data."""
    notification_type: str
    title: str
    message: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.notification_type:
            raise ValueError("Notification type is required")
        if not self.title:
            raise ValueError("Title is required")
        if not self.message:
            raise ValueError("Message is required")
        
        valid_types = ['info', 'warning', 'success', 'error']
        if self.notification_type not in valid_types:
            raise ValueError(f"Invalid notification type. Must be one of: {valid_types}")
