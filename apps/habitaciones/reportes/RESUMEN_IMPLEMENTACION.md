# Resumen de Implementación: Porcentaje de Ocupación en Reportes de Habitaciones

## ✅ Archivos Creados

### 1. `servicios.py`
- **Función principal**: `calcular_porcentaje_ocupacion(habitacion_id, fecha_inicio, fecha_fin)`
  - Calcula el % de ocupación de una habitación en un período
  - Por defecto usa los últimos 30 días
  - Considera solo reservas confirmadas o realizadas
  
- **Función auxiliar**: `agregar_porcentaje_ocupacion_a_rows(rows, fecha_inicio, fecha_fin)`
  - Añade la columna calculada a las filas del reporte
  - Itera sobre cada fila y calcula su porcentaje

### 2. `views.py`
- **HabitacionesReportPreviewView**: Vista personalizada para preview
  - Extiende la funcionalidad base de reportes
  - Intercepta la petición para obtener parámetros de fecha
  - Añade el porcentaje de ocupación si se solicita en `columns`
  
- **HabitacionesReportExportView**: Vista personalizada para exportación
  - Similar al preview pero para exportar a XLSX/DOCX/PDF
  - Soporta los mismos parámetros de fecha

### 3. `tests.py`
- Tests unitarios completos para la funcionalidad
- Casos cubiertos:
  - Sin reservas (0%)
  - Reserva completa (100%)
  - Reserva parcial (50%)
  - Reservas canceladas no cuentan
  - Múltiples reservas
  - Reservas fuera del período
  - Solapamientos parciales

### 4. `README.md`
- Documentación técnica completa
- Descripción de columnas disponibles
- Explicación del algoritmo de cálculo
- Parámetros opcionales
- Endpoints disponibles

### 5. `EJEMPLOS.md`
- Ejemplos prácticos de uso con cURL
- Múltiples casos de uso
- Ejemplos de respuesta
- Notas importantes

## 📝 Archivos Modificados

### 1. `registry.py`
**Cambios**:
- Añadida columna `porcentaje_ocupacion` (tipo decimal, sin operadores de filtrado)
- Descomentadas columnas `tipo`, `precio_noche`, `capacidad`
- Actualizada descripción del reporte

**Antes**:
```python
columns=[
    ReportField("id", "ID", "int", ...),
    ReportField("hotel__nombre", "Hotel", "str", ...),
    ReportField("numero", "Número", "str", ...),
    ReportField("estado", "Estado", "str", ...),
    # Campos opcionales comentados
],
```

**Después**:
```python
columns=[
    ReportField("id", "ID", "int", ...),
    ReportField("hotel__nombre", "Hotel", "str", ...),
    ReportField("numero", "Número", "str", ...),
    ReportField("estado", "Estado", "str", ...),
    ReportField("tipo", "Tipo", "str", ...),
    ReportField("precio_noche", "Precio por noche", "decimal", ...),
    ReportField("capacidad", "Capacidad", "str", ...),
    ReportField("porcentaje_ocupacion", "% Ocupación (30 días)", "decimal", ()),  # Nueva columna calculada
],
```

### 2. `urls.py`
**Cambios**:
- Importadas las vistas personalizadas
- Reemplazados los endpoints de preview y export con las vistas personalizadas
- Mantenidos los endpoints de list y schema con las vistas base

**Antes**:
```python
from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY

urlpatterns = build_urlpatterns_for_registry(REGISTRY)
```

**Después**:
```python
from django.urls import path
from apps._reporting.endpoints import build_views_for_registry
from .registry import REGISTRY
from .views import HabitacionesReportPreviewView, HabitacionesReportExportView

ListV, SchemaV, _, _ = build_views_for_registry(REGISTRY)

urlpatterns = [
    path('', ListV.as_view(), name='habitaciones-report-list'),
    path('<slug:slug>/schema', SchemaV.as_view(), name='habitaciones-report-schema'),
    path('<slug:slug>/preview', HabitacionesReportPreviewView.as_view(), ...),
    path('<slug:slug>/export', HabitacionesReportExportView.as_view(), ...),
]
```

