"""
Advanced Full-Text Search for News Events App.

Provides PostgreSQL full-text search capabilities with ranking and highlighting.
"""
from typing import Dict, Any, List, Optional
from django.db.models import Q, QuerySet, F
from django.db import connection
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, TrigramSimilarity
)
from django.core.cache import cache
import logging

from .models import NewsArticle, Event, Category

logger = logging.getLogger(__name__)


class AdvancedSearchService:
    """Service for advanced full-text search functionality."""
    
    @staticmethod
    def is_postgresql() -> bool:
        """Check if database is PostgreSQL."""
        return 'postgresql' in connection.vendor.lower()
    
    @staticmethod
    def full_text_search_articles(
        query: str,
        limit: int = 20,
        category_id: Optional[int] = None,
        featured_only: bool = False
    ) -> QuerySet:
        """
        Perform full-text search on articles using PostgreSQL search vectors.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            category_id: Optional category filter
            featured_only: Filter featured articles only
            
        Returns:
            QuerySet of matching articles ordered by relevance
        """
        if not AdvancedSearchService.is_postgresql():
            # Fallback to basic search if not PostgreSQL
            logger.warning("Full-text search requires PostgreSQL. Using basic search.")
            return AdvancedSearchService._basic_search_articles(query, limit, category_id, featured_only)
        
        try:
            # Create search vector from multiple fields
            search_vector = SearchVector('title', weight='A', config='english') + \
                          SearchVector('excerpt', weight='B', config='english') + \
                          SearchVector('content', weight='C', config='english')
            
            # Create search query
            search_query = SearchQuery(query, config='english')
            
            # Build base queryset
            articles = NewsArticle.objects.filter(
                status=NewsArticle.Status.PUBLISHED
            ).annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query)
            
            # Apply filters
            if category_id:
                articles = articles.filter(category_id=category_id)
            if featured_only:
                articles = articles.filter(is_featured=True)
            
            # Order by rank and published date
            articles = articles.order_by('-rank', '-published_date')[:limit]
            
            return articles
            
        except Exception as e:
            logger.error(f"Full-text search error: {e}")
            return AdvancedSearchService._basic_search_articles(query, limit, category_id, featured_only)
    
    @staticmethod
    def _basic_search_articles(
        query: str,
        limit: int = 20,
        category_id: Optional[int] = None,
        featured_only: bool = False
    ) -> QuerySet:
        """Fallback basic search using icontains."""
        articles = NewsArticle.objects.filter(
            status=NewsArticle.Status.PUBLISHED
        ).filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        )
        
        if category_id:
            articles = articles.filter(category_id=category_id)
        if featured_only:
            articles = articles.filter(is_featured=True)
        
        return articles.order_by('-published_date')[:limit]
    
    @staticmethod
    def full_text_search_events(
        query: str,
        limit: int = 20,
        event_type: Optional[str] = None,
        featured_only: bool = False
    ) -> QuerySet:
        """
        Perform full-text search on events using PostgreSQL search vectors.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            event_type: Optional event type filter
            featured_only: Filter featured events only
            
        Returns:
            QuerySet of matching events ordered by relevance
        """
        if not AdvancedSearchService.is_postgresql():
            return AdvancedSearchService._basic_search_events(query, limit, event_type, featured_only)
        
        try:
            search_vector = SearchVector('title', weight='A', config='english') + \
                          SearchVector('short_description', weight='B', config='english') + \
                          SearchVector('description', weight='C', config='english')
            
            search_query = SearchQuery(query, config='english')
            
            events = Event.objects.filter(
                status=Event.Status.PUBLISHED
            ).annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query)
            
            if event_type:
                events = events.filter(event_type=event_type)
            if featured_only:
                events = events.filter(is_featured=True)
            
            events = events.order_by('-rank', '-event_date')[:limit]
            
            return events
            
        except Exception as e:
            logger.error(f"Full-text search error: {e}")
            return AdvancedSearchService._basic_search_events(query, limit, event_type, featured_only)
    
    @staticmethod
    def _basic_search_events(
        query: str,
        limit: int = 20,
        event_type: Optional[str] = None,
        featured_only: bool = False
    ) -> QuerySet:
        """Fallback basic search for events."""
        events = Event.objects.filter(
            status=Event.Status.PUBLISHED
        ).filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )
        
        if event_type:
            events = events.filter(event_type=event_type)
        if featured_only:
            events = events.filter(is_featured=True)
        
        return events.order_by('-event_date')[:limit]
    
    @staticmethod
    def similarity_search(
        query: str,
        content_type: str = 'articles',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search using trigram similarity.
        Useful for finding similar content even with typos.
        
        Args:
            query: Search query string
            content_type: 'articles' or 'events'
            limit: Maximum number of results
            
        Returns:
            List of dictionaries with content and similarity score
        """
        if not AdvancedSearchService.is_postgresql():
            return []
        
        try:
            if content_type == 'articles':
                results = NewsArticle.objects.filter(
                    status=NewsArticle.Status.PUBLISHED
                ).annotate(
                    similarity=TrigramSimilarity('title', query) +
                              TrigramSimilarity('excerpt', query) * 0.5
                ).filter(similarity__gt=0.1).order_by('-similarity')[:limit]
                
                return [
                    {
                        'article': article,
                        'similarity': article.similarity,
                        'type': 'article'
                    }
                    for article in results
                ]
            else:
                results = Event.objects.filter(
                    status=Event.Status.PUBLISHED
                ).annotate(
                    similarity=TrigramSimilarity('title', query) +
                              TrigramSimilarity('short_description', query) * 0.5
                ).filter(similarity__gt=0.1).order_by('-similarity')[:limit]
                
                return [
                    {
                        'event': event,
                        'similarity': event.similarity,
                        'type': 'event'
                    }
                    for event in results
                ]
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    @staticmethod
    def advanced_search(
        query: str,
        content_type: str = 'all',
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Perform advanced search with full-text search and filters.
        
        Args:
            query: Search query string
            content_type: 'all', 'articles', or 'events'
            filters: Dictionary of additional filters
            limit: Maximum number of results per content type
            
        Returns:
            Dictionary with search results and metadata
        """
        filters = filters or {}
        
        results = {
            'query': query,
            'articles': [],
            'events': [],
            'total_results': 0,
            'search_type': 'full-text' if AdvancedSearchService.is_postgresql() else 'basic'
        }
        
        # Search articles
        if content_type in ['all', 'articles']:
            articles = AdvancedSearchService.full_text_search_articles(
                query=query,
                limit=limit,
                category_id=filters.get('category_id'),
                featured_only=filters.get('featured_only', False)
            )
            results['articles'] = list(articles)
        
        # Search events
        if content_type in ['all', 'events']:
            events = AdvancedSearchService.full_text_search_events(
                query=query,
                limit=limit,
                event_type=filters.get('event_type'),
                featured_only=filters.get('featured_only', False)
            )
            results['events'] = list(events)
        
        results['total_results'] = len(results['articles']) + len(results['events'])
        
        return results

