from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

SERVICIOS_BASE = ReportDefinition(
    slug="servicios_base",
    name="Servicios (basico)",
    model_path="apps.servicios.models.Servicio",
    default_ordering=["nombre", "tipo"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("nombre", "Nombre", "str", ("eq","icontains","in")),
        ReportField("descripcion", "Descripción", "str", ("eq","icontains","in")),
        ReportField("precio", "Precio", "decimal", ("eq","between","gte","lte")),
        ReportField("tipo", "Tipo", "str", ("eq","icontains","in")),
        ReportField("created_at", "Creado", "datetime", ("eq","between","gte","lte")),
        ReportField("updated_at", "Actualizado", "datetime", ("eq","between","gte","lte")),
    ],
    filterable=[
        ReportField("nombre", "Nombre", "str", ("eq","icontains","in")),
        ReportField("tipo", "Tipo", "str", ("eq","icontains","in")),
        ReportField("precio", "Precio", "decimal", ("between","gte","lte","eq")),
        ReportField("created_at", "Creado", "datetime", ("between","gte","lte","eq")),
    ],
    description="Listado y filtrado de servicios por nombre, tipo y precio.",
)

REGISTRY.register(SERVICIOS_BASE)