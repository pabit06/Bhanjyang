"""
Tests for gallery app admin classes
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from apps.gallery.models import (
    GalleryImage, GalleryAlbum, GalleryImageLike, GalleryImageComment,
    GalleryImageShare, GalleryImageDownload, SmartCollection,
    SmartCollectionImage, AutoCategorizationRule, ImageAnalysisJob
)
from apps.gallery.admin import (
    GalleryAlbumAdmin, GalleryImageAdmin, SmartCollectionAdmin,
    SmartCollectionImageAdmin, AutoCategorizationRuleAdmin, ImageAnalysisJobAdmin
)


class GalleryAdminTestCase(TestCase):
    """Base test case for gallery admin tests"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.request = self.factory.get('/admin/')
        self.request.user = self.admin_user
        
        # Add session and messages middleware for admin actions
        SessionMiddleware(lambda req: None).process_request(self.request)
        MessageMiddleware(lambda req: None).process_request(self.request)
        self.request._messages = FallbackStorage(self.request)
        
        self.album = GalleryAlbum.objects.create(
            name='Test Album',
            description='Test description',
            is_active=True
        )


class GalleryAlbumAdminTest(GalleryAdminTestCase):
    """Test GalleryAlbumAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = GalleryAlbumAdmin(GalleryAlbum, self.site)
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
        self.assertIn('get_image_count', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('is_featured', self.admin.list_filter)
        self.assertIn('is_active', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('description', self.admin.search_fields)
    
    def test_list_editable(self):
        """Test list editable fields"""
        self.assertIn('is_featured', self.admin.list_editable)
        self.assertIn('is_active', self.admin.list_editable)
        self.assertIn('order', self.admin.list_editable)
    
    def test_get_path(self):
        """Test get_path method"""
        result = self.admin.get_path(self.album)
        self.assertIsNotNone(result)
    
    def test_get_image_count(self):
        """Test get_image_count method"""
        result = self.admin.get_image_count(self.album)
        self.assertIsInstance(result, int)
    
    def test_get_sub_album_count(self):
        """Test get_sub_album_count method"""
        result = self.admin.get_sub_album_count(self.album)
        self.assertIsInstance(result, int)


class GalleryImageAdminTest(GalleryAdminTestCase):
    """Test GalleryImageAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = GalleryImageAdmin(GalleryImage, self.site)
        self.image = GalleryImage.objects.create(
            title='Test Image',
            album=self.album,
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('title', self.admin.list_display)
        self.assertIn('album', self.admin.list_display)
        self.assertIn('is_featured', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('is_featured', self.admin.list_filter)
        self.assertIn('is_active', self.admin.list_filter)
        self.assertIn('category', self.admin.list_filter)
    
    def test_search_fields(self):
        """Test search fields"""
        self.assertIn('title', self.admin.search_fields)
        self.assertIn('description', self.admin.search_fields)
    
    def test_list_editable(self):
        """Test list editable fields"""
        self.assertIn('is_featured', self.admin.list_editable)
        self.assertIn('is_active', self.admin.list_editable)
    
    def test_get_thumbnail(self):
        """Test get_thumbnail method"""
        result = self.admin.get_thumbnail(self.image)
        self.assertIsNotNone(result)
    
    def test_get_thumbnail_link(self):
        """Test get_thumbnail_link method"""
        result = self.admin.get_thumbnail_link(self.image)
        self.assertIsNotNone(result)
    
    def test_mark_as_featured_action(self):
        """Test mark as featured action"""
        queryset = GalleryImage.objects.filter(id=self.image.id)
        self.admin.mark_as_featured(self.request, queryset)
        self.image.refresh_from_db()
        self.assertTrue(self.image.is_featured)
    
    def test_mark_as_unfeatured_action(self):
        """Test mark as unfeatured action"""
        self.image.is_featured = True
        self.image.save()
        queryset = GalleryImage.objects.filter(id=self.image.id)
        self.admin.mark_as_unfeatured(self.request, queryset)
        self.image.refresh_from_db()
        self.assertFalse(self.image.is_featured)
    
    def test_mark_as_active_action(self):
        """Test mark as active action"""
        self.image.is_active = False
        self.image.save()
        queryset = GalleryImage.objects.filter(id=self.image.id)
        self.admin.mark_as_active(self.request, queryset)
        self.image.refresh_from_db()
        self.assertTrue(self.image.is_active)
    
    def test_mark_as_inactive_action(self):
        """Test mark as inactive action"""
        queryset = GalleryImage.objects.filter(id=self.image.id)
        self.admin.mark_as_inactive(self.request, queryset)
        self.image.refresh_from_db()
        self.assertFalse(self.image.is_active)
    
    def test_changelist_view(self):
        """Test changelist view"""
        response = self.admin.changelist_view(self.request)
        self.assertEqual(response.status_code, 200)


class SmartCollectionAdminTest(GalleryAdminTestCase):
    """Test SmartCollectionAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = SmartCollectionAdmin(SmartCollection, self.site)
        self.collection = SmartCollection.objects.create(
            name='Test Collection',
            description='Test description',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)
    
    def test_list_filter(self):
        """Test list filters"""
        self.assertIn('is_active', self.admin.list_filter)


class AutoCategorizationRuleAdminTest(GalleryAdminTestCase):
    """Test AutoCategorizationRuleAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = AutoCategorizationRuleAdmin(AutoCategorizationRule, self.site)
        self.rule = AutoCategorizationRule.objects.create(
            name='Test Rule',
            is_active=True
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('name', self.admin.list_display)
        self.assertIn('is_active', self.admin.list_display)


class ImageAnalysisJobAdminTest(GalleryAdminTestCase):
    """Test ImageAnalysisJobAdmin"""
    
    def setUp(self):
        super().setUp()
        self.admin = ImageAnalysisJobAdmin(ImageAnalysisJob, self.site)
        # Create image for the job
        self.image = GalleryImage.objects.create(
            title='Test Image',
            album=self.album,
            is_active=True
        )
        self.job = ImageAnalysisJob.objects.create(
            image=self.image,
            status='pending'
        )
    
    def test_list_display(self):
        """Test list display fields"""
        self.assertIn('image', self.admin.list_display)
        self.assertIn('status', self.admin.list_display)

