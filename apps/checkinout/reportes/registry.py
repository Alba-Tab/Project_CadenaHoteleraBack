from apps._reporting.base import ReportDefinition, ReportField, ReportRegistry

REGISTRY = ReportRegistry()

CHECKINOUT_BASE = ReportDefinition(
    slug="checkinout_base",
    name="Check-In/Out (básico)",
    model_path="apps.checkinout.models.CheckInOut",
    default_ordering=["-fecha_checkin", "-hora_checkin"],
    columns=[
        ReportField("id", "ID", "int", ("eq","in","gte","lte")),
        ReportField("fecha_checkin", "Fecha Check-In", "date", ("eq","between","gte","lte")),
        ReportField("hora_checkin", "Hora Check-In", "str", ("eq","icontains","in")),
        ReportField("fecha_checkout", "Fecha Check-Out", "date", ("eq","between","gte","lte")),
        ReportField("hora_checkout", "Hora Check-Out", "str", ("eq","icontains","in")),
        ReportField("observaciones", "Observaciones", "str", ("eq","icontains","in")),
        ReportField("reserva__id", "ID Reserva", "int", ("eq","in","gte","lte")),
        ReportField("reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("reserva__habitacion__numero", "Habitación", "str", ("eq","icontains","in")),
        ReportField("reserva__huesped__username", "Huésped (usuario)", "str", ("eq","icontains","in")),
        ReportField("reserva__huesped__first_name", "Nombre Huésped", "str", ("eq","icontains","in")),
        ReportField("reserva__huesped__last_name", "Apellido Huésped", "str", ("eq","icontains","in")),
        ReportField("reserva__estado", "Estado Reserva", "str", ("eq","in","ne","icontains")),
    ],
    filterable=[
        ReportField("fecha_checkin", "Fecha Check-In", "date", ("between","gte","lte","eq")),
        ReportField("fecha_checkout", "Fecha Check-Out", "date", ("between","gte","lte","eq")),
        ReportField("reserva__hotel__nombre", "Hotel", "str", ("eq","icontains","in")),
        ReportField("reserva__estado", "Estado Reserva", "str", ("eq","in","ne","icontains")),
        ReportField("reserva__huesped__email", "Email Huésped", "str", ("eq","icontains","in")),
    ],
    description="Listado y filtrado de check-ins/check-outs con información de reserva y huésped.",
)

REGISTRY.register(CHECKINOUT_BASE)