# 📋 Sistema de Suscripciones y Planes

## 🎯 ¿Qué hace este sistema?

Controla cuántos **hoteles** y **usuarios** puede crear cada tenant según su plan de suscripción.

## 🏗️ Arquitectura: Público vs Tenant

### Esquema PÚBLICO (shared_apps)
Los modelos `Plan`, `Suscripcion` y `UsoTenant` están en el **esquema público** porque:
- Son compartidos entre todos los tenants
- No se duplican en cada base de datos de tenant
- Se accede con `schema_context("public")`

### Esquema TENANT
Los modelos como `Hotel`, `User`, `Reserva` están en el **esquema del tenant** porque:
- Cada tenant tiene sus propios datos aislados
- Son específicos de cada hotel/empresa

## 📊 Modelos

### Plan (esquema público)
```python
nombre = "Básico", "Premium", etc.
max_usuarios = 10      # Límite de usuarios
max_hoteles = 5        # Límite de hoteles
precio = 99.99
tipo = "Mensual", "Anual"
activo = True/False
```

### Suscripcion (esquema público)
```python
tenant = FK a Tenant
plan = FK a Plan
estado = "activo", "vencido", "pausado", "cancelado", "prueba"
inicio_periodo = fecha
fin_periodo = fecha
```

### UsoTenant (esquema público)
```python
tenant = FK a Tenant
hoteles = 3            # Contador actual
usuarios = 8           # Contador actual
ultima_actualizacion = datetime
```

## 🔒 ¿Cómo funciona la validación?

1. **Middleware** carga `request.suscripcion` automáticamente
2. **Permisos** validan antes de crear recursos:
   - `EscrituraPermitida`: ¿Suscripción activa?
   - `DentroDeCuota`: ¿No excede límites?
3. **ViewSet** incrementa contador al crear, decrementa al eliminar

## 📡 Endpoints

### PÚBLICOS (sin tenant, sin autenticación)
Accesibles desde `public.localhost:8000` o IP directa:

```
GET  /api/planes/                    - Ver planes disponibles
GET  /api/planes/{id}/               - Detalle de un plan

POST /api/suscripciones/             - Crear suscripción (registro)
GET  /api/suscripciones/             - Listar suscripciones (admin)
GET  /api/suscripciones/{id}/        - Ver una suscripción
PUT  /api/suscripciones/{id}/        - Actualizar suscripción
```

### TENANT (requiere autenticación)
Accesibles desde `mihotel.localhost:8000`:

```
GET /api/mi-suscripcion/              - Ver MI suscripción
GET /api/mi-suscripcion/actual/       - Suscripción activa
GET /api/mi-suscripcion/estadisticas/ - Uso y límites
```

## 🛠️ Implementación en un ViewSet

```python
from rest_framework import viewsets
from core.permissions import EscrituraPermitida, DentroDeCuota
from apps.suscripciones.models import UsoTenant
from django_tenants.utils import schema_context
from django.db import transaction

class HotelViewSet(viewsets.ModelViewSet):
    permission_classes = [EscrituraPermitida, DentroDeCuota]
    creando_hoteles = True  # ← Indica que crea hoteles
    
    def initial(self, request, *args, **kwargs):
        # Contadores para validación
        request.contadores_tenant = {
            "hoteles": Hotel.objects.count(),
            "usuarios": User.objects.count()
        }
        return super().initial(request, *args, **kwargs)
    
    @transaction.atomic
    def perform_create(self, serializer):
        tenant = self.request.tenant
        
        # Incrementar contador en esquema público
        with schema_context("public"):
            uso, _ = UsoTenant.objects.select_for_update().get_or_create(tenant=tenant)
            uso.hoteles += 1
            uso.save()
        
        try:
            serializer.save()
        except Exception:
            # Revertir si falla
            with schema_context("public"):
                uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
                uso.hoteles = max(0, uso.hoteles - 1)
                uso.save()
            raise
    
    @transaction.atomic
    def perform_destroy(self, instance):
        tenant = self.request.tenant
        instance.delete()
        
        # Decrementar contador
        with schema_context("public"):
            uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
            uso.hoteles = max(0, uso.hoteles - 1)
            uso.save()
```

## 🔧 Configuración

### 1. Middleware (settings.py)
```python
MIDDLEWARE = [
    "django_tenants.middleware.TenantMainMiddleware",
    'apps.suscripciones.middleware.SuscripcionMiddleware',  # ← Después de TenantMainMiddleware
    ...
]
```

### 2. Apps compartidas (settings.py)
```python
SHARED_APPS = [
    'django_tenants',
    'core',
    ...
    'apps.suscripciones',  # ← En shared para que esté en público
]
```

