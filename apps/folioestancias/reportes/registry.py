from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportDefinition(
    slug="folioestancias_base",
    name="Folios de Estancia (basico)",
    model_path="apps.folioestancias.models.FolioEstancia",
    default_ordering=["-id", "estado"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("total_pagado", "Total Pagado", "decimal", ("eq","between","gte","lte")),
        ReportField("huesped__username", "Huésped (usuario)", "str", ("eq","icontains","in")),
        ReportField("huesped__first_name", "Nombre Huésped", "str", ("eq","icontains","in")),
        ReportField("huesped__last_name", "Apellido Huésped", "str", ("eq","icontains","in")),
        ReportField("huesped__email", "Email Huésped", "str", ("eq","icontains","in")),
        ReportField("reserva__id", "ID Reserva", "int", ("eq","in","gte","lte")),
        ReportField("reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("reserva__habitacion__numero", "Habitación", "str", ("eq","icontains","in")),
        ReportField("reserva__fecha_entrada", "Fecha Entrada", "date", ("eq","between","gte","lte")),
        ReportField("reserva__fecha_salida", "Fecha Salida", "date", ("eq","between","gte","lte")),
    ],
    filterable=[
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("total_pagado", "Total Pagado", "decimal", ("between","gte","lte","eq")),
        ReportField("huesped__email", "Email Huésped", "str", ("eq","icontains","in")),
        ReportField("reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("reserva__fecha_entrada", "Fecha Entrada", "date", ("between","gte","lte","eq")),
        ReportField("reserva__fecha_salida", "Fecha Salida", "date", ("between","gte","lte","eq")),
    ],
    description="Listado y filtrado de folios de estancia con informacion de reserva y huesped.",
)

REGISTRY.register(FOLIOESTANCIAS_BASE)