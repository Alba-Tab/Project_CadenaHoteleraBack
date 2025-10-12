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

    habitacion.estado = Habitacion.RESERVADA
    habitacion.save()

    # Asociamos los servicios a la reserva
    # asociar_servicios(reserva, habitacion, servicios)

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

    # # Actualizamos las habitaciones asociadas a la reserva
    # # Se actualizan las habitaciones solo si se proporcionan nuevas habitaciones
    # # if habitaciones:
    # #     reserva.habitaciones_reservadas.all().delete()  # Se eliminan las habitaciones anteriores
    # #     for habitacion in habitaciones:
    # #         HabitacionReserva.objects.create(
    # #             reserva=reserva,
    # #             habitacion=habitacion
    # #         )
    # if habitaciones:
    #     actualizar_habitaciones(reserva, habitaciones)


# Funciones auxiliares
def verificar_fechas(fecha_entrada, fecha_salida):
    if fecha_salida <= fecha_entrada:
        raise ValidationError("La fecha de salida debe ser mayor a la fecha de entrada.")

def calcular_total_reserva(habitaciones, total_noches):
    servicios = habitaciones
    total = sum(habitacion.precio_noche for habitacion in habitaciones)
    return total * total_noches

# def actualizar_habitaciones(reserva, habitaciones):
#     # Obtener las habitaciones actuales asociadas con la reserva
#     habitaciones_actuales = reserva.habitaciones_reservadas.all()
#
#     # 1. Eliminar las habitaciones que ya no están en la lista de habitaciones
#     habitaciones_ids = [habitacion.id for habitacion in habitaciones]  # IDs de habitaciones recibidos
#     habitaciones_a_eliminar = habitaciones_actuales.filter(habitacion__id__notin=habitaciones_ids)
#     habitaciones_a_eliminar.delete()
#
#     # 2. Agregar las habitaciones nuevas que no estén asociadas aún
#     for habitacion_id in habitaciones_ids:
#         if not habitaciones_actuales.filter(habitacion__id=habitacion_id).exists():
#             DetalleReserva.objects.create(
#                 reserva=reserva,
#                 habitacion_id=habitacion_id  # Usamos el ID directamente
#             )
#
# def asociar_servicios(reserva, habitacion, servicios):
#     for servicio in servicios:
#         ServicioReserva.objects.create(
#             reserva=reserva,
#             servicio=servicio,
#             cantidad=1,  # Asumimos una cantidad de 1 por defecto
#             precio_unitario=servicio.precio,
#             monto_total=servicio.precio  # Cantidad * Precio unitario
#         )