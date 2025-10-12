from rest_framework import serializers

from apps.habitaciones.models import Habitacion
from apps.habitaciones.serializers import HabitacionSimpleSerializer
from apps.reservas.models import Reserva


# class ServicioExtraSerializer(serializers.ModelSerializer):
#     servicio = serializers.PrimaryKeyRelatedField(queryset='servicios.Servicio'.objects.all())
#
#     class Meta:
#         model = ServicioExtra
#         fields = ['servicio', 'cantidad',]

# class DetalleServicioExtraSerializer(serializers.ModelSerializer):
#     habitacion = serializers.PrimaryKeyRelatedField(queryset=Habitacion.objects.all())
#     servicios = ServicioExtraSerializer(many=True, required=False)
#
#     class Meta:
#         model = DetalleReserva
#         fields = ['habitacion', 'servicios',]

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
    # servicios = serializers.ListSerializer(
    #     child=serializers.PrimaryKeyRelatedField(
    #         queryset='servicios.Servicio'.objects.all()
    #     ),
    #     required=False,    #Permite que el campo no sea obligatorio
    #     write_only=True     #solo sea recibido en la solicitud
    # )
    # Para recibir una lista de IDs de habitaciones
    # habitaciones = serializers.ListSerializer(
    #     child=serializers.PrimaryKeyRelatedField(
    #         queryset=Habitacion.objects.all()
    #     ),
    #     #required=False,    #Permite que el campo no sea obligatorio
    #     write_only=True     #solo sea recibido en la solicitud
    # )
    # habitaciones = DetalleServicioExtraSerializer(many=True, write_only=True)

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
            # 'servicios',
        ]

class DetalleReservaSerializer(serializers.ModelSerializer):
    nombre_huesped = serializers.CharField(
        source='huesped.nombre',
        read_only=True
    )
    habitaciones = HabitacionSimpleSerializer(
        many=True,
        source='habitaciones_reservadas.habitacion',
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
            'habitaciones',
        ]