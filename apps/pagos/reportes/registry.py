from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

PAGOS_BASE = ReportDefinition(
    slug="pagos_base",
    name="Pagos (básico)",
    model_path="apps.pagos.models.Pago",
    default_ordering=["-fecha_pago","-id"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("fecha_pago", "Fecha de pago", "date", ("eq","between","gte","lte")),
        ReportField("monto", "Monto", "decimal", ("eq","between","gte","lte")),
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("metodo", "Método", "str", ("eq","in","icontains")),
        ReportField("folio_estancia__huesped__username", "Huésped", "str", ("eq","icontains","in")),
        ReportField("folio_estancia__reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
    ],
    filterable=[
        ReportField("fecha_pago", "Fecha de pago", "date", ("between","gte","lte","eq")),
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("metodo", "Método", "str", ("eq","in","icontains")),
        ReportField("folio_estancia__reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
    ],
    description="Pagos por fecha, estado, método y relación con hotel/huésped.",
)

REGISTRY.register(PAGOS_BASE)
