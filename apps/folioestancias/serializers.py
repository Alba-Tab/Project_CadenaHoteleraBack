from rest_framework import serializers
from apps.folioestancias.models import FolioEstancia
from apps.servicios.serializers import ServicioReservaSerializer


class FolioEstanciaSerializer(serializers.ModelSerializer):
    reserva_id = serializers.PrimaryKeyRelatedField(read_only=True)
    huesped_id = serializers.PrimaryKeyRelatedField(read_only=True)
    nombre_huesped = serializers.SerializerMethodField()

    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "total_pagado",
            "huesped",
            "reserva",
            "huesped_id",
            "reserva_id",
            "nombre_huesped",
        ]

    def get_nombre_huesped(self, obj):
        return f"{obj.huesped.first_name} {obj.huesped.last_name}"

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