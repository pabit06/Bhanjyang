"""
Members Exceptions

Custom exceptions for the Members app.
These exceptions provide specific error handling
for different types of failures in the member system.
"""


class MemberServiceException(Exception):
    """Base exception for member service operations."""
    pass


class ValidationException(MemberServiceException):
    """Exception raised for validation errors."""
    pass


class KYCServiceException(MemberServiceException):
    """Exception raised for KYC-related errors."""
    pass


class CBSConnectionException(MemberServiceException):
    """Exception raised for CBS connection errors."""
    pass


class CBSServiceException(MemberServiceException):
    """Exception raised for CBS service errors."""
    pass


class NotificationServiceException(MemberServiceException):
    """Exception raised for notification service errors."""
    pass


class AccountServiceException(MemberServiceException):
    """Exception raised for account service errors."""
    pass


class MemberNotFoundException(MemberServiceException):
    """Exception raised when a member is not found."""
    pass


class RegistrationNotFoundException(MemberServiceException):
    """Exception raised when a registration is not found."""
    pass


class AccountNotFoundException(MemberServiceException):
    """Exception raised when an account is not found."""
    pass


class InsufficientBalanceException(AccountServiceException):
    """Exception raised when account has insufficient balance."""
    pass


class InvalidTransactionException(AccountServiceException):
    """Exception raised for invalid transaction operations."""
    pass


class DocumentValidationException(KYCServiceException):
    """Exception raised for document validation errors."""
    pass


class VerificationException(KYCServiceException):
    """Exception raised for verification process errors."""
    pass
