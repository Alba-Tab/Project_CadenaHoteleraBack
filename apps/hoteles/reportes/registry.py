from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

HOTELES_BASE = ReportDefinition(
    slug="hoteles_base",
    name="Hoteles (basico)",
    model_path="apps.hoteles.models.Hotel",
    default_ordering=["nombre", "ciudad", "pais"],
    columns=[
        ReportField("id", "ID", "int", ("eq", "in", "gte", "lte")),
        ReportField("nombre", "Nombre", "str", ("eq","icontains","in")),
        ReportField("telefono", "Teléfono", "str", ("eq","icontains","in")),
        ReportField("direccion", "Dirección", "str", ("eq","icontains","in")),
        ReportField("ciudad", "Ciudad", "str", ("eq","icontains","in")),
        ReportField("pais", "País", "str", ("eq","icontains","in")),
        ReportField("estado", "Estado", "str", ("eq","icontains","in")),
    ],
    filterable=[
        ReportField("nombre", "Nombre", "str", ("eq","icontains","in")),
        ReportField("ciudad", "Ciudad", "str", ("eq","icontains","in")),
        ReportField("pais", "País", "str", ("eq","icontains","in")),
        ReportField("estado", "Estado", "str", ("eq","icontains","in")),
        ReportField("telefono", "Teléfono", "str", ("eq","icontains","in")),
    ],
    description="Listado y filtrado de hoteles por nombre, ciudad, pais y estado.",
)

REGISTRY.register(HOTELES_BASE)