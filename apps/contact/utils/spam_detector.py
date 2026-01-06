"""
Spam Detection Utilities

Service for detecting spam content in contact form submissions.

Author: Bhanjyang Tech Team
Created: 2026-01-06
"""

import re
import logging

logger = logging.getLogger(__name__)

class SpamDetectionService:
    """Service to detect spam in text content."""
    
    # Common spam keywords (English and attempts at others)
    SPAM_KEYWORDS = [
        'casino', 'viagra', 'cryptocurrency', 'bitcoin', 'investment',
        'lottery', 'prize', 'winner', 'click here', 'buy now',
        'seo ranking', 'marketing service', 'dating', 'singles'
    ]
    
    @classmethod
    def is_spam(cls, content):
        """
        Check if content contains spam indicators.
        
        Args:
            content (str): Text content to check
            
        Returns:
            bool: True if spam detected, False otherwise
        """
        if not content:
            return False
            
        content_lower = content.lower()
        
        # Check keywords
        for keyword in cls.SPAM_KEYWORDS:
            if keyword in content_lower:
                logger.info(f"Spam detected (keyword '{keyword}'): {content[:50]}...")
                return True
        
        # Check for excessive links (more than 2)
        link_count = len(re.findall(r'http[s]?://', content_lower))
        if link_count > 2:
             logger.info(f"Spam detected (excessive links): {content[:50]}...")
             return True
             
        return False
