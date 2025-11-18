from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

SERVICIOS_ASOCIADOS_BASE = ReportDefinition(
    slug="servicios_asociados_base",
    name="Servicios Asociados (básico)",
    model_path="apps.servicios_asociados.models.ServiciosAsociados",
    default_ordering=["-fecha_servicio", "estado"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("servicio__nombre", "Servicio", "str", ("eq","icontains","in")),
        ReportField("servicio__tipo", "Tipo Servicio", "str", ("eq","icontains","in")),
        ReportField("servicio__precio", "Precio Unitario", "decimal", ("eq","gte","lte","between")),
        ReportField("cantidad", "Cantidad", "int", ("eq","gte","lte","between")),
        ReportField("monto_total", "Monto Total", "decimal", ("eq","gte","lte","between")),
        ReportField("fecha_servicio", "Fecha Servicio", "datetime", ("eq","between","gte","lte")),
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("reserva__id", "ID Reserva", "int", ("eq","in","gte","lte")),
        ReportField("reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("reserva__habitacion__numero", "Habitación", "str", ("eq","icontains","in")),
        ReportField("reserva__huesped__username", "Huésped (usuario)", "str", ("eq","icontains","in")),
        ReportField("reserva__huesped__first_name", "Nombre Huésped", "str", ("eq","icontains","in")),
        ReportField("reserva__huesped__last_name", "Apellido Huésped", "str", ("eq","icontains","in")),
        ReportField("folioestancia__id", "ID Folio", "int", ("eq","in","gte","lte")),
        ReportField("observaciones", "Observaciones", "str", ("eq","icontains","in")),
    ],
    filterable=[
        ReportField("estado", "Estado", "str", ("eq","in","ne","icontains")),
        ReportField("servicio__nombre", "Servicio", "str", ("eq","icontains","in")),
        ReportField("servicio__tipo", "Tipo Servicio", "str", ("eq","icontains","in")),
        ReportField("fecha_servicio", "Fecha Servicio", "datetime", ("between","gte","lte","eq")),
        ReportField("reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("monto_total", "Monto Total", "decimal", ("gte","lte","between","eq")),
        ReportField("reserva__huesped__email", "Email Huésped", "str", ("eq","icontains","in")),
    ],
    description="Listado de servicios asociados a reservas con información de cantidad, monto y estado.",
)

REGISTRY.register(SERVICIOS_ASOCIADOS_BASE)