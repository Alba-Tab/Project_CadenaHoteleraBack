"""
Servicios de negocio para el módulo de Pagos.
Contiene la lógica de negocio relacionada con los pagos.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Pago
from apps.folioestancias.models import FolioEstancia


class PagoService:
    """
    Servicio para gestionar la lógica de negocio de los pagos.
    """
    
    @staticmethod
    def crear_pago(folio_estancia_id, monto, metodo, referencia=None):
        """
        Crea un nuevo pago y actualiza el folio de estancia.
        
        Args:
            folio_estancia_id: ID del folio de estancia
            monto: Monto del pago
            metodo: Método de pago (efectivo, tarjeta, etc.)
            referencia: Referencia del pago (opcional)
            
        Returns:
            Pago creado
        """
        with transaction.atomic():
            # Crear el pago
            pago = Pago.objects.create(
                folio_estancia_id=folio_estancia_id,
                monto=monto,
                metodo=metodo,
                referencia=referencia,
                fecha_pago=timezone.now().date(),
                estado=Pago.ESTADO_PENDIENTE
            )
            
            # Actualizar el folio de estancia si existe
            if folio_estancia_id:
                try:
                    folio = FolioEstancia.objects.get(id=folio_estancia_id)
                    folio.total_pagado = Decimal(folio.total_pagado or 0) + Decimal(monto)
                    folio.save()
                except FolioEstancia.DoesNotExist:
                    pass
            
            return pago
    
    @staticmethod
    def marcar_como_completado(pago_id):
        """
        Marca un pago como completado.
        
        Args:
            pago_id: ID del pago
            
        Returns:
            Pago actualizado
        """
        pago = Pago.objects.get(id=pago_id)
        pago.estado = Pago.ESTADO_COMPLETADO
        pago.save()
        return pago
    
    @staticmethod
    def marcar_como_fallido(pago_id):
        """
        Marca un pago como fallido y revierte el monto en el folio.
        
        Args:
            pago_id: ID del pago
            
        Returns:
            Pago actualizado
        """
        with transaction.atomic():
            pago = Pago.objects.get(id=pago_id)
            pago.estado = Pago.ESTADO_FALLIDO
            pago.save()
            
            # Revertir el monto del folio si existe
            if pago.folio_estancia:
                folio = pago.folio_estancia
                folio.total_pagado = Decimal(folio.total_pagado or 0) - Decimal(pago.monto)
                if folio.total_pagado < 0:
                    folio.total_pagado = Decimal('0.00')
                folio.save()
            
            return pago
    
    @staticmethod
    def obtener_pagos_por_folio(folio_estancia_id):
        """
        Obtiene todos los pagos de un folio de estancia.
        
        Args:
            folio_estancia_id: ID del folio de estancia
            
        Returns:
            QuerySet de pagos
        """
        return Pago.objects.filter(folio_estancia_id=folio_estancia_id).order_by('-fecha_pago')
    
    @staticmethod
    def obtener_total_pagado_por_folio(folio_estancia_id):
        """
        Calcula el total pagado de un folio de estancia.
        
        Args:
            folio_estancia_id: ID del folio de estancia
            
        Returns:
            Total pagado (Decimal)
        """
        from django.db.models import Sum
        
        resultado = Pago.objects.filter(
            folio_estancia_id=folio_estancia_id,
            estado=Pago.ESTADO_COMPLETADO
        ).aggregate(total=Sum('monto'))
        
        return resultado['total'] or Decimal('0.00')
    
    @staticmethod
    def cancelar_pago(pago_id):
        """
        Cancela un pago y revierte el monto del folio.
        
        Args:
            pago_id: ID del pago
            
        Returns:
            bool: True si se canceló correctamente
        """
        with transaction.atomic():
            pago = Pago.objects.get(id=pago_id)
            
            # Solo se pueden cancelar pagos pendientes o completados
            if pago.estado == Pago.ESTADO_FALLIDO:
                return False
            
            # Revertir el monto del folio si existe
            if pago.folio_estancia:
                folio = pago.folio_estancia
                folio.total_pagado = Decimal(folio.total_pagado or 0) - Decimal(pago.monto)
                if folio.total_pagado < 0:
                    folio.total_pagado = Decimal('0.00')
                folio.save()
            
            # Eliminar el pago
            pago.delete()
            
            return True
