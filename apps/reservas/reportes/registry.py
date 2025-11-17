from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry
# from .registry import REGISTRY 

#Define y registra los reportes solo de la app reservas.

REGISTRY = ReportRegistry()

RESERVAS_BASE = ReportDefinition(
    slug="reservas_base",
    name="Reservas (básico)",
    model_path="apps.reservas.models.Reserva",
    default_ordering=["-id"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("fecha_entrada", "Fecha entrada", "date", ("eq","between","gte","lte")),
        ReportField("fecha_salida", "Fecha salida", "date", ("eq","between","gte","lte")),
        ReportField("hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("habitacion__numero", "Nro habitación", "str", ("eq","icontains","in")),
        ReportField("huesped__username", "Huésped (usuario)", "str", ("eq","icontains","in")),
    ],
    filterable=[
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("fecha_entrada", "Fecha entrada", "date", ("between","gte","lte","eq")),
        ReportField("fecha_salida", "Fecha salida", "date", ("between","gte","lte","eq")),
        ReportField("hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
    ],
    description="Listado y filtrado de reservas por fechas, estado, hotel, habitación y huésped.",
)

REGISTRY.register(RESERVAS_BASE)
