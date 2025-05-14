from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        label="Confirm password"
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({
                "password": "Error: Passwords don't match.",
                "password2": "Error: Passwords don't match.",
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


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number", "date_of_birth")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, label="Confirm new password")

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password2"):
            raise serializers.ValidationError({
                "new_password": "Passwords do not match.",
                "new_password2": "Passwords do not match.",
            })
        return attrs
