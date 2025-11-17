from django.utils import timezone
from rest_framework import serializers
from django.db import transaction

from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from apps.folioestancias.models import FolioEstancia
from apps.checkinout.models import CheckInOut
from apps.facial_recognition.services import FacialRecognitionService


class CheckInCreateSerializer(serializers.ModelSerializer):
    reserva_id = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), source="reserva", write_only=True
    )
    photo_checkin = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = CheckInOut
        fields = [
            "id",
            "reserva_id",
            "fecha_checkin",
            "hora_checkin",
            "observaciones",
            "photo_checkin",
        ]

    def validate(self, attrs):
        reserva: Reserva = attrs["reserva"]
        photo_checkin = attrs.pop("photo_checkin")
        
        # No permitir check-in si ya existe
        if hasattr(reserva, "checkinout"):
            raise serializers.ValidationError("Esta reserva ya tiene un check-in registrado.")
        # Validar estado de la reserva
        if reserva.estado not in (Reserva.CONFIRMADA, Reserva.REALIZADA, Reserva.PENDIENTE):
            raise serializers.ValidationError("La reserva no permite check-in por su estado actual.")
        
        # Verificación facial con AWS
        try:
            from django.core.files.storage import default_storage
            temp_path = default_storage.save(f'temp_checkin/{reserva.id}.jpg', photo_checkin)
            
            result = FacialRecognitionService.search_face(temp_path)
            
            default_storage.delete(temp_path)
            
            if not result:
                raise serializers.ValidationError("Rostro no reconocido.")
            
            if result['user_id'] != reserva.huesped.id:
                raise serializers.ValidationError(
                    f"La persona no coincide con el huésped de la reserva."
                )
            
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"Error en verificación facial: {str(e)}")
        
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        reserva: Reserva = validated_data["reserva"]
        # Si no vienen fechas/horas, usar ahora
        validated_data.setdefault("fecha_checkin", timezone.localdate())
        validated_data.setdefault("hora_checkin", timezone.localtime().time())

        checkin = CheckInOut.objects.create(**validated_data)

        # Cambiar el estado de la habitación a OCUPADA al hacer check-in
        habitacion = reserva.habitacion
        habitacion.estado = Habitacion.OCUPADA
        habitacion.save(update_fields=['estado'])

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
        if not self.instance:
            raise serializers.ValidationError("No se encontró el check-in.")
        
        checkin: CheckInOut = self.instance
        
        # Verificar si ya tiene checkout
        if checkin.fecha_checkout:
            raise serializers.ValidationError("Esta reserva ya tiene check-out registrado.")
        
        # Validar folio (opcional - solo advertencia)
        folio = checkin.reserva.folios_estancia.first()
        if folio is None:
            # Solo advertencia, no error crítico
            print("⚠️ Advertencia: No existe folio para esta reserva.")
        elif folio.estado != FolioEstancia.PAGADO:
            # Solo advertencia, no error crítico
            print(f"⚠️ Advertencia: El folio está en estado {folio.estado}, no PAGADO.")
        
        return attrs

    def update(self, instance, validated_data):
        instance.fecha_checkout = validated_data.get("fecha_checkout", timezone.localdate())
        instance.hora_checkout = validated_data.get("hora_checkout", timezone.localtime().time())
        instance.observaciones = validated_data.get("observaciones", instance.observaciones)
        instance.save()


        reserva = instance.reserva
        reserva.estado = Reserva.REALIZADA
        reserva.save(update_fields=["estado"])
        habitacion = reserva.habitacion
        habitacion.estado = Habitacion.DISPONIBLE
        habitacion.save()

        return instance
    