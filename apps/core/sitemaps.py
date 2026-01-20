"""
Dynamic sitemap generation for SEO.
Automatically includes all published content from various apps.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from apps.news_events.models import NewsArticle, Event
from apps.services.models import (
    SavingsAccount, LoanType, FixedDeposit,
    RemittanceService, MemberRelief, DigitalService
)
from apps.gallery.models import GalleryAlbum
from apps.downloads.models import DownloadableFile


class StaticPagesSitemap(Sitemap):
    """Static pages that don't have models"""
    changefreq = 'weekly'
    
    def items(self):
        return [
            {'name': 'home:index', 'priority': 1.0, 'changefreq': 'daily'},
            {'name': 'about:introduction', 'priority': 0.9, 'changefreq': 'monthly'},
            {'name': 'services:overview', 'priority': 0.9, 'changefreq': 'weekly'},
            {'name': 'contact:contact_view', 'priority': 0.8, 'changefreq': 'monthly'},
            {'name': 'news_events:home', 'priority': 0.8, 'changefreq': 'daily'},
            {'name': 'downloads:download_center', 'priority': 0.7, 'changefreq': 'weekly'},
            {'name': 'gallery:album_list', 'priority': 0.7, 'changefreq': 'weekly'},
        ]
    
    def location(self, item):
        return reverse(item['name'])
    
    def priority(self, item):
        return item.get('priority', 0.5)
    
    def changefreq(self, item):
        return item.get('changefreq', 'monthly')


class NewsArticleSitemap(Sitemap):
    """News articles sitemap"""
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return NewsArticle.objects.filter(
            status='PB'  # Published
        ).order_by('-published_date')
    
    def lastmod(self, obj):
        return obj.updated_at or obj.published_date
    
    def location(self, obj):
        return reverse('news_events:article_detail', args=[obj.slug])


class EventSitemap(Sitemap):
    """Events sitemap"""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return Event.objects.filter(
            is_active=True,
            event_date__gte=timezone.now()
        ).order_by('event_date')
    
    def lastmod(self, obj):
        return obj.updated_at or obj.created_at
    
    def location(self, obj):
        return reverse('news_events:event_detail', args=[obj.slug])


class SavingsAccountSitemap(Sitemap):
    """Savings accounts sitemap"""
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return SavingsAccount.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('services:savings_detail', args=[obj.slug])


class LoanTypeSitemap(Sitemap):
    """Loan types sitemap"""
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return LoanType.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('services:loan_detail', args=[obj.slug])


class FixedDepositSitemap(Sitemap):
    """Fixed deposits sitemap"""
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return FixedDeposit.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('services:fixed_deposit_detail', args=[obj.slug])


class RemittanceServiceSitemap(Sitemap):
    """Remittance services sitemap"""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return RemittanceService.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('services:remittance_detail', args=[obj.slug])


class DigitalServiceSitemap(Sitemap):
    """Digital services sitemap"""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return DigitalService.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('services:digital_detail', args=[obj.slug])


class MemberReliefSitemap(Sitemap):
    """Member relief services sitemap"""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return MemberRelief.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('services:relief_detail', args=[obj.slug])


class GalleryAlbumSitemap(Sitemap):
    """Gallery albums sitemap"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return GalleryAlbum.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at or obj.created_at
    
    def location(self, obj):
        return reverse('gallery:album_detail', args=[obj.slug])


class DocumentSitemap(Sitemap):
    """Documents sitemap"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return DownloadableFile.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at or obj.uploaded_at
    
    def location(self, obj):
        return reverse('downloads:file_detail', args=[obj.pk])
