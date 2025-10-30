from rest_framework import views, permissions
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.utils.text import slugify
from io import BytesIO

from apps._reporting.qbe import apply_filters, import_model, project_columns
from apps._reporting.exporters import export_docx, export_xlsx, export_pdf
from apps._reporting.serializers import PreviewRequestSerializer, ExportRequestSerializer, EmailRequestSerializer
from apps._reporting.email_service import enviar_reporte_por_email
from .registry import REGISTRY
from .servicios import agregar_porcentaje_ocupacion_a_rows


class IsReportViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


def _get_report(slug: str):
    try:
        return REGISTRY.get(slug)
    except KeyError:
        raise Http404


class HabitacionesReportPreviewView(views.APIView):
    """
    Vista personalizada para preview de reportes de habitaciones.
    Añade automáticamente el porcentaje de ocupación a todas las filas.
    """
    permission_classes = [IsReportViewer]

    def post(self, request, slug: str):
        r = _get_report(slug)
        ser = PreviewRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # Obtener parámetros opcionales para el cálculo de ocupación
        fecha_inicio = request.data.get('fecha_inicio_ocupacion')
        fecha_fin = request.data.get('fecha_fin_ocupacion')

        model = import_model(r.model_path)
        qs = model.objects.all()
        qs = apply_filters(qs, r, data.get("filters", []))
        ordering = data.get("ordering") or r.default_ordering
        qs = qs.order_by(*ordering)

        # Proyectar columnas (excluir porcentaje_ocupacion porque no existe en BD)
        columns = data["columns"]
        columns_bd = [c for c in columns if c != 'porcentaje_ocupacion']
        rows = project_columns(qs, columns_bd)

        # SIEMPRE añadir porcentaje de ocupación (columna calculada)
        rows = agregar_porcentaje_ocupacion_a_rows(rows, fecha_inicio, fecha_fin)

        # Limitar resultados después de añadir columnas calculadas
        rows = rows[:data["limit"]]
        total = qs.count()

        return Response({"total": total, "rows": rows})


class HabitacionesReportExportView(views.APIView):
    """
    Vista personalizada para exportar reportes de habitaciones.
    Añade automáticamente el porcentaje de ocupación a todas las filas.
    """
    permission_classes = [IsReportViewer]

    def post(self, request, slug: str):
        r = _get_report(slug)
        ser = ExportRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # Obtener parámetros opcionales para el cálculo de ocupación
        fecha_inicio = request.data.get('fecha_inicio_ocupacion')
        fecha_fin = request.data.get('fecha_fin_ocupacion')

        model = import_model(r.model_path)
        qs = model.objects.all()
        qs = apply_filters(qs, r, data.get("filters", []))
        ordering = data.get("ordering") or r.default_ordering
        qs = qs.order_by(*ordering)

        # Proyectar columnas (excluir porcentaje_ocupacion porque no existe en BD)
        columns = data["columns"]
        columns_bd = [c for c in columns if c != 'porcentaje_ocupacion']
        rows = project_columns(qs, columns_bd)

        # SIEMPRE añadir porcentaje de ocupación (columna calculada)
        rows = agregar_porcentaje_ocupacion_a_rows(rows, fecha_inicio, fecha_fin)

        fname = slugify(r.name)
        fmt = data["format"]

        if fmt == "xlsx":
            blob, ct, fn = export_xlsx(rows, fname)
        elif fmt == "docx":
            blob, ct, fn = export_docx(rows, r.name, fname)
        elif fmt == "pdf":
            blob, ct, fn = export_pdf(rows, r.name, fname)
        else:
            return Response({"detail": "Formato no soportado"}, status=400)

        file_obj = BytesIO(blob)
        file_obj.seek(0)
        resp = FileResponse(file_obj, as_attachment=True, filename=fn, content_type=ct)
        resp["X-Content-Type-Options"] = "nosniff"
        return resp


class HabitacionesReportEmailView(views.APIView):
    """
    Vista personalizada para enviar reportes de habitaciones por email.
    Añade automáticamente el porcentaje de ocupación a todas las filas.
    """
    permission_classes = [IsReportViewer]

    def post(self, request, slug: str):
        r = _get_report(slug)
        ser = EmailRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # Obtener parámetros opcionales para el cálculo de ocupación
        fecha_inicio = request.data.get('fecha_inicio_ocupacion')
        fecha_fin = request.data.get('fecha_fin_ocupacion')

        model = import_model(r.model_path)
        qs = model.objects.all()
        qs = apply_filters(qs, r, data.get("filters", []))
        ordering = data.get("ordering") or r.default_ordering
        qs = qs.order_by(*ordering)

        # Proyectar columnas (excluir porcentaje_ocupacion porque no existe en BD)
        columns = data["columns"]
        columns_bd = [c for c in columns if c != 'porcentaje_ocupacion']
        rows = project_columns(qs, columns_bd)

        # SIEMPRE añadir porcentaje de ocupación (columna calculada)
        rows = agregar_porcentaje_ocupacion_a_rows(rows, fecha_inicio, fecha_fin)

        # Enviar el reporte por email usando el servicio genérico
        result = enviar_reporte_por_email(
            rows=rows,
            report_name=r.name,
            format=data["format"],
            recipient_email=data["recipient_email"],
            subject=data["subject"],
            message=data.get("message"),
            tenant=getattr(request, 'tenant', None)  # Pasar el tenant si existe
        )

        if result["success"]:
            return Response({"detail": result["message"]}, status=200)
        else:
            return Response({"detail": result["message"]}, status=500)
