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
