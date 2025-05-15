from rest_framework import serializers
from django.utils import timezone
from airport.models import (
    Airport, Route, AirplaneType, Airplane, Crew,
    Flight, Order, SeatClass, Seat, Ticket
)

# Airport serializers
class BaseAirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id", "name", "closest_big_city", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        if Airport.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Airport with this name already exists.")
        return value

class AirportListSerializer(BaseAirportSerializer):
    class Meta(BaseAirportSerializer.Meta):
        fields = (
            "id", "name", "closest_big_city",
        )

class AirportDetailSerializer(BaseAirportSerializer):
    class Meta(BaseAirportSerializer.Meta):
        fields = (
            "id", "name", "closest_big_city", "created_at", "updated_at",
        )


# Route serializers
class BaseRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id", "source", "destination", "distance", "created_at", "updated_at",
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

class RouteListSerializer(BaseRouteSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta(BaseRouteSerializer.Meta):
        fields = (
            "id", "source", "destination", "distance",
        )

class RouteDetailSerializer(BaseRouteSerializer):
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)

    class Meta(BaseRouteSerializer.Meta):
        fields = (
            "id", "source", "destination", "distance", "created_at", "updated_at",
        )


# AirplaneType serializers
class BaseAirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id", "name", "rows", "seats_in_row", "created_at", "updated_at",
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

class AirplaneTypeListSerializer(BaseAirplaneTypeSerializer):
    class Meta(BaseAirplaneTypeSerializer.Meta):
        fields = (
            "id", "name", "rows", "seats_in_row",
        )

class AirplaneTypeDetailSerializer(BaseAirplaneTypeSerializer):
    class Meta(BaseAirplaneTypeSerializer.Meta):
        fields = (
            "id", "name", "rows", "seats_in_row", "created_at", "updated_at",
        )


# Airplane serializers
class BaseAirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "airplane_type", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

class AirplaneListSerializer(BaseAirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta(BaseAirplaneSerializer.Meta):
        fields = (
            "id", "name", "airplane_type",
        )

class AirplaneDetailSerializer(BaseAirplaneSerializer):
    airplane_type = AirplaneTypeListSerializer(read_only=True)

    class Meta(BaseAirplaneSerializer.Meta):
        fields = (
            "id", "name", "airplane_type", "created_at", "updated_at",
        )


# Crew serializers
class BaseCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id", "first_name", "last_name", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

class CrewListSerializer(BaseCrewSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta(BaseCrewSerializer.Meta):
        fields = (
            "id", "full_name",
        )

    def get_full_name(self, crew_instance):
        return f"{crew_instance.first_name} {crew_instance.last_name}"

class CrewDetailSerializer(BaseCrewSerializer):
    class Meta(BaseCrewSerializer.Meta):
        fields = (
            "id", "first_name", "last_name", "created_at", "updated_at",
        )

# Flight serializers
class BaseFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crew", "created_at", "updated_at",
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

class FlightListSerializer(BaseFlightSerializer):
    route = serializers.SerializerMethodField()
    airplane = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta(BaseFlightSerializer.Meta):
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time",
        )

    def get_route(self, flight_instance):
        source_airport = flight_instance.route.source
        destination_airport = flight_instance.route.destination
        source_name = source_airport.name
        source_city = source_airport.closest_big_city
        destination_name = destination_airport.name
        destination_city = destination_airport.closest_big_city
        return f"{source_name} ({source_city}) - {destination_name} ({destination_city})"

class FlightDetailSerializer(BaseFlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewListSerializer(many=True, read_only=True)

    class Meta(BaseFlightSerializer.Meta):
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crew", "created_at", "updated_at",
        )


# Order serializers
class BaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id", "user", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        user = self.context["request"].user
        return Order.objects.create(user=user, **validated_data)

class OrderListSerializer(BaseOrderSerializer):
    class Meta(BaseOrderSerializer.Meta):
        fields = (
            "id", "user",
        )

class OrderDetailSerializer(BaseOrderSerializer):
    class Meta(BaseOrderSerializer.Meta):
        fields = (
            "id", "user", "created_at", "updated_at",
        )


# SeatClass serializers
class BaseSeatClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatClass
        fields = (
            "id", "name", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Seat class name cannot be blank.")
        return name

class SeatClassListSerializer(BaseSeatClassSerializer):
    class Meta(BaseSeatClassSerializer.Meta):
        fields = (
            "id", "name",
        )

class SeatClassDetailSerializer(BaseSeatClassSerializer):
    class Meta(BaseSeatClassSerializer.Meta):
        fields = (
            "id", "name", "created_at", "updated_at",
        )


# Seat serializers
class BaseSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = (
            "id", "airplane_type", "row", "seat", "seat_class", "created_at", "updated_at",
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

class SeatListSerializer(BaseSeatSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    seat_class = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta(BaseSeatSerializer.Meta):
        fields = (
            "id", "airplane_type", "row", "seat", "seat_class",
        )

class SeatDetailSerializer(BaseSeatSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    seat_class = serializers.SlugRelatedField(read_only=True, slug_field="name")
    class Meta(BaseSeatSerializer.Meta):
        fields = (
            "id", "airplane_type", "row", "seat", "seat_class", "created_at", "updated_at",
        )


# Ticket serializers
class BaseTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id", "flight", "seat", "order", "created_at", "updated_at",
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

class TicketListSerializer(BaseTicketSerializer):
    class Meta(BaseTicketSerializer.Meta):
        fields = (
            "id", "flight", "seat",
        )

class TicketDetailSerializer(BaseTicketSerializer):
    class Meta(BaseTicketSerializer.Meta):
        fields = (
            "id", "flight", "seat", "order", "created_at", "updated_at",
        )
