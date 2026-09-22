from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "TrustyHomes Admin"
admin.site.site_title = "TrustyHomes Admin"
admin.site.index_title = "Manage listings, agents & reports"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("agents/", include("agents.urls")),
    path("properties/", include("listings.urls")),
    path("notifications/", include("notifications.urls")),
    path("messages/", include("messaging.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
