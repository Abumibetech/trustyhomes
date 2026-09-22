from django.conf import settings


def site_settings(request):
    return {
        "SITE_WHATSAPP_NUMBER": settings.SITE_WHATSAPP_NUMBER,
        "SITE_NAME": settings.SITE_NAME,
    }
