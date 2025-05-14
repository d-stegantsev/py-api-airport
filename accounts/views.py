from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from accounts.serializers import (
    EmailTokenObtainPairSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from accounts.throttles import TokenRateThrottle, SignupRateThrottle
from base.mixins import BaseViewSetMixin

User = get_user_model()


@extend_schema(
    summary="Obtain JWT token pair",
    description="Generate access and refresh JWT tokens by providing email and password.",
    request=EmailTokenObtainPairSerializer,
    responses={200: OpenApiResponse(description="Access and refresh tokens")},
)
class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint for user authentication and JWT token generation.
    """
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [TokenRateThrottle]


class UserViewSet(BaseViewSetMixin, ModelViewSet):
    """
    A viewset for user account management, including signup, profile retrieval/update, and password change.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    throttle_classes = [SignupRateThrottle]

    action_serializers = {
        "create": UserCreateSerializer,
        "retrieve": UserSerializer,
        "update": UserUpdateSerializer,
        "partial_update": UserUpdateSerializer,
        "signup": UserCreateSerializer,
        "me": UserUpdateSerializer,
        "password": ChangePasswordSerializer,
    }
    action_permissions = {
        "create": [IsAdminUser],
        "list": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
        "signup": [AllowAny],
        "me": [IsAuthenticated],
        "password": [IsAuthenticated],
    }

    @extend_schema(
        summary="Retrieve or update own profile",
        description="GET retrieves the authenticated user profile; PATCH updates first name, last name, phone number, and date of birth.",
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
    )
    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
        else:
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="User signup",
        description="Register a new user by providing email, password, password confirmation, first name, last name, phone number, and date of birth.",
        request=UserCreateSerializer,
        responses={201: UserSerializer},
    )
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Change password",
        description="Change the password of the authenticated user. Requires old_password, new_password, and new_password2 for confirmation.",
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Password updated successfully")},
    )
    @action(detail=False, methods=["post"], url_path="password")
    def password(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
