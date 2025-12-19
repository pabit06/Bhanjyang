"""
Pytest configuration and shared fixtures for integration tests.
"""
import pytest
from django.test import Client
from django.contrib.auth import get_user_model


@pytest.fixture
def client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    User = get_user_model()
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    User = get_user_model()
    return User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123'
    )