### 3. URLs
```python
# config/urls_public.py - Para gestionar planes y suscripciones
path("api/", include("apps.suscripciones.urls_public")),

# config/urls_tenant.py - Para que cada tenant vea SU suscripción
path('api/', include('apps.suscripciones.urls')),
```

## 🚀 Pasos para implementar

1. **Aplica migraciones:**
```bash
python manage.py makemigrations suscripciones
python manage.py migrate suscripciones
```

2. **Crea planes desde el admin o shell:**
```python
from apps.suscripciones.models import Plan

Plan.objects.create(
    nombre="Básico",
    max_usuarios=5,
    max_hoteles=1,
    precio=29.99,
    tipo="Mensual",
    activo=True
)
```

3. **Crea suscripción para un tenant:**
```python
from apps.suscripciones.models import Suscripcion
from core.models import Tenant
from datetime import date, timedelta

tenant = Tenant.objects.get(schema_name='mihotel')
plan = Plan.objects.get(nombre='Básico')

Suscripcion.objects.create(
    tenant=tenant,
    plan=plan,
    estado='activo',
    inicio_periodo=date.today(),
    fin_periodo=date.today() + timedelta(days=30)
)
```

## 📊 Ejemplo de respuesta de estadísticas

```json
{
  "suscripcion": {
    "plan_nombre": "Premium",
    "estado": "activo",
    "dias_restantes": 25
  },
  "uso": {
    "hoteles": 3,
    "usuarios": 8,
    "porcentaje_hoteles": 60.0,
    "porcentaje_usuarios": 80.0
  },
  "limite_hoteles": 5,
  "limite_usuarios": 10,
  "puede_crear_hotel": true,
  "puede_crear_usuario": true
}
```

## ❓ Preguntas Frecuentes

### ¿Por qué uso `schema_context("public")`?
Porque los modelos de suscripciones están en `SHARED_APPS`, viven en el esquema público.

### ¿Cómo crear suscripciones desde el frontend?
Usa el endpoint público: `POST http://public.localhost:8000/api/suscripciones/`

### ¿Cómo ver mi suscripción desde el tenant?
Usa: `GET http://mihotel.localhost:8000/api/mi-suscripcion/actual/`

### ¿Necesito sincronizar contadores manualmente?
No, se actualizan automáticamente al crear/eliminar recursos.

## 📊 Modelos

### Plan

Representa un plan de suscripción con sus límites de recursos.

**Campos:**

- `nombre`: Nombre del plan (ej: "Básico", "Premium")
- `max_usuarios`: Número máximo de usuarios permitidos
- `max_hoteles`: Número máximo de hoteles permitidos
- `precio`: Precio del plan
- `tipo`: Tipo de plan (Mensual, Anual, Trimestral)
- `activo`: Indica si el plan está disponible

### Suscripcion

Representa la suscripción activa de un tenant a un plan.

**Campos:**

- `tenant`: Referencia al tenant (inquilino)
- `plan`: Plan contratado
- `estado`: Estado de la suscripción (activo, vencido, pausado, cancelado, prueba)
- `inicio_periodo`: Fecha de inicio del período
- `fin_periodo`: Fecha de fin del período

**Métodos:**

- `esta_activa()`: Verifica si el estado es "activo"
- `puede_escribir`: Property que valida si permite crear recursos

### UsoTenant

Contador materializado de recursos utilizados por cada tenant.

**Campos:**

- `tenant`: Referencia al tenant
- `hoteles`: Cantidad de hoteles creados
- `usuarios`: Cantidad de usuarios creados
- `ultima_actualizacion`: Última fecha de actualización

## 🔒 Permisos

### EscrituraPermitida

Valida que la suscripción esté activa y permita operaciones de escritura.

**Uso:**

```python
permission_classes = [EscrituraPermitida]
```

### DentroDeCuota

Valida que el tenant no haya excedido los límites de su plan.

**Uso:**

```python
class MiViewSet(viewsets.ModelViewSet):
    permission_classes = [EscrituraPermitida, DentroDeCuota]
    creando_hoteles = True  # o creando_usuarios = True
```

## 🔄 Middleware

### SuscripcionMiddleware

Agrega automáticamente la suscripción activa del tenant al request.

**Configuración en settings.py:**

```python
MIDDLEWARE = [
    "django_tenants.middleware.TenantMainMiddleware",
    'apps.suscripciones.middleware.SuscripcionMiddleware',  # ← Después de TenantMainMiddleware
    ...
]
```

**Acceso en vistas:**

```python
suscripcion = request.suscripcion  # Objeto Suscripcion o None
```

## 🛠️ Servicios

### obtener_suscripcion_activa(tenant)

Obtiene la suscripción activa de un tenant.

### obtener_uso_tenant(tenant)

Obtiene el registro de uso de recursos de un tenant.

### validar_puede_crear_hotel(tenant)

