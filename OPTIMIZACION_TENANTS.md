# 🚀 Guía de Optimización: Creación de Tenants

## Problema Actual

La creación de tenants tarda **5-6 minutos** porque Django ejecuta **80+ migraciones** cada vez que se crea un nuevo tenant.

## ✅ Optimizaciones Implementadas

### 1. **Email Asíncrono** (Implementado)

- ✅ El envío de email ahora se ejecuta en un thread separado
- ✅ La respuesta HTTP se devuelve inmediatamente sin esperar el email
- ✅ Reduce ~2-5 segundos del tiempo de respuesta

### 2. **Logging Mejorado** (Implementado)

- ✅ Logs más descriptivos con emojis para seguimiento
- ✅ Identificación clara de cada paso del proceso

## 🔧 Optimizaciones Adicionales Recomendadas

### Opción A: Consolidar Migraciones (RECOMENDADO) ⚡

**Tiempo estimado de reducción: De 5-6 min → 1-2 min**

Las migraciones se pueden consolidar usando `squashmigrations`:

```bash
# Para cada app, ejecutar:
python manage.py squashmigrations usuarios 0001 0005
python manage.py squashmigrations hoteles 0001
python manage.py squashmigrations habitaciones 0001 0002
python manage.py squashmigrations servicios 0001 0002
# ... etc para cada app
```

**Ventajas:**

- ✅ Reduce drásticamente el número de migraciones
- ✅ Mantiene la funcionalidad exacta
- ✅ No requiere cambios en producción

**Desventajas:**

- ⚠️ Requiere ejecutar comando para cada app
- ⚠️ Necesita testing después de consolidar

### Opción B: Creación de Schema Pre-poblado 🎯

**Tiempo estimado de reducción: De 5-6 min → 10-30 seg**

Crear un template de schema y clonarlo en lugar de ejecutar migraciones:

1. Crear un schema template una sola vez
2. Al crear nuevo tenant, clonar el schema template
3. Solo actualizar datos específicos del tenant

**Implementación:**

```python
# En core/services.py
def create_tenant_fast(validated: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Crear schema vacío
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

    # 2. Clonar desde template
    with connection.cursor() as cursor:
        cursor.execute(f"""
            CREATE SCHEMA {schema_name}
            AUTHORIZATION postgres;

            -- Copiar todas las tablas desde template
            CREATE TABLE {schema_name}.auth_user
            (LIKE template_tenant.auth_user INCLUDING ALL);

            -- ... copiar resto de tablas
        """)

    # 3. Crear tenant sin auto_create_schema
    tenant = Tenant(schema_name=schema_name, name=nombre_empresa)
    tenant.auto_create_schema = False
    tenant.save()
```

**Ventajas:**

- ✅ Velocidad extremadamente rápida
- ✅ No ejecuta migraciones
- ✅ Ideal para muchos tenants

**Desventajas:**

- ⚠️ Complejidad de implementación alta
- ⚠️ Requiere mantener template actualizado
- ⚠️ Difícil de depurar errores

### Opción C: Procesamiento en Background con Celery 🔄

**Tiempo de respuesta: Inmediato (proceso en background)**

Mover todo el proceso a una tarea asíncrona de Celery:

```python
# En core/tasks.py
from celery import shared_task

@shared_task
def create_tenant_async(validated_data):
    return TenantFormService.create_tenant_with_domain(validated_data)

# En core/views.py
def create(self, request, *args, **kwargs):
    serializer = TenantFormSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Encolar tarea
    task = create_tenant_async.delay(serializer.validated_data)

    return Response({
        "message": "Tenant en proceso de creación",
        "task_id": task.id,
        "status_url": f"/api/tasks/{task.id}/status/"
    }, status=202)
```

**Ventajas:**

- ✅ Respuesta inmediata al usuario
- ✅ No bloquea el servidor
- ✅ Reintentos automáticos si falla
- ✅ Monitoreo del progreso

