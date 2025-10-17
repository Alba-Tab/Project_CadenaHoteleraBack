from rest_framework import viewsets, permissions, filters
from .models import Pago
from .serializers import PagoSerializer

class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los pagos.
    Permite crear, listar, actualizar y eliminar pagos.
    """
    queryset = Pago.objects.select_related('folio_estancia').all()
    serializer_class = PagoSerializer
    permission_classes = [permissions.AllowAny]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['metodo', 'estado', 'referencia']
    ordering_fields = ['fecha_pago', 'monto', 'created_at', 'id']
    ordering = ['-fecha_pago', '-id']
    
    def get_queryset(self):
        """
        Opcionalmente filtra pagos por parámetros de query.
        """
        queryset = super().get_queryset()
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por método
        metodo = self.request.query_params.get('metodo', None)
        if metodo:
            queryset = queryset.filter(metodo__icontains=metodo)
        
        # Filtrar por folio_estancia
        folio_estancia = self.request.query_params.get('folio_estancia', None)
        if folio_estancia:
            queryset = queryset.filter(folio_estancia_id=folio_estancia)
        
        return queryset
