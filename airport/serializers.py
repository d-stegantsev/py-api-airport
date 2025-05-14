from rest_framework import serializers
from .models import (
    Airport, Route, AirplaneType, Airplane, Crew,
    Flight, Order, SeatClass, Seat, Ticket
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
            "closest_big_city",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "created_at",
            "updated_at",
            "source",
            "destination",
            "distance",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
            "rows",
            "seats_in_row",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
            "airplane_type",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "created_at",
            "updated_at",
            "first_name",
            "last_name",
        )


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "created_at",
            "updated_at",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "updated_at",
            "user",
        )


class SeatClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatClass
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
        )


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = (
            "id",
            "airplane_type",
            "row",
            "seat",
            "seat_class",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "created_at",
            "updated_at",
            "flight",
            "seat",
            "order",
        )
