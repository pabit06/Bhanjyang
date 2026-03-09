from datetime import date
from types import SimpleNamespace

from apps.about.models import CooperativeInfo

# Fallback when no CooperativeInfo exists (e.g. fresh clone / new install).
# Templates expect site_info attributes; None would cause VariableDoesNotExist.
# Must match attributes/methods used in templates: established_date, introduction_text, get_years_display.
DEFAULT_SITE_INFO = SimpleNamespace(
    cooperative_name="Bhanjyang Saving & Credit Cooperative Society Ltd.",
    cooperative_name_nepali="भञ्ज्याङ्ग बचत तथा ऋण सहकारी संस्था लिमिटेड",
    meta_title=None,
    meta_description=None,
    meta_keywords=None,
    description="भञ्ज्याङ बचत तथा ऋण सहकारी संस्था लिमिटेडको मुख्य पृष्ठ।",
    description_nepali=None,
    address="Rupa R.M.-5, Deurali Bazar, Kaski",
    phone="+977 9856083101",
    email="info@bhanjyang.coop.np",
    website=None,
    featured_image=None,
    logo=None,
    og_image=None,
    established_date=date(1999, 1, 1),
    introduction_text="भञ्ज्याङ बचत तथा ऋण सहकारी संस्था लिमिटेडको मुख्य पृष्ठ। सहकारीले सदस्यहरूलाई बचत, ऋण र अन्य सेवाहरू प्रदान गर्दछ।",
    get_years_display="25+ Years",
)


def site_settings(request):
    """
    Context processor to make cooperative info available to all templates.
    Uses DEFAULT_SITE_INFO when no active CooperativeInfo exists (e.g. fresh DB).
    """
    info = CooperativeInfo.objects.active().first()
    return {'site_info': info if info is not None else DEFAULT_SITE_INFO}

