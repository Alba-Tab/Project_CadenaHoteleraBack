from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgramaFidelizacionViewSet, CuentaFidelizacionViewSet

# Crear el router para las URLs de la API
router = DefaultRouter()
router.register(r'programas', ProgramaFidelizacionViewSet, basename='programa-fidelizacion')
router.register(r'cuentas', CuentaFidelizacionViewSet, basename='cuenta-fidelizacion')

urlpatterns = [
    path('', include(router.urls)),
]

"""
URLs disponibles:

Programas de Fidelización:
- GET /programas/ - Listar todos los programas
- POST /programas/ - Crear nuevo programa
- GET /programas/{id}/ - Obtener programa específico
- PUT /programas/{id}/ - Actualizar programa completo
- PATCH /programas/{id}/ - Actualizar programa parcialmente
- DELETE /programas/{id}/ - Eliminar programa
- GET /programas/activos/ - Obtener solo programas activos
- GET /programas/{id}/estadisticas/ - Obtener estadísticas del programa

Parámetros de consulta para programas:
- ?activo=true/false - Filtrar por estado
- ?search=texto - Búsqueda en nombre y descripción

Cuentas de Fidelización:
- GET /cuentas/ - Listar todas las cuentas
- POST /cuentas/ - Crear nueva cuenta
- GET /cuentas/{id}/ - Obtener cuenta específica
- PUT /cuentas/{id}/ - Actualizar cuenta completa
- PATCH /cuentas/{id}/ - Actualizar cuenta parcialmente
- DELETE /cuentas/{id}/ - Eliminar cuenta
- GET /cuentas/mis_cuentas/ - Obtener cuentas del usuario autenticado
- POST /cuentas/{id}/acumular_puntos/ - Acumular puntos
- POST /cuentas/{id}/calcular_descuento/ - Calcular descuento disponible
- POST /cuentas/{id}/canjear_puntos/ - Canjear puntos por descuento

Parámetros de consulta para cuentas:
- ?cliente=id - Filtrar por cliente
- ?programa=id - Filtrar por programa
- ?con_puntos=true - Solo cuentas con puntos
"""