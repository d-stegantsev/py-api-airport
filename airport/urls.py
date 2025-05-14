from rest_framework.routers import DefaultRouter
from .views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    SeatClassViewSet,
    SeatViewSet,
    TicketViewSet,
)

app_name = "airport"

router = DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("crews", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("orders", OrderViewSet, basename="order")
router.register("seat-classes", SeatClassViewSet, basename="seat-class")
router.register("seats", SeatViewSet, basename="seat")
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = router.urls
