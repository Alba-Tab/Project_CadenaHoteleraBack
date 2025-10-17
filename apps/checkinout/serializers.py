from rest_framework import serializers
from .models import CheckInOut
from ..folioestancias.models import FolioEstancia


class CheckInOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInOut
        fields = '__all__'

    def create(self, validated_data):
        # Obtenemos la reserva del diccionario validated_data
        reserva = validated_data.get('reserva')
        # Creamos el folio de estancia asociado a la reserva
        folio = FolioEstancia.objects.create(
            estado=FolioEstancia.PENDIENTE,
            total_pagado=0,
            huesped=reserva.huesped,
            reserva=reserva
        )

        return CheckInOut.objects.create(**validated_data)