"""Tests for contact migration graph integrity."""
import importlib

from django.test import TestCase


class ContactMigrationGraphTest(TestCase):
    """Squashed contact migration must declare replaced migrations for existing DBs."""

    def test_squashed_migration_declares_replaces(self):
        migration = importlib.import_module(
            'apps.contact.migrations.0001_initial'
        ).Migration
        self.assertTrue(hasattr(migration, 'replaces'))
        self.assertEqual(len(migration.replaces), 8)
        self.assertEqual(migration.replaces[0], ('contact', '0001_initial'))
        self.assertEqual(migration.replaces[-1], ('contact', '0008_faq'))
