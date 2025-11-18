from rest_framework import viewsets, permissions
from auditlog.models import LogEntry

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # 👇 Import diferido (solo cuando se llama a la vista)
        from .serializers_audit import LogEntrySerializer
        return LogEntrySerializer

    def get_queryset(self):
        queryset = LogEntry.objects.select_related('actor').order_by('-timestamp')

        # Parámetros GET opcionales
        modelo = self.request.query_params.get('modelo')
        usuario = self.request.query_params.get('usuario')

        if modelo:
            queryset = queryset.filter(content_type__model__icontains=modelo)
        if usuario:
            queryset = queryset.filter(actor__username__icontains=usuario)

        return queryset
# Vista para acceder a los logs de auditoría