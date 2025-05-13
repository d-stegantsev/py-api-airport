from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.serializers import (
    EmailTokenObtainPairSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserSerializer,
)
from base.mixins import BaseViewSetMixin


User = get_user_model()


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class UserViewSet(BaseViewSetMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    action_serializers = {
        "create": UserCreateSerializer,
        "update": UserUpdateSerializer,
    }

    action_permissions = {
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "list": [IsAuthenticated],
    }
