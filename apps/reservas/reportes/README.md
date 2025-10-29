# Reportes de Reservas

## Descripción

Este módulo permite generar reportes de reservas con capacidad de filtrado, exportación y envío por email.

## Columnas Disponibles

- **id**: ID de la reserva
- **estado**: Estado actual (confirmada, cancelada, pendiente, realizada)
- **fecha_entrada**: Fecha de entrada
- **fecha_salida**: Fecha de salida
- **hotel__nombre**: Nombre del hotel
- **habitacion__numero**: Número de habitación
- **huesped__username**: Nombre de usuario del huésped

## Filtros Disponibles

- **estado**: Filtrar por estado de la reserva
- **fecha_entrada**: Filtrar por fecha de entrada (soporta rangos)
- **fecha_salida**: Filtrar por fecha de salida (soporta rangos)
- **hotel__nombre**: Filtrar por nombre del hotel

## Endpoints

### 1. Listar reportes disponibles
```
GET /api/reservas/reportes/
```

### 2. Obtener esquema del reporte
```
GET /api/reservas/reportes/reservas_base/schema
```

### 3. Preview del reporte
```
POST /api/reservas/reportes/reservas_base/preview
```

**Body:**
```json
{
  "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre"],
  "filters": [
    {
      "field": "estado",
      "op": "eq",
      "value": "confirmada"
    }
  ],
  "limit": 50
}
```

### 4. Exportar reporte
```
POST /api/reservas/reportes/reservas_base/export
```

**Body:**
```json
{
  "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre", "habitacion__numero"],
  "format": "xlsx",
  "filters": [
    {
      "field": "fecha_entrada",
      "op": "between",
      "value": ["2025-10-01", "2025-10-31"]
    }
  ]
}
```

### 5. Enviar reporte por email ⭐ NUEVO
```
POST /api/reservas/reportes/reservas_base/email
```

**Body:**
```json
{
  "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre"],
  "format": "pdf",
  "recipient_email": "usuario@ejemplo.com",
  "subject": "Reporte de Reservas",
  "message": "Adjunto el reporte solicitado.",
  "filters": [
    {
      "field": "estado",
      "op": "eq",
      "value": "confirmada"
    }
  ]
}
```

**Ver documentación completa**: [EMAIL_ENDPOINT.md](./EMAIL_ENDPOINT.md)

## Operadores de Filtro

| Operador | Descripción | Ejemplo |
|----------|-------------|---------|
| `eq` | Igual a | `{"field": "estado", "op": "eq", "value": "confirmada"}` |
| `ne` | No igual a | `{"field": "estado", "op": "ne", "value": "cancelada"}` |
| `in` | En lista | `{"field": "estado", "op": "in", "value": ["confirmada", "realizada"]}` |
| `icontains` | Contiene (case-insensitive) | `{"field": "hotel__nombre", "op": "icontains", "value": "Grand"}` |
| `gte` | Mayor o igual | `{"field": "fecha_entrada", "op": "gte", "value": "2025-10-01"}` |
| `lte` | Menor o igual | `{"field": "fecha_salida", "op": "lte", "value": "2025-10-31"}` |
| `between` | Entre dos valores | `{"field": "fecha_entrada", "op": "between", "value": ["2025-10-01", "2025-10-31"]}` |

## Ejemplos de Uso

### Ejemplo 1: Reservas confirmadas del día

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "habitacion__numero", "huesped__username"],
    "filters": [
      {
        "field": "fecha_entrada",
        "op": "eq",
        "value": "2025-10-29"
      },
      {
        "field": "estado",
        "op": "eq",
        "value": "confirmada"
      }
    ],
    "limit": 100
  }'
```

### Ejemplo 2: Exportar reservas del mes a Excel

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/export" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre", "habitacion__numero", "huesped__username"],
    "format": "xlsx",
    "filters": [
      {
        "field": "fecha_entrada",
        "op": "between",
        "value": ["2025-10-01", "2025-10-31"]
      }
    ],
    "ordering": ["fecha_entrada"]
  }' \
  --output reservas_octubre.xlsx
```

### Ejemplo 3: Enviar reporte por email

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre"],
    "format": "pdf",
    "recipient_email": "gerencia@hotel.com",
    "subject": "Reporte de Reservas - Octubre 2025",
    "filters": [
      {
        "field": "fecha_entrada",
        "op": "between",
        "value": ["2025-10-01", "2025-10-31"]
      }
    ]
  }'
```

## Casos de Uso Comunes

### 1. Check-ins del día
```json
{
  "filters": [
    {"field": "fecha_entrada", "op": "eq", "value": "2025-10-29"},
    {"field": "estado", "op": "in", "value": ["confirmada", "realizada"]}
  ]
}
```

### 2. Check-outs pendientes
```json
{
  "filters": [
    {"field": "fecha_salida", "op": "eq", "value": "2025-10-29"},
    {"field": "estado", "op": "eq", "value": "confirmada"}
  ]
}
```

### 3. Reservas canceladas
```json
{
  "filters": [
    {"field": "estado", "op": "eq", "value": "cancelada"},
    {"field": "fecha_entrada", "op": "gte", "value": "2025-10-01"}
  ]
}
```

### 4. Reservas de un hotel específico
```json
{
  "filters": [
    {"field": "hotel__nombre", "op": "icontains", "value": "Grand"}
  ]
}
```

## Notas

- Los reportes se generan en tiempo real desde la base de datos
- El filtrado y ordenamiento se realizan a nivel de base de datos para mejor rendimiento
- Los archivos exportados se generan en memoria y no se guardan en el servidor
- El envío de emails es síncrono (la petición espera hasta que se envíe)

