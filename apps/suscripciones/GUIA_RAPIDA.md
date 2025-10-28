# 🎯 GUÍA RÁPIDA: Sistema de Suscripciones

## 📍 ¿Dónde está cada cosa?

### ESQUEMA PÚBLICO (base de datos `public`)
```
Plan              → Planes disponibles (Básico, Premium, etc.)
Suscripcion       → Qué plan tiene cada tenant
UsoTenant         → Contador: cuántos hoteles/usuarios tiene cada tenant
```

### ESQUEMA TENANT (base de datos por cada hotel: `hotel1`, `hotel2`, etc.)
```
Hotel             → Los hoteles del tenant
User              → Los usuarios del tenant
Reserva           → Las reservas del tenant
```

## 🔄 Flujo Completo

### 1️⃣ Crear un Plan (admin o shell)
```python
# En el shell de Django
from apps.suscripciones.models import Plan

Plan.objects.create(
    nombre="Básico",
    max_usuarios=5,
    max_hoteles=2,
    precio=29.99,
    tipo="Mensual",
    activo=True
)
```

### 2️⃣ Crear un Tenant (ya lo tienes implementado)
```python
from core.models import Tenant, Domain

tenant = Tenant.objects.create(
    schema_name='hotelparaiso',
    name='Hotel Paraiso'
)

Domain.objects.create(
    domain='hotelparaiso.localhost',
    tenant=tenant,
    is_primary=True
)
```

### 3️⃣ Asignar Suscripción al Tenant
```python
# Opción A: Desde el shell
from apps.suscripciones.models import Suscripcion
from datetime import date, timedelta

Suscripcion.objects.create(
    tenant=tenant,
    plan=Plan.objects.get(nombre='Básico'),
    estado='activo',
    inicio_periodo=date.today(),
    fin_periodo=date.today() + timedelta(days=30)
)

# Opción B: Desde API pública (POST /api/suscripciones/)
{
  "tenant": 1,
  "plan": 1,
  "estado": "activo",
  "inicio_periodo": "2024-01-01",
  "fin_periodo": "2024-12-31"
}
```

### 4️⃣ El tenant intenta crear un hotel
```
1. Usuario hace POST a http://hotelparaiso.localhost:8000/api/hoteles/
2. TenantMainMiddleware identifica tenant 'hotelparaiso'
3. SuscripcionMiddleware carga su suscripción activa
4. EscrituraPermitida verifica: ¿suscripción activa? ✅
5. DentroDeCuota verifica: ¿tiene espacio? (usa 0 de 2 hoteles) ✅
6. HotelViewSet.perform_create():
   - Incrementa contador: UsoTenant.hoteles = 1
   - Crea el hotel en esquema 'hotelparaiso'
7. Respuesta 201 Created ✅
```

### 5️⃣ ¿Qué pasa si intenta crear el 3er hotel?
```
1-5. Igual que arriba...
6. DentroDeCuota verifica: usa 2 de 2 hoteles ❌
7. Respuesta 403 Forbidden:
   {
     "detail": "Límite de hoteles alcanzado (2). Actualiza tu plan para crear más hoteles."
   }
```

## 📡 Endpoints que puedes usar

### Endpoints PÚBLICOS (acceso desde cualquier dominio)
```bash
# Ver planes disponibles
GET http://localhost:8000/api/planes/

# Crear suscripción (cuando registras un tenant)
POST http://localhost:8000/api/suscripciones/
{
  "tenant": 1,
  "plan": 2,
  "estado": "activo",
  "inicio_periodo": "2024-01-01",
  "fin_periodo": "2024-12-31"
}

# Listar todas las suscripciones (admin)
GET http://localhost:8000/api/suscripciones/

# Actualizar suscripción (cambiar plan, extender fecha)
PUT http://localhost:8000/api/suscripciones/1/
```

### Endpoints de TENANT (cada hotel ve solo SU info)
```bash
# Ver MI suscripción actual
GET http://hotelparaiso.localhost:8000/api/mi-suscripcion/actual/

# Ver estadísticas de uso
GET http://hotelparaiso.localhost:8000/api/mi-suscripcion/estadisticas/
# Responde:
{
  "suscripcion": {
    "plan_nombre": "Básico",
    "estado": "activo",
    "dias_restantes": 25
  },
  "uso": {
    "hoteles": 2,
    "usuarios": 4,
    "porcentaje_hoteles": 100.0,
    "porcentaje_usuarios": 80.0
  },
  "limite_hoteles": 2,
  "limite_usuarios": 5,
  "puede_crear_hotel": false,
  "puede_crear_usuario": true
}
```

## 🔧 Aplicar en tu código existente

### Para validar hoteles (ya está hecho en HotelViewSet)
```python
class HotelViewSet(viewsets.ModelViewSet):
    permission_classes = [EscrituraPermitida, DentroDeCuota]
    creando_hoteles = True  # ← Esto activa la validación
```

### Para validar usuarios (todavía no implementado)
```python
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [EscrituraPermitida, DentroDeCuota]
    creando_usuarios = True  # ← Agregar esto
    
    def initial(self, request, *args, **kwargs):
        request.contadores_tenant = {
            "hoteles": Hotel.objects.count(),
            "usuarios": User.objects.count()  # ← Agregar esto
        }
        return super().initial(request, *args, **kwargs)
    
    # Copiar perform_create y perform_destroy de HotelViewSet
    # pero cambiando uso.hoteles por uso.usuarios
```

## 🛠️ Comandos útiles

```bash
# Crear migraciones
python manage.py makemigrations suscripciones

# Aplicar migraciones
python manage.py migrate suscripciones

# Entrar al shell
python manage.py shell

# Crear un plan desde shell
from apps.suscripciones.models import Plan
Plan.objects.create(nombre="Premium", max_usuarios=20, max_hoteles=10, precio=99.99, tipo="Anual", activo=True)

# Ver todos los planes
Plan.objects.all()

# Ver suscripciones
from apps.suscripciones.models import Suscripcion
Suscripcion.objects.all()

# Ver uso de un tenant
from apps.suscripciones.models import UsoTenant
UsoTenant.objects.all()
```

## ❓ Dudas Comunes

**P: ¿Por qué están en SHARED_APPS?**
R: Porque todos los tenants comparten los mismos planes. No tiene sentido duplicar los planes en cada base de datos.

**P: ¿Cómo accedo a modelos públicos desde el tenant?**
R: Con `schema_context("public")`:
```python
from django_tenants.utils import schema_context
with schema_context("public"):
    planes = Plan.objects.all()
```

**P: ¿Y si no quiero validar cuotas en alguna vista?**
R: Simplemente no uses `DentroDeCuota` en permission_classes.

**P: ¿Puedo tener varias suscripciones por tenant?**
R: Sí, pero el middleware usa solo la más reciente con estado activo/prueba.

**P: ¿Cómo extender una suscripción?**
R: `PUT /api/suscripciones/{id}/` y cambia `fin_periodo`.

**P: ¿Los contadores se sincronizan solos?**
R: Sí, al crear/eliminar recursos. Si se dessincronizan, puedes recalcular manualmente en el shell:
```python
from apps.suscripciones.models import UsoTenant
from apps.hoteles.models import Hotel
from core.models import Tenant
from django_tenants.utils import schema_context

tenant = Tenant.objects.get(schema_name='hotelparaiso')
with schema_context(tenant.schema_name):
    count = Hotel.objects.count()
with schema_context("public"):
    uso = UsoTenant.objects.get(tenant=tenant)
    uso.hoteles = count
    uso.save()
```
