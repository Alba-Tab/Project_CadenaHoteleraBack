"""
Servicios para generar y gestionar recomendaciones de precios
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.habitaciones.models import Habitacion
from .models import RecomendacionPrecio, HistorialRecomendacion
from .ml_model import ModeloRecomendacionPrecios


class ServicioRecomendaciones:
    """
    Servicio para gestionar el ciclo de vida de las recomendaciones
    """
    
    def __init__(self):
        self.modelo = ModeloRecomendacionPrecios()
    
    def generar_recomendaciones(self, usuario=None):
        """
        Genera recomendaciones para todas las habitaciones del tenant actual
        
        Args:
            usuario: Usuario que solicita las recomendaciones (opcional)
        
        Returns:
            dict con resultados de la generación
        """
        # Obtener tipos únicos de habitaciones
        tipos_habitacion = Habitacion.objects.values_list('tipo', flat=True).distinct()
        
        recomendaciones_creadas = []
        errores = []
        
        for tipo in tipos_habitacion:
            try:
                # Obtener habitaciones de este tipo
                habitaciones = Habitacion.objects.filter(tipo=tipo)
                
                if not habitaciones.exists():
                    continue
                
                # Predecir precio para este tipo
                precio_sugerido, confianza, motivo = self.modelo.predecir_precio(tipo)
                
                # Crear recomendación para cada habitación de este tipo
                for habitacion in habitaciones:
                    # Eliminar recomendaciones anteriores no aceptadas
                    RecomendacionPrecio.objects.filter(
                        habitacion=habitacion,
                        aceptada=False
                    ).delete()
                    
                    # Crear nueva recomendación
                    recomendacion = RecomendacionPrecio.objects.create(
                        habitacion=habitacion,
                        tarifa_actual=habitacion.precio_noche,
                        tarifa_sugerida=precio_sugerido,
                        confianza=Decimal(str(confianza)),
                        motivo=motivo
                    )
                    
                    recomendaciones_creadas.append(recomendacion)
            
            except Exception as e:
                errores.append({
                    'tipo': tipo,
                    'error': str(e)
                })
        
        return {
            'total_generadas': len(recomendaciones_creadas),
            'tipos_procesados': len(tipos_habitacion),
            'errores': errores,
            'recomendaciones': recomendaciones_creadas
        }
    
    @transaction.atomic
    def aceptar_recomendaciones(self, ids=None, todas=False, usuario=None):
        """
        Acepta recomendaciones y aplica los cambios de precio
        
        Args:
            ids: Lista de IDs de recomendaciones a aceptar
            todas: Si es True, acepta todas las pendientes
            usuario: Usuario que acepta las recomendaciones
        
        Returns:
            dict con resultados
        """
        # Obtener recomendaciones a aceptar
        if todas:
            recomendaciones = RecomendacionPrecio.objects.filter(
                aceptada=False,
                aplicada=False
            )
        elif ids:
            recomendaciones = RecomendacionPrecio.objects.filter(
                id__in=ids,
                aceptada=False,
                aplicada=False
            )
        else:
            return {
                'error': 'Debes proporcionar IDs o marcar "todas" como True',
                'aplicadas': 0
            }
        
        if not recomendaciones.exists():
            return {
                'mensaje': 'No hay recomendaciones pendientes',
                'aplicadas': 0
            }
        
        aplicadas = []
        errores = []
        
        for recomendacion in recomendaciones:
            try:
                # Guardar precio anterior
                precio_anterior = recomendacion.habitacion.precio_noche
                
                # Aplicar nuevo precio
                recomendacion.habitacion.precio_noche = recomendacion.tarifa_sugerida
                recomendacion.habitacion.save()
                
                # Marcar recomendación como aceptada y aplicada
                recomendacion.aceptada = True
                recomendacion.aplicada = True
                recomendacion.save()
                
                # Crear registro en historial
                HistorialRecomendacion.objects.create(
                    habitacion=recomendacion.habitacion,
                    tarifa_anterior=precio_anterior,
                    tarifa_nueva=recomendacion.tarifa_sugerida,
                    confianza=recomendacion.confianza,
                    motivo=recomendacion.motivo,
                    aceptado_por=usuario
                )
                
                aplicadas.append({
                    'habitacion': str(recomendacion.habitacion),
                    'precio_anterior': float(precio_anterior),
                    'precio_nuevo': float(recomendacion.tarifa_sugerida)
                })
            
            except Exception as e:
                errores.append({
                    'habitacion': str(recomendacion.habitacion),
                    'error': str(e)
                })
        
        return {
            'aplicadas': len(aplicadas),
            'detalles': aplicadas,
            'errores': errores
        }
    
    def rechazar_todas(self):
        """
        Rechaza (elimina) todas las recomendaciones pendientes
        
        Returns:
            int: Cantidad de recomendaciones eliminadas
        """
        cantidad = RecomendacionPrecio.objects.filter(
            aceptada=False,
            aplicada=False
        ).count()
        
        RecomendacionPrecio.objects.filter(
            aceptada=False,
            aplicada=False
        ).delete()
        
        return cantidad
    
    def obtener_recomendaciones_pendientes(self):
        """
        Obtiene todas las recomendaciones no aceptadas
        
        Returns:
            QuerySet de RecomendacionPrecio
        """
        return RecomendacionPrecio.objects.filter(
            aceptada=False,
            aplicada=False
        ).select_related('habitacion', 'habitacion__hotel').order_by('-fecha_generacion')
    
    def obtener_historial(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene el historial de recomendaciones aceptadas
        
        Args:
            fecha_desde: Fecha inicial del filtro
            fecha_hasta: Fecha final del filtro
        
        Returns:
            QuerySet de HistorialRecomendacion
        """
        queryset = HistorialRecomendacion.objects.select_related(
            'habitacion',
            'habitacion__hotel',
            'aceptado_por'
        ).order_by('-fecha_aceptacion')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_aceptacion__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_aceptacion__lte=fecha_hasta)
        
        return queryset
