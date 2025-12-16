from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.gallery.services import GalleryService

User = get_user_model()

class GalleryServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teststaff', password='password', is_staff=True)
        self.album = GalleryAlbum.objects.create(name="Test Album", is_active=True)
        self.image = GalleryImage.objects.create(
            title="Test Image", album=self.album, is_active=True,
            image="test.jpg"
        )

    def test_get_gallery_home_data(self):
        data = GalleryService.get_gallery_home_data()
        self.assertIn('albums', data)
        self.assertIn('gallery_images', data)
        self.assertEqual(len(data['albums']), 1)
        self.assertEqual(len(data['gallery_images']), 1)

    def test_get_analytics_data(self):
        data = GalleryService.get_analytics_data()
        self.assertEqual(data['total_views'], 0)
        
        GalleryService.record_interaction(
            self.image.id, 'view', {'ip': '127.0.0.1'}
        )
        
        data = GalleryService.get_analytics_data()
        self.assertEqual(data['total_views'], 1)

    def test_record_interaction(self):
        res = GalleryService.record_interaction(self.image.id, 'like', {'ip': '127.0.0.1', 'session': 'abc'})
        self.assertTrue(res['success'])
        self.assertEqual(res['like_count'], 1)
        
        res = GalleryService.record_interaction(self.image.id, 'like', {'ip': '127.0.0.1', 'session': 'abc'})
        self.assertEqual(res['like_count'], 0)
