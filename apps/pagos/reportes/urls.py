from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY

urlpatterns = build_urlpatterns_for_registry(REGISTRY)



# Listar reportes disponibles
# GET /api/pagos/reportes/
# # Obtener esquema (campos y operadores)
# GET /api/pagos/reportes/pagos_base/schema

# # Query By Example (QBE)
# POST /api/pagos/reportes/pagos_base/preview
# # Exportar con filtros
# POST /api/pagos/reportes/pagos_base/export
# # Enviar por email
# POST /api/pagos/reportes/pagos_base/email
# # Nuevo endpoint QBE avanzado
# POST /api/pagos/reportes/pagos_base/qbe



# levanta endpoints solo de pagos:
# GET /api/pagos/reportes/
# GET /api/pagos/reportes/{slug}/schema
# POST /api/pagos/reportes/{slug}/preview
# POST /api/pagos/reportes/{slug}/export