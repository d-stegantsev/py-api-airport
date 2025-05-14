from rest_framework import serializers
from django.utils import timezone
from .models import (
    Airport, Route, AirplaneType, Airplane, Crew,
    Flight, Order, SeatClass, Seat, Ticket
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id", "created_at", "updated_at", "name", "closest_big_city",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        if Airport.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Airport with this name already exists.")
        return value


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id", "created_at", "updated_at", "source", "destination", "distance",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        if attrs.get("source") == attrs.get("destination"):
            raise serializers.ValidationError("Source and destination must differ.")
        return attrs

    def validate_distance(self, value):
        if value <= 0:
            raise serializers.ValidationError("Distance must be greater than 0.")
        return value


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id", "created_at", "updated_at", "name", "rows", "seats_in_row",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_rows(self, value):
        if value < 1:
            raise serializers.ValidationError("Rows must be at least 1.")
        return value

    def validate_seats_in_row(self, value):
        if value < 1:
            raise serializers.ValidationError("Seats in row must be at least 1.")
        return value


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "created_at", "updated_at", "name", "airplane_type",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id", "created_at", "updated_at", "first_name", "last_name",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id", "created_at", "updated_at", "route", "airplane",
            "departure_time", "arrival_time", "crew",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        departure = attrs.get("departure_time")
        arrival = attrs.get("arrival_time")
        if departure and arrival and departure >= arrival:
            raise serializers.ValidationError("Departure must be before arrival.")
        if departure and departure < timezone.now():
            raise serializers.ValidationError("Departure cannot be in the past.")
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id", "created_at", "updated_at", "user",
        )
        read_only_fields = ("id", "created_at", "updated_at", "user")

    def create(self, validated_data):
        user = self.context["request"].user
        return Order.objects.create(user=user, **validated_data)


class SeatClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatClass
        fields = (
            "id", "created_at", "updated_at", "name",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Seat class name cannot be blank.")
        return name


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = (
            "id", "airplane_type", "row", "seat", "seat_class",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        airplane_type = attrs.get("airplane_type")
        row = attrs.get("row")
        seat = attrs.get("seat")
        if airplane_type:
            max_rows = airplane_type.rows
            if row is not None and (row < 1 or row > max_rows):
                raise serializers.ValidationError(
                    f"Row must be between 1 and {max_rows}."
                )
            if seat:
                index = ord(seat.upper()) - ord('A') + 1
                max_seats = airplane_type.seats_in_row
                if index < 1 or index > max_seats:
                    raise serializers.ValidationError(
                        f"Seat letter must be within 1 and {max_seats}."
                    )
        return attrs


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id", "created_at", "updated_at", "flight", "seat", "order",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        flight = attrs.get("flight")
        seat = attrs.get("seat")
        if flight and seat:
            if seat.airplane_type != flight.airplane.airplane_type:
                raise serializers.ValidationError(
                    "Seat does not match flight airplane type."
                )
            if Ticket.objects.filter(flight=flight, seat=seat).exists():
                raise serializers.ValidationError(
                    "This seat is already booked for the selected flight."
                )
            if flight.departure_time <= timezone.now():
                raise serializers.ValidationError(
                    "Cannot book ticket for a flight that has already departed."
                )
        return attrs
