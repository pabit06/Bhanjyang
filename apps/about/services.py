"""
Service layer for the About app.

Handles business logic, data fetching, caching, and data aggregation
for all About Us related functionality.
"""
import logging
from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any, List, Optional

from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Committee, Staff, Person
)
from .constants import CACHE_TIMEOUT_MEDIUM, ERROR_UNABLE_TO_LOAD
from apps.core.view_mixins import create_breadcrumbs

logger = logging.getLogger(__name__)

class AboutService:
    """
    Service Layer for the About App.
    
    Handles data fetching, caching, and business logic for 'About Us' related pages
    including cooperative information, timeline, affiliations, and team data.
    Implements caching strategies to improve performance.
    
    All methods are static for easy access without instantiation.
    """

    # =============================================================================
    # Data Retrieval Methods
    # =============================================================================

    @staticmethod
    def get_about_home_data(is_staff: bool = False) -> Dict[str, Any]:
        """
        Retrieve all data required for the main About Us page.
        
        NOTE: This method is currently not used in views but kept for:
        - Potential future use (e.g., API endpoints, dashboard)
        - Backward compatibility with tests
        - Reference implementation for similar data aggregation
        
        Args:
            is_staff: If True, bypasses cache and shows all content including inactive items
            
        Returns:
            Dictionary containing cooperative info, timeline, stats, etc.
        """
        cache_key = f'about_home_data_{is_staff}'
        cached_data = cache.get(cache_key)
        
        if cached_data and not is_staff:
            return cached_data

        try:
            # Use published() manager for status-based filtering
            info = CooperativeInfo.objects.filter(status=CooperativeInfo.Status.PUBLISHED).first()
            timeline = list(CooperativeTimeline.objects.filter(
                status=CooperativeTimeline.Status.PUBLISHED, is_featured=True
            )[:6])
            stats = list(CooperativeStatistic.objects.filter(
                status=CooperativeStatistic.Status.PUBLISHED
            ).order_by('order'))
            affiliations = list(CooperativeAffiliation.objects.filter(
                status=CooperativeAffiliation.Status.PUBLISHED, is_featured=True
            ))
            messages = list(LeadershipMessage.objects.filter(
                status=LeadershipMessage.Status.PUBLISHED
            ).order_by('order'))
            
            # Counts
            total_committees = Committee.objects.filter(is_active=True).count()
            total_staff = Staff.objects.filter(is_active=True).count()

            context = {
                'cooperative_info': info,
                'timeline_events': timeline,
                'statistics': stats,
                'affiliations': affiliations,
                'leadership_messages': messages,
                'total_committees': total_committees,
                'total_staff': total_staff,
                'breadcrumbs': create_breadcrumbs(
                    (_('Home'), 'home:index'),
                    (_('About Us'), None)
                )
            }

            if not is_staff:
                try:
                    cache.set(cache_key, context, CACHE_TIMEOUT_MEDIUM)
                except Exception as e:
                    logger.warning(f"Failed to cache about data: {e}")
            
            return context

        except Exception as e:
            logger.error(f"Error fetching about home data: {e}", exc_info=True)
            return {'error': str(ERROR_UNABLE_TO_LOAD)}

    @staticmethod
    def get_timeline_events() -> QuerySet[CooperativeTimeline]:
        """
        Retrieve all published timeline events ordered by date (newest first).
        
        Returns:
            QuerySet of CooperativeTimeline objects
        """
        return CooperativeTimeline.objects.filter(
            status=CooperativeTimeline.Status.PUBLISHED
        ).order_by('-event_date')

    @staticmethod
    def get_affiliations() -> QuerySet[CooperativeAffiliation]:
        """
        Retrieve all published affiliations ordered by display order.
        
        Returns:
            QuerySet of CooperativeAffiliation objects
        """
        return CooperativeAffiliation.objects.filter(
            status=CooperativeAffiliation.Status.PUBLISHED
        ).order_by('order')

    @staticmethod
    def get_leadership_messages() -> QuerySet[LeadershipMessage]:
        """
        Retrieve all active leadership messages ordered by display order.
        
        Returns:
            QuerySet of LeadershipMessage objects
        """
        return LeadershipMessage.objects.active().order_by('order')

    @staticmethod
    def get_active_team() -> tuple[QuerySet[Committee], QuerySet[Staff]]:
        """
        Retrieve active committees and staff members with optimized queries.
        Uses prefetch_related and select_related to avoid N+1 queries.
        
        Returns:
            Tuple of (committees QuerySet, staff QuerySet)
        """
        committees = Committee.objects.filter(is_active=True).prefetch_related('memberships__person')
        staff = Staff.objects.filter(is_active=True).select_related('person')
        return committees, staff

    @staticmethod
    def get_past_committees() -> QuerySet[Committee]:
        """
        Retrieve inactive (past) committees ordered by tenure.
        
        Returns:
            QuerySet of inactive Committee objects
        """
        return Committee.objects.filter(is_active=False).order_by('-tenure_bs').prefetch_related('memberships__person')

    # =============================================================================
    # Search and Statistics Methods
    # =============================================================================

    @staticmethod
    def get_search_results(query: str) -> Dict[str, Any]:
        """
        Perform a global search across about app models.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with search results grouped by model type
        """
        results = {
            'query': query,
            'cooperative_info': list(CooperativeInfo.objects.filter(
                status=CooperativeInfo.Status.PUBLISHED
            ).filter(
                Q(cooperative_name__icontains=query) |
                Q(description__icontains=query) |
                Q(mission__icontains=query) |
                Q(vision__icontains=query)
            )[:5]),
            'timeline': list(CooperativeTimeline.objects.filter(
                status=CooperativeTimeline.Status.PUBLISHED
            ).filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:5]),
            'affiliations': list(CooperativeAffiliation.objects.filter(
                status=CooperativeAffiliation.Status.PUBLISHED
            ).filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:5]),
            'leadership': list(LeadershipMessage.objects.filter(
                status=LeadershipMessage.Status.PUBLISHED
            ).filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author_name__icontains=query)
            )[:5]),
            'team': list(Person.objects.filter(is_active=True).filter(
                Q(full_name__icontains=query) |
                Q(bio__icontains=query) |
                Q(position_general__icontains=query)
            )[:5])
        }
        return results

    @staticmethod
    def get_site_statistics() -> Dict[str, Any]:
        """
        Get aggregated site statistics.
        
        Returns:
            Dictionary with counts for all models and last_updated timestamp
        """
        return {
            'cooperative_info_count': CooperativeInfo.objects.filter(status=CooperativeInfo.Status.PUBLISHED).count(),
            'timeline_events_count': CooperativeTimeline.objects.filter(status=CooperativeTimeline.Status.PUBLISHED).count(),
            'affiliations_count': CooperativeAffiliation.objects.filter(status=CooperativeAffiliation.Status.PUBLISHED).count(),
            'leadership_messages_count': LeadershipMessage.objects.filter(status=LeadershipMessage.Status.PUBLISHED).count(),
            'team_members_count': Person.objects.filter(is_active=True).count(),
            'committees_count': Committee.objects.filter(is_active=True).count(),
            'staff_count': Staff.objects.filter(is_active=True).count(),
            'last_updated': timezone.now().isoformat()
        }
