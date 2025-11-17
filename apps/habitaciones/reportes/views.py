from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .services import obtener_recomendaciones_habitaciones
from .serializers import RecomendacionesHabitacionesResponseSerializer


class RecomendacionPrecioHabitacionesView(APIView):

    permission_classes = [permissions.IsAuthenticated]  # con tu configuración global ya es así

    def get(self, request, *args, **kwargs):
        inicio_str = request.query_params.get("inicio")
        fin_str = request.query_params.get("fin")
        hotel_id = request.query_params.get("hotel_id")

        fecha_inicio = fecha_fin = None

        try:
            if inicio_str:
                fecha_inicio = date.fromisoformat(inicio_str)
            if fin_str:
                fecha_fin = date.fromisoformat(fin_str)
        except ValueError:
            return Response(
                {"detail": "Formato de fecha inválido. Usa YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hotel_id is not None:
            try:
                hotel_id = int(hotel_id)
            except ValueError:
                return Response(
                    {"detail": "hotel_id debe ser un entero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        data = obtener_recomendaciones_habitaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            hotel_id=hotel_id,
        )

        serializer = RecomendacionesHabitacionesResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
