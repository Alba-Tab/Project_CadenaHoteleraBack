from rest_framework import serializers

from apps.folioestancias.models import FolioEstancia
from apps.servicios.serializers import ServicioReservaSerializer


class FolioEstanciaSerializer(serializers.ModelSerializer):
    nombre_huesped = serializers.ReadOnlyField(source='huesped.first_name')
    class Meta:
        model = FolioEstancia
        fields = '__all__'

class DetalleFolioSerializer(serializers.ModelSerializer):
    servicios_reservas = ServicioReservaSerializer(source='folioestancias', many=True)
    class Meta:
        model = FolioEstancia
        fields = [
            'id',
            'estado',
            'total_pagado',
            'huesped',
            'reserva',
            'servicios_reservas'
        ]
        depth = 1  # Profundidad de anidamiento para incluir detalles del usuario y la reserva