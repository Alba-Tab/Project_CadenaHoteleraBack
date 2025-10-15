from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import ProgramaFidelizacion, CuentaFidelizacion
from .serializers import (
    ProgramaFidelizacionSerializer,
    CuentaFidelizacionSerializer,
    CuentaFidelizacionCreateSerializer,
    AcumularPuntosSerializer,
    CanjearPuntosSerializer
)
from .services import FidelizacionService


class ProgramaFidelizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los programas de fidelización
    """
    queryset = ProgramaFidelizacion.objects.all()
    serializer_class = ProgramaFidelizacionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar programas según parámetros de consulta"""
        queryset = super().get_queryset()
        
        # Filtrar por estado activo/inactivo
        activo = self.request.query_params.get('activo')
        if activo is not None:
            activo_bool = activo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activo=activo_bool)
        
        # Búsqueda por nombre o descripción
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        
        return queryset.order_by('-id')
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas de un programa de fidelización"""
        try:
            stats = FidelizacionService.obtener_estadisticas_programa(pk)
            return Response(stats, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Obtener solo programas activos"""
        programas_activos = self.get_queryset().filter(activo=True)
        serializer = self.get_serializer(programas_activos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CuentaFidelizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las cuentas de fidelización de los clientes
    """
    queryset = CuentaFidelizacion.objects.select_related('cliente', 'fidelizacion').all()
    serializer_class = CuentaFidelizacionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar serializer específico para creación"""
        if self.action == 'create':
            return CuentaFidelizacionCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        """Filtrar cuentas según parámetros de consulta"""
        queryset = super().get_queryset()
        
        # Filtrar por cliente
        cliente_id = self.request.query_params.get('cliente')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        # Filtrar por programa
        programa_id = self.request.query_params.get('programa')
        if programa_id:
            queryset = queryset.filter(fidelizacion_id=programa_id)
        
        # Filtrar cuentas con puntos
        con_puntos = self.request.query_params.get('con_puntos')
        if con_puntos and con_puntos.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(puntos_acumulados__gt=0)
        
        return queryset.order_by('-puntos_acumulados')
    
    def create(self, request, *args, **kwargs):
        """Crear cuenta usando el servicio"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            cuenta = FidelizacionService.crear_cuenta_fidelizacion(
                cliente=serializer.validated_data['cliente'],
                programa_id=serializer.validated_data['fidelizacion'].id
            )
            
            response_serializer = CuentaFidelizacionSerializer(cuenta)
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def acumular_puntos(self, request, pk=None):
        """Acumular puntos por una compra"""
        serializer = AcumularPuntosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            resultado = FidelizacionService.acumular_puntos(
                cuenta_id=pk,
                monto_gastado=serializer.validated_data['monto_gastado'] #type: ignore
            )
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def calcular_descuento(self, request, pk=None):
        total_cuenta = request.data.get('total_cuenta')
        
        if not total_cuenta:
            return Response(
                {'error': 'El campo total_cuenta es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            total_cuenta = float(total_cuenta)
            resultado = FidelizacionService.calcular_descuento_disponible(
                cuenta_id=pk,
                total_cuenta=total_cuenta
            )
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'El total_cuenta debe ser un número válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def canjear_puntos(self, request, pk=None):
        """Canjear puntos por descuento"""
        serializer = CanjearPuntosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            resultado = FidelizacionService.canjear_puntos(
                cuenta_id=pk,
                monto_descuento=serializer.validated_data['monto_descuento'],#type: ignore
                total_cuenta=serializer.validated_data['total_cuenta']#type: ignore
            )
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def mis_cuentas(self, request):
        """Obtener las cuentas de fidelización del usuario autenticado"""
        cuentas = self.get_queryset().filter(cliente=request.user)
        serializer = self.get_serializer(cuentas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
        