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
    canjear_puntos = serializers.BooleanField(default=False, write_only=True, required=False)
    monto_descuento = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, required=False, allow_null=True
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
            "canjear_puntos",
            "monto_descuento",
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
        canjear_puntos = validated_data.pop('canjear_puntos', False)
        monto_descuento = validated_data.pop('monto_descuento', None)
        
        folio: FolioEstancia = validated_data["folio_estancia"]
        cliente = folio.reserva.huesped
        
        descuento_aplicado = Decimal('0.00')
        puntos_canjeados = 0
        
        if canjear_puntos and monto_descuento and monto_descuento > 0:
            descuento_aplicado, puntos_canjeados = self._aplicar_descuento_fidelizacion(
                cliente=cliente,
                monto_descuento=float(monto_descuento),
                total_cuenta=float(validated_data['monto'])
            )
            validated_data['monto'] = validated_data['monto'] - Decimal(descuento_aplicado)
        
        # Crear el pago con el monto (ya con descuento aplicado si corresponde)
        pago = Pago.objects.create(
            **validated_data,
            estado=Pago.ESTADO_COMPLETADO,
        )
        
        # Actualizar el folio
        folio.total_pagado = (folio.total_pagado + pago.monto)
        folio.estado = FolioEstancia.PAGADO  
        folio.save(update_fields=["total_pagado", "estado"])
        
        # Acumular puntos de fidelización por el pago realizado
        self._acumular_puntos_fidelizacion(folio, pago)
        
        # Guardar info de descuento en el objeto para la respuesta
        pago._descuento_aplicado = descuento_aplicado  # type: ignore
        pago._puntos_canjeados = puntos_canjeados  # type: ignore
        
        return pago
    
    def _aplicar_descuento_fidelizacion(self, cliente, monto_descuento, total_cuenta):
        """
        Valida y aplica el descuento usando el servicio de fidelización.
        
        Returns:
            tuple: (descuento_aplicado, puntos_canjeados)
        """
        try:
            # Buscar cuenta de fidelización del cliente
            cuenta = CuentaFidelizacion.objects.filter(
                cliente=cliente,
                fidelizacion__activo=True
            ).first()
            
            if not cuenta:
                raise serializers.ValidationError({
                    "canjear_puntos": "El cliente no tiene una cuenta de fidelización activa."
                })
            
            # Usar el servicio para validar y canjear puntos
            resultado = FidelizacionService.canjear_puntos(
                cuenta_id=cuenta.pk,
                monto_descuento=monto_descuento,
                total_cuenta=total_cuenta
            )
            
            return (Decimal(str(resultado['descuento_aplicado'])), resultado['puntos_canjeados'])
            
        except Exception as e:
            raise serializers.ValidationError({
                "canjear_puntos": f"Error al canjear puntos: {str(e)}"
            })
    
    def _acumular_puntos_fidelizacion(self, folio: FolioEstancia, pago: Pago):
        """
        Busca o crea una cuenta de fidelización para el cliente y acumula puntos.
        Si no existe un programa activo, no hace nada.
        """
        try:
            # Obtener el cliente de la reserva
            cliente = folio.reserva.huesped
            
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
