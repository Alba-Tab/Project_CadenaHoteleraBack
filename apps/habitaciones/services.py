from datetime import date
from typing import Optional

from django.db.models import Q, Count
from django.db.models.functions import ExtractYear, ExtractMonth

from apps.habitaciones.models import Habitacion
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

def obtener_ranking_y_demanda(
        id_hotel: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
):
    # 1. Preparar QuerySet base de Habitaciones
    qs_habitaciones = Habitacion.objects.select_related('hotel')

    # 2. Preparar QuerySet base de Reservas válidas (Solo por estado y hotel)
    # Este QS será la fuente del Histórico (demanda_mensual_historica)
    qs_reservas_base = Reserva.objects.filter(
        estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA]
    )

    # 3. Aplicar Filtros COMUNES (Hotel)
    if id_hotel is not None:
        qs_habitaciones = qs_habitaciones.filter(hotel_id=id_hotel)
        qs_reservas_base = qs_reservas_base.filter(hotel_id=id_hotel)

        # 4. Construir el objeto Q para el RANKING (Status + Fechas)
    # Este filtro se aplica únicamente al ranking individual (total_reservas).
    ranking_filter_q = Q(reservas__estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA])

    if fecha_inicio and fecha_fin:
        # Filtramos por fecha directamente en la relación
        ranking_filter_q &= Q(reservas__fecha_entrada__range=(fecha_inicio, fecha_fin))

    # 5. Ranking de habitaciones por INSTANCIA (USA EL FILTRO Q DIRECTO)
    ranking_por_habitacion = qs_habitaciones.values(
        'id',
        'numero',
        'tipo',
        'precio_noche',
        'hotel__nombre'
    ).annotate(
        # Contamos las reservas que cumplen el filtro de STATUS y FECHA
        total_reservas=Count(
            'reservas',
            filter=ranking_filter_q
        )
    ).order_by('-total_reservas')[:15]  # Top 15 habitaciones

    # 6. Estadísticas de demanda histórica por mes/año
    # 💡 CLAVE: Usamos qs_reservas_base para el Histórico (sin filtro de rango de fechas del ranking)
    demanda_mensual = qs_reservas_base.annotate(
        year=ExtractYear('fecha_entrada'),
        month=ExtractMonth('fecha_entrada')
    ).values('year', 'month').annotate(
        total_reservas_mes=Count('id')
    ).order_by('-year', '-month')

    return {
        "ranking_por_habitacion": ranking_por_habitacion,
        "demanda_mensual_historica": demanda_mensual
    }


# Otros operadores útiles en filtros de Django:
# __lt: Menor que.
# __lte: Menor o igual que.
# __gt: Mayor que.
# __gte: Mayor o igual que.
# __exact: Igual que.
# __range: Dentro de un rango de valores (e.g., fecha_salida__range=[start_date, end_date]).
# __in: Dentro de un conjunto de valores (e.g., estado__in=[Reserva.CONFIRMADA, Reserva.PENDIENTE]).