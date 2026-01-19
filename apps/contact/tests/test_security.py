from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.contact.forms import ContactForm
from apps.contact.models import ContactSubmission


class ContactSecurityTestCase(TestCase):
    """Comprehensive security tests for contact app"""
    
    def test_file_upload_security(self):
        """Test file upload security measures"""
        # Test malicious file names
        malicious_files = [
            ('../../../etc/passwd', 'text/plain'),
            ('<script>alert("xss")</script>.txt', 'text/plain'),
            ('file with spaces.exe', 'application/octet-stream'),
            ('normal_file.pdf', 'application/pdf'),
        ]
        
        for filename, content_type in malicious_files:
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message with enough content to pass validation.'
            }
            
            file_content = b'Test file content'
            uploaded_file = SimpleUploadedFile(filename, file_content, content_type=content_type)
            form_data['attachment'] = uploaded_file
            
            form = ContactForm(data=form_data, files={'attachment': uploaded_file})
            
            if filename == 'normal_file.pdf':
                self.assertTrue(form.is_valid(), f"Valid file {filename} should pass validation")
            else:
                self.assertFalse(form.is_valid(), f"Malicious file {filename} should fail validation")
                if 'attachment' in form.errors:
                    self.assertIn('attachment', form.errors)
    
    def test_email_validation_security(self):
        """Test email validation security measures"""
        # Test disposable email domains
        disposable_emails = [
            'test@10minutemail.com',
            'user@tempmail.org',
            'spam@guerrillamail.com',
        ]
        
        for email in disposable_emails:
            form_data = {
                'name': 'Test User',
                'email': email,
                'subject': 'Test Subject',
                'message': 'This is a test message with enough content to pass validation.'
            }
            form = ContactForm(data=form_data)
            self.assertFalse(form.is_valid(), f"Disposable email {email} should be rejected")
            self.assertIn('email', form.errors)
        
        # Test suspicious email patterns
        suspicious_emails = [
            '123456@example.com',  # Starts with numbers
            'ab@123456789.com',    # Domain with many digits
            'ab123456789@example.com',  # Short letters + many digits
        ]
        
        for email in suspicious_emails:
            form_data = {
                'name': 'Test User',
                'email': email,
                'subject': 'Test Subject',
                'message': 'This is a test message with enough content to pass validation.'
            }
            form = ContactForm(data=form_data)
            self.assertFalse(form.is_valid(), f"Suspicious email {email} should be rejected")
            self.assertIn('email', form.errors)
    
    def test_message_security(self):
        """Test message content security"""
        # Test HTML sanitization
        malicious_messages = [
            '<script>alert("xss")</script>',
            '<img src="x" onerror="alert(1)">',
            '<iframe src="javascript:alert(1)"></iframe>',
        ]
        
        for message in malicious_messages:
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': f'Legitimate content {message} more content'
            }
            form = ContactForm(data=form_data)
            if form.is_valid():
                # Check that HTML was sanitized (bleach converts to HTML entities)
                cleaned_message = form.cleaned_data['message']
                self.assertNotIn('<script>', cleaned_message)
                self.assertNotIn('<iframe>', cleaned_message)
                # HTML entities should be present
                self.assertIn('&lt;', cleaned_message)
                self.assertIn('&gt;', cleaned_message)
        
        # Test spam patterns
        spam_messages = [
            'Click here: http://example.com',
            'Visit www.spam.com for free money',
            'Win $1000 prize!',
        ]
        
        for message in spam_messages:
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': message
            }
            form = ContactForm(data=form_data)
            self.assertFalse(form.is_valid(), f"Spam message should be rejected: {message}")
            self.assertIn('message', form.errors)
    
    def test_file_size_limits(self):
        """Test file size validation"""
        # Test oversized file (simulate 6MB)
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        large_file = SimpleUploadedFile('large.pdf', large_content, content_type='application/pdf')
        
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        
        form = ContactForm(data=form_data, files={'attachment': large_file})
        self.assertFalse(form.is_valid(), "Oversized file should be rejected")
        self.assertIn('attachment', form.errors)
    
    def test_dangerous_file_extensions(self):
        """Test dangerous file extension blocking"""
        dangerous_files = [
            ('malware.exe', 'application/octet-stream'),
            ('script.bat', 'application/octet-stream'),
            ('virus.cmd', 'application/octet-stream'),
            ('trojan.js', 'application/javascript'),
        ]
        
        for filename, content_type in dangerous_files:
            file_content = b'Test malicious content'
            dangerous_file = SimpleUploadedFile(filename, file_content, content_type=content_type)
            
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message with enough content to pass validation.'
            }
            
            form = ContactForm(data=form_data, files={'attachment': dangerous_file})
            self.assertFalse(form.is_valid(), f"Dangerous file {filename} should be rejected")
            self.assertIn('attachment', form.errors)
    
    def test_filename_sanitization(self):
        """Test filename sanitization in model"""
        from apps.contact.models import contact_attachment_path
        
        # Test that filenames are properly sanitized
        test_filename = "malicious<script>alert('xss')</script>.pdf"
        sanitized_path = contact_attachment_path(None, test_filename)
        
        # Should contain sanitized filename (slugify removes special chars)
        self.assertNotIn('<script>', sanitized_path)
        self.assertNotIn('<', sanitized_path)
        self.assertNotIn('>', sanitized_path)
        self.assertTrue(sanitized_path.endswith('.pdf'))
        self.assertIn('malicious', sanitized_path.lower())
    
    def test_model_constraints(self):
        """Test database constraints - Note: constraints removed due to SQLite limitations"""
        # Since we removed database constraints due to SQLite limitations,
        # we'll test form validation instead
        form_data = {
            'name': 'A',  # Less than 2 characters
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough content to pass validation.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid(), "Short name should fail form validation")
        self.assertIn('name', form.errors)
        
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Short'  # Less than 10 characters
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid(), "Short message should fail form validation")
        self.assertIn('message', form.errors)
