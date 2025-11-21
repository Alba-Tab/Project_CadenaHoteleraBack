from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
import logging
import threading

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
        from django.db import connection
        data = serializer.validated_data
        print(f"⏱️ PERFORM_CREATE INICIO")
        logger.info(f"⏱️ Inicio perform_create")

        reserva = procesar_reserva(data)
        serializer.instance = reserva
        print(f"⏱️ RESERVA CREADA: ID={reserva.id}")

        # 🔔 ENVIAR NOTIFICACIÓN DIRECTAMENTE (SIN THREAD) - GARANTIZADO
        huesped = reserva.huesped

        if huesped and huesped.fcm_token:
            print(f"✅ ENVIANDO NOTIFICACION DIRECTA al usuario {huesped.username}")
            try:
                # Guardar info necesaria ANTES de cualquier thread
                token = huesped.fcm_token
                username = huesped.username
                hotel_nombre = reserva.hotel.nombre
                fecha_entrada = str(reserva.fecha_entrada)
                fecha_salida = str(reserva.fecha_salida)
                reserva_id = reserva.id

                # Enviar DIRECTAMENTE - sin thread
                NotificationService.send_to_token(
                    token=token,
                    title='Reserva Confirmada',
                    body=f"Tu reserva en {hotel_nombre} del {fecha_entrada} al {fecha_salida} ha sido confirmada",
                    data={
                        'type': 'reserva',
                        'notification_type': 'confirmacion',
                        'reserva_id': str(reserva_id),
                        'timestamp': str(timezone.now())
                    }
                )
                print(f"✅ NOTIFICACION ENVIADA")
            except Exception as e:
                print(f"❌ ERROR ENVIANDO: {str(e)}")
                logger.error(f"Error: {str(e)}")
        else:
            print(f"❌ NO HAY TOKEN FCM")

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
