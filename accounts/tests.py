import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        defaults = {
            "email": "user@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        defaults.update(kwargs)
        user = User.objects.create_user(
            email=defaults["email"],
            password=defaults["password"],
            first_name=defaults.get("first_name"),
            last_name=defaults.get("last_name"),
            phone_number=defaults.get("phone_number", ""),
            date_of_birth=defaults.get("date_of_birth"),
        )
        return user
    return make_user

@pytest.fixture
def user(create_user):
    return create_user()

@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        email="admin@example.com",
        password="AdminPass123!"
    )
    print("ADMIN USER CREATED:", user.is_staff, user.is_superuser)
    return user

@pytest.mark.django_db
def test_signup(api_client):
    url = reverse("v1:accounts:accounts-signup")
    data = {
        "email": "newuser@example.com",
        "password": "NewPass123!",
        "password2": "NewPass123!",
        "first_name": "Alice",
        "last_name": "Smith",
        "phone_number": "+380931234567",
        "date_of_birth": "1990-01-01"
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="newuser@example.com").exists()

@pytest.mark.django_db
def test_signup_passwords_do_not_match(api_client):
    url = reverse("v1:accounts:accounts-signup")
    data = {
        "email": "fail@example.com",
        "password": "Password1!",
        "password2": "Password2!",
        "first_name": "Fail",
        "last_name": "Test"
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_token_obtain(api_client, user):
    url = reverse("v1:accounts:token_obtain_pair")
    data = {"email": user.email, "password": "TestPass123!"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_user_list_admin_only(api_client, admin_user, user):
    url = reverse("v1:accounts:accounts-list")
    # Unauthorized
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Auth as regular user
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Auth as admin
    api_client.force_authenticate(user=admin_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_me_endpoint_get_patch(api_client, user):
    url = reverse("v1:accounts:accounts-me")
    # Not auth
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Auth
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email

    # Update profile
    patch_data = {"first_name": "Updated"}
    response = api_client.patch(url, patch_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["first_name"] == "Updated"

@pytest.mark.django_db
def test_change_password(api_client, user):
    url = reverse("v1:accounts:accounts-password")
    api_client.force_authenticate(user=user)
    data = {
        "old_password": "TestPass123!",
        "new_password": "NewPass1234!",
        "new_password2": "NewPass1234!"
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NewPass1234!")

@pytest.mark.django_db
def test_set_admin_rights(api_client, admin_user, user):
    url = reverse("v1:accounts:accounts-set-admin", kwargs={"pk": user.pk})
    api_client.force_authenticate(user=admin_user)
    data = {"is_staff": True, "is_superuser": False}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_staff

@pytest.mark.django_db
def test_permissions_for_non_admin(api_client, user):
    api_client.force_authenticate(user=user)
    # Try list
    url = reverse("v1:accounts:accounts-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # Try set admin
    url = reverse("v1:accounts:accounts-set-admin", kwargs={"pk": user.pk})
    response = api_client.post(url, {"is_staff": True})
    assert response.status_code == status.HTTP_403_FORBIDDEN