# Resumen: Implementación de Envío de Reportes por Email

## ✅ Implementación Completada

Se ha implementado exitosamente el sistema de envío de reportes por email, con un **servicio genérico reutilizable** en `_reporting` que puede usarse en todos los módulos (habitaciones, reservas, pagos, etc.).

## 📁 Archivos Creados/Modificados

### En `apps/_reporting/` (Genérico - Reutilizable)

#### 1. **`email_service.py`** ✨ NUEVO
- **Función**: `enviar_reporte_por_email(rows, report_name, format, recipient_email, subject, message)`
- **Propósito**: Servicio genérico para enviar reportes por email
- **Reutilizable**: ✅ Puede usarse en habitaciones, reservas, pagos, etc.
- **Funcionalidad**:
  - Genera el archivo en el formato solicitado (PDF/Excel/Word)
  - Crea el email con asunto y mensaje personalizados
  - Adjunta el archivo generado
  - Envía el email usando Django Email
  - Retorna resultado con éxito/error

#### 2. **`serializers.py`** 📝 MODIFICADO
- **Añadido**: `EmailRequestSerializer`
- **Hereda de**: `ExportRequestSerializer`
- **Campos adicionales**:
  - `recipient_email`: Email del destinatario (requerido)
  - `subject`: Asunto del email (requerido)
  - `message`: Cuerpo del email (opcional)

### En `apps/habitaciones/reportes/` (Específico)

#### 3. **`views.py`** 📝 MODIFICADO
- **Añadido**: `HabitacionesReportEmailView`
- **Hereda de**: `views.APIView`
- **Funcionalidad**:
  1. Valida la petición con `EmailRequestSerializer`
  2. Obtiene datos del modelo `Habitacion`
  3. Aplica filtros y ordenamiento
  4. **Añade columna calculada** `porcentaje_ocupacion`
  5. Llama al servicio genérico `enviar_reporte_por_email()`
  6. Retorna respuesta de éxito o error

#### 4. **`urls.py`** 📝 MODIFICADO
- **Añadido**: Endpoint `<slug:slug>/email`
- **URL completa**: `POST /api/habitaciones/reportes/habitaciones_base/email`

#### 5. **`EMAIL_ENDPOINT.md`** ✨ NUEVO
- Documentación completa del endpoint de email
- Ejemplos de uso con cURL
- Configuración requerida
- Casos de uso comunes

#### 6. **`README.md`** 📝 MODIFICADO
- Añadida sección del endpoint de email
- Link a la documentación detallada

## 🎯 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/habitaciones/reportes/` | Listar reportes |
| GET | `/api/habitaciones/reportes/{slug}/schema` | Esquema del reporte |
| POST | `/api/habitaciones/reportes/{slug}/preview` | Preview (con limit) |
| POST | `/api/habitaciones/reportes/{slug}/export` | Exportar archivo |
| POST | `/api/habitaciones/reportes/{slug}/email` | **Enviar por email** ⭐ |

## 🔄 Flujo de Ejecución

```
1. Cliente hace petición POST
   ↓
2. HabitacionesReportEmailView
   - Valida datos (EmailRequestSerializer)
   - Extrae parámetros de fecha
   ↓
3. Obtiene datos de BD
   - Aplica filtros
   - Ordena resultados
   ↓
4. Añade columna calculada
   - agregar_porcentaje_ocupacion_a_rows()
   ↓
5. Llama al servicio genérico
   - enviar_reporte_por_email()
     • Genera archivo (PDF/XLSX/DOCX)
     • Crea email
     • Adjunta archivo
     • Envía
   ↓
6. Retorna respuesta
   - 200: "Reporte enviado exitosamente..."
   - 500: "Error al enviar el email..."
```

## 📧 Petición de Ejemplo

```json
POST /api/habitaciones/reportes/habitaciones_base/email
{
  "columns": [
    "id",
    "hotel__nombre",
    "numero",
    "estado",
    "tipo",
    "precio_noche",
    "capacidad",
    "porcentaje_ocupacion"
  ],
  "filters": [
    {
      "field": "hotel__nombre",
      "op": "icontains",
      "value": "Grand"
    }
  ],
  "ordering": ["hotel__nombre", "numero"],
  "format": "pdf",
  "recipient_email": "fotosvideosyotrascosas@gmail.com",
  "subject": "Reporte de Habitaciones - octubre de 2025",
  "message": "Adjunto el reporte solicitado de habitaciones.",
  "fecha_inicio_ocupacion": "2025-10-01",
  "fecha_fin_ocupacion": "2025-10-29"
}
```

## 🔧 Configuración Requerida

En el archivo `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=tu_email@gmail.com
```

**⚠️ Importante para Gmail**:
1. Habilitar verificación en dos pasos
2. Generar "Contraseña de aplicación" en https://myaccount.google.com/apppasswords
3. Usar esa contraseña en `EMAIL_HOST_PASSWORD`

## ♻️ Reutilización en Otros Módulos

Para implementar el mismo endpoint en **reservas** o **pagos**:

### 1. En `apps/reservas/reportes/views.py`:

```python
from apps._reporting.serializers import EmailRequestSerializer
from apps._reporting.email_service import enviar_reporte_por_email

class ReservasReportEmailView(views.APIView):
    permission_classes = [IsReportViewer]
    
    def post(self, request, slug: str):
        r = _get_report(slug)
        ser = EmailRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        
        # Obtener datos
        model = import_model(r.model_path)
        qs = model.objects.all()
        qs = apply_filters(qs, r, data.get("filters", []))
        ordering = data.get("ordering") or r.default_ordering
        qs = qs.order_by(*ordering)
        rows = project_columns(qs, data["columns"])
        
        # Enviar por email (servicio genérico)
        result = enviar_reporte_por_email(
            rows=rows,
            report_name=r.name,
            format=data["format"],
            recipient_email=data["recipient_email"],
            subject=data["subject"],
            message=data.get("message")
        )
        
        if result["success"]:
            return Response({"detail": result["message"]}, status=200)
        else:
            return Response({"detail": result["message"]}, status=500)
```

### 2. En `apps/reservas/reportes/urls.py`:

```python
from .views import ReservasReportEmailView

urlpatterns = [
    # ...otras urls...
    path('<slug:slug>/email', ReservasReportEmailView.as_view(), name='reservas-report-email'),
]
```

**¡Y listo!** El endpoint de email estará disponible en:
```
POST /api/reservas/reportes/reservas_base/email
```

## ✨ Ventajas del Diseño

1. ✅ **Código reutilizable**: El 90% está en `_reporting`
2. ✅ **Consistente**: Misma interfaz en todos los módulos
3. ✅ **Fácil de extender**: Solo creas una vista personalizada si necesitas columnas calculadas
4. ✅ **Mantenible**: Cambios en el servicio se reflejan en todos lados
5. ✅ **Validación automática**: El serializer valida todos los campos
6. ✅ **Flexible**: Soporta filtros, ordenamiento y formatos múltiples

## 🧪 Testing

Para probar el endpoint:

```bash
curl -X POST "http://localhost:8000/api/habitaciones/reportes/habitaciones_base/email" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
    "format": "pdf",
    "recipient_email": "test@ejemplo.com",
    "subject": "Test de Reporte"
  }'
```

## 📌 Notas Finales

- El envío es **síncrono** (la petición espera hasta que se envíe)
- Si hay muchos datos, puede tardar (considerar tareas asíncronas con Celery en el futuro)
- El archivo se genera en memoria y no se guarda en disco
- El servicio maneja errores y retorna mensajes descriptivos
- Compatible con el sistema de reportes existente

