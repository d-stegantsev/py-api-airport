from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext as _


User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        attrs["username"] = attrs.get("email")
        return super().validate(attrs)


class PasswordConfirmationMixin(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        label=_("Confirm password")
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if (password or password2) and password != password2:
            raise serializers.ValidationError({
                "password": _("Error: Passwords don't match."),
                "password2": _("Error: Passwords don't match."),
            })
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number", "date_of_birth")


class UserCreateSerializer(PasswordConfirmationMixin,
                           serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "password2", "first_name", "last_name", "phone_number", "date_of_birth")

    def create(self, validated_data):
        validated_data.pop("password2", None)
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(PasswordConfirmationMixin,
                           serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        required=False
    )
    password2 = serializers.CharField(
        write_only=True,
        label=_("Confirm password"),
        required=False
    )

    class Meta:
        model = User
        fields = ("email", "password", "password2", "first_name", "last_name", "phone_number", "date_of_birth")

    def update(self, instance, validated_data):
        validated_data.pop("password2", None)
        new_password = validated_data.pop("password", None)
        if new_password:
            instance.set_password(new_password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
