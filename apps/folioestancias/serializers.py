from rest_framework import serializers
from apps.folioestancias.models import FolioEstancia
from apps.servicios.models import ServicioReserva
from apps.servicios.serializers import ServicioReservaSerializer 

class FolioEstanciaSerializer(serializers.ModelSerializer):
    # Campos calculados
    huesped_nombre = serializers.CharField(
        source='huesped.get_full_name', read_only=True
    )
    reserva_id = serializers.IntegerField(source='reserva.id', read_only=True)
    reserva_total = serializers.DecimalField(
        source='reserva.total', max_digits=10, decimal_places=2, read_only=True
    )
    fecha_entrada = serializers.DateField(source='reserva.fecha_entrada', read_only=True)
    fecha_salida = serializers.DateField(source='reserva.fecha_salida', read_only=True)
    hotel_nombre = serializers.CharField(source='reserva.hotel.nombre', read_only=True)

    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "total_pagado",
            "huesped_id",
            "huesped_nombre",
            "reserva_id",
            "reserva_total",
            "fecha_entrada",
            "fecha_salida",
            "hotel_nombre",
        ]

# class ServicioReservaSerializer(serializers.ModelSerializer):
#     nombre_servicio = serializers.CharField(source='servicio.nombre', read_only=True)
#
#     class Meta:
#         model = ServicioReserva
#         fields = ["id", "nombre_servicio", "cantidad", "monto_total"]


# --- SERIALIZER DETALLE ---
class FolioDetalleSerializer(serializers.ModelSerializer):
    huesped_nombre = serializers.CharField(source='huesped.get_full_name', read_only=True)
    hotel_nombre = serializers.CharField(source='reserva.hotel.nombre', read_only=True)
    reserva_total = serializers.DecimalField(source='reserva.total', max_digits=10, decimal_places=2, read_only=True)
    fecha_entrada = serializers.DateField(source='reserva.fecha_entrada', read_only=True)
    fecha_salida = serializers.DateField(source='reserva.fecha_salida', read_only=True)

    # servicios asociados a la reserva
    servicios_reservas = ServicioReservaSerializer(
        many=True,
        read_only=True,
        source='reserva.servicios_reserva'  # <- debe coincidir con el related_name del modelo
    )

    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "total_pagado",
            "huesped_id",
            "huesped_nombre",
            "reserva_id",
            "reserva_total",
            "fecha_entrada",
            "fecha_salida",
            "hotel_nombre",
            "servicios_reservas",
        ]

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
        depth = 2  # Profundidad de anidamiento para incluir detalles del usuario y la reserva