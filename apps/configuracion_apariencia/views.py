from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ConfiguracionApariencia
from .serializers import ConfiguracionAparienciaSerializer
from apps.hoteles.models import Hotel


class ConfiguracionAparienciaViewSet(viewsets.ModelViewSet):
    serializer_class = ConfiguracionAparienciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrar por hotel del usuario si es necesario
        return ConfiguracionApariencia.objects.all()

    def create(self, request, *args, **kwargs):
        # Aquí podrías validar que no exista otra config para el mismo hotel
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'patch', 'put'], url_path='hotel/(?P<hotel_id>[^/.]+)')
    def configuracion_por_hotel(self, request, hotel_id=None):
        """
        GET/PATCH/PUT /api/configuracion-apariencia/hotel/1/

        Obtiene o actualiza la configuración de un hotel específico.
        Si no existe configuración, la crea automáticamente en PATCH/PUT.
        """
        try:
            # Verificar que el hotel existe
            hotel = Hotel.objects.get(id=hotel_id)

            if request.method == 'GET':
                # Para GET, solo obtener si existe
                try:
                    config = ConfiguracionApariencia.objects.get(hotel=hotel)
                    serializer = self.get_serializer(config)
                    return Response(serializer.data)
                except ConfiguracionApariencia.DoesNotExist:
                    return Response(
                        {'error': 'No existe configuración para este hotel'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            elif request.method in ['PATCH', 'PUT']:
                # Para PATCH/PUT, obtener o crear automáticamente
                config, created = ConfiguracionApariencia.objects.get_or_create(
                    hotel=hotel,
                    defaults={
                        'color_primario': '#00a1ff',
                        'color_secundario': '#16cdc7',
                        'color_fondo': '#f8fafd',
                        'familia_fuente': 'Inter',
                        'tamano_fuente_base': 14,
                        'modo_tema': 'claro',
                        'tema': 'Por defecto',
                        'tipo_letra': 'Inter'
                    }
                )

                # Si se creó, informar al usuario
                if created:
                    message = "Configuración creada automáticamente y actualizada"
                else:
                    message = "Configuración actualizada"

                # Actualizar con los datos enviados
                partial = request.method == 'PATCH'
                serializer = self.get_serializer(
                    config,
                    data=request.data,
                    partial=partial
                )

                if serializer.is_valid():
                    serializer.save()
                    response_data = serializer.data
                    response_data['message'] = message
                    response_data['created'] = created
                    return Response(response_data)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Hotel.DoesNotExist:
            return Response(
                {'error': 'Hotel no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
