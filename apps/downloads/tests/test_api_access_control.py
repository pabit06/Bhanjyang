"""
Tests for downloads API access control and secure URL exposure.
"""
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.downloads.models import DownloadableFile, FileCategory


class DownloadsAPIAccessControlTest(TestCase):
    """Ensure API respects category-based access rules and secure URLs."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpass123',
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.pdf = SimpleUploadedFile(
            'report.pdf',
            b'%PDF-1.4 confidential',
            content_type='application/pdf',
        )

        self.public_form = DownloadableFile.objects.create(
            title='Public Form',
            file=SimpleUploadedFile('form.pdf', b'form', content_type='application/pdf'),
            category=FileCategory.FORM,
            is_active=True,
            requires_login=False,
        )
        self.financial_report = DownloadableFile.objects.create(
            title='Annual Report',
            file=self.pdf,
            category=FileCategory.REPORT,
            is_active=True,
            requires_login=False,
        )
        self.policy_doc = DownloadableFile.objects.create(
            title='Internal Policy',
            file=SimpleUploadedFile('policy.pdf', b'policy', content_type='application/pdf'),
            category=FileCategory.POLICY,
            is_active=True,
            requires_login=False,
        )

        self.list_url = reverse('file-list')

    def test_anonymous_list_excludes_restricted_categories(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        titles = {item['title'] for item in response.data['results']}
        self.assertIn('Public Form', titles)
        self.assertNotIn('Annual Report', titles)
        self.assertNotIn('Internal Policy', titles)

    def test_anonymous_list_uses_secure_serve_url(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        form_entry = next(
            item for item in response.data['results'] if item['title'] == 'Public Form'
        )
        self.assertIn(f'/downloads/{self.public_form.pk}/serve/', form_entry['file_url'])
        self.assertNotIn('/media/downloads/', form_entry['file_url'])

    def test_non_staff_cannot_retrieve_policy_document(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('file-detail', kwargs={'pk': self.policy_doc.pk})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 404)

    def test_download_action_returns_secure_url(self):
        self.client.force_authenticate(user=self.staff_user)
        download_url = reverse('file-download', kwargs={'pk': self.public_form.pk})

        response = self.client.post(download_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f'/downloads/{self.public_form.pk}/serve/',
            response.data['file_url'],
        )
        self.assertNotIn('/media/downloads/', response.data['file_url'])

    def test_anonymous_download_financial_report_forbidden(self):
        download_url = reverse('file-download', kwargs={'pk': self.financial_report.pk})

        response = self.client.post(download_url)

        self.assertEqual(response.status_code, 403)
