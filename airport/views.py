from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from airport.models import (
    Airport, Route, AirplaneType, Airplane, Crew,
    Flight, Order, SeatClass, Seat, Ticket
)
from airport.serializers import (
    BaseAirportSerializer, AirportListSerializer, AirportDetailSerializer,
    BaseRouteSerializer, RouteListSerializer, RouteDetailSerializer,
    BaseAirplaneTypeSerializer, AirplaneTypeListSerializer, AirplaneTypeDetailSerializer,
    BaseAirplaneSerializer, AirplaneListSerializer, AirplaneDetailSerializer,
    BaseCrewSerializer, CrewListSerializer, CrewDetailSerializer,
    BaseFlightSerializer, FlightListSerializer, FlightDetailSerializer,
    BaseOrderSerializer, OrderListSerializer, OrderCreateSerializer,
    BaseSeatClassSerializer, SeatClassListSerializer, SeatClassDetailSerializer,
    BaseSeatSerializer, SeatListSerializer, SeatDetailSerializer,
    BaseTicketSerializer, TicketListSerializer, TicketDetailSerializer, OrderDetailSerializer,
    AirplaneImageUploadSerializer,
)
from base.mixins import BaseViewSetMixin

FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]


@extend_schema_view(
    list=extend_schema(
        summary="List all airports",
        description="Returns a list of all airports. Supports search and ordering by name and closest_big_city.",
        responses={200: AirportListSerializer(many=True)},
        parameters=[
            OpenApiParameter(name="search", type=str, description="Search by airport name or closest_big_city"),
            OpenApiParameter(name="ordering", type=str, description="Order by name or closest_big_city"),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve airport details",
        description="Get detailed information about a specific airport by its ID.",
        responses={200: AirportDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new airport",
        description="Admin only. Create a new airport object.",
        request=BaseAirportSerializer,
        responses={201: AirportDetailSerializer},
    ),
    update=extend_schema(
        summary="Update airport",
        description="Admin only. Update airport data.",
        request=BaseAirportSerializer,
        responses={200: AirportDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update airport",
        description="Admin only. Partially update airport data.",
        request=BaseAirportSerializer,
        responses={200: AirportDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete airport",
        description="Admin only. Delete an airport.",
        responses={204: OpenApiResponse(description="No content, airport deleted")},
    ),
)
class AirportViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = BaseAirportSerializer
    action_serializers = {
        'list': AirportListSerializer,
        'retrieve': AirportDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {
        'name': ['exact', 'icontains'],
        'closest_big_city': ['exact', 'icontains'],
    }
    search_fields = ['name', 'closest_big_city']
    ordering_fields = ['name', 'closest_big_city', 'created_at']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

# --- ROUTE ---

@extend_schema_view(
    list=extend_schema(
        summary="List all routes",
        description="Returns a list of all routes. Supports filtering by source, destination, and distance.",
        responses={200: RouteListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve route details",
        description="Get detailed information about a specific route.",
        responses={200: RouteDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new route",
        description="Admin only. Create a new route.",
        request=BaseRouteSerializer,
        responses={201: RouteDetailSerializer},
    ),
    update=extend_schema(
        summary="Update route",
        description="Admin only. Update route data.",
        request=BaseRouteSerializer,
        responses={200: RouteDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update route",
        description="Admin only. Partially update route data.",
        request=BaseRouteSerializer,
        responses={200: RouteDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete route",
        description="Admin only. Delete a route.",
        responses={204: OpenApiResponse(description="No content, route deleted")},
    ),
)
class RouteViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination').all()
    serializer_class = BaseRouteSerializer
    action_serializers = {
        'list': RouteListSerializer,
        'retrieve': RouteDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {
        'source': ['exact'],
        'destination': ['exact'],
        'distance': ['gte', 'lte'],
    }
    ordering_fields = ['distance']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

# --- AIRPLANE TYPE ---

@extend_schema_view(
    list=extend_schema(
        summary="List all airplane types",
        description="Returns a list of all airplane types. Supports filtering by rows and seats_in_row.",
        responses={200: AirplaneTypeListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve airplane type details",
        description="Get detailed information about a specific airplane type.",
        responses={200: AirplaneTypeDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new airplane type",
        description="Admin only. Create a new airplane type.",
        request=BaseAirplaneTypeSerializer,
        responses={201: AirplaneTypeDetailSerializer},
    ),
    update=extend_schema(
        summary="Update airplane type",
        description="Admin only. Update airplane type data.",
        request=BaseAirplaneTypeSerializer,
        responses={200: AirplaneTypeDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update airplane type",
        description="Admin only. Partially update airplane type data.",
        request=BaseAirplaneTypeSerializer,
        responses={200: AirplaneTypeDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete airplane type",
        description="Admin only. Delete an airplane type.",
        responses={204: OpenApiResponse(description="No content, airplane type deleted")},
    ),
)
class AirplaneTypeViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = BaseAirplaneTypeSerializer
    action_serializers = {
        'list': AirplaneTypeListSerializer,
        'retrieve': AirplaneTypeDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {
        'rows': ['gte', 'lte'],
        'seats_in_row': ['gte', 'lte'],
    }
    search_fields = ['name']
    ordering_fields = ['name', 'rows', 'seats_in_row']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

# --- AIRPLANE ---

@extend_schema_view(
    list=extend_schema(
        summary="List all airplanes",
        description="Returns a list of all airplanes. Supports filtering by airplane_type and search by name.",
        responses={200: AirplaneListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve airplane details",
        description="Get detailed information about a specific airplane.",
        responses={200: AirplaneDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new airplane",
        description="Admin only. Create a new airplane.",
        request=BaseAirplaneSerializer,
        responses={201: AirplaneDetailSerializer},
    ),
    update=extend_schema(
        summary="Update airplane",
        description="Admin only. Update airplane data.",
        request=BaseAirplaneSerializer,
        responses={200: AirplaneDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update airplane",
        description="Admin only. Partially update airplane data.",
        request=BaseAirplaneSerializer,
        responses={200: AirplaneDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete airplane",
        description="Admin only. Delete an airplane.",
        responses={204: OpenApiResponse(description="No content, airplane deleted")},
    ),
)
class AirplaneViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related('airplane_type').all()
    serializer_class = BaseAirplaneSerializer
    action_serializers = {
        'list': AirplaneListSerializer,
        'retrieve': AirplaneDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {'airplane_type': ['exact']}
    search_fields = ['name']
    ordering_fields = ['name']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

    @extend_schema(
        summary="Upload airplane image",
        description="Admin only. Upload or replace the image for a specific airplane.",
        request=AirplaneImageUploadSerializer,
        responses={200: AirplaneImageUploadSerializer},
    )
    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
        serializer_class=AirplaneImageUploadSerializer,
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# --- CREW ---

@extend_schema_view(
    list=extend_schema(
        summary="List all crew members",
        description="Returns a list of all crew members. Supports search and ordering by last name.",
        responses={200: CrewListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve crew member details",
        description="Get detailed information about a specific crew member.",
        responses={200: CrewDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new crew member",
        description="Admin only. Create a new crew member.",
        request=BaseCrewSerializer,
        responses={201: CrewDetailSerializer},
    ),
    update=extend_schema(
        summary="Update crew member",
        description="Admin only. Update crew member data.",
        request=BaseCrewSerializer,
        responses={200: CrewDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update crew member",
        description="Admin only. Partially update crew member data.",
        request=BaseCrewSerializer,
        responses={200: CrewDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete crew member",
        description="Admin only. Delete a crew member.",
        responses={204: OpenApiResponse(description="No content, crew member deleted")},
    ),
)
class CrewViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = BaseCrewSerializer
    action_serializers = {
        'list': CrewListSerializer,
        'retrieve': CrewDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['last_name']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

# --- FLIGHT ---

@extend_schema_view(
    list=extend_schema(
        summary="List all flights",
        description="Returns a list of all flights. Supports filtering by route, airplane, and date range.",
        responses={200: FlightListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve flight details",
        description="Get detailed information about a specific flight.",
        responses={200: FlightDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new flight",
        description="Admin only. Create a new flight.",
        request=BaseFlightSerializer,
        responses={201: FlightDetailSerializer},
    ),
    update=extend_schema(
        summary="Update flight",
        description="Admin only. Update flight data.",
        request=BaseFlightSerializer,
        responses={200: FlightDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update flight",
        description="Admin only. Partially update flight data.",
        request=BaseFlightSerializer,
        responses={200: FlightDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete flight",
        description="Admin only. Delete a flight.",
        responses={204: OpenApiResponse(description="No content, flight deleted")},
    ),
)
class FlightViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Flight.objects.select_related('route', 'airplane').prefetch_related('crew').all()
    serializer_class = BaseFlightSerializer
    action_serializers = {
        'list': FlightListSerializer,
        'retrieve': FlightDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {
        'route': ['exact'],
        'airplane': ['exact'],
        'departure_time': ['date', 'gte', 'lte'],
        'arrival_time': ['date', 'gte', 'lte'],
    }
    ordering_fields = ['departure_time', 'arrival_time']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

    @extend_schema(
        summary="Get available seats for flight",
        description="Returns list of available seats for the selected flight.",
        responses={200: SeatListSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="seats/available")
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        booked_ids = Ticket.objects.filter(flight=flight).values_list('seat_id', flat=True)
        seats = Seat.objects.filter(
            airplane_type=flight.airplane.airplane_type
        ).exclude(pk__in=booked_ids)
        if not seats.exists():
            return Response({"detail": "No seats available"}, status=200)
        serializer = SeatListSerializer(seats, many=True)
        return Response(serializer.data)


# --- ORDER ---

@extend_schema_view(
    list=extend_schema(
        summary="List all orders (user only)",
        description="Returns a list of all orders belonging to the current user. Admins see all orders.",
        responses={200: OrderListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve order details",
        description="Get detailed information about a specific order. Users can only access their own orders.",
        responses={200: OrderDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new order",
        description="Create a new order with selected tickets. Only authenticated users.",
        request=OrderCreateSerializer,
        responses={201: OrderDetailSerializer},
    ),
    update=extend_schema(
        summary="Update order (admin only)",
        description="Admin only. Update order details.",
        request=BaseOrderSerializer,
        responses={200: OrderDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update order (admin only)",
        description="Admin only. Partially update order details.",
        request=BaseOrderSerializer,
        responses={200: OrderDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete order",
        description="Delete an order. Users can only delete their own orders.",
        responses={204: OpenApiResponse(description="No content, order deleted")},
    ),
)
class OrderViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').all()
    serializer_class = BaseOrderSerializer
    action_serializers = {
        'list': OrderListSerializer,
        'retrieve': OrderDetailSerializer,
        'create': OrderCreateSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {'created_at': ['date', 'gte', 'lte']}
    ordering_fields = ['created_at']
    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAuthenticated],
    }

    def get_queryset(self):
        request_user = self.request.user
        queryset = self.queryset
        if not request_user.is_staff:
            queryset = queryset.filter(user=request_user)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderDetailSerializer(order, context=self.get_serializer_context())
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# --- SEAT CLASS ---

@extend_schema_view(
    list=extend_schema(
        summary="List all seat classes",
        description="Returns a list of all seat classes. Supports search by name.",
        responses={200: SeatClassListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve seat class details",
        description="Get detailed information about a specific seat class.",
        responses={200: SeatClassDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new seat class",
        description="Admin only. Create a new seat class.",
        request=BaseSeatClassSerializer,
        responses={201: SeatClassDetailSerializer},
    ),
    update=extend_schema(
        summary="Update seat class",
        description="Admin only. Update seat class data.",
        request=BaseSeatClassSerializer,
        responses={200: SeatClassDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update seat class",
        description="Admin only. Partially update seat class data.",
        request=BaseSeatClassSerializer,
        responses={200: SeatClassDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete seat class",
        description="Admin only. Delete a seat class.",
        responses={204: OpenApiResponse(description="No content, seat class deleted")},
    ),
)
class SeatClassViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = BaseSeatClassSerializer
    action_serializers = {
        'list': SeatClassListSerializer,
        'retrieve': SeatClassDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {'name': ['exact', 'icontains']}
    search_fields = ['name']
    ordering_fields = ['name']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

# --- SEAT ---

@extend_schema_view(
    list=extend_schema(
        summary="List all seats",
        description="Returns a list of all seats. Supports filtering by airplane_type, seat_class, row and seat number.",
        responses={200: SeatListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve seat details",
        description="Get detailed information about a specific seat.",
        responses={200: SeatDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new seat",
        description="Admin only. Create a new seat.",
        request=BaseSeatSerializer,
        responses={201: SeatDetailSerializer},
    ),
    update=extend_schema(
        summary="Update seat",
        description="Admin only. Update seat data.",
        request=BaseSeatSerializer,
        responses={200: SeatDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update seat",
        description="Admin only. Partially update seat data.",
        request=BaseSeatSerializer,
        responses={200: SeatDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete seat",
        description="Admin only. Delete a seat.",
        responses={204: OpenApiResponse(description="No content, seat deleted")},
    ),
)
class SeatViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Seat.objects.select_related('airplane_type', 'seat_class').all()
    serializer_class = BaseSeatSerializer
    action_serializers = {
        'list': SeatListSerializer,
        'retrieve': SeatDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {
        'airplane_type': ['exact'],
        'seat_class': ['exact'],
        'row': ['gte', 'lte'],
        'seat': ['exact', 'iexact'],
    }
    ordering_fields = ['row', 'seat']
    action_permissions = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

# --- TICKET ---

@extend_schema_view(
    list=extend_schema(
        summary="List all tickets (user only)",
        description="Returns a list of all tickets for the current user. Admins see all tickets.",
        responses={200: TicketListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve ticket details",
        description="Get detailed information about a specific ticket.",
        responses={200: TicketDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new ticket (user only)",
        description="Authenticated users can create new tickets (as part of order creation).",
        request=BaseTicketSerializer,
        responses={201: TicketDetailSerializer},
    ),
    update=extend_schema(
        summary="Update ticket (admin only)",
        description="Admin only. Update ticket data.",
        request=BaseTicketSerializer,
        responses={200: TicketDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Partial update ticket (admin only)",
        description="Admin only. Partially update ticket data.",
        request=BaseTicketSerializer,
        responses={200: TicketDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Delete ticket (user only)",
        description="Authenticated users can delete their own tickets.",
        responses={204: OpenApiResponse(description="No content, ticket deleted")},
    ),
)
class TicketViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        'flight', 'seat', 'order',
        'seat__airplane_type', 'seat__seat_class',
        'flight__route', 'flight__airplane'
    ).all()
    serializer_class = BaseTicketSerializer
    action_serializers = {
        'list': TicketListSerializer,
        'retrieve': TicketDetailSerializer,
    }
    filter_backends = FILTER_BACKENDS
    filterset_fields = {
        'flight': ['exact'],
        'seat__seat_class': ['exact'],
        'order': ['exact'],
    }
    ordering_fields = ['flight__departure_time', 'seat__row', 'seat__seat']
    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAuthenticated],
    }

    @transaction.atomic
    def perform_create(self, ticket_serializer):
        ticket_serializer.save()
