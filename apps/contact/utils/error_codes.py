"""
Error codes for the Contact app.
"""
from typing import Dict

class ContactErrorCodes:
    SUBMISSION_ERROR = 'CONTACT_SUBMISSION_ERROR'
    VALIDATION_ERROR = 'CONTACT_VALIDATION_ERROR'
    FORM_VALIDATION_ERROR = 'CONTACT_FORM_VALIDATION_ERROR'
    RATE_LIMIT_EXCEEDED = 'CONTACT_RATE_LIMIT_EXCEEDED'
    SPAM_DETECTED = 'CONTACT_SPAM_DETECTED'
    HONEYPOT_FILLED = 'CONTACT_HONEYPOT_FILLED'
    FILE_UPLOAD_ERROR = 'CONTACT_FILE_UPLOAD_ERROR'
    FILE_SIZE_EXCEEDED = 'CONTACT_FILE_SIZE_EXCEEDED'
    INVALID_FILE_TYPE = 'CONTACT_INVALID_FILE_TYPE'
    EMAIL_SEND_ERROR = 'CONTACT_EMAIL_SEND_ERROR'
    DATABASE_ERROR = 'CONTACT_DATABASE_ERROR'
    PDF_GENERATION_ERROR = 'PDF_GENERATION_ERROR'
    AJAX_REQUIRED = 'CONTACT_AJAX_REQUIRED'
    INVALID_REQUEST = 'CONTACT_INVALID_REQUEST'

ERROR_STATUS_MAP: Dict[str, int] = {
    ContactErrorCodes.SUBMISSION_ERROR: 500,
    ContactErrorCodes.VALIDATION_ERROR: 400,
    ContactErrorCodes.FORM_VALIDATION_ERROR: 400,
    ContactErrorCodes.RATE_LIMIT_EXCEEDED: 429,
    ContactErrorCodes.SPAM_DETECTED: 403,
    ContactErrorCodes.HONEYPOT_FILLED: 403,
    ContactErrorCodes.FILE_UPLOAD_ERROR: 400,
    ContactErrorCodes.FILE_SIZE_EXCEEDED: 400,
    ContactErrorCodes.INVALID_FILE_TYPE: 400,
    ContactErrorCodes.EMAIL_SEND_ERROR: 500,
    ContactErrorCodes.DATABASE_ERROR: 500,
    ContactErrorCodes.PDF_GENERATION_ERROR: 500,
    ContactErrorCodes.AJAX_REQUIRED: 400,
    ContactErrorCodes.INVALID_REQUEST: 400,
}

def get_status_code_for_error(error_code: str) -> int:
    return ERROR_STATUS_MAP.get(error_code, 500)

def get_user_friendly_message(error_code: str) -> str:
    messages = {
        ContactErrorCodes.SUBMISSION_ERROR: 'An error occurred while processing your submission. Please try again.',
        ContactErrorCodes.VALIDATION_ERROR: 'Please check your input and try again.',
        ContactErrorCodes.FORM_VALIDATION_ERROR: 'Please fill in all required fields correctly.',
        ContactErrorCodes.RATE_LIMIT_EXCEEDED: 'Too many requests. Please wait a moment before trying again.',
        ContactErrorCodes.SPAM_DETECTED: 'Your submission was flagged as spam. Please contact us directly if you believe this is an error.',
        ContactErrorCodes.HONEYPOT_FILLED: 'Invalid submission detected.',
        ContactErrorCodes.FILE_UPLOAD_ERROR: 'An error occurred while uploading your file. Please try again.',
        ContactErrorCodes.FILE_SIZE_EXCEEDED: 'File size exceeds the maximum allowed limit.',
        ContactErrorCodes.INVALID_FILE_TYPE: 'File type not allowed. Please check the allowed file types.',
        ContactErrorCodes.EMAIL_SEND_ERROR: 'Your submission was received, but we encountered an error sending the confirmation email.',
        ContactErrorCodes.DATABASE_ERROR: 'A database error occurred. Please try again later.',
        ContactErrorCodes.PDF_GENERATION_ERROR: 'An error occurred while generating the PDF. Please try again.',
        ContactErrorCodes.AJAX_REQUIRED: 'This endpoint only accepts AJAX requests.',
        ContactErrorCodes.INVALID_REQUEST: 'Invalid request. Please try again.',
    }
    return messages.get(error_code, 'An unexpected error occurred. Please try again.')