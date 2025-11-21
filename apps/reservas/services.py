from django.db import transaction
from rest_framework.exceptions import ValidationError
import logging

from apps.folioestancias.models import FolioEstancia
from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva
from core.notifications_service import NotificationService

logger = logging.getLogger(__name__)


# Función para procesar una nueva reserva
@transaction.atomic
def procesar_reserva(data):
    # Obtenemos las habitaciones y fechas del diccionario data
    habitacion = data.get('habitacion')
    fecha_entrada = data.get('fecha_entrada')
    fecha_salida = data.get('fecha_salida')

    # Verificamos que las fechas sean válidas
    verificar_fechas(fecha_entrada, fecha_salida)
    # Calculamos el total de noches
    total_noches = (fecha_salida - fecha_entrada).days
    # Calculamos el total de la reserva
    total = habitacion.precio_noche * total_noches
    # Creamos la reserva
    reserva = Reserva.objects.create(
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        total=total,
        huesped=data.get('huesped'),
        hotel=data.get('hotel'),
        habitacion=habitacion
    )

    # Actualizamos el estado de la habitación a 'reservada'
    habitacion.estado = Habitacion.RESERVADA
    habitacion.save()

    # 🔔 Enviar notificación push al huésped si tiene token FCM
    huesped = reserva.huesped
    if huesped and huesped.fcm_token:
        try:
            NotificationService.send_reserva_notification(
                usuario=huesped,
                reserva_id=reserva.id,
                mensaje=f"Tu reserva en {reserva.hotel.nombre} del {fecha_entrada} al {fecha_salida} ha sido confirmada",
                notification_type='confirmacion'
            )
            logger.info(f"✅ Notificación enviada al huésped {huesped.username}")
        except Exception as e:
            # No romper la transacción si falla la notificación
            logger.error(f"⚠️ Error enviando notificación: {str(e)}")

    return reserva


# Función para actualizar una reserva existente
@transaction.atomic
def actualizar_reserva(reserva, data):
    # Obtenemos las habitaciones y fechas del diccionario data
    # Si no se proporcionan, se mantienen las actuales
    habitacion = data.get('habitaciones')
    fecha_entrada = data.get('fecha_entrada', reserva.fecha_entrada)
    fecha_salida = data.get('fecha_salida', reserva.fecha_salida)

    # Verificamos que las fechas sean válidas
    verificar_fechas(fecha_entrada, fecha_salida)
    # Calculamos el total de noches
    total_noches = (fecha_salida - fecha_entrada).days

    if habitacion:
        # Cambiamos el estado de las habitaciones si es necesario
        cambiar_estados(habitacion, reserva.habitacion)
    else:
        # Si no se proporciona una nueva habitación, mantenemos la actual
        habitacion = reserva.habitacion

    # Calculamos el total de la reserva
    total = habitacion.precio_noche * total_noches

    # Actualizamos los campos de la reserva
    reserva.fecha_entrada = fecha_entrada
    reserva.fecha_salida = fecha_salida
    reserva.total = total
    reserva.estado = data.get('estado', reserva.estado)
    reserva.huesped = data.get('huesped', reserva.huesped)
    reserva.habitacion = habitacion
    reserva.hotel = data.get('hotel', reserva.hotel)

    if reserva.estado == Reserva.CANCELADA or reserva.estado == Reserva.REALIZADA:
        # Liberamos la habitación si la reserva es cancelada
        habitacion.estado = Habitacion.DISPONIBLE
        habitacion.save()

    # Guardamos los cambios
    reserva.save()


# Funciones auxiliares
def verificar_fechas(fecha_entrada, fecha_salida):
    if fecha_salida <= fecha_entrada:
        raise ValidationError("La fecha de salida debe ser mayor a la fecha de entrada.")

def cambiar_estados(nueva_habitacion, habitacion_actual):
    if nueva_habitacion != habitacion_actual:
        # Liberamos la habitación actual
        habitacion_actual.estado = Habitacion.DISPONIBLE
        habitacion_actual.save()
        # Reservamos la nueva habitación
        nueva_habitacion.estado = Habitacion.RESERVADA
        nueva_habitacion.save()
