from rest_framework import serializers


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
