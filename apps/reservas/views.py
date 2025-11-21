from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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
        data = serializer.validated_data
        print(f"⏱️ PERFORM_CREATE INICIO - data: {data}")
        logger.info(f"⏱️ Inicio perform_create - data: {data}")

        reserva = procesar_reserva(data)
        serializer.instance = reserva
        print(f"⏱️ RESERVA CREADA: ID={reserva.id}")
        logger.info(f"⏱️ Reserva creada: ID={reserva.id}")

        # 🔔 Enviar notificación push en BACKGROUND (no bloquea respuesta)
        huesped = reserva.huesped
        print(f"🔍 DEBUG HUESPED: {huesped}, ID={huesped.id if huesped else 'None'}, HAS_TOKEN={bool(huesped.fcm_token if huesped else False)}")
        logger.info(f"🔍 DEBUG: huesped={huesped}, huesped.id={huesped.id if huesped else 'None'}, token={'[' + huesped.fcm_token[:20] + '...]' if huesped and huesped.fcm_token else 'None'}")

        if huesped and huesped.fcm_token:
            print(f"✅ HUESPED TIENE TOKEN FCM: {huesped.fcm_token[:30]}...")
            # ✅ Ejecutar en thread separado (no espera que termine)
            def enviar_notificacion_background():
                try:
                    print("🔔 THREAD INICIADO: Enviando notificación push...")
                    logger.info("🔔 Thread: Enviando notificación push...")
                    
                    result = NotificationService.send_reserva_notification(
                        usuario=huesped,
                        reserva_id=reserva.id,
                        mensaje=f"Tu reserva en {reserva.hotel.nombre} del {reserva.fecha_entrada} al {reserva.fecha_salida} ha sido confirmada",
                        notification_type='confirmacion'
                    )
                    print(f"✅ THREAD COMPLETADO: Notificación enviada={result}")
                    logger.info(f"✅ Thread: Notificación enviada al huésped {huesped.username}, result={result}")
                except Exception as e:
                    print(f"❌❌❌ THREAD ERROR: {str(e)}")
                    logger.error(f"⚠️ Thread: Error enviando notificación: {str(e)}")
                    import traceback
                    print(f"❌ TRACEBACK: {traceback.format_exc()}")

            thread = threading.Thread(target=enviar_notificacion_background, daemon=True)
            thread.start()
            print("🚀 THREAD LANZADO - Respondiendo al cliente")
            logger.info("🚀 Thread de notificación iniciado - respondiendo al cliente")
        else:
            print(f"❌ NO SE ENVIA NOTIFICACION - Huésped={huesped}, Token={huesped.fcm_token if huesped else 'N/A'}")
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
