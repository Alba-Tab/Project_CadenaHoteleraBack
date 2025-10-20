from rest_framework import serializers

from apps.checkinout.serializers import CheckInCreateSerializer
from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva

class ReservaSerializer(serializers.ModelSerializer):
    nombre_huesped = serializers.SerializerMethodField()
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
    ckeckinout = CheckInCreateSerializer(source="checkinout", read_only=True)

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
            'ckeckinout',
        ]

    def get_nombre_huesped(self, obj):
        return f"{obj.huesped.first_name} {obj.huesped.last_name}"