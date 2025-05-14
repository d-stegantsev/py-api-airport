from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

User = get_user_model()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'JWT example',
            summary='Example token response',
            value={
                'refresh': 'string',
                'access': 'string',
            },
            response_only=True,
        )
    ]
)
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for obtaining JWT tokens using email as the username field.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)


class PasswordConfirmationMixin(serializers.Serializer):
    """
    Mixin to enforce entering password twice for confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text='Password (write-only).'
    )
    password2 = serializers.CharField(
        write_only=True,
        label='Confirm password',
        help_text='Confirm password (write-only).'
    )

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.',
                'password2': 'Passwords do not match.',
            })
        return attrs


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Profile example',
            summary='User profile response',
            value={
                'email': 'user@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+1234567890',
                'date_of_birth': '1990-01-01'
            },
            response_only=True,
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth')
        extra_kwargs = {
            'email': {'help_text': "User's unique email address."},
            'first_name': {'help_text': 'First name.'},
            'last_name': {'help_text': 'Last name.'},
            'phone_number': {'help_text': 'Mobile phone number.'},
            'date_of_birth': {'help_text': 'Date of birth (YYYY-MM-DD).'},
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Create user example',
            summary='User creation request and response',
            value={
                'email': 'new@example.com',
                'password': 'Password123!',
                'password2': 'Password123!',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'phone_number': '+19876543210',
                'date_of_birth': '1992-02-02'
            }
        )
    ]
)
class UserCreateSerializer(PasswordConfirmationMixin, serializers.ModelSerializer):
    """
    Serializer for registering a new user account.
    """
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone_number', 'date_of_birth')
        extra_kwargs = {
            'email': {'help_text': 'Email address for registration.'},
        }

    def create(self, validated_data):
        validated_data.pop('password2', None)
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile. Excludes password fields.
    """
    email = serializers.EmailField(
        read_only=True,
        help_text='Read-only email identifier.'
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth')
        extra_kwargs = {
            'first_name': {'help_text': 'First name.'},
            'last_name': {'help_text': 'Last name.'},
            'phone_number': {'help_text': 'Mobile phone number.'},
            'date_of_birth': {'help_text': 'Date of birth (YYYY-MM-DD).'},
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Change password example',
            summary='Password change request',
            value={
                'old_password': 'OldPass123!',
                'new_password': 'NewPass456!',
                'new_password2': 'NewPass456!'
            }
        )
    ]
)
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        write_only=True,
        help_text='Current password (write-only).'
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text='New password (write-only).'
    )
    new_password2 = serializers.CharField(
        write_only=True,
        label='Confirm new password',
        help_text='Confirm new password (write-only).'
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password2'):
            raise serializers.ValidationError({
                'new_password': 'Passwords do not match.',
                'new_password2': 'Passwords do not match.',
            })
        return attrs
