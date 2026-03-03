"""
Comprehensive tests for contact app models
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date, timedelta
from apps.contact.models import ContactSubmission


class ContactSubmissionModelTest(TestCase):
    """Test suite for ContactSubmission model"""
    
    def setUp(self):
        """Set up test data"""
        self.submission = ContactSubmission.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            subject="Test Subject",
            message="Test message content",
            ip_address="192.168.1.1",
            user_agent="Test User Agent"
        )
    
    def test_submission_creation(self):
        """Test basic submission creation"""
        self.assertEqual(self.submission.name, "John Doe")
        self.assertEqual(self.submission.email, "john@example.com")
        self.assertEqual(self.submission.status, "new")
        self.assertIsNotNone(self.submission.created_at)
    
    def test_str_representation(self):
        """Test string representation"""
        expected = f"John Doe - Test Subject ({self.submission.created_at.strftime('%Y-%m-%d')})"
        self.assertEqual(str(self.submission), expected)
    
    def test_status_choices(self):
        """Test status choices"""
        statuses = ['new', 'in_progress', 'resolved', 'spam']
        for status in statuses:
            submission = ContactSubmission.objects.create(
                name="Test User",
                email=f"test{status}@example.com",
                subject="Test",
                message="Test",
                ip_address="192.168.1.1",
                status=status
            )
            self.assertEqual(submission.status, status)
    
    def test_get_status_display_color(self):
        """Test get_status_display_color method"""
        self.submission.status = 'new'
        self.assertEqual(self.submission.get_status_display_color(), 'text-blue-600')
        
        self.submission.status = 'in_progress'
        self.assertEqual(self.submission.get_status_display_color(), 'text-yellow-600')
        
        self.submission.status = 'resolved'
        self.assertEqual(self.submission.get_status_display_color(), 'text-green-600')
        
        self.submission.status = 'spam'
        self.assertEqual(self.submission.get_status_display_color(), 'text-red-600')
    
    def test_is_recent(self):
        """Test is_recent method"""
        # Recent submission (just created)
        self.assertTrue(self.submission.is_recent())
        
        # Old submission
        old_submission = ContactSubmission.objects.create(
            name="Old User",
            email="old@example.com",
            subject="Old",
            message="Old",
            ip_address="192.168.1.1"
        )
        # Manually set created_at to 2 days ago
        old_submission.created_at = timezone.now() - timedelta(days=2)
        old_submission.save()
        self.assertFalse(old_submission.is_recent())
    
    def test_mark_as_resolved(self):
        """Test mark_as_resolved method"""
        self.submission.mark_as_resolved()
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, 'resolved')
        self.assertIsNotNone(self.submission.resolved_at)
    
    def test_mark_as_spam(self):
        """Test mark_as_spam method"""
        self.submission.mark_as_spam()
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, 'spam')
    
    def test_has_attachment(self):
        """Test has_attachment method"""
        # No attachment
        self.assertFalse(self.submission.has_attachment())
        
        # With attachment
        test_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
        submission_with_file = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test",
            ip_address="192.168.1.1",
            attachment=test_file
        )
        self.assertTrue(submission_with_file.has_attachment())
    
    def test_get_attachment_filename(self):
        """Test get_attachment_filename method"""
        # No attachment
        self.assertIsNone(self.submission.get_attachment_filename())
        
        # With attachment
        test_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
        submission_with_file = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test",
            ip_address="192.168.1.1",
            attachment=test_file
        )
        filename = submission_with_file.get_attachment_filename()
        self.assertIsNotNone(filename)
        self.assertIn("test", filename.lower())
    
    def test_get_attachment_size(self):
        """Test get_attachment_size method"""
        # No attachment
        self.assertEqual(self.submission.get_attachment_size(), 0)
        
        # With attachment
        test_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
        submission_with_file = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test",
            ip_address="192.168.1.1",
            attachment=test_file
        )
        size = submission_with_file.get_attachment_size()
        self.assertGreater(size, 0)
    
    def test_get_attachment_size_display(self):
        """Test get_attachment_size_display method"""
        # No attachment
        self.assertEqual(self.submission.get_attachment_size_display(), "No attachment")
        
        # With attachment
        test_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
        submission_with_file = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test",
            ip_address="192.168.1.1",
            attachment=test_file
        )
        size_display = submission_with_file.get_attachment_size_display()
        self.assertIn("B", size_display)
        self.assertNotEqual(size_display, "No attachment")
    
    def test_ordering(self):
        """Test model ordering"""
        submission2 = ContactSubmission.objects.create(
            name="Second User",
            email="second@example.com",
            subject="Second",
            message="Second",
            ip_address="192.168.1.2"
        )
        submissions = list(ContactSubmission.objects.all())
        # Should be ordered by -created_at (newest first)
        self.assertEqual(submissions[0], submission2)
        self.assertEqual(submissions[1], self.submission)

