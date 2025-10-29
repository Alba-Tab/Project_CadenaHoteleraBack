# Reportes de Pagos

## Descripción

Este módulo permite generar reportes de pagos con capacidad de filtrado, exportación y envío por email.

## Columnas Disponibles

- **id**: ID del pago
- **fecha_pago**: Fecha en que se realizó el pago
- **monto**: Monto del pago
- **estado**: Estado actual (completado, pendiente, cancelado, fallido)
- **metodo**: Método de pago (tarjeta, efectivo, transferencia, etc.)
- **folio_estancia__huesped__username**: Usuario del huésped
- **folio_estancia__reserva__hotel__nombre**: Nombre del hotel

## Filtros Disponibles

- **fecha_pago**: Filtrar por fecha de pago (soporta rangos)
- **estado**: Filtrar por estado del pago
- **metodo**: Filtrar por método de pago
- **folio_estancia__reserva__hotel__nombre**: Filtrar por hotel

## Endpoints

### 1. Listar reportes disponibles
```
GET /api/pagos/reportes/
```

### 2. Obtener esquema del reporte
```
GET /api/pagos/reportes/pagos_base/schema
```

### 3. Preview del reporte
```
POST /api/pagos/reportes/pagos_base/preview
```

**Body:**
```json
{
  "columns": ["id", "fecha_pago", "monto", "estado", "metodo"],
  "filters": [
    {
      "field": "estado",
      "op": "eq",
      "value": "completado"
    }
  ],
  "limit": 50
}
```

### 4. Exportar reporte
```
POST /api/pagos/reportes/pagos_base/export
```

**Body:**
```json
{
  "columns": ["id", "fecha_pago", "monto", "estado", "metodo", "folio_estancia__huesped__username"],
  "format": "xlsx",
  "filters": [
    {
      "field": "fecha_pago",
      "op": "between",
      "value": ["2025-10-01", "2025-10-31"]
    }
  ]
}
```

### 5. Enviar reporte por email ⭐ NUEVO
```
POST /api/pagos/reportes/pagos_base/email
```

**Body:**
```json
{
  "columns": ["id", "fecha_pago", "monto", "estado", "metodo"],
  "format": "pdf",
  "recipient_email": "usuario@ejemplo.com",
  "subject": "Reporte de Pagos",
  "message": "Adjunto el reporte solicitado.",
  "filters": [
    {
      "field": "estado",
      "op": "eq",
      "value": "completado"
    }
  ]
}
```

**Ver documentación completa**: [EMAIL_ENDPOINT.md](./EMAIL_ENDPOINT.md)

## Operadores de Filtro

| Operador | Descripción | Ejemplo |
|----------|-------------|---------|
| `eq` | Igual a | `{"field": "estado", "op": "eq", "value": "completado"}` |
| `ne` | No igual a | `{"field": "estado", "op": "ne", "value": "cancelado"}` |
| `in` | En lista | `{"field": "metodo", "op": "in", "value": ["tarjeta", "efectivo"]}` |
| `icontains` | Contiene (case-insensitive) | `{"field": "metodo", "op": "icontains", "value": "tarjeta"}` |
| `gte` | Mayor o igual | `{"field": "monto", "op": "gte", "value": 100}` |
| `lte` | Menor o igual | `{"field": "monto", "op": "lte", "value": 1000}` |
| `between` | Entre dos valores | `{"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]}` |

## Ejemplos de Uso

### Ejemplo 1: Pagos del día

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/preview" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "monto", "metodo", "folio_estancia__huesped__username"],
    "filters": [
      {
        "field": "fecha_pago",
        "op": "eq",
        "value": "2025-10-29"
      },
      {
        "field": "estado",
        "op": "eq",
        "value": "completado"
      }
    ],
    "limit": 100
  }'
```

### Ejemplo 2: Exportar ingresos mensuales a Excel

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/export" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "metodo", "estado", "folio_estancia__reserva__hotel__nombre"],
    "format": "xlsx",
    "filters": [
      {
        "field": "fecha_pago",
        "op": "between",
        "value": ["2025-10-01", "2025-10-31"]
      },
      {
        "field": "estado",
        "op": "eq",
        "value": "completado"
      }
    ],
    "ordering": ["fecha_pago"]
  }' \
  --output pagos_octubre.xlsx
```

### Ejemplo 3: Enviar reporte por email

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "metodo", "estado"],
    "format": "pdf",
    "recipient_email": "finanzas@hotel.com",
    "subject": "Reporte de Ingresos - Octubre 2025",
    "filters": [
      {
        "field": "fecha_pago",
        "op": "between",
        "value": ["2025-10-01", "2025-10-31"]
      },
      {
        "field": "estado",
        "op": "eq",
        "value": "completado"
      }
    ]
  }'
```

## Casos de Uso Comunes

### 1. Ingresos diarios
```json
{
  "filters": [
    {"field": "fecha_pago", "op": "eq", "value": "2025-10-29"},
    {"field": "estado", "op": "eq", "value": "completado"}
  ]
}
```

### 2. Pagos pendientes
```json
{
  "filters": [
    {"field": "estado", "op": "eq", "value": "pendiente"}
  ]
}
```

### 3. Análisis por método de pago
```json
{
  "filters": [
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]}
  ],
  "ordering": ["metodo", "-monto"]
}
```

### 4. Pagos de un hotel específico
```json
{
  "filters": [
    {"field": "folio_estancia__reserva__hotel__nombre", "op": "icontains", "value": "Grand"}
  ]
}
```

### 5. Pagos por rango de monto
```json
{
  "filters": [
    {"field": "monto", "op": "between", "value": [100, 1000]},
    {"field": "estado", "op": "eq", "value": "completado"}
  ]
}
```

### 6. Conciliación bancaria (tarjeta y transferencia)
```json
{
  "filters": [
    {"field": "metodo", "op": "in", "value": ["tarjeta", "transferencia"]},
    {"field": "estado", "op": "eq", "value": "completado"},
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]}
  ]
}
```

## Métricas Comunes

### Total de ingresos del mes
```json
{
  "columns": ["monto"],
  "filters": [
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]},
    {"field": "estado", "op": "eq", "value": "completado"}
  ]
}
```
*Nota: Suma los montos manualmente en el frontend o usa herramientas de análisis con el Excel exportado*

### Pagos por método
```json
{
  "columns": ["metodo", "monto"],
  "filters": [
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]},
    {"field": "estado", "op": "eq", "value": "completado"}
  ],
  "ordering": ["metodo"]
}
```

### Tasa de éxito de pagos
```json
{
  "columns": ["estado", "id"],
  "filters": [
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]}
  ],
  "ordering": ["estado"]
}
```

## Notas

- Los reportes se generan en tiempo real desde la base de datos
- El filtrado y ordenamiento se realizan a nivel de base de datos para mejor rendimiento
- Los archivos exportados se generan en memoria y no se guardan en el servidor
- El envío de emails es síncrono (la petición espera hasta que se envíe)
- Soporte para configuración de email por tenant (multitenant)

## Estados de Pago Comunes

- **completado**: Pago procesado exitosamente
- **pendiente**: Pago en proceso de confirmación
- **cancelado**: Pago cancelado por el usuario o sistema
- **fallido**: Error al procesar el pago
- **reembolsado**: Pago devuelto al cliente

## Métodos de Pago Comunes

- **tarjeta**: Tarjeta de crédito/débito
- **efectivo**: Pago en efectivo
- **transferencia**: Transferencia bancaria
- **paypal**: Pago vía PayPal
- **wallet**: Billetera digital

