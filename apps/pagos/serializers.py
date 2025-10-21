from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from apps.pagos.models import Pago
from apps.folioestancias.models import FolioEstancia
from apps.fidelizacion.models import ProgramaFidelizacion, CuentaFidelizacion
from apps.fidelizacion.services import FidelizacionService


class PagoCreateSerializer(serializers.ModelSerializer):
    folio_id = serializers.PrimaryKeyRelatedField(
        queryset=FolioEstancia.objects.all(), source="folio_estancia"
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

    # def validate(self, attrs):
    #     folio: FolioEstancia = attrs["folio_estancia"]
    #     total_reserva = folio.reserva.total
    #     pendiente = (Decimal(total_reserva) - Decimal(folio.total_pagado)).quantize(Decimal("0.01"))
    #     monto = attrs["monto"]
    #
    #     if pendiente <= 0:
    #         raise serializers.ValidationError("El folio ya está totalmente pagado.")
    #     if monto != pendiente:
    #         raise serializers.ValidationError(f"El pago debe ser por el total pendiente: {pendiente}. No se permiten pagos parciales.")
    #     return attrs

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
        
        # Acumular puntos de fidelización
        self._acumular_puntos_fidelizacion(folio, pago)
        
        return pago
    
    def _acumular_puntos_fidelizacion(self, folio: FolioEstancia, pago: Pago):

        try:
            # Obtener el cliente
            cliente = folio.huesped
            
            # Buscar un programa activo (tomar el primero disponible)
            programa = ProgramaFidelizacion.objects.filter(activo=True).first()
            
            if not programa:
                # No hay programa activo, no se acumulan puntos
                return
            
            # Buscar o crear cuenta de fidelización
            cuenta, created = CuentaFidelizacion.objects.get_or_create(
                cliente=cliente,
                fidelizacion=programa,
                defaults={'puntos_acumulados': 0}
            )
            
            # Acumular puntos usando el servicio (monto del pago = puntos)
            FidelizacionService.acumular_puntos(
                cuenta_id=cuenta.pk,
                monto_gastado=float(pago.monto)
            )
            
        except Exception as e:
            # Log del error pero no fallar la transacción del pago
            print(f"Error al acumular puntos de fidelización: {e}")
