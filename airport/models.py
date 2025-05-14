from django.conf import settings
from django.db import models

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

    def __str__(self):
        return self.name


class Airplane(TimestampedUUIDBaseModel):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
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


class Ticket(TimestampedUUIDBaseModel):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = ("flight", "row", "seat")

    def __str__(self):
        return f"Ticket {self.id}: {self.flight} Seat {self.row}{self.seat}"
