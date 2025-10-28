from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

# Reporte de Programas de Fidelización
PROGRAMAS_FIDELIZACION = ReportDefinition(
    slug="programas_fidelizacion",
    name="Programas de Fidelización",
    model_path="apps.fidelizacion.models.ProgramaFidelizacion",
    default_ordering=["nombre", "activo"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("nombre", "Nombre", "str", ("eq","icontains","in")),
        ReportField("descripcion", "Descripción", "str", ("eq","icontains","in")),
        ReportField("descuento_maximo", "Descuento Máximo (%)", "int", ("eq","gte","lte","between")),
        ReportField("puntos_por_dolar_descuento", "Puntos por $1", "int", ("eq","gte","lte","between")),
        ReportField("activo", "Activo", "bool", ("eq",)),
    ],
    filterable=[
        ReportField("nombre", "Nombre", "str", ("eq","icontains","in")),
        ReportField("activo", "Activo", "bool", ("eq",)),
        ReportField("descuento_maximo", "Descuento Máximo (%)", "int", ("gte","lte","between","eq")),
    ],
    description="Listado de programas de fidelización con configuración de descuentos y puntos.",
)

# Reporte de Cuentas de Fidelización
CUENTAS_FIDELIZACION = ReportDefinition(
    slug="cuentas_fidelizacion",
    name="Cuentas de Fidelización",
    model_path="apps.fidelizacion.models.CuentaFidelizacion",
    default_ordering=["-puntos_acumulados", "cliente__username"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("cliente__username", "Cliente (usuario)", "str", ("eq","icontains","in")),
        ReportField("cliente__first_name", "Nombre Cliente", "str", ("eq","icontains","in")),
        ReportField("cliente__last_name", "Apellido Cliente", "str", ("eq","icontains","in")),
        ReportField("cliente__email", "Email Cliente", "str", ("eq","icontains","in")),
        ReportField("fidelizacion__nombre", "Programa", "str", ("eq","icontains","in")),
        ReportField("puntos_acumulados", "Puntos Acumulados", "int", ("eq","gte","lte","between")),
        ReportField("fidelizacion__activo", "Programa Activo", "bool", ("eq",)),
    ],
    filterable=[
        ReportField("cliente__email", "Email Cliente", "str", ("eq","icontains","in")),
        ReportField("fidelizacion__nombre", "Programa", "str", ("eq","icontains","in")),
        ReportField("puntos_acumulados", "Puntos Acumulados", "int", ("gte","lte","between","eq")),
        ReportField("fidelizacion__activo", "Programa Activo", "bool", ("eq",)),
    ],
    description="Listado de cuentas de fidelización de clientes con puntos acumulados.",
)

REGISTRY.register(PROGRAMAS_FIDELIZACION)
REGISTRY.register(CUENTAS_FIDELIZACION)