# Envío de Reportes por Email - Reservas

## Endpoint

```
POST /api/reservas/reportes/reservas_base/email
```

## Descripción

Este endpoint permite enviar reportes de reservas por email en formato PDF, Excel o Word.

## Parámetros de la Petición

```json
{
  "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre", "habitacion__numero", "huesped__username"],
  "filters": [
    {
      "field": "estado",
      "op": "eq",
      "value": "confirmada"
    }
  ],
  "ordering": ["-fecha_entrada"],
  "format": "pdf",
  "recipient_email": "usuario@ejemplo.com",
  "subject": "Reporte de Reservas - octubre de 2025",
  "message": "Adjunto el reporte de reservas solicitado."
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

- `id` - ID de la reserva
- `estado` - Estado (confirmada, cancelada, pendiente, realizada)
- `fecha_entrada` - Fecha de entrada
- `fecha_salida` - Fecha de salida
- `hotel__nombre` - Nombre del hotel
- `habitacion__numero` - Número de habitación
- `huesped__username` - Nombre de usuario del huésped

## Filtros Disponibles

- `estado` - Por estado de la reserva
- `fecha_entrada` - Por fecha de entrada
- `fecha_salida` - Por fecha de salida
- `hotel__nombre` - Por nombre del hotel

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

### Ejemplo 1: Enviar todas las reservas confirmadas

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_entrada", "fecha_salida", "hotel__nombre", "habitacion__numero", "huesped__username"],
    "filters": [
      {
        "field": "estado",
        "op": "eq",
        "value": "confirmada"
      }
    ],
    "ordering": ["-fecha_entrada"],
    "format": "pdf",
    "recipient_email": "recepcion@hotel.com",
    "subject": "Reservas Confirmadas"
  }'
```

### Ejemplo 2: Enviar reservas por rango de fechas

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "hotel__nombre", "habitacion__numero"],
    "filters": [
      {
        "field": "fecha_entrada",
        "op": "between",
        "value": ["2025-10-01", "2025-10-31"]
      }
    ],
    "ordering": ["fecha_entrada"],
    "format": "xlsx",
    "recipient_email": "gerencia@hotel.com",
    "subject": "Reservas de Octubre 2025",
    "message": "Adjunto el reporte de todas las reservas del mes de octubre."
  }'
```

### Ejemplo 3: Enviar reservas de un hotel específico

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "estado", "fecha_entrada", "fecha_salida", "habitacion__numero", "huesped__username"],
    "filters": [
      {
        "field": "hotel__nombre",
        "op": "icontains",
        "value": "Grand"
      },
      {
        "field": "estado",
        "op": "in",
        "value": ["confirmada", "realizada"]
      }
    ],
    "ordering": ["-fecha_entrada"],
    "format": "docx",
    "recipient_email": "admin@grandhotel.com",
    "subject": "Historial de Reservas - Grand Hotel"
  }'
```

### Ejemplo 4: Enviar reservas pendientes

```bash
curl -X POST "http://localhost:8000/api/reservas/reportes/reservas_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "fecha_entrada", "fecha_salida", "hotel__nombre", "habitacion__numero", "huesped__username"],
    "filters": [
      {
        "field": "estado",
        "op": "eq",
        "value": "pendiente"
      }
    ],
    "ordering": ["fecha_entrada"],
    "format": "pdf",
    "recipient_email": "seguimiento@hotel.com",
    "subject": "Reservas Pendientes de Confirmación",
    "message": "Listado de reservas que requieren seguimiento y confirmación."
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
- ✅ Utiliza el mismo servicio genérico que habitaciones
- ⚠️ Si hay muchos registros, la generación y envío puede tomar tiempo
- ⚠️ Verifica que tu servidor tenga correctamente configurado el SMTP

## Casos de Uso Comunes

### 1. Reporte diario de check-ins
Enviar todas las reservas con entrada en el día actual:
```json
{
  "filters": [
    {"field": "fecha_entrada", "op": "eq", "value": "2025-10-29"},
    {"field": "estado", "op": "eq", "value": "confirmada"}
  ]
}
```

### 2. Reporte semanal de ocupación
Enviar reservas de la próxima semana:
```json
{
  "filters": [
    {"field": "fecha_entrada", "op": "between", "value": ["2025-11-01", "2025-11-07"]}
  ]
}
```

### 3. Seguimiento de cancelaciones
Enviar reservas canceladas del mes:
```json
{
  "filters": [
    {"field": "estado", "op": "eq", "value": "cancelada"},
    {"field": "fecha_entrada", "op": "between", "value": ["2025-10-01", "2025-10-31"]}
  ]
}
```

## Integración con el Sistema

Este endpoint utiliza:
- **Servicio genérico**: `apps._reporting.email_service.enviar_reporte_por_email()`
- **Exportadores**: Los mismos que usa el endpoint de export (`export_pdf`, `export_xlsx`, `export_docx`)
- **Filtros y ordenamiento**: Sistema estándar de reportes de `_reporting`
- **Django Email**: Sistema nativo de Django para envío de emails

