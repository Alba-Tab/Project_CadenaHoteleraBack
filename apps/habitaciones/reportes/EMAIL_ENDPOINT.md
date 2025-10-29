# Envío de Reportes por Email - Habitaciones

## Endpoint

```
POST /api/habitaciones/reportes/habitaciones_base/email
```

## Descripción

Este endpoint permite enviar reportes de habitaciones por email en formato PDF, Excel o Word. El reporte incluye automáticamente el **porcentaje de ocupación** de cada habitación.

## Parámetros de la Petición

```json
{
  "columns": ["id", "hotel__nombre", "numero", "estado", "tipo", "precio_noche", "capacidad", "porcentaje_ocupacion"],
  "filters": [
    {
      "field": "hotel__nombre",
      "op": "icontains",
      "value": "Grand"
    }
  ],
  "ordering": ["hotel__nombre", "numero"],
  "format": "pdf",  // "pdf", "xlsx" o "docx"
  "recipient_email": "usuario@ejemplo.com",
  "subject": "Reporte de Habitaciones - octubre de 2025",
  "message": "Adjunto el reporte solicitado de habitaciones.",
  "fecha_inicio_ocupacion": "2025-10-01",  // Opcional
  "fecha_fin_ocupacion": "2025-10-29"      // Opcional
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
| `fecha_inicio_ocupacion` | string | Fecha inicio para calcular % ocupación (formato: YYYY-MM-DD) |
| `fecha_fin_ocupacion` | string | Fecha fin para calcular % ocupación (formato: YYYY-MM-DD) |

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

### Ejemplo 1: Enviar reporte básico en PDF

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
    "format": "pdf",
    "recipient_email": "manager@hotel.com",
    "subject": "Reporte de Ocupación de Habitaciones"
  }'
```

### Ejemplo 2: Enviar reporte filtrado en Excel

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["hotel__nombre", "numero", "tipo", "estado", "precio_noche", "porcentaje_ocupacion"],
    "filters": [
      {
        "field": "estado",
        "op": "eq",
        "value": "disponible"
      },
      {
        "field": "hotel__nombre",
        "op": "icontains",
        "value": "Grand"
      }
    ],
    "ordering": ["porcentaje_ocupacion", "numero"],
    "format": "xlsx",
    "recipient_email": "direccion@hotel.com",
    "subject": "Habitaciones Disponibles - Grand Hotel",
    "message": "Adjunto el reporte de habitaciones disponibles con su porcentaje de ocupación histórico."
  }'
```

### Ejemplo 3: Enviar reporte con período personalizado

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["hotel__nombre", "numero", "tipo", "capacidad", "porcentaje_ocupacion"],
    "format": "docx",
    "recipient_email": "analisis@hotel.com",
    "subject": "Reporte de Ocupación - Octubre 2025",
    "message": "Reporte de ocupación del 1 al 31 de octubre de 2025.",
    "fecha_inicio_ocupacion": "2025-10-01",
    "fecha_fin_ocupacion": "2025-10-31"
  }'
```

### Ejemplo 4: Enviar reporte con múltiples filtros

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "hotel__nombre", "numero", "tipo", "estado", "precio_noche", "capacidad", "porcentaje_ocupacion"],
    "filters": [
      {
        "field": "tipo",
        "op": "in",
        "value": ["suite", "doble"]
      },
      {
        "field": "precio_noche",
        "op": "lte",
        "value": 200
      }
    ],
    "ordering": ["hotel__nombre", "porcentaje_ocupacion"],
    "format": "pdf",
    "recipient_email": "ventas@hotel.com",
    "subject": "Habitaciones Premium Disponibles",
    "message": "Listado de suites y habitaciones dobles con precio menor a $200.",
    "fecha_inicio_ocupacion": "2025-10-01",
    "fecha_fin_ocupacion": "2025-10-29"
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

- ✅ El **porcentaje de ocupación** se calcula e incluye automáticamente
- ✅ Si no especificas fechas, se usa el período de los últimos 30 días
- ✅ El email se envía de forma síncrona (la petición espera hasta que se envíe)
- ✅ El archivo adjunto se genera en el momento del envío
- ⚠️ Si hay muchos registros, la generación y envío puede tomar tiempo
- ⚠️ Verifica que tu servidor tenga correctamente configurado el SMTP

## Arquitectura

Este endpoint utiliza:
- **Servicio genérico**: `apps._reporting.email_service.enviar_reporte_por_email()`
- **Exportadores**: Los mismos que usa el endpoint de export (`export_pdf`, `export_xlsx`, `export_docx`)
- **Columna calculada**: El porcentaje de ocupación se añade antes de generar el archivo
- **Django Email**: Sistema nativo de Django para envío de emails

Este diseño permite reutilizar el código en otros módulos (reservas, pagos, etc.) simplemente creando vistas similares que usen el mismo servicio genérico.

