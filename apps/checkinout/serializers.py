from rest_framework import serializers
from .models import CheckInOut

class CheckInOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInOut
        fields = '__all__'