**Desventajas:**

- ⚠️ Requiere configurar Celery + Redis/RabbitMQ
- ⚠️ Mayor complejidad de infraestructura
- ⚠️ Usuario debe esperar y verificar status

### Opción D: Optimizar Configuración de Django-Tenants ⚙️

**Tiempo estimado de reducción: De 5-6 min → 3-4 min**

Ajustar configuración en `settings.py`:

```python
# Deshabilitar validación en cada migración
TENANT_CREATION_FAKES_MIGRATIONS = True

# Ejecutar migraciones en paralelo (requiere PostgreSQL 9.6+)
DATABASES = {
    'default': {
        # ... config existente
        'OPTIONS': {
            'options': '-c search_path=public,tenant_schema'
        },
        'ATOMIC_REQUESTS': False,  # Mejor performance
    }
}
```

## 📊 Comparación de Opciones

| Opción                       | Tiempo    | Complejidad | Recomendado                      |
| ---------------------------- | --------- | ----------- | -------------------------------- |
| **A: Squash Migrations**     | 1-2 min   | Baja        | ✅ SÍ (corto plazo)              |
| **B: Schema Template**       | 10-30 seg | Alta        | ⚠️ Solo si tienes muchos tenants |
| **C: Celery Background**     | Inmediato | Media       | ✅ SÍ (largo plazo)              |
| **D: Config Optimization**   | 3-4 min   | Baja        | ✅ Complementario                |
| **Email Asíncrono** (actual) | 5-6 min   | Baja        | ✅ Ya implementado               |

## 🎯 Recomendación de Implementación

### Fase 1: Inmediata (Ya implementado)

- ✅ Email asíncrono

### Fase 2: Corto Plazo (Esta semana)

```bash
# 1. Consolidar migraciones de todas las apps
python manage.py squashmigrations usuarios 0001 0005
python manage.py squashmigrations hoteles 0001
# ... resto de apps

# 2. Hacer commit
git add .
git commit -m "perf: Consolidar migraciones para reducir tiempo de creación de tenants"
```

### Fase 3: Mediano Plazo (Próximo sprint)

- Implementar Celery para procesamiento background
- Agregar endpoint de status para verificar progreso
- Notificar al usuario por email cuando termine

### Fase 4: Largo Plazo (Opcional)

- Si tienes 100+ tenants: Implementar schema template
- Monitoreo y métricas de performance

## 🔍 Monitoreo

Para medir mejoras, agrega timing logs:

```python
import time

def create_tenant_with_domain(validated: Dict[str, Any]):
    start_time = time.time()

    # ... código existente ...

    elapsed = time.time() - start_time
    logger.info(f"⏱️ Tenant creado en {elapsed:.2f} segundos")
```

## 📝 Comandos Útiles

```bash
# Ver todas las migraciones
python manage.py showmigrations

# Consolidar migraciones de una app
python manage.py squashmigrations <app_name> <start_migration> <end_migration>

# Ejemplo:
python manage.py squashmigrations usuarios 0001 0005

# Ver tiempo de ejecución de cada migración
python manage.py migrate --verbosity 2

# Optimizar base de datos
python manage.py sqlflush  # Ver SQL de reset
python manage.py dbshell  # Acceder a PostgreSQL
```

## 🐛 Debugging

Si después de optimizar sigues teniendo problemas:

1. **Verificar logs:**

   ```bash
   tail -f logs/django.log
   ```

2. **Perfil de queries:**

   ```python
   from django.db import connection
   print(len(connection.queries))  # Número de queries
   ```

3. **Time profiling:**
   ```bash
   python -m cProfile manage.py migrate
   ```

## ✅ Checklist de Implementación

- [x] Email asíncrono implementado
- [ ] Squash migrations ejecutado
- [ ] Testing de migraciones consolidadas
- [ ] Deploy a producción
- [ ] Celery configurado (opcional)
- [ ] Monitoreo de tiempos implementado
