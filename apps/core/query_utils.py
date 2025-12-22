"""
Query utilities and managers for common database patterns.
"""
from typing import TypeVar, Type, List, Optional
from django.db import models
from django.db.models import QuerySet as DjangoQuerySet

ModelType = TypeVar('ModelType', bound=models.Model)


class ActiveManager(models.Manager):
    """Manager for active objects only."""
    
    def get_queryset(self) -> DjangoQuerySet:
        """Return only active objects."""
        return super().get_queryset().filter(is_active=True)


class FeaturedManager(ActiveManager):
    """Manager for featured active objects."""
    
    def get_queryset(self) -> DjangoQuerySet:
        """Return only featured active objects."""
        return super().get_queryset().filter(is_featured=True)


def get_active_queryset(
    model_class: Type[ModelType],
    fields: Optional[List[str]] = None,
    order_by: Optional[List[str]] = None
) -> DjangoQuerySet[ModelType]:
    """
    Get active queryset with optional field limiting and ordering.
    
    Args:
        model_class: The model class to query
        fields: Optional list of fields to fetch (uses only())
        order_by: Optional list of fields to order by
        
    Returns:
        QuerySet of active objects
    """
    queryset = model_class.objects.filter(is_active=True)
    
    if fields:
        queryset = queryset.only(*fields)
    
    if order_by:
        queryset = queryset.order_by(*order_by)
    
    return queryset


def get_featured_queryset(
    model_class: Type[ModelType],
    fields: Optional[List[str]] = None,
    limit: Optional[int] = None
) -> DjangoQuerySet[ModelType]:
    """
    Get featured active queryset with optional field limiting.
    
    Args:
        model_class: The model class to query
        fields: Optional list of fields to fetch (uses only())
        limit: Optional limit on number of results
        
    Returns:
        QuerySet of featured active objects
    """
    queryset = model_class.objects.filter(
        is_active=True,
        is_featured=True
    )
    
    if fields:
        queryset = queryset.only(*fields)
    
    if limit:
        queryset = queryset[:limit]
    
    return queryset

