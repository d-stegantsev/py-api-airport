import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Q, F, CheckConstraint, UniqueConstraint
from django.utils.text import slugify

from base.models import TimestampedUUIDBaseModel


class Airport(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=255, unique=True)
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
    distance = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(source=F('destination')), name='route_source_destination_diff'),
            CheckConstraint(check=Q(distance__gt=0), name='route_distance_positive'),
            UniqueConstraint(fields=('source', 'destination'), name='unique_route')
        ]

    def __str__(self):
        return f"{self.source} → {self.destination}"


class AirplaneType(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=100, unique=True)
    rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name


def airplane_image_path(instance, filename):
    ext = pathlib.Path(filename).suffix
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{ext}"
    return pathlib.Path("uploads/airplanes") / filename


class Airplane(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=100)
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.PROTECT,
        related_name="airplanes"
    )
    image = models.ImageField(null=True, blank=True, upload_to=airplane_image_path)

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

    class Meta:
        constraints = [
            CheckConstraint(check=Q(departure_time__lt=F('arrival_time')), name='flight_times_order')
        ]

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


class Seat(TimestampedUUIDBaseModel):
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

    def clean(self):
        super().clean()
        max_rows = self.airplane_type.rows
        max_seats = self.airplane_type.seats_in_row
        if not (1 <= self.row <= max_rows):
            raise ValidationError(f'Row must be between 1 and {max_rows}.')
        if ord(self.seat.upper()) - ord('A') + 1 > max_seats:
            raise ValidationError(f'Seat letter must be within 1 and {max_seats}.')

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
        super().clean()
        if self.seat.airplane_type != self.flight.airplane.airplane_type:
            raise ValidationError("Seat does not match flight airplane type.")

    def __str__(self):
        return f"Ticket {self.id}: {self.flight} Seat {self.seat.row}{self.seat.seat} ({self.seat.seat_class})"
