from datetime import date
from decimal import Decimal

from django.db.models import (
    Count,
    F,
    ExpressionWrapper,
    DurationField,
    Sum,
    Min,
    Max,
)

from apps.reservas.models import Reserva


def obtener_recomendaciones_habitaciones(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    hotel_id: int | None = None,
):

    # Solo consideramos reservas que realmente aportan demanda
    reservas = Reserva.objects.filter(
        estado__in=[Reserva.CONFIRMADA, Reserva.REALIZADA]
    )

    if hotel_id:
        reservas = reservas.filter(hotel_id=hotel_id)

    # Filtro por fechas (estadía, no fecha de creación)
    if fecha_inicio and fecha_fin:
        reservas = reservas.filter(
            fecha_entrada__gte=fecha_inicio,
            fecha_salida__lte=fecha_fin,
        )

    if not reservas.exists():
        return {
            "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
            "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
            "dias_periodo": 0,
            "habitaciones": [],
        }

    # Si no se pasó rango, usamos el min/max de las reservas encontradas
    if not (fecha_inicio and fecha_fin):
        rango = reservas.aggregate(
            min_entrada=Min("fecha_entrada"),
            max_salida=Max("fecha_salida"),
        )
        fecha_inicio = rango["min_entrada"]
        fecha_fin = rango["max_salida"]

    dias_periodo = (fecha_fin - fecha_inicio).days or 1

    # Duración de cada reserva en noches (timedelta)
    duracion = ExpressionWrapper(
        F("fecha_salida") - F("fecha_entrada"),
        output_field=DurationField(),
    )

    qs = (
        reservas
        .values(
            "habitacion_id",
            "habitacion__numero",
            "habitacion__tipo",
            "habitacion__precio_noche",
            "hotel_id",
            "hotel__nombre",
        )
        .annotate(
            total_reservas=Count("id"),
            total_estadia=Sum(duracion),
        )
    )

    items = []
    for row in qs:
        total_estadia = row["total_estadia"]
        noches_reservadas = total_estadia.days if total_estadia else 0

        porcentaje_ocupacion = (
            (noches_reservadas / dias_periodo) * 100
            if dias_periodo > 0 else 0
        )

        items.append(
            {
                "habitacion_id": row["habitacion_id"],
                "hotel_id": row["hotel_id"],
                "hotel_nombre": row["hotel__nombre"],
                "numero": row["habitacion__numero"],
                "tipo": row["habitacion__tipo"],
                "precio_actual": row["habitacion__precio_noche"],
                "precio_noche": row["habitacion__precio_noche"],
                "reservas_totales": row["total_reservas"],
                "noches_reservadas": noches_reservadas,
                "porcentaje_ocupacion": round(porcentaje_ocupacion, 2),
            }
        )

    # Ordenamos por demanda para asignar ranking
    items.sort(key=lambda x: x["reservas_totales"], reverse=True)
    for idx, item in enumerate(items, start=1):
        item["ranking"] = idx

    # Máxima ocupación del conjunto (para comparar relativamentre)
    max_ocupacion = max(i["porcentaje_ocupacion"] for i in items) or 0

    for item in items:
        if max_ocupacion > 0:
            rel = item["porcentaje_ocupacion"] / max_ocupacion
        else:
            rel = 0

        # Reglas de negocio para recomendación (ajústalas a gusto)
        if rel >= 0.8:
            rec_pct = 12
            motivo = "Demanda muy alta (top del hotel)."
        elif rel >= 0.6:
            rec_pct = 8
            motivo = "Demanda alta, superior al promedio."
        elif rel >= 0.4:
            rec_pct = 5
            motivo = "Demanda moderada; se puede ajustar ligeramente."
        else:
            rec_pct = 0
            motivo = "Demanda baja/normal; no se recomienda subir el precio."

        item["recomendacion_porcentaje"] = rec_pct

        precio = item["precio_noche"]
        if isinstance(precio, float):
            precio = Decimal(str(precio))

        factor = Decimal(1) + (Decimal(rec_pct) / Decimal(100))
        precio_recomendado = (precio * factor).quantize(Decimal("0.01"))
        item["precio_recomendado"] = precio_recomendado
        item["motivo"] = motivo

    return {
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "dias_periodo": dias_periodo,
        "habitaciones": items,
    }
