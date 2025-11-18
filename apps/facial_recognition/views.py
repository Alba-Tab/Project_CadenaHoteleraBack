from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FaceRecognitionSerializer
from .services import FacialRecognitionService

class FacialRecognitionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'], url_path='recognize')
    def recognize(self, request):
        """
        POST /api/facial-recognition/recognize/
        Body: image (file), similarity_threshold (float, opcional)
        """
        serializer = FaceRecognitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Subir imagen temporal a S3
        from django.core.files.storage import default_storage
        import uuid
        temp_key = f"temp/recognize_{uuid.uuid4()}.jpg"
        temp_path = default_storage.save(temp_key, serializer.validated_data['image'])
        
        try:
            # Buscar en colección
            threshold = serializer.validated_data.get('similarity_threshold', 80.0)
            match = FacialRecognitionService.search_face(temp_path, threshold)
            
            if match:
                return Response({
                    'recognized': True,
                    'user': match,
                    'message': f'✅ Usuario reconocido ({match["confidence"]}%)'
                })
            else:
                return Response({
                    'recognized': False,
                    'message': '❌ No se encontró coincidencia'
                }, status=status.HTTP_404_NOT_FOUND)
        finally:
            # Eliminar imagen temporal
            default_storage.delete(temp_path)
