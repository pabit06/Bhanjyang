"""Regression tests for contact migration history."""

import importlib


def test_squashed_initial_migration_declares_replaces():
    """
    contact.0001_initial squashes 0001–0008; without ``replaces`` Django cannot
    reconcile databases that already applied the old chain after the old files
    were removed from the repo (e60c3fe).
    """
    migration = importlib.import_module('apps.contact.migrations.0001_initial').Migration

    assert hasattr(migration, 'replaces'), 'Squashed migration must declare replaces'
    replaced = {name for _app, name in migration.replaces}
    assert replaced == {
        '0001_initial',
        '0002_contactsubmission_attachment',
        '0003_add_indexes',
        '0004_kymsubmission',
        '0005_add_database_indexes',
        '0006_add_office_location_model',
        '0007_privacypolicy',
        '0008_faq',
    }
