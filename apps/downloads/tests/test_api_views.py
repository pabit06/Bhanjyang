"""
Tests for downloads REST API access control and secure URLs.
"""
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.downloads.models import DownloadableFile, FileCategory


class DownloadableFileAPITest(TestCase):
    """API must not expose direct /media/ URLs for restricted files."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='member', password='pass')
        self.staff = User.objects.create_user(
            username='staff', password='pass', is_staff=True
        )
        self.file_content = SimpleUploadedFile(
            'report.pdf', b'%PDF-1.4 test', content_type='application/pdf'
        )
        self.public_report = DownloadableFile.objects.create(
            category=FileCategory.REPORT,
            title='Annual Report',
            file=self.file_content,
            is_active=True,
            requires_login=False,
        )
        self.public_doc = DownloadableFile.objects.create(
            category=FileCategory.FORM,
            title='Application Form',
            file=SimpleUploadedFile(
                'form.pdf', b'%PDF-1.4 form', content_type='application/pdf'
            ),
            is_active=True,
            requires_login=False,
        )

    def test_list_excludes_financial_reports_for_anonymous_users(self):
        response = self.client.get('/api/v1/downloads/files/')
        self.assertEqual(response.status_code, 200)
        ids = [item['id'] for item in response.data['results']]
        self.assertNotIn(self.public_report.id, ids)
        self.assertIn(self.public_doc.id, ids)

    def test_list_file_url_uses_secure_serve_path(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/v1/downloads/files/')
        self.assertEqual(response.status_code, 200)
        report = next(
            item for item in response.data['results']
            if item['id'] == self.public_report.id
        )
        self.assertIn('/downloads/', report['file_url'])
        self.assertIn('/serve/', report['file_url'])
        self.assertNotIn('/media/downloads/', report['file_url'])

    def test_download_action_returns_secure_url(self):
        self.client.force_authenticate(user=self.staff)
        url = f'/api/v1/downloads/files/{self.public_report.pk}/download/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        file_url = response.data['file_url']
        self.assertIn('/downloads/', file_url)
        self.assertIn('/serve/', file_url)
        self.assertNotIn('/media/downloads/', file_url)
