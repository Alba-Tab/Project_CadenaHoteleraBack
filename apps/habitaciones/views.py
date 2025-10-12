from datetime import date

from django.utils.timezone import localdate
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Habitacion
from .serializers import HabitacionSerializer
from .services import obtener_habitaciones_reservadas_disponibles


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
        habitaciones_disponibles = Habitacion.objects.filter(tipo=Habitacion.DISPONIBLE)
        # Unimos ambas listas
        habitaciones = list(habitaciones_disponibles) + list(habitaciones_reservadas)
        # Serializamos y retornamos la respuesta
        serializer = self.get_serializer(habitaciones, many=True)
        return Response(serializer.data)
