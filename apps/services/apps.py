from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServicesConfig(AppConfig):
    """
    App configuration for the 'services' application.

    This configuration sets the default auto field for models, specifies the app's
    name, and provides a human-readable verbose name for the Django admin interface.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services'
    # IMPROVEMENT: Changed verbose_name to be human-readable for the admin panel.
    verbose_name = _("Financial Services")
