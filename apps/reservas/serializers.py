from rest_framework import serializers

from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva

class ReservaSerializer(serializers.ModelSerializer):
    nombre_huesped = serializers.CharField(
        source='huesped.nombre',
        read_only=True
    )
    nombre_hotel = serializers.CharField(
        source='hotel.nombre',
        read_only=True
    )
    habitacion = serializers.PrimaryKeyRelatedField(
        queryset=Habitacion.objects.all()
    )
    nro_habitacion = serializers.CharField(
        source='habitacion.numero',
        read_only=True
    )

    class Meta:
        model = Reserva
        fields = [
            'id',
            'fecha_reserva',
            'fecha_entrada',
            'fecha_salida',
            'total',
            'estado',
            'huesped',
            'nombre_huesped',
            'hotel',
            'nombre_hotel',
            'habitacion',
            'nro_habitacion',
        ]