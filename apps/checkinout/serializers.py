from django.utils import timezone
from rest_framework import serializers
from django.db import transaction

from apps.reservas.models import Reserva
from apps.folioestancias.models import FolioEstancia
from apps.checkinout.models import CheckInOut


class CheckInCreateSerializer(serializers.ModelSerializer):
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source="reserva", write_only=True
    )

    class Meta:
        model = CheckInOut
        fields = [
            "id",
            "reserva_id",
            "fecha_checkin",
            "hora_checkin",
            "observaciones",
        ]

    def validate(self, attrs):
        reserva: Reserva = attrs["reserva"]
        # No permitir check-in si ya existe
        if hasattr(reserva, "checkinout"):
            raise serializers.ValidationError("Esta reserva ya tiene un check-in registrado.")
        # (Opcional) Validar estado de la reserva
        if reserva.estado not in (Reserva.CONFIRMADA, Reserva.REALIZADA, Reserva.PENDIENTE):
            raise serializers.ValidationError("La reserva no permite check-in por su estado actual.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        reserva: Reserva = validated_data["reserva"]
        # Si no vienen fechas/horas, usar ahora
        validated_data.setdefault("fecha_checkin", timezone.localdate())
        validated_data.setdefault("hora_checkin", timezone.localtime().time())

        checkin = CheckInOut.objects.create(**validated_data)

        # Crear folio una sola vez por reserva
        FolioEstancia.objects.get_or_create(
            reserva=reserva,
            huesped=reserva.huesped,
            defaults={
                "estado": FolioEstancia.PENDIENTE,
                "total_pagado": 0,
            },
        )
        return checkin


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInOut
        fields = ["id", "fecha_checkout", "hora_checkout", "observaciones"]

    def validate(self, attrs):
        checkin: CheckInOut = self.instance
        folio = checkin.reserva.folios_estancia.first()
        if folio is None:
            raise serializers.ValidationError("No existe folio para esta reserva.")
        if folio.estado != FolioEstancia.PAGADO:
            raise serializers.ValidationError("No se puede hacer check-out hasta que el folio esté Pagado.")
        return attrs

    def update(self, instance, validated_data):
        instance.fecha_checkout = validated_data.get("fecha_checkout", timezone.localdate())
        instance.hora_checkout = validated_data.get("hora_checkout", timezone.localtime().time())
        instance.observaciones = validated_data.get("observaciones", instance.observaciones)
        instance.save()


        reserva = instance.reserva
        reserva.estado = Reserva.REALIZADA
        reserva.save(update_fields=["estado"])

        return instance
    