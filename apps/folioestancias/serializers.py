from rest_framework import serializers
from apps.folioestancias.models import FolioEstancia

class FolioEstanciaSerializer(serializers.ModelSerializer):
    reserva_id = serializers.PrimaryKeyRelatedField(read_only=True)
    huesped_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FolioEstancia
        fields = [
            "id",
            "estado",
            "total_pagado",
            "huesped",
            "reserva",
        ]
