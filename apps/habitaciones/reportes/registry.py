from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

#Define el catálogo de reportes de la app Habitaciones (por ahora uno básico, listo para preview/export con filtros).

REGISTRY = ReportRegistry()

HABITACIONES_BASE = ReportDefinition(
    slug="habitaciones_base",
    name="Habitaciones (básico)",
    model_path="apps.habitaciones.models.Habitacion",
    default_ordering=["hotel__nombre", "numero"],  # ajusta si tu campo es distinto
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("numero", "Número", "str", ("eq","icontains","in")),      # cambia si tu campo es 'codigo'
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")), # ej. disponible/ocupada/mantenimiento
        ReportField("tipo", "Tipo", "str", ("eq","in","icontains")),
        ReportField("precio_noche", "Precio por noche", "decimal", ("eq","between","gte","lte")),
        ReportField("capacidad", "Capacidad", "str", ("eq","icontains")),
        ReportField("porcentaje_ocupacion", "% Ocupación (30 días)", "decimal", ()),  # Columna calculada
    ],
    filterable=[
        ReportField("hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("numero", "Número", "str", ("eq","icontains","in")),
        ReportField("tipo", "Tipo", "str", ("eq","in","icontains")),
        ReportField("precio_noche", "Precio por noche", "decimal", ("between","gte","lte","eq")),
    ],
    description="Listado y filtrado de habitaciones por hotel, número, estado y porcentaje de ocupación.",
)

REGISTRY.register(HABITACIONES_BASE)
