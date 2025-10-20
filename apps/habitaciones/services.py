from apps.reservas.models import Reserva

# Función para obtener las habitaciones que estarán disponibles a partir de una fecha dada
def obtener_habitaciones_reservadas_disponibles(fecha):
    # Obtenemos las reservas que terminan antes o en la fecha dada y que están confirmadas
    reservas = Reserva.objects.filter(
        fecha_salida__lte=fecha,
        estado=Reserva.CONFIRMADA
    )

    # Extraemos las habitaciones de las reservas obtenidas
    habitaciones = []
    for reserva in reservas:
        habitaciones.append(reserva.habitacion)

    return habitaciones



# Otros operadores útiles en filtros de Django:
# __lt: Menor que.
# __lte: Menor o igual que.
# __gt: Mayor que.
# __gte: Mayor o igual que.
# __exact: Igual que.
# __range: Dentro de un rango de valores (e.g., fecha_salida__range=[start_date, end_date]).
# __in: Dentro de un conjunto de valores (e.g., estado__in=[Reserva.CONFIRMADA, Reserva.PENDIENTE]).