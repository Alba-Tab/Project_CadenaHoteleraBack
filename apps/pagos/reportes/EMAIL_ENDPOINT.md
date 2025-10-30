# Envío de Reportes por Email - Pagos

## Endpoint

```
POST /api/pagos/reportes/pagos_base/email
```

## Descripción

Este endpoint permite enviar reportes de pagos por email en formato PDF, Excel o Word.

## Parámetros de la Petición

```json
{
  "columns": ["id", "fecha_pago", "monto", "estado", "metodo", "folio_estancia__huesped__username", "folio_estancia__reserva__hotel__nombre"],
  "filters": [
    {
      "field": "estado",
      "op": "eq",
      "value": "completado"
    }
  ],
  "ordering": ["-fecha_pago"],
  "format": "pdf",
  "recipient_email": "usuario@ejemplo.com",
  "subject": "Reporte de Pagos - octubre de 2025",
  "message": "Adjunto el reporte de pagos solicitado."
}
```

### Campos Requeridos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `columns` | Array[string] | Columnas a incluir en el reporte |
| `format` | string | Formato del archivo: `"pdf"`, `"xlsx"` o `"docx"` |
| `recipient_email` | string | Email del destinatario |
| `subject` | string | Asunto del email |

### Campos Opcionales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `message` | string | Mensaje del cuerpo del email |
| `filters` | Array[object] | Filtros a aplicar al reporte |
| `ordering` | Array[string] | Orden de las filas |

## Columnas Disponibles

- `id` - ID del pago
- `fecha_pago` - Fecha del pago
- `monto` - Monto del pago
- `estado` - Estado (completado, pendiente, cancelado, etc.)
- `metodo` - Método de pago (tarjeta, efectivo, transferencia, etc.)
- `folio_estancia__huesped__username` - Usuario del huésped
- `folio_estancia__reserva__hotel__nombre` - Nombre del hotel

## Filtros Disponibles

- `fecha_pago` - Por fecha de pago
- `estado` - Por estado del pago
- `metodo` - Por método de pago
- `folio_estancia__reserva__hotel__nombre` - Por nombre del hotel

## Respuesta

### Éxito (200)
```json
{
  "detail": "Reporte enviado exitosamente a usuario@ejemplo.com"
}
```

### Error de validación (400)
```json
{
  "columns": ["Este campo es requerido."],
  "recipient_email": ["Ingrese una dirección de correo electrónico válida."]
}
```

### Error de envío (500)
```json
{
  "detail": "Error al enviar el email: [descripción del error]"
}
```

## Ejemplos de Uso

### Ejemplo 1: Enviar pagos completados del día

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "metodo", "folio_estancia__huesped__username"],
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
    "ordering": ["-fecha_pago"],
    "format": "pdf",
    "recipient_email": "contabilidad@hotel.com",
    "subject": "Pagos del Día"
  }'
```

### Ejemplo 2: Enviar reporte mensual de ingresos

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "estado", "metodo", "folio_estancia__reserva__hotel__nombre"],
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
    "ordering": ["fecha_pago"],
    "format": "xlsx",
    "recipient_email": "finanzas@hotel.com",
    "subject": "Ingresos de Octubre 2025",
    "message": "Adjunto el reporte de todos los pagos completados del mes de octubre."
  }'
```

### Ejemplo 3: Enviar pagos por método de pago

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "metodo", "estado"],
    "filters": [
      {
        "field": "metodo",
        "op": "in",
        "value": ["tarjeta", "transferencia"]
      },
      {
        "field": "fecha_pago",
        "op": "gte",
        "value": "2025-10-01"
      }
    ],
    "ordering": ["metodo", "-monto"],
    "format": "xlsx",
    "recipient_email": "auditoria@hotel.com",
    "subject": "Pagos Electrónicos - Octubre"
  }'
```

### Ejemplo 4: Enviar pagos pendientes

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "estado", "folio_estancia__huesped__username", "folio_estancia__reserva__hotel__nombre"],
    "filters": [
      {
        "field": "estado",
        "op": "eq",
        "value": "pendiente"
      }
    ],
    "ordering": ["fecha_pago"],
    "format": "pdf",
    "recipient_email": "cobranzas@hotel.com",
    "subject": "Pagos Pendientes de Confirmación",
    "message": "Listado de pagos que requieren seguimiento."
  }'
```

