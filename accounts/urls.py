from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from accounts.views import EmailTokenObtainPairView, UserViewSet

app_name = "accounts"

router = DefaultRouter()
router.register("", UserViewSet, basename="account")

urlpatterns = [
    path("", include(router.urls)),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]