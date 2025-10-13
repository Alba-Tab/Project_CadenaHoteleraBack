from django.core.exceptions import ValidationError
from django.db import transaction
from .models import ProgramaFidelizacion, CuentaFidelizacion
from decimal import Decimal


class FidelizacionService:
    """Servicio para manejar la lógica de negocio de fidelización"""
    
    @staticmethod
    def crear_cuenta_fidelizacion(cliente, programa_id):
        """Crear una nueva cuenta de fidelización para un cliente"""
        try:
            programa = ProgramaFidelizacion.objects.get(id=programa_id, activo=True)
        except ProgramaFidelizacion.DoesNotExist:
            raise ValidationError("El programa de fidelización no existe o está inactivo")
        
        if CuentaFidelizacion.objects.filter(cliente=cliente, fidelizacion=programa).exists():
            raise ValidationError("El cliente ya tiene una cuenta en este programa")
        
        with transaction.atomic():
            cuenta = CuentaFidelizacion.objects.create(
                cliente=cliente,
                fidelizacion=programa,
                puntos_acumulados=0
            )
        
        return cuenta
    
    @staticmethod
    def acumular_puntos(cuenta_id, monto_gastado):
        """Acumular puntos por una compra"""
        try:
            cuenta = CuentaFidelizacion.objects.select_related('fidelizacion').get(id=cuenta_id)
        except CuentaFidelizacion.DoesNotExist:
            raise ValidationError("La cuenta de fidelización no existe")
        
        if not cuenta.fidelizacion.activo:
            raise ValidationError("El programa de fidelización está inactivo")
        
        if monto_gastado <= 0:
            raise ValidationError("El monto gastado debe ser mayor a 0")
        
        with transaction.atomic():
            puntos_ganados = cuenta.acumular_puntos(float(monto_gastado))
        
        return {
            'puntos_ganados': puntos_ganados,
            'puntos_totales': cuenta.puntos_acumulados,
            'monto_gastado': monto_gastado
        }
    
    @staticmethod
    def calcular_descuento_disponible(cuenta_id, total_cuenta):
        """Calcular el descuento disponible para una cuenta"""
        try:
            cuenta = CuentaFidelizacion.objects.select_related('fidelizacion').get(id=cuenta_id)
        except CuentaFidelizacion.DoesNotExist:
            raise ValidationError("La cuenta de fidelización no existe")
        
        if not cuenta.fidelizacion.activo:
            return 0
        
        if total_cuenta <= 0:
            raise ValidationError("El total de la cuenta debe ser mayor a 0")
        
        descuento_disponible = cuenta.calcular_descuento_disponible(float(total_cuenta))
        
        return {
            'descuento_maximo_disponible': round(descuento_disponible, 2),
            'puntos_actuales': cuenta.puntos_acumulados,
            'porcentaje_maximo': cuenta.fidelizacion.descuento_maximo,
            'puntos_por_dolar': cuenta.fidelizacion.puntos_por_dolar_descuento
        }
    
    @staticmethod
    def canjear_puntos(cuenta_id, monto_descuento, total_cuenta):
        """Canjear puntos por descuento"""
        try:
            cuenta = CuentaFidelizacion.objects.select_related('fidelizacion').get(id=cuenta_id)
        except CuentaFidelizacion.DoesNotExist:
            raise ValidationError("La cuenta de fidelización no existe")
        
        if not cuenta.fidelizacion.activo:
            raise ValidationError("El programa de fidelización está inactivo")
        
        if monto_descuento <= 0:
            raise ValidationError("El monto de descuento debe ser mayor a 0")
        
        if total_cuenta <= 0:
            raise ValidationError("El total de la cuenta debe ser mayor a 0")
        
        if monto_descuento > total_cuenta:
            raise ValidationError("El descuento no puede ser mayor al total de la cuenta")
        
        # Verificar que el descuento solicitado no exceda el disponible
        descuento_disponible = cuenta.calcular_descuento_disponible(float(total_cuenta))
        
        if float(monto_descuento) > descuento_disponible:
            raise ValidationError(
                f"El descuento solicitado (${monto_descuento}) excede el disponible (${descuento_disponible:.2f})"
            )
        
        with transaction.atomic():
            # Canjear los puntos
            puntos_antes = cuenta.puntos_acumulados
            exito = cuenta.canjear_puntos(float(monto_descuento))
            
            if not exito:
                raise ValidationError("No se pudieron canjear los puntos")
        
        puntos_canjeados = puntos_antes - cuenta.puntos_acumulados
        
        return {
            'descuento_aplicado': float(monto_descuento),
            'puntos_canjeados': puntos_canjeados,
            'puntos_restantes': cuenta.puntos_acumulados,
            'total_final': float(total_cuenta) - float(monto_descuento)
        }
    
    @staticmethod
    def obtener_estadisticas_programa(programa_id):
        """Obtener estadísticas de un programa de fidelización"""
        try:
            programa = ProgramaFidelizacion.objects.get(id=programa_id)
        except ProgramaFidelizacion.DoesNotExist:
            raise ValidationError("El programa de fidelización no existe")
        
        cuentas = CuentaFidelizacion.objects.filter(fidelizacion=programa)
        
        estadisticas = {
            'programa': programa.nombre,
            'total_cuentas': cuentas.count(),
            'puntos_totales_sistema': sum(cuenta.puntos_acumulados for cuenta in cuentas),
            'promedio_puntos_por_cuenta': 0,
            'cuentas_activas': cuentas.filter(puntos_acumulados__gt=0).count()
        }
        
        if estadisticas['total_cuentas'] > 0:
            estadisticas['promedio_puntos_por_cuenta'] = round(
                estadisticas['puntos_totales_sistema'] / estadisticas['total_cuentas'], 2
            )
        
        return estadisticas