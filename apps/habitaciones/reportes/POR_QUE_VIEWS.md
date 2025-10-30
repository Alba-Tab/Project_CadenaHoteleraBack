# ¿Por qué es necesaria la views.py?

## Pregunta
Si la columna `porcentaje_ocupacion` siempre se va a incluir en el reporte, ¿es necesaria la `views.py`?

## Respuesta: SÍ, es NECESARIA

### Razón Principal
El campo `porcentaje_ocupacion` **NO EXISTE en la base de datos**. Es un valor calculado que se obtiene dinámicamente consultando las reservas asociadas a cada habitación.

## Explicación Técnica

### El Problema

El sistema base de reportes (`apps/_reporting/`) funciona así:

1. Define columnas basadas en campos del modelo Django
2. Usa `project_columns(qs, columns)` que internamente hace:
   ```python
   return list(qs.values(*columns))
   ```
3. `qs.values()` solo puede proyectar campos que existen en la tabla `habitaciones`

### Campos en la tabla `habitaciones`:
```
- id
- hotel_id
- numero
- capacidad
- descripcion
- precio_noche
- estado
- tamanio
- tipo
```

**⚠️ NO existe el campo `porcentaje_ocupacion`**

### Si intentamos incluir `porcentaje_ocupacion` sin la vista personalizada:

```python
# En el sistema base:
rows = project_columns(qs, ["id", "hotel__nombre", "numero", "porcentaje_ocupacion"])
# Internamente hace:
rows = list(qs.values("id", "hotel__nombre", "numero", "porcentaje_ocupacion"))
```

**Resultado**: ❌ ERROR - Django lanzará:
```
FieldError: Cannot resolve keyword 'porcentaje_ocupacion' into field
```

## La Solución: Views Personalizadas

### ¿Qué hace la `views.py`?

```python
# 1. Obtener solo las columnas que existen en BD
columns_bd = [c for c in columns if c != 'porcentaje_ocupacion']
rows = project_columns(qs, columns_bd)  # ✅ Solo campos reales

# 2. DESPUÉS, añadir la columna calculada
rows = agregar_porcentaje_ocupacion_a_rows(rows, fecha_inicio, fecha_fin)
# Esto consulta la tabla de reservas y calcula el %
```

### Flujo Completo

```
1. Cliente hace petición
   ↓
2. HabitacionesReportPreviewView (PERSONALIZADA)
   ↓
3. Proyecta columnas de BD: [id, hotel__nombre, numero, estado, ...]
   ↓
4. Por cada fila:
   - Consulta Reserva.objects.filter(habitacion_id=row['id'], ...)
   - Calcula días ocupados / días totales * 100
   - Añade row['porcentaje_ocupacion'] = resultado
   ↓
5. Devuelve filas enriquecidas con la columna calculada
```

## Alternativas Descartadas

### ❌ Opción 1: Añadir un campo en el modelo
```python
class Habitacion(models.Model):
    # ...
    porcentaje_ocupacion = models.DecimalField(...)  # ❌ NO
```
**Problema**: 
- El porcentaje cambia cada día
- Habría que recalcularlo constantemente
- No es eficiente
- No permite periodos personalizados

### ❌ Opción 2: Usar anotaciones de Django
```python
qs = qs.annotate(
    porcentaje_ocupacion=...  # ❌ Muy complejo con subconsultas
)
```
**Problema**:
- Requiere subconsultas complejas
- Difícil de mantener
- No permite parámetros de fecha flexibles

### ✅ Opción 3: Vista personalizada (LA IMPLEMENTADA)
**Ventajas**:
- Simple y mantenible
- Flexible (acepta parámetros de fecha)
- Reutilizable
- No afecta el modelo
- Se integra bien con el sistema de reportes

## Resumen

**La `views.py` es ABSOLUTAMENTE NECESARIA** porque:

1. ✅ `porcentaje_ocupacion` no existe en la BD
2. ✅ Se debe calcular consultando otra tabla (Reservas)
3. ✅ El cálculo es dinámico (depende del período)
4. ✅ El sistema base no soporta columnas calculadas
5. ✅ Necesitamos interceptar después de `project_columns()`

**Sin la `views.py`**: El sistema fallaría con un error de Django.

**Con la `views.py`**: Funciona perfectamente, calculando y añadiendo la columna antes de devolver la respuesta.

