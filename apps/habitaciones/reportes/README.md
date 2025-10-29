# Reportes de Habitaciones con Porcentaje de Ocupación

## Descripción

Este módulo de reportes permite generar listados de habitaciones con la capacidad de incluir el **porcentaje de ocupación** calculado de forma dinámica.

## Características

### Columnas Disponibles

- **id**: ID de la habitación
- **hotel__nombre**: Nombre del hotel
- **numero**: Número de habitación
- **estado**: Estado actual (disponible, ocupada, mantenimiento, reservada)
- **tipo**: Tipo de habitación (individual, doble, suite)
- **precio_noche**: Precio por noche
- **capacidad**: Capacidad de la habitación
- **porcentaje_ocupacion**: Porcentaje de ocupación (columna calculada)

### Columna Calculada: Porcentaje de Ocupación

**⚠️ IMPORTANTE**: La columna `porcentaje_ocupacion` **SIEMPRE se incluye automáticamente** en todos los reportes de habitaciones.

El porcentaje de ocupación se calcula basándose en:
- Reservas **confirmadas** o **realizadas**
- Por defecto: últimos **30 días**
- Se puede personalizar el período mediante parámetros

#### Parámetros Opcionales

Al hacer peticiones POST a los endpoints de preview o export, se pueden incluir:

```json
{
  "columns": ["id", "hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
  "fecha_inicio_ocupacion": "2025-01-01",  // Opcional, formato: YYYY-MM-DD
  "fecha_fin_ocupacion": "2025-01-31",     // Opcional, formato: YYYY-MM-DD
  "filters": [...],
  "ordering": ["hotel__nombre", "numero"],
  "limit": 100  // Solo para preview
}
```

**Nota**: Las fechas deben enviarse en formato ISO 8601: `YYYY-MM-DD` (ejemplo: `"2025-10-29"`)

## Endpoints

### 1. Listar reportes disponibles
```
GET /api/habitaciones/reportes/
```

### 2. Obtener esquema del reporte
```
GET /api/habitaciones/reportes/habitaciones_base/schema
```

### 3. Preview del reporte
```
POST /api/habitaciones/reportes/habitaciones_base/preview
```

**Body:**
```json
{
  "columns": ["id", "hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
  "fecha_inicio_ocupacion": "2025-01-01",
  "fecha_fin_ocupacion": "2025-01-31",
  "limit": 50
}
```

### 4. Exportar reporte
```
POST /api/habitaciones/reportes/habitaciones_base/export
```

**Body:**
```json
{
  "columns": ["id", "hotel__nombre", "numero", "tipo", "estado", "porcentaje_ocupacion"],
  "format": "xlsx",  // "xlsx", "docx", o "pdf"
  "fecha_inicio_ocupacion": "2025-01-01",
  "fecha_fin_ocupacion": "2025-01-31"
}
```

### 5. Enviar reporte por email ⭐ NUEVO
```
POST /api/habitaciones/reportes/habitaciones_base/email
```

**Body:**
```json
{
  "columns": ["hotel__nombre", "numero", "estado", "porcentaje_ocupacion"],
  "format": "pdf",
  "recipient_email": "usuario@ejemplo.com",
  "subject": "Reporte de Habitaciones",
  "message": "Adjunto el reporte solicitado.",
  "fecha_inicio_ocupacion": "2025-01-01",
  "fecha_fin_ocupacion": "2025-01-31"
}
```

**Ver documentación completa**: [EMAIL_ENDPOINT.md](./EMAIL_ENDPOINT.md)

## Implementación Técnica

### Archivos Creados/Modificados

1. **servicios.py**: Contiene la lógica de cálculo del porcentaje de ocupación
   - `calcular_porcentaje_ocupacion()`: Calcula % para una habitación
   - `agregar_porcentaje_ocupacion_a_rows()`: Añade la columna a las filas del reporte

2. **views.py**: Vistas personalizadas que extienden el sistema de reportes base
   - `HabitacionesReportPreviewView`: Preview con soporte para % ocupación
   - `HabitacionesReportExportView`: Export con soporte para % ocupación

3. **registry.py**: Definición del reporte con la columna calculada
   - Incluye `porcentaje_ocupacion` como columna disponible

4. **urls.py**: Configuración de URLs que usan las vistas personalizadas

## Cálculo del Porcentaje de Ocupación

### Algoritmo

1. Se obtienen todas las reservas en estado `CONFIRMADA` o `REALIZADA`
2. Se filtran las que tienen solapamiento con el período solicitado
3. Para cada reserva, se calculan los días ocupados dentro del período
4. Se suma el total de días ocupados
5. Se calcula: `(días_ocupados / días_totales) * 100`
6. Se limita al 100% en caso de solapamientos

### Ejemplo

Si una habitación tiene:
- Reserva del 1-5 de enero (5 días)
- Reserva del 10-15 de enero (6 días)
- Período: 1-31 de enero (31 días)

Días ocupados: 11
Porcentaje: (11/31) * 100 = 35.48%

## Notas
- Esta columna **SIEMPRE se incluye automáticamente**, no es opcional
- NO es filtrable (no se pueden aplicar filtros sobre ella)
- El porcentaje de ocupación es una **columna calculada**, no existe en la base de datos
- Si no se especifican fechas, se calculará para los últimos 30 días
- Las fechas deben enviarse en formato **ISO 8601**: `YYYY-MM-DD` (ejemplo: `"2025-10-29"`)
- El cálculo considera solo reservas confirmadas y realizadas (no canceladas ni pendientes)

