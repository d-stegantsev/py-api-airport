from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
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
class AirplaneImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["image"]


class BaseAirplaneSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id", "name", "image", "airplane_type", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

class AirplaneListSerializer(BaseAirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta(BaseAirplaneSerializer.Meta):
        fields = (
            "id", "name", "image", "airplane_type",
        )

class AirplaneDetailSerializer(BaseAirplaneSerializer):
    airplane_type = AirplaneTypeListSerializer(read_only=True)

    class Meta(BaseAirplaneSerializer.Meta):
        fields = (
            "id", "name", "image", "airplane_type", "created_at", "updated_at",
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
    flight = serializers.SerializerMethodField()
    seat = serializers.SerializerMethodField()

    class Meta(BaseTicketSerializer.Meta):
        fields = (
            "id", "flight", "seat",
        )

    def get_flight(self, ticket):
        flight = ticket.flight
        src = flight.route.source
        dst = flight.route.destination
        return f"{src.name} ({src.closest_big_city}) - {dst.name} ({dst.closest_big_city})"

    def get_seat(self, ticket):
        return f"Row {ticket.seat.row}, Seat {ticket.seat.seat}"

class TicketDetailSerializer(BaseTicketSerializer):
    flight = serializers.SerializerMethodField()
    seat = serializers.SerializerMethodField()

    class Meta(BaseTicketSerializer.Meta):
        fields = (
            "id", "flight", "seat", "order", "created_at", "updated_at",
        )

    def get_flight(self, ticket):
        flight = ticket.flight
        src = flight.route.source
        dst = flight.route.destination
        return f"{src.name} ({src.closest_big_city}) - {dst.name} ({dst.closest_big_city})"

    def get_seat(self, ticket):
        return f"Row {ticket.seat.row}, Seat {ticket.seat.seat}"


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
    user = serializers.EmailField(source="user.email", read_only=True)
    class Meta(BaseOrderSerializer.Meta):
        fields = (
            "id", "user",
        )


class OrderDetailSerializer(BaseOrderSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    flight = serializers.SerializerMethodField()
    seats = serializers.SerializerMethodField()

    class Meta(BaseOrderSerializer.Meta):
        fields = ("id", "user", "flight", "seats", "created_at", "updated_at")

    def get_flight(self, order):
        ticket = order.tickets.first()
        if not ticket:
            return None
        flight = ticket.flight
        src = flight.route.source
        dst = flight.route.destination
        return f"{src.name} ({src.closest_big_city}) - {dst.name} ({dst.closest_big_city})"

    def get_seats(self, order):
        return [
            f"Row {ticket.seat.row}, Seat {ticket.seat.seat}"
            for ticket in order.tickets.all()
        ]


# Booking serializers
class OrderCreateSerializer(serializers.Serializer):
    flight_id = serializers.UUIDField()
    seat_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True)

    def validate(self, data):
        try:
            flight = Flight.objects.get(pk=data['flight_id'])
        except Flight.DoesNotExist:
            raise serializers.ValidationError({"flight_id": "Flight does not exist."})
        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError("Cannot book ticket for a flight that has already departed.")
        seat_ids = data['seat_ids']
        valid_seat_ids = Seat.objects.filter(
            airplane_type=flight.airplane.airplane_type,
            pk__in=seat_ids
        ).values_list('id', flat=True)
        if set(seat_ids) != set(valid_seat_ids):
            raise serializers.ValidationError("One or more seats are invalid for this flight.")
        booked = Ticket.objects.filter(
            flight=flight,
            seat_id__in=seat_ids
        ).values_list('seat_id', flat=True)
        if booked:
            raise serializers.ValidationError({
                "seat_ids": f"Seats {list(booked)} are already booked."
            })
        data['flight'] = flight
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        flight = validated_data['flight']
        seat_ids = validated_data['seat_ids']
        with transaction.atomic():
            order = Order.objects.create(user=user)
            for seat_id in seat_ids:
                Ticket.objects.create(
                    order=order,
                    flight=flight,
                    seat_id=seat_id
                )
        return order
