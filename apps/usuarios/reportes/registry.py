from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

USUARIOS_BASE = ReportDefinition(
    slug="usuarios_base",
    name="Usuarios (básico)",
    model_path="apps.usuarios.models.User",
    default_ordering=["username", "email"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("username", "Usuario", "str", ("eq","icontains","in")),
        ReportField("email", "Email", "str", ("eq","icontains","in")),
        ReportField("first_name", "Nombre", "str", ("eq","icontains","in")),
        ReportField("last_name", "Apellido", "str", ("eq","icontains","in")),
        ReportField("is_active", "Activo", "bool", ("eq",)),
        ReportField("is_staff", "Es Staff", "bool", ("eq",)),
        ReportField("is_superuser", "Es Superusuario", "bool", ("eq",)),
        ReportField("date_joined", "Fecha Registro", "datetime", ("eq","between","gte","lte")),
        ReportField("last_login", "Último Login", "datetime", ("eq","between","gte","lte")),
    ],
    filterable=[
        ReportField("username", "Usuario", "str", ("eq","icontains","in")),
        ReportField("email", "Email", "str", ("eq","icontains","in")),
        ReportField("first_name", "Nombre", "str", ("eq","icontains","in")),
        ReportField("last_name", "Apellido", "str", ("eq","icontains","in")),
        ReportField("is_active", "Activo", "bool", ("eq",)),
        ReportField("is_staff", "Es Staff", "bool", ("eq",)),
        ReportField("is_superuser", "Es Superusuario", "bool", ("eq",)),
        ReportField("date_joined", "Fecha Registro", "datetime", ("between","gte","lte","eq")),
        ReportField("last_login", "Último Login", "datetime", ("between","gte","lte","eq")),
    ],
    description="Listado de usuarios del sistema con información de acceso y permisos.",
)

REGISTRY.register(USUARIOS_BASE)