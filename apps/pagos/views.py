from django.shortcuts import render

from rest_framework import viewsets, permissions, filters
from .models import Pago
from .serializers import PagoSerializer

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
    # Para desarrollo; luego puedes cambiar a IsAuthenticated
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["metodo", "estado", "referencia"]
    ordering_fields = ["fecha_pago", "monto", "created_at", "id"]
