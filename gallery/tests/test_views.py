from django.test import TestCase, Client
from django.urls import reverse
from gallery.models import GalleryAlbum, GalleryImage
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import shutil

class GalleryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_image_path = tempfile.mkdtemp()
        
        self.image_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        self.album = GalleryAlbum.objects.create(name="Test Album")
        
        self.image = GalleryImage.objects.create(
            title="Test Image",
            album=self.album,
            image=SimpleUploadedFile(
                name='test_image.png',
                content=self.image_content,
                content_type='image/png'
            ),
            category='events',
            is_active=True
        )

    def tearDown(self):
        shutil.rmtree(self.test_image_path)

    def test_gallery_view_status_code(self):
        """Test that gallery home page returns 200"""
        response = self.client.get(reverse('gallery:gallery'))
        self.assertEqual(response.status_code, 200)

    def test_gallery_view_context(self):
        """Test that gallery view context contains expected data"""
        response = self.client.get(reverse('gallery:gallery'))
        self.assertTrue('gallery_images' in response.context)
        self.assertTrue('albums' in response.context)
        self.assertTrue('categories' in response.context)
        
        # Check if our image is in the context
        images = response.context['gallery_images']
        self.assertTrue(any(img.id == self.image.id for img in images))

    def test_album_detail_view(self):
        """Test album detail view"""
        response = self.client.get(reverse('gallery:album_detail', args=[self.album.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['album'], self.album)

    def test_api_search(self):
        """Test search API"""
        response = self.client.get(reverse('gallery:gallery_search_api'), {'query': 'Test'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(len(data['images']) > 0)
        self.assertEqual(data['images'][0]['title'], "Test Image")

