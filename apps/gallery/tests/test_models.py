from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.gallery.models import GalleryAlbum, GalleryImage
from django.core.exceptions import ValidationError
import tempfile
import shutil

class GalleryModelTest(TestCase):
    def setUp(self):
        # Create temporary directory for media
        self.test_image_path = tempfile.mkdtemp()
        
        # Create a sample image content
        self.image_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_image_path)

    def test_album_creation(self):
        """Test basic album creation"""
        album = GalleryAlbum.objects.create(
            name="Test Album",
            description="Test Description"
        )
        self.assertEqual(album.name, "Test Album")
        self.assertEqual(album.description, "Test Description")
        self.assertTrue(album.is_active)
        self.assertEqual(str(album), "Test Album")

    def test_nested_album_path(self):
        """Test nested album path generation"""
        parent = GalleryAlbum.objects.create(name="Parent")
        child = GalleryAlbum.objects.create(name="Child", parent_album=parent)
        grandchild = GalleryAlbum.objects.create(name="Grandchild", parent_album=child)
        
        self.assertEqual(grandchild.get_path(), "Parent / Child / Grandchild")

    def test_image_creation(self):
        """Test basic image creation"""
        album = GalleryAlbum.objects.create(name="Test Album")
        image_file = SimpleUploadedFile(
            name='test_image.png',
            content=self.image_content,
            content_type='image/png'
        )
        
        image = GalleryImage.objects.create(
            title="Test Image",
            album=album,
            image=image_file,
            category='events'
        )
        
        self.assertEqual(image.title, "Test Image")
        self.assertEqual(image.album, album)
        self.assertEqual(image.category, 'events')
        self.assertEqual(str(image), "Test Image")
        
    def test_image_validation_invalid_extension(self):
        """Test image validation with invalid extension"""
        image_file = SimpleUploadedFile(
            name='test_image.txt',
            content=b'invalid content',
            content_type='text/plain'
        )
        
        image = GalleryImage(
            title="Invalid Image",
            image=image_file
        )
        
        with self.assertRaises(ValidationError):
            image.full_clean()
            
    def test_get_album_path(self):
        """Test getting album path from image"""
        album = GalleryAlbum.objects.create(name="Test Album")
        image_file = SimpleUploadedFile(
            name='test_image.png',
            content=self.image_content,
            content_type='image/png'
        )
        
        image = GalleryImage.objects.create(
            title="Test Image",
            album=album,
            image=image_file
        )
        
        self.assertEqual(image.get_album_path(), "Test Album")
        
        image_no_album = GalleryImage.objects.create(
            title="Orphan Image",
            image=image_file
        )
        self.assertEqual(image_no_album.get_album_path(), "No Album")
