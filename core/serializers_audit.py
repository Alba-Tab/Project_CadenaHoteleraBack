from rest_framework import serializers
from auditlog.models import LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField() 
    content_type = serializers.StringRelatedField()  

    class Meta:
        model = LogEntry
        fields = [
            'id',
            'actor',
            'action',
            'object_pk',
            'content_type',
            'changes',
            'remote_addr',
            'timestamp',
        ]
