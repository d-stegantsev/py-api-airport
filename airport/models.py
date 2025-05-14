from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from base.models import TimestampedUUIDBaseModel


class Airport(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(TimestampedUUIDBaseModel):
    source = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="routes_to"
    )
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source} → {self.destination}"


class AirplaneType(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Airplane(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=100)
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.PROTECT,
        related_name="airplanes"
    )

    def __str__(self):
        return self.name


class Crew(TimestampedUUIDBaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(TimestampedUUIDBaseModel):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(
        Crew,
        related_name="flights"
    )

    def __str__(self):
        return f"Flight {self.id} on {self.route}"


class Order(TimestampedUUIDBaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class SeatClass(TimestampedUUIDBaseModel):
    """
    Represents seat travel classes (e.g., Economy, Business, First).
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    """
    Defines a seat template for each AirplaneType.
    """
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="seat_templates"
    )
    row = models.PositiveIntegerField()
    seat = models.CharField(max_length=1)
    seat_class = models.ForeignKey(
        SeatClass,
        on_delete=models.PROTECT,
        related_name="seat_templates"
    )

    class Meta:
        unique_together = (("airplane_type", "row", "seat"),)

    def __str__(self):
        return f"{self.airplane_type} row {self.row} seat {self.seat} ({self.seat_class})"


class Ticket(TimestampedUUIDBaseModel):
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.PROTECT,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = (("flight", "seat"),)

    def clean(self):
        # Ensure seat belongs to the correct airplane type
        if self.seat.airplane_type != self.flight.airplane.airplane_type:
            raise ValidationError("Seat does not match flight airplane type.")

    def __str__(self):
        return f"Ticket {self.id}: {self.flight} Seat {self.seat.row}{self.seat.seat} ({self.seat.seat_class})"
