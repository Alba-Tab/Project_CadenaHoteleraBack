from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.habitaciones.models import Habitacion
from apps.reservas.models import Reserva


# Función para procesar una nueva reserva
@transaction.atomic
def procesar_reserva(data):
    # Obtenemos las habitaciones y fechas del diccionario data
    habitacion = data.get('habitacion')
    fecha_entrada = data.get('fecha_entrada')
    fecha_salida = data.get('fecha_salida')
    servicios = data.get('servicios', [])

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

    # Asociamos los servicios a la reserva

    return reserva


# Función para actualizar una reserva existente
@transaction.atomic
def actualizar_reserva(reserva, data):
    # Obtenemos las habitaciones y fechas del diccionario data
    # Si no se proporcionan, se mantienen las actuales
    habitacion = data.get('habitaciones', reserva.habitacion)
    fecha_entrada = data.get('fecha_entrada', reserva.fecha_entrada)
    fecha_salida = data.get('fecha_salida', reserva.fecha_salida)

    # Verificamos que las fechas sean válidas
    verificar_fechas(fecha_entrada, fecha_salida)
    # Calculamos el total de noches
    total_noches = (fecha_salida - fecha_entrada).days
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
    # Guardamos los cambios
    reserva.save()


# Funciones auxiliares
def verificar_fechas(fecha_entrada, fecha_salida):
    if fecha_salida <= fecha_entrada:
        raise ValidationError("La fecha de salida debe ser mayor a la fecha de entrada.")