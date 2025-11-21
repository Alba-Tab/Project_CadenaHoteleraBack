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
    serializer_class = ReservaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Optimizado con select_related y prefetch_related para evitar N+1 queries"""
        return Reserva.objects.select_related(
            'huesped',
            'hotel',
            'habitacion'
        ).prefetch_related(
            'habitacion__reservas',
            'folios_estancia'  # Para el método get_folio() del serializer
        ).order_by('-id')

    def perform_create(self, serializer):
        from django.db import connection
        data = serializer.validated_data
        print(f"⏱️ PERFORM_CREATE INICIO")
        logger.info(f"⏱️ Inicio perform_create")

        reserva = procesar_reserva(data)
        serializer.instance = reserva
        print(f"⏱️ RESERVA CREADA: ID={reserva.id}")

        # 🔔 CAPTURAR TODOS LOS DATOS DE BD ANTES DE NOTIFICACIÓN
        # Esto previene pérdida de conexión en RDS Aurora con multi-tenancy
        huesped = reserva.huesped

        if huesped and huesped.fcm_token:
            # ✅ CRÍTICO: Extraer TODOS los datos de la BD AHORA
            # antes de que el middleware resetee el schema
            token = str(huesped.fcm_token)  # Convertir a string inmutable
            username = str(huesped.username)
            hotel_nombre = str(reserva.hotel.nombre)
            fecha_entrada = str(reserva.fecha_entrada)
            fecha_salida = str(reserva.fecha_salida)
            reserva_id = int(reserva.id)
            timestamp = str(timezone.now())

            print(f"📱 Datos capturados para notificación: usuario={username}, token={token[:20]}...")
            logger.info(f"📱 Preparando notificación para usuario {username}")

            # 🔥 ENVIAR EN THREAD SEPARADO - No depende de la conexión BD
            def enviar_notificacion():
                try:
                    print(f"📤 [THREAD] Enviando notificación a {username}")
                    resultado = NotificationService.send_to_token(
                        token=token,
                        title='Reserva Confirmada',
                        body=f"Tu reserva en {hotel_nombre} del {fecha_entrada} al {fecha_salida} ha sido confirmada",
                        data={
                            'type': 'reserva',
                            'notification_type': 'confirmacion',
                            'reserva_id': str(reserva_id),
                            'timestamp': timestamp
                        }
                    )
                    if resultado:
                        print(f"✅ [THREAD] Notificación enviada exitosamente")
                        logger.info(f"✅ Notificación enviada a {username}")
                    else:
                        print(f"⚠️ [THREAD] Fallo al enviar notificación")
                        logger.warning(f"⚠️ Fallo al enviar notificación a {username}")
                except Exception as e:
                    print(f"❌ [THREAD] Error: {str(e)}")
                    logger.error(f"❌ Error en thread de notificación: {str(e)}")

            # Iniciar thread daemon (se cierra automáticamente)
            thread = threading.Thread(target=enviar_notificacion, daemon=True)
            thread.start()
            print(f"✅ Thread de notificación iniciado (no bloqueante)")
        else:
            print(f"⚠️ Usuario sin FCM token - notificación omitida")
            logger.warning(f"⚠️ Usuario {huesped.username if huesped else 'N/A'} sin FCM token")

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
        reservas = Reserva.objects.select_related(
            'huesped', 'hotel', 'habitacion'
        ).filter(estado=Reserva.CONFIRMADA).order_by('-id')
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

        reservas = Reserva.objects.select_related(
            'huesped', 'hotel', 'habitacion'
        ).filter(
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
        reservas = Reserva.objects.select_related(
            'huesped', 'hotel', 'habitacion'
        ).filter(estado=Reserva.REALIZADA).order_by('-id')
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

        reservas = Reserva.objects.select_related(
            'huesped', 'hotel', 'habitacion'
        ).filter(
            estado=Reserva.REALIZADA,
            huesped__id=usuario_id
        ).order_by('-id')
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)
