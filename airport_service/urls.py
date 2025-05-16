from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView

api_v1_patterns = [
    path("airport/", include("airport.urls")),
    path("accounts/", include("accounts.urls")),

# Schema & Docs
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="v1:schema"),
        name="swagger",
    ),
    path(
        "docs/redoc/", SpectacularRedocView.as_view(url_name="v1:schema"), name="redoc"
    ),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "v1"), namespace="v1")),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