### Ejemplo 5: Enviar pagos de un hotel específico

```bash
curl -X POST "http://localhost:8000/api/pagos/reportes/pagos_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_pago", "monto", "metodo", "estado", "folio_estancia__huesped__username"],
    "filters": [
      {
        "field": "folio_estancia__reserva__hotel__nombre",
        "op": "icontains",
        "value": "Grand"
      },
      {
        "field": "fecha_pago",
        "op": "between",
        "value": ["2025-10-01", "2025-10-31"]
      }
    ],
    "ordering": ["-monto"],
    "format": "docx",
    "recipient_email": "admin@grandhotel.com",
    "subject": "Reporte de Ingresos - Grand Hotel"
  }'
```

## Configuración del Email

Para que el envío de emails funcione correctamente, asegúrate de configurar las siguientes variables en tu archivo `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=tu_email@gmail.com
```

### Nota para Gmail

Si usas Gmail, necesitas:
1. Habilitar la verificación en dos pasos en tu cuenta de Google
2. Generar una "Contraseña de aplicación" en https://myaccount.google.com/apppasswords
3. Usar esa contraseña en `EMAIL_HOST_PASSWORD`

## Notas Importantes

- ✅ El email se envía de forma síncrona (la petición espera hasta que se envíe)
- ✅ El archivo adjunto se genera en el momento del envío
- ✅ Utiliza el mismo servicio genérico que habitaciones y reservas
- ✅ Soporte para configuración de email por tenant (multitenant)
- ⚠️ Si hay muchos registros, la generación y envío puede tomar tiempo
- ⚠️ Verifica que tu servidor tenga correctamente configurado el SMTP

## Casos de Uso Comunes

### 1. Reporte diario de ingresos
Enviar todos los pagos completados del día:
```json
{
  "filters": [
    {"field": "fecha_pago", "op": "eq", "value": "2025-10-29"},
    {"field": "estado", "op": "eq", "value": "completado"}
  ]
}
```

### 2. Reporte semanal de ventas
Enviar pagos de la semana:
```json
{
  "filters": [
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-23", "2025-10-29"]},
    {"field": "estado", "op": "eq", "value": "completado"}
  ]
}
```

### 3. Seguimiento de pagos pendientes
Enviar pagos pendientes o fallidos:
```json
{
  "filters": [
    {"field": "estado", "op": "in", "value": ["pendiente", "fallido"]}
  ]
}
```

### 4. Análisis por método de pago
Enviar reporte agrupado por método:
```json
{
  "filters": [
    {"field": "fecha_pago", "op": "between", "value": ["2025-10-01", "2025-10-31"]}
  ],
  "ordering": ["metodo", "-monto"]
}
```

### 5. Conciliación bancaria
Enviar solo pagos con tarjeta o transferencia:
```json
{
  "filters": [
    {"field": "metodo", "op": "in", "value": ["tarjeta", "transferencia"]},
    {"field": "estado", "op": "eq", "value": "completado"}
  ]
}
```

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

## Integración con el Sistema

Este endpoint utiliza:
- **Servicio genérico**: `apps._reporting.email_service.enviar_reporte_por_email()`
- **Exportadores**: Los mismos que usa el endpoint de export (`export_pdf`, `export_xlsx`, `export_docx`)
- **Filtros y ordenamiento**: Sistema estándar de reportes de `_reporting`
- **Django Email**: Sistema nativo de Django para envío de emails
- **Multitenant**: Soporta configuración de email por tenant

## Soporte Multitenant

Si tu sistema usa múltiples tenants (empresas/hoteles):
- Cada tenant puede configurar su propio servidor SMTP
- Los reportes se envían desde el email del tenant
- Fallback automático al email del sistema si el tenant no tiene configuración
- Ver documentación completa en: `apps/_reporting/MULTITENANT_EMAIL.md`

