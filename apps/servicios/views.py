from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Servicio, ServicioReserva
from .serializers import ServicioSerializer, ServicioReservaSerializer

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "tipo"]
    ordering_fields = ["nombre", "precio", "created_at"]

class ServicioReservaViewSet(viewsets.ModelViewSet):
    queryset = ServicioReserva.objects.all()
    serializer_class = ServicioReservaSerializer