## 🔍 Cómo Funciona

### Flujo de Ejecución

1. **Cliente hace petición** POST a `/api/habitaciones/reportes/habitaciones_base/preview`
   ```json
   {
     "columns": ["id", "hotel__nombre", "numero", "porcentaje_ocupacion"],
     "fecha_inicio_ocupacion": "2025-01-01",
     "fecha_fin_ocupacion": "2025-01-31"
   }
   ```

2. **Vista personalizada** (`HabitacionesReportPreviewView`):
   - Valida la petición
   - Extrae `fecha_inicio_ocupacion` y `fecha_fin_ocupacion`
   - Aplica filtros al queryset
   - Proyecta columnas (excepto `porcentaje_ocupacion`)

3. **Servicio** (`agregar_porcentaje_ocupacion_a_rows`):
   - Itera sobre cada fila
   - Llama a `calcular_porcentaje_ocupacion` para cada habitación
   - Añade el valor calculado a la fila

4. **Cálculo** (`calcular_porcentaje_ocupacion`):
   - Obtiene reservas confirmadas/realizadas en el período
   - Calcula días ocupados considerando solapamientos
   - Devuelve porcentaje (0-100%)

5. **Respuesta** al cliente con datos enriquecidos

### Algoritmo de Cálculo

```
días_totales = (fecha_fin - fecha_inicio) + 1

Para cada reserva confirmada/realizada:
    inicio_efectivo = max(reserva.fecha_entrada, fecha_inicio)
    fin_efectivo = min(reserva.fecha_salida, fecha_fin)
    días_reserva = (fin_efectivo - inicio_efectivo) + 1
    días_ocupados += días_reserva

porcentaje = min((días_ocupados / días_totales) * 100, 100)
```

## 🎯 Características Implementadas

✅ Cálculo dinámico de porcentaje de ocupación
✅ Período configurable (por defecto 30 días)
✅ Solo cuenta reservas confirmadas o realizadas
✅ Soporte en preview y export (XLSX, DOCX, PDF)
✅ Filtrado por hotel, estado, tipo, etc. (excepto el % que es calculado)
✅ Tests unitarios completos
✅ Documentación detallada
✅ Ejemplos de uso
✅ **La columna se incluye SIEMPRE automáticamente**

## 📊 Ejemplo de Uso

**Petición**:
```bash
POST /api/habitaciones/reportes/habitaciones_base/preview
{
  "columns": ["hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
  "fecha_inicio_ocupacion": "2025-10-01",
  "fecha_fin_ocupacion": "2025-10-29",
  "limit": 10
}
```

**Respuesta**:
```json
{
  "total": 45,
  "rows": [
    {
      "hotel__nombre": "Grand Hotel",
      "numero": "101",
      "estado": "disponible",
      "porcentaje_ocupacion": 67.74
    },
    {
      "hotel__nombre": "Grand Hotel",
      "numero": "102",
      "estado": "ocupada",
      "porcentaje_ocupacion": 83.87
    }
  ]
}
```

## 🔄 Diferencias con el Sistema Base

El sistema de reportes base (`_reporting`) no soporta columnas calculadas porque:
- `project_columns()` solo hace `.values()` con campos del modelo
- No hay concepto de "computed fields"

**Solución implementada**:
- Vistas personalizadas que extienden las base
- Interceptan después de `project_columns()`
- Añaden columnas calculadas antes de devolver la respuesta
- Mantienen compatibilidad con el sistema base

## 🧪 Ejecutar Tests

```bash
python manage.py test apps.habitaciones.reportes.tests
```

## 📌 Notas Importantes

1. `porcentaje_ocupacion` NO es filtrable (es calculado, no existe en BD)
2. La columna **SIEMPRE se incluye automáticamente** en todos los reportes
3. Si no se especifican fechas, usa últimos 30 días
4. El cálculo es por habitación individual
5. Reservas canceladas o pendientes NO cuentan
6. El porcentaje máximo es 100% (incluso con solapamientos)
7. **La `views.py` es NECESARIA** porque el sistema base no soporta columnas calculadas

