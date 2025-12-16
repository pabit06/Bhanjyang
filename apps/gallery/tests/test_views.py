from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.gallery.models import GalleryAlbum, GalleryImage

User = get_user_model()

class GalleryViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.album = GalleryAlbum.objects.create(name="Test Album", is_active=True)
    
    def test_home_view(self):
        response = self.client.get(reverse('gallery:gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('albums', response.context)

    def test_api_interaction(self):
        img = GalleryImage.objects.create(title="T", album=self.album, is_active=True, image="t.jpg")
        url = reverse('gallery:gallery_interaction_api')
        
        resp = self.client.post(url, {'image_id': img.id, 'action': 'view'})
        self.assertEqual(resp.status_code, 200)
        img.refresh_from_db()
        self.assertEqual(img.views_count, 1)

    def test_staff_access_required(self):
        self.client.logout()
        resp = self.client.get(reverse('gallery:analytics'))
        self.assertNotEqual(resp.status_code, 200)
        self.assertEqual(resp.status_code, 302) 
        
        self.client.force_login(self.user)
        resp = self.client.get(reverse('gallery:analytics'))
        self.assertEqual(resp.status_code, 200)
