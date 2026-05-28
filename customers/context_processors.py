from django.conf import settings


def brand(request):
    return {
        "brand_name": getattr(settings, "VILLAGE_TECH_BRAND", "Village Tech"),
        "brand_phone": getattr(settings, "VILLAGE_TECH_PHONE", ""),
    }
