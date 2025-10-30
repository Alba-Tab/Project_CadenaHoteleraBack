# Ejemplos de uso del reporte de habitaciones con porcentaje de ocupación

## 1. Obtener el esquema del reporte

```bash
curl -X GET "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/schema" \
  -H "Authorization: Bearer TU_TOKEN"
```

## 2. Preview básico (sin porcentaje de ocupación)

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "estado", "tipo"],
    "limit": 10
  }'
```

## 3. Preview CON porcentaje de ocupación (últimos 30 días)

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
    "limit": 20
  }'
```

## 4. Preview con período personalizado

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "estado", "tipo", "porcentaje_ocupacion"],
    "fecha_inicio_ocupacion": "2025-01-01",
    "fecha_fin_ocupacion": "2025-01-31",
    "limit": 50
  }'
```

## 5. Filtrado por hotel

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
    "filters": [
      {
        "field": "hotel__nombre",
        "op": "icontains",
        "value": "Grand"
      }
    ],
    "limit": 50
  }'
```

## 6. Filtrado por estado

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
    "filters": [
      {
        "field": "estado",
        "op": "in",
        "value": ["disponible", "ocupada"]
      }
    ],
    "limit": 50
  }'
```

## 7. Exportar a Excel con porcentaje de ocupación

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/export" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "tipo", "estado", "precio_noche", "porcentaje_ocupacion"],
    "format": "xlsx",
    "fecha_inicio_ocupacion": "2025-01-01",
    "fecha_fin_ocupacion": "2025-01-31"
  }' \
  --output habitaciones_reporte.xlsx
```

## 8. Exportar a PDF

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/export" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
    "format": "pdf"
  }' \
  --output habitaciones_reporte.pdf
```

## 9. Ejemplo completo con múltiples filtros

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "tipo", "estado", "precio_noche", "capacidad", "porcentaje_ocupacion"],
    "filters": [
      {
        "field": "hotel__nombre",
        "op": "icontains",
        "value": "Hotel"
      },
      {
        "field": "estado",
        "op": "eq",
        "value": "disponible"
      },
      {
        "field": "precio_noche",
        "op": "lte",
        "value": 200
      }
    ],
    "ordering": ["porcentaje_ocupacion", "precio_noche"],
    "fecha_inicio_ocupacion": "2025-10-01",
    "fecha_fin_ocupacion": "2025-10-29",
    "limit": 100
  }'
```

## Respuesta de ejemplo (preview)

```json
{
  "total": 45,
  "rows": [
    {
      "id": 1,
      "hotel__nombre": "Grand Hotel Palace",
      "numero": "101",
      "estado": "disponible",
      "tipo": "suite",
      "precio_noche": "150.00",
      "capacidad": "2",
      "porcentaje_ocupacion": 45.16
    },
    {
      "id": 2,
      "hotel__nombre": "Grand Hotel Palace",
      "numero": "102",
      "estado": "ocupada",
      "tipo": "doble",
      "precio_noche": "100.00",
      "capacidad": "2",
      "porcentaje_ocupacion": 67.74
    }
  ]
}
```

## Notas importantes

1. El campo `porcentaje_ocupacion` es calculado dinámicamente, NO se puede usar en filtros
2. Si no se especifican `fecha_inicio_ocupacion` y `fecha_fin_ocupacion`, se calculará para los últimos 30 días
3. El porcentaje considera solo reservas en estado `confirmada` o `realizada`
4. El resultado está limitado a 100% máximo, incluso si hay solapamientos de reservas

