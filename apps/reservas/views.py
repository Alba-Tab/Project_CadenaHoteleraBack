from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from apps.reservas.serializers import ReservaSerializer
from apps.reservas.services import procesar_reserva, actualizar_reserva
from core.notifications_service import NotificationService

logger = logging.getLogger(__name__)


# Create your views here.
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().order_by('-id')
    serializer_class = ReservaSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        data = serializer.validated_data
        logger.info(f"⏱️ Inicio perform_create - data: {data}")

        reserva = procesar_reserva(data)
        serializer.instance = reserva
        logger.info(f"⏱️ Reserva creada: ID={reserva.id}")

        # 🔔 Enviar notificación push DESPUÉS de crear la reserva (no bloquea DB)
        huesped = reserva.huesped
        logger.info(f"🔍 DEBUG: huesped={huesped}, huesped.id={huesped.id if huesped else 'None'}, token={'[' + huesped.fcm_token[:20] + '...]' if huesped and huesped.fcm_token else 'None'}")

        if huesped and huesped.fcm_token:
            logger.info("🔔 Enviando notificación push...")
            try:
                NotificationService.send_reserva_notification(
                    usuario=huesped,
                    reserva_id=reserva.id,
                    mensaje=f"Tu reserva en {reserva.hotel.nombre} del {reserva.fecha_entrada} al {reserva.fecha_salida} ha sido confirmada",
                    notification_type='confirmacion'
                )
                logger.info(f"✅ Notificación enviada al huésped {huesped.username}")
            except Exception as e:
                # No romper la respuesta si falla la notificación
                logger.error(f"⚠️ Error enviando notificación: {str(e)}")
        else:
            logger.warning(f"⚠️ No se envió notificación - Huésped sin token FCM")

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
        detail=False,
        methods=['get'],
        url_path='reservas-confirmadas',
        serializer_class=ReservaSerializer
    )
    def reservas_confirmadas(self, request):
        """Devuelve todas las reservas en estado CONFIRMADA, ordenadas por -id."""
        reservas = Reserva.objects.filter(estado=Reserva.CONFIRMADA).order_by('-id')
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='reservas-confirmadas-por-usuario',
        serializer_class=ReservaSerializer
    )
    def reservas_confirmadas_por_usuario(self, request):
        """Devuelve las reservas confirmadas de un usuario indicado por ?id_usuario=<id>.

        Si no se proporciona id_usuario o no es válido, devuelve 400.
        Devuelve todas las reservas confirmadas del usuario, ordenadas por -id.
        """
        id_usuario = request.query_params.get('id_usuario')
        if not id_usuario:
            return Response({'detail': 'Falta parámetro id_usuario'}, status=400)
        try:
            usuario_id = int(id_usuario)
        except (TypeError, ValueError):
            return Response({'detail': 'id_usuario debe ser un entero'}, status=400)

        reservas = Reserva.objects.filter(
            estado=Reserva.CONFIRMADA,
            huesped__id=usuario_id
        ).order_by('-id')
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='reservas-realizadas',
        serializer_class=ReservaSerializer
    )
    def reservas_realizadas(self, request):
        """Devuelve todas las reservas en estado REALIZADA, ordenadas por -id."""
        reservas = Reserva.objects.filter(estado=Reserva.REALIZADA).order_by('-id')
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='reservas-realizadas-por-usuario',
        serializer_class=ReservaSerializer
    )
    def reservas_realizadas_por_usuario(self, request):
        """Devuelve las reservas realizadas de un usuario indicado por ?id_usuario=<id>.

        Si no se proporciona id_usuario o no es válido, devuelve 400.
        Devuelve todas las reservas realizadas del usuario, ordenadas por -id.
        """
        id_usuario = request.query_params.get('id_usuario')
        if not id_usuario:
            return Response({'detail': 'Falta parámetro id_usuario'}, status=400)
        try:
            usuario_id = int(id_usuario)
        except (TypeError, ValueError):
            return Response({'detail': 'id_usuario debe ser un entero'}, status=400)

        reservas = Reserva.objects.filter(
            estado=Reserva.REALIZADA,
            huesped__id=usuario_id
        ).order_by('-id')
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)
