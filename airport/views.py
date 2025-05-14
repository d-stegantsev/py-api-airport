from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from airport.models import (
    Airport, Route, AirplaneType, Airplane, Crew,
    Flight, Order, SeatClass, Seat, Ticket
)
from airport.serializers import (
    AirportSerializer, RouteSerializer, AirplaneTypeSerializer,
    AirplaneSerializer, CrewSerializer, FlightSerializer,
    OrderSerializer, SeatClassSerializer, SeatSerializer, TicketSerializer
)
from base.mixins import BaseViewSetMixin

FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]

class AirportViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
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
    serializer_class = RouteSerializer
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
    serializer_class = AirplaneTypeSerializer
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
    serializer_class = AirplaneSerializer
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

class CrewViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
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
    serializer_class = FlightSerializer
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

class OrderViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').all()
    serializer_class = OrderSerializer
    filter_backends = FILTER_BACKENDS
    filterset_fields = {'created_at': ['date', 'gte', 'lte']}
    ordering_fields = ['created_at']
    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated],
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }

    def get_queryset(self):
        request_user = self.request.user
        queryset = self.queryset
        if not request_user.is_staff:
            queryset = queryset.filter(user=request_user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SeatClassViewSet(BaseViewSetMixin, viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
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
    serializer_class = SeatSerializer
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
    serializer_class = TicketSerializer
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
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }

    def get_queryset(self):
        request_user = self.request.user
        queryset = self.queryset
        if not request_user.is_staff:
            queryset = queryset.filter(order__user=request_user)
        return queryset

    @transaction.atomic
    def perform_create(self, ticket_serializer):
        ticket_serializer.save()