Valida si se puede crear un hotel según el plan.

### validar_puede_crear_usuario(tenant)

Valida si se puede crear un usuario según el plan.

## 📡 API Endpoints

### Planes

- `GET /api/planes/` - Lista todos los planes activos
- `GET /api/planes/{id}/` - Detalle de un plan

### Suscripciones

- `GET /api/suscripciones/` - Lista suscripciones del tenant
- `GET /api/suscripciones/{id}/` - Detalle de una suscripción
- `GET /api/suscripciones/actual/` - Suscripción activa del tenant actual
- `GET /api/suscripciones/estadisticas/` - Estadísticas de uso y límites

### Uso de Tenant

- `GET /api/uso-tenant/` - Lista el uso del tenant
- `GET /api/uso-tenant/actual/` - Uso actual del tenant

## 📝 Ejemplo de Uso en un ViewSet

```python
from rest_framework import viewsets
from core.permissions import EscrituraPermitida, DentroDeCuota
from apps.suscripciones.models import UsoTenant
from django_tenants.utils import schema_context
from django.db import transaction

class HotelViewSet(viewsets.ModelViewSet):
    permission_classes = [EscrituraPermitida, DentroDeCuota]
    creando_hoteles = True

    def initial(self, request, *args, **kwargs):
        # Agregar contadores para validación
        request.contadores_tenant = {
            "hoteles": Hotel.objects.count(),
            "usuarios": User.objects.count()
        }
        return super().initial(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        tenant = self.request.tenant

        # Incrementar contador en el esquema público
        with schema_context("public"):
            uso, _ = UsoTenant.objects.select_for_update().get_or_create(tenant=tenant)
            uso.hoteles += 1
            uso.save()

        try:
            serializer.save()
        except Exception:
            # Revertir contador si falla
            with schema_context("public"):
                uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
                uso.hoteles = max(0, uso.hoteles - 1)
                uso.save()
            raise

    @transaction.atomic
    def perform_destroy(self, instance):
        tenant = self.request.tenant
        instance.delete()

        # Decrementar contador
        with schema_context("public"):
            uso = UsoTenant.objects.select_for_update().get(tenant=tenant)
            uso.hoteles = max(0, uso.hoteles - 1)
            uso.save()
```

## 🔧 Comandos de Gestión

### Sincronizar contadores de uso

```bash
python manage.py sincronizar_uso_tenants
```

Este comando recalcula los contadores de recursos de todos los tenants basándose en los datos reales de la base de datos.

## 📋 Migraciones

Para aplicar los cambios de nombres a español:

```bash
python manage.py migrate suscripciones
```

## 🎯 Checklist de Implementación

- ✅ Modelos unificados en español
- ✅ Middleware configurado
- ✅ Permisos implementados
- ✅ Servicios de validación
- ✅ ViewSets y serializers
- ✅ Endpoints API
- ✅ Comando de sincronización
- ✅ HotelViewSet con control de cuotas
- ✅ Documentación completa

## 📌 Notas Importantes

1. **Esquema público**: Los modelos Plan, Suscripcion y UsoTenant viven en el esquema público (shared_apps)
2. **Atomicidad**: Usa transacciones atómicas al modificar contadores
3. **Select for update**: Usa `select_for_update()` para evitar condiciones de carrera
4. **Rollback**: Siempre revierte los contadores si la creación del recurso falla
5. **Middleware order**: SuscripcionMiddleware debe ir después de TenantMainMiddleware

## 🔄 Flujo de Validación

1. Request llega al servidor
2. TenantMainMiddleware identifica el tenant
3. SuscripcionMiddleware carga la suscripción activa
4. EscrituraPermitida valida que la suscripción permita escribir
5. DentroDeCuota valida que no se excedan los límites
6. perform_create incrementa el contador atómicamente
7. Si falla, revierte el contador

## 🌐 Respuestas de Error

```json
// Suscripción inactiva
{
  "detail": "Suscripción inactiva o vencida."
}

// Límite de hoteles
{
  "detail": "Límite de hoteles alcanzado (5). Actualiza tu plan para crear más hoteles."
}

// Límite de usuarios
{
  "detail": "Límite de usuarios alcanzado (10)."
}
```

## 📊 Estadísticas de Uso (Ejemplo de Respuesta)

```json
{
  "suscripcion": {
    "id": 1,
    "plan_nombre": "Premium",
    "estado": "activo",
    "esta_activa": true,
    "dias_restantes": 25
  },
  "uso": {
    "hoteles": 3,
    "usuarios": 8,
    "porcentaje_hoteles": 60.0,
    "porcentaje_usuarios": 80.0
  },
  "limite_hoteles": 5,
  "limite_usuarios": 10,
  "puede_crear_hotel": true,
  "puede_crear_usuario": true
}
```
