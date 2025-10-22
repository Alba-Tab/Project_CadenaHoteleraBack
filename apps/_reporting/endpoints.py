from typing import Callable
from django.http import FileResponse, Http404
from django.utils.text import slugify
from rest_framework import permissions, status, views
from rest_framework.response import Response

from .base import ReportRegistry
from .qbe import apply_filters, import_model, project_columns
from .exporters import export_docx, export_xlsx, export_pdf
from .serializers import PreviewRequestSerializer, ExportRequestSerializer

from io import BytesIO

#Que hace: crea clases de vista atadas al registry de esa app y devuelve los urlpatterns listos. Cada app usa su propio ReportRegistry.



class IsReportViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

def build_views_for_registry(registry: ReportRegistry):
    def _get(slug: str):
        try:
            return registry.get(slug)
        except KeyError:
            raise Http404

    class ReportListView(views.APIView):
        permission_classes = [IsReportViewer]
        def get(self, request):
            data = [{"slug": r.slug, "name": r.name, "description": r.description} for r in registry.all()]
            return Response(data)

    class ReportSchemaView(views.APIView):
        permission_classes = [IsReportViewer]
        def get(self, request, slug: str):
            r = _get(slug)
            def to_dict(f): return {"key": f.key, "label": f.label, "type": f.type, "ops": list(f.ops)}
            payload = {
                "slug": r.slug,
                "name": r.name,
                "description": r.description,
                "columns": [to_dict(c) for c in r.columns],
                "filterable": [to_dict(f) for f in r.filterable],
                "default_ordering": list(r.default_ordering),
            }
            return Response(payload)

    class ReportPreviewView(views.APIView):
        permission_classes = [IsReportViewer]
        def post(self, request, slug: str):
            r = _get(slug)
            ser = PreviewRequestSerializer(data=request.data); ser.is_valid(raise_exception=True)
            data = ser.validated_data
            model = import_model(r.model_path)
            qs = model.objects.all()
            qs = apply_filters(qs, r, data.get("filters", []))
            ordering = data.get("ordering") or r.default_ordering
            qs = qs.order_by(*ordering)
            rows = project_columns(qs, data["columns"])[: data["limit"]]
            total = qs.count()
            return Response({"total": total, "rows": rows})

    class ReportExportView(views.APIView):
        permission_classes = [IsReportViewer]
        def post(self, request, slug: str):
            r = _get(slug)
            ser = ExportRequestSerializer(data=request.data); ser.is_valid(raise_exception=True)
            data = ser.validated_data
            model = import_model(r.model_path)
            qs = model.objects.all()
            qs = apply_filters(qs, r, data.get("filters", []))
            ordering = data.get("ordering") or r.default_ordering
            qs = qs.order_by(*ordering)
            rows = project_columns(qs, data["columns"])
            fname = slugify(r.name)
            fmt = data["format"]

            if fmt == "xlsx":
                blob, ct, fn = export_xlsx(rows, fname)
            elif fmt == "docx":
                blob, ct, fn = export_docx(rows, r.name, fname)
            elif fmt == "pdf":
                blob, ct, fn = export_pdf(rows, r.name, fname)
            else:
                return Response({"detail": "Formato no soportado"}, status=40)
                
            file_obj = BytesIO(blob)
            file_obj.seek(0)  # por si acaso
            resp = FileResponse(file_obj, as_attachment=True, filename=fn, content_type=ct)
            resp["X-Content-Type-Options"] = "nosniff"  # evita que clientes 'adivinen' el tipo
            return resp

    return ReportListView, ReportSchemaView, ReportPreviewView, ReportExportView

def build_urlpatterns_for_registry(registry: ReportRegistry):
    ListV, SchemaV, PreviewV, ExportV = build_views_for_registry(registry)
    from django.urls import path
    return [
        path('', ListV.as_view(), name='report-list'),
        path('<slug:slug>/schema', SchemaV.as_view(), name='report-schema'),
        path('<slug:slug>/preview', PreviewV.as_view(), name='report-preview'),
        path('<slug:slug>/export', ExportV.as_view(), name='report-export'),
    ]


