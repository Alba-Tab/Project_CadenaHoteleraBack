from rest_framework import views, permissions
from rest_framework.response import Response
from django.http import Http404

from apps._reporting.qbe import apply_filters, import_model, project_columns
from apps._reporting.serializers import EmailRequestSerializer
from apps._reporting.email_service import enviar_reporte_por_email
from .registry import REGISTRY


class IsReportViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


def _get_report(slug: str):
    try:
        return REGISTRY.get(slug)
    except KeyError:
        raise Http404


class PagosReportEmailView(views.APIView):
    """
    Vista para enviar reportes de pagos por email.
    """
    permission_classes = [IsReportViewer]

    def post(self, request, slug: str):
        r = _get_report(slug)
        ser = EmailRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        model = import_model(r.model_path)
        qs = model.objects.all()
        qs = apply_filters(qs, r, data.get("filters", []))
        ordering = data.get("ordering") or r.default_ordering
        qs = qs.order_by(*ordering)

        # Proyectar columnas
        rows = project_columns(qs, data["columns"])

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

