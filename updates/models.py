from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

# Helper function to calculate read time
def calculate_read_time(content):
    if not content:
        return 0
    word_count = len(content.split())
    # Assumes an average reading speed of 200 words per minute
    read_time = (word_count + 199) // 200
    return max(1, read_time) # Ensure a minimum of 1 minute read time

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('updates:article-by-category', args=[self.slug])

class NewsArticle(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_articles')
    image = models.ImageField(upload_to='updates/images/', blank=True, null=True)
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    # NEW: read_time field to store the calculated value
    read_time = models.PositiveIntegerField(default=0, editable=False, help_text="Estimated read time in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ['-published_date']
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('updates:detail', kwargs={'slug': self.slug})

    # MODIFIED: save method now automatically calculates and saves the read_time
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Calculate read time based on content before saving
        if self.content:
            self.read_time = calculate_read_time(self.content)
        super().save(*args, **kwargs)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=150, default="Cooperative Office")
    event_date = models.DateTimeField()
    
    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
