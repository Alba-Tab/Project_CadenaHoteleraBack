from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from apps.reservas.serializers import ReservaSerializer, DetalleReservaSerializer
from apps.reservas.services import procesar_reserva, actualizar_reserva


# Create your views here.
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        data = serializer.validated_data
        reserva = procesar_reserva(data)
        serializer.instance = reserva

    def perform_update(self, serializer):
        data = serializer.validated_data
        reserva = self.get_object()
        actualizar_reserva(reserva, data)
        serializer.instance = reserva

    def perform_destroy(self, instance):
        reserva = self.get_object()
        habitacion = reserva.habitacion
        # Al eliminar la reserva, se libera la habitación
        habitacion.estado = Habitacion.DISPONIBLE
        habitacion.save()
        instance.delete()

    @action(
        detail=True,
        methods=['get'],
        url_path='detalle',
        serializer_class=DetalleReservaSerializer,
        pagination_class=None
    )
    def detalle(self, request, pk=None):
        reserva = self.get_object()
        serializer = DetalleReservaSerializer(reserva)
        return Response(serializer.data)