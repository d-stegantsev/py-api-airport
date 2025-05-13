from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

api_v1_patterns = [
    path("airport/", include("airport.urls")),
    path("accounts/", include("accounts.urls")),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "v1"), namespace="v1")),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
