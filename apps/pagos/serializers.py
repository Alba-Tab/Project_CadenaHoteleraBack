from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from apps.pagos.models import Pago
from apps.folioestancias.models import FolioEstancia


class PagoCreateSerializer(serializers.ModelSerializer):
    folio_id = serializers.PrimaryKeyRelatedField(
        queryset=FolioEstancia.objects.all(), source="folio_estancia", write_only=True
    )

    class Meta:
        model = Pago
        fields = [
            "id",
            "folio_id",
            "fecha_pago",
            "metodo",
            "monto",
            "referencia",
            "estado",
            "created_at",
        ]
        read_only_fields = ["estado", "created_at"]

    def validate(self, attrs):
        folio: FolioEstancia = attrs["folio_estancia"]
        total_reserva = folio.reserva.total
        pendiente = (Decimal(total_reserva) - Decimal(folio.total_pagado)).quantize(Decimal("0.01"))
        monto = attrs["monto"]

        if pendiente <= 0:
            raise serializers.ValidationError("El folio ya está totalmente pagado.")
        if monto != pendiente:
            raise serializers.ValidationError(f"El pago debe ser por el total pendiente: {pendiente}. No se permiten pagos parciales.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        folio: FolioEstancia = validated_data["folio_estancia"]
        pago = Pago.objects.create(
            **validated_data,
            estado=Pago.ESTADO_COMPLETADO,
        )
        folio.total_pagado = (folio.total_pagado + pago.monto)
        folio.estado = FolioEstancia.PAGADO  
        folio.save(update_fields=["total_pagado", "estado"])
        return pago
