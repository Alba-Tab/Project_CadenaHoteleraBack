from rest_framework import serializers

from apps.checkinout.serializers import CheckInCreateSerializer, CheckoutSerializer
from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from apps.checkinout.models import CheckInOut
from apps.folioestancias.models import FolioEstancia


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
    checkin = CheckInCreateSerializer(source="checkinout", read_only=True)
    checkout = CheckoutSerializer(source="checkinout", read_only=True)

    # 🔹 Campos agregados para el front
    checkin = serializers.SerializerMethodField()
    checkout = serializers.SerializerMethodField()
    folio = serializers.SerializerMethodField()

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
            # 👇 nuevos campos
            'checkin',
            'checkout',
            'folio',
        ]
    def get_nombre_huesped(self, obj):
        """Devuelve el nombre completo del huésped"""
        if obj.huesped:
            nombre = f"{obj.huesped.first_name or ''} {obj.huesped.last_name or ''}".strip()
            return nombre if nombre else obj.huesped.username
        return None

    # 🔸 Métodos que obtienen la información relacionada
    def get_checkin(self, obj):
        """Devuelve la información del check-in si existe"""
        checkin = getattr(obj, "checkinout", None)
        if checkin:
            return {
                "id": checkin.id,
                "fecha_checkin": checkin.fecha_checkin,
                "hora_checkin": checkin.hora_checkin,
                "observaciones": checkin.observaciones,
            }
        return None

    def get_checkout(self, obj):
        """Devuelve info del check-out si ya se realizó"""
        checkin = getattr(obj, "checkinout", None)
        if checkin and checkin.fecha_checkout:
            return {
                "id": checkin.id,
                "fecha_checkout": checkin.fecha_checkout,
                "hora_checkout": checkin.hora_checkout,
                "observaciones": checkin.observaciones,
            }
        return None

    def get_folio(self, obj):
        """Devuelve el folio de estancia asociado"""
        folio = FolioEstancia.objects.filter(reserva=obj).first()
        if folio:
            return {
                "id": folio.id,
                "estado": folio.estado,
                "total_pagado": str(folio.total_pagado),
            }
        return None
