import calendar
from datetime import datetime, date, timedelta

from django.utils.timezone import localdate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Habitacion
from .serializers import HabitacionSerializer, HabitacionRankingSerializer
from .services import obtener_habitaciones_reservadas_disponibles, obtener_ranking_y_demanda


# from .services import obtener_habitaciones_reservadas_disponibles


class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

    # Acción personalizada para obtener habitaciones disponibles a partir de una fecha dada
    @action(
        detail=False,
        methods=['get'],
        url_path='disponibles',
        serializer_class=HabitacionSerializer
    )
    def disponibles(self, request):
        # Obtenemos la fecha desde los parámetros de consulta, por defecto es la fecha actual
        fecha = request.query_params.get('fecha', localdate())
        # Obtenemos las habitaciones que estarán disponibles a partir de la fecha dada
        habitaciones_reservadas = obtener_habitaciones_reservadas_disponibles(fecha)
        # También incluimos las habitaciones que ya están disponibles
        habitaciones_disponibles = Habitacion.objects.filter(estado=Habitacion.DISPONIBLE)
        # Unimos ambas listas
        habitaciones = list(habitaciones_disponibles) + list(habitaciones_reservadas)
        # Serializamos y retornamos la respuesta
        serializer = self.get_serializer(habitaciones, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='ranking-demanda',
        serializer_class=HabitacionRankingSerializer,
        permission_classes = [IsAuthenticated]
    )
    def ranking_demanda(self, request):
        id_hotel_param = request.query_params.get('id_hotel', None)
        fecha_inicio_str = request.query_params.get('fecha_inicio', None)
        fecha_fin_str = request.query_params.get('fecha_fin', None)

        id_hotel = None
        fecha_inicio = None
        fecha_fin = None
        nota_periodo = "Rango definido por el usuario."

        try:
            if id_hotel_param:
                id_hotel = int(id_hotel_param)
        except ValueError:
            return Response(
                {"error": "id_hotel debe ser un número entero válido."},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Las fechas deben estar en formato YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not fecha_inicio_str and not fecha_fin_str:
            hoy = date.today()
            fecha_inicio = hoy.replace(day=1)
            fecha_fin = hoy - timedelta(days=1) # Un día antes de hoy(AYER)
            nota_periodo = "Rango por defecto: Primer día del Mes Actual hasta Ayer."

        if (fecha_inicio_str and not fecha_fin_str) or (fecha_fin_str and not fecha_inicio_str):
            return Response(
                {
                    "error": "Para filtrar por un rango específico, debe proporcionar tanto 'fecha_inicio' como 'fecha_fin'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            return Response(
                {"error": "La fecha de inicio no puede ser posterior a la fecha de fin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultados = obtener_ranking_y_demanda(
            id_hotel=id_hotel,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        ranking_serializer = HabitacionRankingSerializer(
            resultados["ranking_por_habitacion"], many=True
        )

        return Response({
            "ranking_por_habitacion": ranking_serializer.data,
            "demanda_mensual_historica": list(resultados["demanda_mensual_historica"]),
            "periodo_ranking_usado": {
                "inicio": fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else None,
                "fin": fecha_fin.strftime("%Y-%m-%d") if fecha_fin else None,
                "nota": nota_periodo
            }
        }, status=status.HTTP_200_OK)