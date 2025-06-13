import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    SeatClass,
    Seat,
    Ticket,
    Order,
)
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
import uuid

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpass"
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@example.com", password="userpass")


@pytest.fixture
def airport_a(db):
    return Airport.objects.create(name="Kyiv Boryspil", closest_big_city="Kyiv")


@pytest.fixture
def airport_b(db):
    return Airport.objects.create(name="Lviv Danylo Halytskyi", closest_big_city="Lviv")


@pytest.fixture
def route(db, airport_a, airport_b):
    return Route.objects.create(source=airport_a, destination=airport_b, distance=500)


@pytest.fixture
def airplane_type(db):
    return AirplaneType.objects.create(name="Boeing 737", rows=5, seats_in_row=4)


@pytest.fixture
def airplane(db, airplane_type):
    return Airplane.objects.create(name="Boeing-123", airplane_type=airplane_type)


@pytest.fixture
def crew(db):
    return Crew.objects.create(first_name="John", last_name="Doe")


@pytest.fixture
def flight(db, route, airplane, crew):
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=timezone.now() + timedelta(days=1),
        arrival_time=timezone.now() + timedelta(days=1, hours=2),
    )
    flight.crew.add(crew)
    return flight


@pytest.fixture
def seat_class(db):
    return SeatClass.objects.create(name="Economy")


@pytest.fixture
def seat(db, airplane_type, seat_class):
    return Seat.objects.create(
        airplane_type=airplane_type, row=1, seat="A", seat_class=seat_class
    )


@pytest.fixture
def ticket(db, flight, seat, order):
    return Ticket.objects.create(flight=flight, seat=seat, order=order)


@pytest.fixture
def order(db, user):
    return Order.objects.create(user=user)


@pytest.mark.django_db
def test_airport_list(api_client, airport_a, airport_b):
    url = reverse("v1:airport:airport-list")
    response = api_client.get(url)
    assert response.status_code == 200
    results = response.data["results"]
    assert any(a["name"] == airport_a.name for a in results)


@pytest.mark.django_db
def test_airport_search(api_client, airport_a, airport_b):
    url = reverse("v1:airport:airport-list") + "?search=kyiv"
    response = api_client.get(url)
    assert response.status_code == 200
    results = response.data["results"]
    assert any("kyiv" in airport["closest_big_city"].lower() for airport in results)


@pytest.mark.django_db
def test_airport_filter(api_client, airport_a, airport_b):
    url = reverse("v1:airport:airport-list") + f"?name={airport_a.name}"
    response = api_client.get(url)
    assert response.status_code == 200
    results = response.data["results"]
    assert all(airport["name"] == airport_a.name for airport in results)


@pytest.mark.django_db
def test_route_create_by_admin(api_client, admin_user, airport_a, airport_b):
    api_client.force_authenticate(user=admin_user)
    url = reverse("v1:airport:route-list")
    payload = {
        "source": str(airport_a.id),
        "destination": str(airport_b.id),
        "distance": 123,
    }
    response = api_client.post(url, payload)
    assert response.status_code == 201
    assert response.data["distance"] == 123


@pytest.mark.django_db
def test_route_create_by_non_admin(api_client, user, airport_a, airport_b):
    api_client.force_authenticate(user=user)
    url = reverse("v1:airport:route-list")
    payload = {
        "source": str(airport_a.id),
        "destination": str(airport_b.id),
        "distance": 123,
    }
    response = api_client.post(url, payload)
    assert response.status_code == 403


@pytest.mark.django_db
def test_flight_filter_by_route(api_client, flight):
    url = reverse("v1:airport:flight-list") + f"?route={flight.route.id}"
    response = api_client.get(url)
    assert response.status_code == 200
    results = response.data["results"]
    assert any(
        f["route"]
        == f"{flight.route.source.name} ({flight.route.source.closest_big_city}) - {flight.route.destination.name} ({flight.route.destination.closest_big_city})"
        for f in results
    )


@pytest.mark.django_db
def test_flight_ordering(api_client, flight):
    url = reverse("v1:airport:flight-list") + "?ordering=departure_time"
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_booking(api_client, user, flight, seat):
    api_client.force_authenticate(user=user)
    url = reverse("v1:airport:order-list")
    payload = {"flight_id": str(flight.id), "seat_ids": [str(seat.id)]}
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert "flight" in response.data
    assert "seats" in response.data


@pytest.mark.django_db
def test_booking_same_seat_twice(api_client, user, flight, seat):
    api_client.force_authenticate(user=user)
    url = reverse("v1:airport:order-list")
    payload = {"flight_id": str(flight.id), "seat_ids": [str(seat.id)]}
    # First booking
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    # Second booking should fail
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 400
    assert "seat_ids" in response.data or "Seats" in str(response.data)


@pytest.mark.django_db
def test_booking_seat_with_wrong_type(api_client, user, flight, seat_class):
    # Create another seat with different airplane_type
    airplane_type = AirplaneType.objects.create(
        name="Airbus 320", rows=5, seats_in_row=4
    )
    wrong_seat = Seat.objects.create(
        airplane_type=airplane_type, row=1, seat="B", seat_class=seat_class
    )
    api_client.force_authenticate(user=user)
    url = reverse("v1:airport:order-list")
    payload = {"flight_id": str(flight.id), "seat_ids": [str(wrong_seat.id)]}
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 400
    assert "seats" in str(response.data) or "seat" in str(response.data).lower()


@pytest.mark.django_db
def test_booking_for_departed_flight(api_client, user, route, airplane, seat_class):
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=timezone.now() - timedelta(days=1),
        arrival_time=timezone.now(),
    )
    airplane_type = airplane.airplane_type
    seat = Seat.objects.create(
        airplane_type=airplane_type, row=1, seat="C", seat_class=seat_class
    )
    api_client.force_authenticate(user=user)
    url = reverse("v1:airport:order-list")
    payload = {"flight_id": str(flight.id), "seat_ids": [str(seat.id)]}
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 400
    assert "departed" in str(response.data) or "already" in str(response.data)


@pytest.mark.django_db
def test_available_seats(api_client, flight, seat):
    url = reverse("v1:airport:flight-available-seats", kwargs={"pk": str(flight.id)})
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(s["id"] == str(seat.id) for s in response.data)
