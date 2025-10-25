"""
Comprehensive API views for the Bhanjyang Cooperative services.
"""
import logging
from typing import Dict, Any, List
from decimal import Decimal
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
# from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample  # Commented out until installed

from .models import (
    SavingsAccount, FixedDeposit, LoanType, RemittanceService, 
    MemberRelief, ServiceApplication, ServiceAnalytics, ServiceRecommendation
)
from .serializers import (
    SavingsAccountSerializer, FixedDepositSerializer, LoanTypeSerializer,
    RemittanceServiceSerializer, MemberReliefSerializer, ServiceApplicationSerializer,
    ServiceAnalyticsSerializer, ServiceRecommendationSerializer, ServiceCalculatorSerializer,
    ServiceSearchSerializer
)

logger = logging.getLogger(__name__)


class ServicePagination(PageNumberPagination):
    """Custom pagination for service endpoints."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SavingsAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for Savings Account management."""
    
    queryset = SavingsAccount.objects.filter(is_active=True)
    serializer_class = SavingsAccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'is_featured', 'interest_rate']
    search_fields = ['english_name', 'nepali_name', 'description']
    ordering_fields = ['english_name', 'interest_rate', 'created_at']
    ordering = ['-is_featured', 'interest_rate']
    
    # @extend_schema(
    #     summary="Get featured savings accounts",
    #     description="Retrieve all featured savings accounts",
    #     responses={200: SavingsAccountSerializer(many=True)}
    # )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured savings accounts."""
        featured_accounts = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_accounts, many=True)
        return Response(serializer.data)
    
    # @extend_schema(
    #     summary="Calculate interest for savings account",
    #     description="Calculate interest for a given amount and duration",
    #     parameters=[
    #         OpenApiParameter(name='amount', description='Principal amount', required=True, type=float),
    #         OpenApiParameter(name='months', description='Duration in months', required=True, type=int),
    #     ],
    #     responses={200: {'description': 'Interest calculation result'}}
    # )
    @action(detail=True, methods=['get'])
    def calculate_interest(self, request, pk=None):
        """Calculate interest for a savings account."""
        account = self.get_object()
        amount = request.query_params.get('amount')
        months = request.query_params.get('months')
        
        if not amount or not months:
            return Response(
                {'error': 'Amount and months parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(amount)
            months = int(months)
            
            if amount <= 0 or months <= 0:
                return Response(
                    {'error': 'Amount and months must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate interest
            annual_rate = account.interest_rate / 100
            interest = amount * annual_rate * (months / 12)
            total_amount = amount + interest
            
            result = {
                'principal': float(amount),
                'interest_rate': float(account.interest_rate),
                'duration_months': months,
                'interest_amount': float(interest),
                'total_amount': float(total_amount),
                'account': account.english_name
            }
            
            return Response(result)
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': 'Invalid amount or months value'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FixedDepositViewSet(viewsets.ModelViewSet):
    """ViewSet for Fixed Deposit management."""
    
    queryset = FixedDeposit.objects.filter(is_active=True)
    serializer_class = FixedDepositSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['duration_months', 'payment_frequency', 'interest_rate']
    search_fields = ['benefits']
    ordering_fields = ['duration_months', 'interest_rate', 'created_at']
    ordering = ['duration_months', 'interest_rate']
    
    # @extend_schema(
    #     summary="Get fixed deposits by duration",
    #     description="Retrieve fixed deposits filtered by duration",
    #     parameters=[
    #         OpenApiParameter(name='duration', description='Duration in months', required=True, type=int),
    #     ],
    #     responses={200: FixedDepositSerializer(many=True)}
    # )
    @action(detail=False, methods=['get'])
    def by_duration(self, request):
        """Get fixed deposits by duration."""
        duration = request.query_params.get('duration')
        if not duration:
            return Response(
                {'error': 'Duration parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            duration = int(duration)
            deposits = self.queryset.filter(duration_months=duration)
            serializer = self.get_serializer(deposits, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Invalid duration value'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoanTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for Loan Type management."""
    
    queryset = LoanType.objects.filter(is_active=True)
    serializer_class = LoanTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['loan_category', 'is_featured', 'monthly_interest_rate']
    search_fields = ['english_name', 'nepali_name', 'description']
    ordering_fields = ['english_name', 'monthly_interest_rate', 'created_at']
    ordering = ['-is_featured', 'english_name']
    
    # @extend_schema(
    #     summary="Calculate monthly payment for loan",
    #     description="Calculate monthly payment for a loan",
    #     parameters=[
    #         OpenApiParameter(name='amount', description='Loan amount', required=True, type=float),
    #         OpenApiParameter(name='months', description='Loan duration in months', required=True, type=int),
    #     ],
    #     responses={200: {'description': 'Monthly payment calculation result'}}
    # )
    @action(detail=True, methods=['get'])
    def calculate_payment(self, request, pk=None):
        """Calculate monthly payment for a loan."""
        loan_type = self.get_object()
        amount = request.query_params.get('amount')
        months = request.query_params.get('months')
        
        if not amount or not months:
            return Response(
                {'error': 'Amount and months parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(amount)
            months = int(months)
            
            if amount <= 0 or months <= 0:
                return Response(
                    {'error': 'Amount and months must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check loan limits
            if loan_type.minimum_amount and amount < loan_type.minimum_amount:
                return Response(
                    {'error': f'Amount must be at least {loan_type.minimum_amount}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if loan_type.maximum_amount and amount > loan_type.maximum_amount:
                return Response(
                    {'error': f'Amount cannot exceed {loan_type.maximum_amount}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate monthly payment using simple interest formula
            monthly_rate = loan_type.monthly_interest_rate / 100
            monthly_payment = amount * monthly_rate + (amount / months)
            total_payment = monthly_payment * months
            total_interest = total_payment - amount
            
            result = {
                'loan_amount': float(amount),
                'monthly_rate': float(loan_type.monthly_interest_rate),
                'duration_months': months,
                'monthly_payment': float(monthly_payment),
                'total_payment': float(total_payment),
                'total_interest': float(total_interest),
                'loan_type': loan_type.english_name
            }
            
            return Response(result)
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': 'Invalid amount or months value'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RemittanceServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Remittance Service management."""
    
    queryset = RemittanceService.objects.filter(is_active=True)
    serializer_class = RemittanceServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service_type', 'is_featured']
    search_fields = ['english_name', 'nepali_name', 'description']
    ordering_fields = ['english_name', 'created_at']
    ordering = ['-is_featured', 'english_name']


class MemberReliefViewSet(viewsets.ModelViewSet):
    """ViewSet for Member Relief management."""
    
    queryset = MemberRelief.objects.filter(is_active=True)
    serializer_class = MemberReliefSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['relief_type', 'is_featured']
    search_fields = ['english_name', 'nepali_name', 'description', 'eligibility']
    ordering_fields = ['english_name', 'created_at']
    ordering = ['-is_featured', 'english_name']


class ServiceApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Service Application management."""
    
    queryset = ServiceApplication.objects.all()
    serializer_class = ServiceApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'content_type']
    search_fields = ['applicant_name', 'applicant_email', 'service_name']
    ordering_fields = ['applied_date', 'status']
    ordering = ['-applied_date']
    
    def perform_create(self, serializer):
        """Set the applicant information when creating an application."""
        serializer.save()
        logger.info(f"New service application created: {serializer.instance.id}")
    
    # @extend_schema(
    #     summary="Get applications by status",
    #     description="Retrieve applications filtered by status",
    #     parameters=[
    #         OpenApiParameter(name='status', description='Application status', required=True, type=str),
    #     ],
    #     responses={200: ServiceApplicationSerializer(many=True)}
    # )
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get applications by status."""
        status_filter = request.query_params.get('status')
        if not status_filter:
            return Response(
                {'error': 'Status parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = self.queryset.filter(status=status_filter)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)


class ServiceAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Service Analytics (read-only)."""
    
    queryset = ServiceAnalytics.objects.all()
    serializer_class = ServiceAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['content_type', 'date']
    ordering_fields = ['date', 'page_views', 'applications_received']
    ordering = ['-date']


class ServiceRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Service Recommendations (read-only)."""
    
    queryset = ServiceRecommendation.objects.all()
    serializer_class = ServiceRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ServicePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['confidence_score', 'created_at']
    ordering = ['-confidence_score', '-created_at']


class ServiceSearchViewSet(viewsets.ViewSet):
    """ViewSet for comprehensive service search."""
    
    permission_classes = [permissions.AllowAny]
    
    # @extend_schema(
    #     summary="Search services",
    #     description="Search across all service types",
    #     request=ServiceSearchSerializer,
    #     responses={200: {'description': 'Search results'}}
    # )
    def list(self, request):
        """Search across all service types."""
        serializer = ServiceSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        results = {}
        
        # Search savings accounts
        if not data.get('service_type') or data['service_type'] == 'savings':
            savings_qs = SavingsAccount.objects.filter(is_active=True)
            if data.get('query'):
                savings_qs = savings_qs.filter(
                    Q(english_name__icontains=data['query']) |
                    Q(nepali_name__icontains=data['query']) |
                    Q(description__icontains=data['query'])
                )
            if data.get('is_featured') is not None:
                savings_qs = savings_qs.filter(is_featured=data['is_featured'])
            if data.get('min_interest_rate'):
                savings_qs = savings_qs.filter(interest_rate__gte=data['min_interest_rate'])
            if data.get('max_interest_rate'):
                savings_qs = savings_qs.filter(interest_rate__lte=data['max_interest_rate'])
            
            results['savings_accounts'] = SavingsAccountSerializer(savings_qs[:10], many=True).data
        
        # Search loan types
        if not data.get('service_type') or data['service_type'] == 'loan':
            loan_qs = LoanType.objects.filter(is_active=True)
            if data.get('query'):
                loan_qs = loan_qs.filter(
                    Q(english_name__icontains=data['query']) |
                    Q(nepali_name__icontains=data['query']) |
                    Q(description__icontains=data['query'])
                )
            if data.get('is_featured') is not None:
                loan_qs = loan_qs.filter(is_featured=data['is_featured'])
            
            results['loan_types'] = LoanTypeSerializer(loan_qs[:10], many=True).data
        
        # Search fixed deposits
        if not data.get('service_type') or data['service_type'] == 'fixed_deposit':
            fd_qs = FixedDeposit.objects.filter(is_active=True)
            if data.get('query'):
                fd_qs = fd_qs.filter(benefits__icontains=data['query'])
            
            results['fixed_deposits'] = FixedDepositSerializer(fd_qs[:10], many=True).data
        
        # Search remittance services
        if not data.get('service_type') or data['service_type'] == 'remittance':
            remit_qs = RemittanceService.objects.filter(is_active=True)
            if data.get('query'):
                remit_qs = remit_qs.filter(
                    Q(english_name__icontains=data['query']) |
                    Q(nepali_name__icontains=data['query']) |
                    Q(description__icontains=data['query'])
                )
            
            results['remittance_services'] = RemittanceServiceSerializer(remit_qs[:10], many=True).data
        
        # Search member relief
        if not data.get('service_type') or data['service_type'] == 'relief':
            relief_qs = MemberRelief.objects.filter(is_active=True)
            if data.get('query'):
                relief_qs = relief_qs.filter(
                    Q(english_name__icontains=data['query']) |
                    Q(nepali_name__icontains=data['query']) |
                    Q(description__icontains=data['query']) |
                    Q(eligibility__icontains=data['query'])
                )
            
            results['member_relief'] = MemberReliefSerializer(relief_qs[:10], many=True).data
        
        return Response(results)
