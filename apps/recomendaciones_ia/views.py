from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import RecomendacionPrecio, HistorialRecomendacion
from .serializers import (
    RecomendacionPrecioSerializer,
    HistorialRecomendacionSerializer,
    AceptarRecomendacionSerializer
)
from .services import ServicioRecomendaciones


class RecomendacionIAViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestionar recomendaciones de precios con IA
    
    Endpoints:
    - GET /api/ia/recomendar/ - Listar recomendaciones pendientes
    - POST /api/ia/recomendar/generar/ - Generar nuevas recomendaciones
    - POST /api/ia/recomendar/aceptar/ - Aceptar recomendaciones
    - POST /api/ia/recomendar/rechazar/ - Rechazar todas
    - GET /api/ia/recomendar/historial/ - Ver historial
    """
    permission_classes = [IsAdminUser]
    serializer_class = RecomendacionPrecioSerializer
    servicio = ServicioRecomendaciones()
    
    def get_queryset(self):
        """Lista las recomendaciones pendientes"""
        return self.servicio.obtener_recomendaciones_pendientes()
    
    @action(detail=False, methods=['post'], url_path='generar')
    def generar(self, request):
        """
        POST /api/ia/recomendar/generar/
        Genera nuevas recomendaciones de precios basadas en IA
        """
        try:
            resultado = self.servicio.generar_recomendaciones(
                usuario=request.user
            )
            
            if resultado['errores']:
                return Response({
                    'mensaje': f'Generadas {resultado["total_generadas"]} recomendaciones con algunos errores',
                    'total_generadas': resultado['total_generadas'],
                    'tipos_procesados': resultado['tipos_procesados'],
                    'errores': resultado['errores']
                }, status=status.HTTP_206_PARTIAL_CONTENT)
            
            return Response({
                'mensaje': f'Se generaron {resultado["total_generadas"]} recomendaciones correctamente',
                'total_generadas': resultado['total_generadas'],
                'tipos_procesados': resultado['tipos_procesados']
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'error': f'Error al generar recomendaciones: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='aceptar')
    def aceptar(self, request):
        """
        POST /api/ia/recomendar/aceptar/
        Acepta recomendaciones y aplica los cambios de precio
        
        Body:
        {
            "ids": [1, 2, 3],  // IDs específicos
            "todas": false     // o true para aceptar todas
        }
        """
        serializer = AceptarRecomendacionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = self.servicio.aceptar_recomendaciones(
                ids=serializer.validated_data.get('ids'),
                todas=serializer.validated_data.get('todas', False),
                usuario=request.user
            )
            
            if 'error' in resultado:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
            
            if resultado['aplicadas'] == 0:
                return Response({
                    'mensaje': 'No hay recomendaciones pendientes para aplicar'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'mensaje': f'Se aplicaron {resultado["aplicadas"]} cambios de precio correctamente',
                'aplicadas': resultado['aplicadas'],
                'detalles': resultado['detalles'],
                'errores': resultado.get('errores', [])
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': f'Error al aceptar recomendaciones: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='rechazar')
    def rechazar(self, request):
        """
        POST /api/ia/recomendar/rechazar/
        Rechaza (elimina) todas las recomendaciones pendientes
        """
        try:
            cantidad = self.servicio.rechazar_todas()
            
            return Response({
                'mensaje': f'Se rechazaron {cantidad} recomendaciones',
                'cantidad': cantidad
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': f'Error al rechazar recomendaciones: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='historial')
    def historial(self, request):
        """
        GET /api/ia/recomendar/historial/?fecha_desde=2025-01-01&fecha_hasta=2025-12-31
        Obtiene el historial de recomendaciones aceptadas
        """
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        try:
            historial = self.servicio.obtener_historial(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            serializer = HistorialRecomendacionSerializer(historial, many=True)
            
            return Response({
                'total': historial.count(),
                'resultados': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': f'Error al obtener historial: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
