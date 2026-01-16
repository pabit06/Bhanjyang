"""
Integration tests for the Bhanjyang Cooperative application.

These tests verify that multiple components work together correctly,
including views, models, forms, and services.
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.test import override_settings


@pytest.mark.django_db
class TestHomePageIntegration:
    """Integration tests for the home page."""
    
    def test_home_page_loads(self, client):
        """Test that the home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Bhanjyang' in response.content.decode()


@pytest.mark.django_db
class TestContactFormIntegration:
    """Integration tests for contact form."""
    
    def test_contact_page_loads(self, client):
        """Test that the contact page loads successfully."""
        response = client.get('/contact/')
        assert response.status_code == 200
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_contact_form_submission(self, client):
        """Test contact form submission."""
        url = reverse('contact:contact_view')
        response = client.post(url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


@pytest.mark.django_db
class TestDownloadsIntegration:
    """Integration tests for downloads functionality."""
    
    def test_downloads_page_loads(self, client):
        """Test that the downloads page loads successfully."""
        response = client.get('/downloads/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestNewsEventsIntegration:
    """Integration tests for news and events."""
    
    def test_news_events_page_loads(self, client):
        """Test that the news-events page loads successfully."""
        response = client.get('/news-events/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestServicesIntegration:
    """Integration tests for services."""
    
    def test_services_page_loads(self, client):
        """Test that the services page loads successfully."""
        response = client.get('/services/', follow=True)
        assert response.status_code == 200

