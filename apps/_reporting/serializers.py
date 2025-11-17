from rest_framework import serializers
from .qbe import OP_LOOKUPS


#valida columns/filters/ordering/limit y formato.

class FilterSerializer(serializers.Serializer):
    field = serializers.CharField()
    op = serializers.CharField()
    value = serializers.JSONField(required=False, allow_null=True)

class PreviewRequestSerializer(serializers.Serializer):
    columns = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    filters = serializers.ListField(child=FilterSerializer(), required=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500, default=100)
    ordering = serializers.ListField(child=serializers.CharField(), required=False)

class ExportRequestSerializer(PreviewRequestSerializer):
    format = serializers.ChoiceField(choices=["xlsx", "docx", "pdf"])
    

class EmailReportRequestSerializer(serializers.Serializer):
    columns = serializers.ListField(child=serializers.CharField())
    filters = serializers.ListField(child=serializers.DictField(), default=list)
    ordering = serializers.ListField(child=serializers.CharField(), default=list)
    format = serializers.ChoiceField(choices=["xlsx", "docx", "pdf"])
    
    # Nuevos campos para email
    recipient_email = serializers.EmailField(help_text="Email del destinatario")
    subject = serializers.CharField(
        max_length=200, 
        required=False, 
        help_text="Asunto del email (opcional)"
    )
    message = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Mensaje adicional (opcional)"
    )


class QBEFilterSerializer(serializers.Serializer):
    field = serializers.CharField()
    op = serializers.ChoiceField(choices=list(OP_LOOKUPS.keys()))
    value = serializers.JSONField(required=False, allow_null=True)
    
    def validate(self, data):
        # Validar que el field existe en el reporte
        # Validar que el op es válido para el tipo de campo
        return data