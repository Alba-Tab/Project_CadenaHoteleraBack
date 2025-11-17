from django.shortcuts import render
from rest_framework import viewsets
from .models import ServiciosAsociados
from .serializers import ServiciosAsociadosSerializer

class ServiciosAsociadosViewSet(viewsets.ModelViewSet):
    queryset = ServiciosAsociados.objects.all()
    serializer_class = ServiciosAsociadosSerializer
    
    ordering_fields = ["fecha_consumo", "folioestancia"]

