from django.contrib import admin
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    SeatClass,
    Seat,
    Ticket,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city", "created_at")
    search_fields = ("name", "closest_big_city")
    list_filter = ("closest_big_city",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name")
    list_filter = ("source", "destination")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row")
    search_fields = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "airplane_type", "created_at")
    search_fields = ("name",)
    list_filter = ("airplane_type",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "airplane", "departure_time", "arrival_time")
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "airplane__name",
    )
    list_filter = ("route", "airplane", "departure_time")
    filter_horizontal = ("crew",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__email",)
    list_filter = ("created_at",)


@admin.register(SeatClass)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("airplane_type", "row", "seat", "seat_class")
    search_fields = ("airplane_type__name", "seat")
    list_filter = ("airplane_type", "seat_class")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "flight", "seat", "order")
    search_fields = ("flight__id", "order__user__email")
    list_filter = ("flight", "order")
