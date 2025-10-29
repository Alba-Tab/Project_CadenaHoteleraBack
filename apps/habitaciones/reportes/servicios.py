from datetime import datetime, timedelta
from apps.reservas.models import Reserva


def calcular_porcentaje_ocupacion(habitacion_id, fecha_inicio=None, fecha_fin=None):
    """
    Calcula el porcentaje de ocupación de una habitación en un período de tiempo.

    Args:
        habitacion_id: ID de la habitación
        fecha_inicio: Fecha inicial del período (str 'YYYY-MM-DD' o date, por defecto: hace 30 días)
        fecha_fin: Fecha final del período (str 'YYYY-MM-DD' o date, por defecto: hoy)

    Returns:
        float: Porcentaje de ocupación (0-100)
    """
    # Convertir strings a objetos date si es necesario
    if isinstance(fecha_fin, str):
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    elif fecha_fin is None:
        fecha_fin = datetime.now().date()

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    elif fecha_inicio is None:
        fecha_inicio = fecha_fin - timedelta(days=30)

    # Calcular días totales del período
    dias_totales = (fecha_fin - fecha_inicio).days + 1

    if dias_totales <= 0:
        return 0.0

    # Obtener reservas confirmadas o realizadas en el período
    reservas = Reserva.objects.filter(
        habitacion_id=habitacion_id,
        estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA],
        fecha_entrada__lte=fecha_fin,
        fecha_salida__gte=fecha_inicio
    )

    # Calcular días ocupados
    dias_ocupados = 0
    for reserva in reservas:
        # Ajustar fechas al período solicitado
        inicio_efectivo = max(reserva.fecha_entrada, fecha_inicio)
        fin_efectivo = min(reserva.fecha_salida, fecha_fin)

        # Calcular días de esta reserva
        dias_reserva = (fin_efectivo - inicio_efectivo).days + 1
        if dias_reserva > 0:
            dias_ocupados += dias_reserva

    # Calcular porcentaje (limitado a 100% en caso de solapamientos)
    porcentaje = min((dias_ocupados / dias_totales) * 100, 100.0)

    return round(porcentaje, 2)


def agregar_porcentaje_ocupacion_a_rows(rows, fecha_inicio=None, fecha_fin=None):
    """
    Añade el porcentaje de ocupación a cada fila del reporte.

    Args:
        rows: Lista de diccionarios con los datos del reporte
        fecha_inicio: Fecha inicial del período para calcular ocupación
        fecha_fin: Fecha final del período para calcular ocupación

    Returns:
        list: Lista de diccionarios con la columna 'porcentaje_ocupacion' añadida
    """
    for row in rows:
        habitacion_id = row.get('id')
        if habitacion_id:
            porcentaje = calcular_porcentaje_ocupacion(habitacion_id, fecha_inicio, fecha_fin)
            row['% ocupacion'] = porcentaje
        else:
            row['% ocupacion'] = 0.0

    return rows

