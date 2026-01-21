from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel
from apps.downloads.views import DownloadCenterView, DownloadFileView, FileDetailView

class DownloadsRefactorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.file = DownloadableFile.objects.create(
            title="Test File",
            file=SimpleUploadedFile("test.pdf", b"content"),
            category=FileCategory.FORM,
            priority=PriorityLevel.HIGH,
            is_active=True,
            is_featured=True
        )

    def test_download_center_cbv(self):
        response = self.client.get(reverse('downloads:download_center'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('files_by_category', response.context)
        self.assertIn('featured_files', response.context)

    def test_file_detail_cbv(self):
        response = self.client.get(reverse('downloads:file_detail', args=[self.file.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['file'], self.file)

    def test_download_file_cbv(self):
        response = self.client.get(reverse('downloads:download_file', args=[self.file.id]))
        # Should redirect to the secure serve url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('downloads:serve_file', kwargs={'pk': self.file.pk}))

    def test_download_file_cbv_permission(self):
        self.file.requires_login = True
        self.file.save()
        # Anonymous
        response = self.client.get(reverse('downloads:download_file', args=[self.file.id]))
        self.assertEqual(response.status_code, 403)
        
        # Authenticated
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('downloads:download_file', args=[self.file.id]))
        self.assertEqual(response.status_code, 302)

