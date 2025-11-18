from rest_framework import serializers

class FaceRecognitionSerializer(serializers.Serializer):
    """Serializer simple para reconocimiento facial"""
    image = serializers.ImageField(required=True)
    similarity_threshold = serializers.FloatField(default=80.0, min_value=0.0, max_value=100.0)

    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Imagen muy grande (max 10MB)")
        return value