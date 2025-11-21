from urllib import request
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
from .ml_model import ModeloRecomendacionPrecios


class RecomendacionIAViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAdminUser]
    serializer_class = RecomendacionPrecioSerializer
    servicio = ServicioRecomendaciones()

    def get_queryset(self):
        return self.servicio.obtener_recomendaciones_pendientes()
    @action(detail=False, methods=['post'], url_path='generar')
    def generar(self, request):
        try:
            resultado = self.servicio.generar_recomendaciones(usuario=request.user)
            return Response(resultado, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    # ---------------------------------------------------------
    # ENTRENAR MODELO MANUALMENTE
    # ---------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='entrenar')
    def entrenar(self, request):
        tipo = request.data.get("tipo")
        if not tipo:
            return Response({'error': 'El tipo de habitación es requerido'}, status=400)
         
        hotel_id = getattr(request.user, "hotel_id", None)

        if not hotel_id:
            return Response({'error': 'El usuario no tiene hotel asociado'}, status=400)

        modelo = ModeloRecomendacionPrecios()
        exito, mensaje, confianza = modelo.entrenar_modelo(hotel_id, tipo)

        return Response({
            'exito': exito,
            'mensaje': mensaje,
            'confianza': confianza
        })

    # ---------------------------------------------------------
    # ACEPTAR RECOMENDACIONES
    # ---------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='aceptar')
    def aceptar(self, request):
        serializer = AceptarRecomendacionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        resultado = self.servicio.aceptar_recomendaciones(
            ids=serializer.validated_data.get('ids'),
            todas=serializer.validated_data.get('todas'),
            usuario=request.user
        )

        return Response(resultado)

    # ---------------------------------------------------------
    # RECHAZAR TODAS
    # ---------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='rechazar')
    def rechazar(self, request):
        cantidad = self.servicio.rechazar_todas()
        return Response({'mensaje': f'{cantidad} recomendaciones eliminadas'})

    # ---------------------------------------------------------
    # HISTORIAL
    # ---------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='historial')
    def historial(self, request):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')

        historial = self.servicio.obtener_historial(fecha_desde, fecha_hasta)

        ser = HistorialRecomendacionSerializer(historial, many=True)

        return Response({
            'total': historial.count(),
            'resultados': ser.data
        })
