# 🎨 DIAGRAMA: Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS POSTGRESQL                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  ESQUEMA: public (SHARED_APPS)                        │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │                                                         │      │
│  │  📋 Plan                                               │      │
│  │    - nombre: "Básico", "Premium"                      │      │
│  │    - max_usuarios: 5                                   │      │
│  │    - max_hoteles: 2                                    │      │
│  │    - precio: 29.99                                     │      │
│  │                                                         │      │
│  │  📄 Suscripcion                                        │      │
│  │    - tenant: FK → Tenant                               │      │
│  │    - plan: FK → Plan                                   │      │
│  │    - estado: "activo"                                  │      │
│  │    - fin_periodo: 2024-12-31                          │      │
│  │                                                         │      │
│  │  📊 UsoTenant                                          │      │
│  │    - tenant: FK → Tenant                               │      │
│  │    - hoteles: 1 (contador)                             │      │
│  │    - usuarios: 3 (contador)                            │      │
│  │                                                         │      │
│  │  🏢 Tenant                                              │      │
│  │    - schema_name: "hotelparaiso"                      │      │
│  │    - name: "Hotel Paraiso"                            │      │
│  │                                                         │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  ESQUEMA: hotelparaiso (TENANT_APPS)                  │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │                                                         │      │
│  │  🏨 Hotel                                               │      │
│  │    - nombre: "Sucursal Centro"                        │      │
│  │    - direccion: "Calle 123"                           │      │
│  │                                                         │      │
│  │  👤 User                                                │      │
│  │    - username: "admin"                                 │      │
│  │    - email: "admin@hotel.com"                         │      │
│  │                                                         │      │
│  │  🛏️ Habitacion, Reserva, etc...                        │      │
│  │                                                         │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  ESQUEMA: otroholel (TENANT_APPS)                     │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │  ... sus propios datos aislados ...                    │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 FLUJO: Usuario crea un hotel

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. REQUEST                                                        │
│    POST http://hotelparaiso.localhost:8000/api/hoteles/         │
│    { "nombre": "Sucursal Norte", "direccion": "..." }           │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│ 2. DJANGO MIDDLEWARE                                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TenantMainMiddleware                                            │
│  ├─ Lee dominio: "hotelparaiso.localhost"                       │
│  ├─ Busca Tenant con schema_name="hotelparaiso"                 │
│  └─ Agrega: request.tenant = <Tenant hotelparaiso>              │
│                                                                   │
│  SuscripcionMiddleware                                           │
│  ├─ Lee: request.tenant                                          │
│  ├─ Busca en esquema público:                                    │
│  │  Suscripcion.objects.filter(                                  │
│  │    tenant=request.tenant,                                     │
│  │    estado__in=["activo", "prueba"]                           │
│  │  )                                                             │
│  └─ Agrega: request.suscripcion = <Suscripcion activa>          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│ 3. PERMISOS (permission_classes)                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  EscrituraPermitida                                              │
│  ├─ Lee: request.suscripcion                                     │
│  ├─ Valida: suscripcion.puede_escribir                          │
│  │  ├─ estado in ["activo", "prueba"]? ✅                       │
│  │  └─ fin_periodo >= hoy? ✅                                    │
│  └─ Resultado: PERMITIDO ✅                                       │
│                                                                   │
│  DentroDeCuota                                                   │
│  ├─ Lee: request.suscripcion                                     │
│  ├─ Lee: view.creando_hoteles = True                            │
│  ├─ Busca en esquema público:                                    │
│  │  uso = UsoTenant.objects.get(tenant=request.tenant)          │
│  ├─ Compara:                                                     │
│  │  uso.hoteles (1) < suscripcion.plan.max_hoteles (2)? ✅      │
│  └─ Resultado: PERMITIDO ✅                                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│ 4. VIEWSET: HotelViewSet.perform_create()                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  @transaction.atomic                                             │
│  def perform_create(self, serializer):                           │
│                                                                   │
│    # Paso A: Incrementar contador en esquema público            │
│    with schema_context("public"):                                │
│      uso = UsoTenant.objects.get(tenant=self.request.tenant)    │
│      uso.hoteles += 1  # 1 → 2                                   │
│      uso.save()                                                  │
│                                                                   │
│    # Paso B: Crear hotel en esquema del tenant                  │
│    try:                                                           │
│      serializer.save()  # Crea en esquema "hotelparaiso"        │
│    except Exception:                                             │
│      # Si falla, revertir contador                              │
│      with schema_context("public"):                              │
│        uso.hoteles -= 1  # 2 → 1                                 │
│        uso.save()                                                │
│      raise                                                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│ 5. RESPUESTA                                                     │
│    201 Created                                                   │
│    {                                                             │
│      "id": 2,                                                    │
│      "nombre": "Sucursal Norte",                                │
│      "direccion": "..."                                          │
│    }                                                             │
└──────────────────────────────────────────────────────────────────┘
```

## 🚫 FLUJO: Usuario excede el límite

```
Usuario intenta crear el 3er hotel (límite es 2)
                          ↓
Middleware carga suscripción ✅
                          ↓
EscrituraPermitida: Suscripción activa ✅
                          ↓
DentroDeCuota:
  uso.hoteles (2) < plan.max_hoteles (2)? ❌
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│ RESPUESTA: 403 Forbidden                                         │
│ {                                                                 │
│   "detail": "Límite de hoteles alcanzado (2). Actualiza tu      │
│              plan para crear más hoteles."                       │
│ }                                                                 │
└──────────────────────────────────────────────────────────────────┘
```

## 📡 ESTRUCTURA DE URLs

```
┌─────────────────────────────────────────────────────────────────┐
│  URLs PÚBLICAS (config/urls_public.py)                          │
│  Dominio: http://localhost:8000                                 │
│  o        http://public.localhost:8000                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  /api/planes/              → PlanPublicoViewSet                 │
│  /api/suscripciones/       → SuscripcionPublicaViewSet          │
│  /api/public/tenants/      → TenantViewSet (core)               │
│                                                                   │
│  Acceso: Sin tenant, sin autenticación                          │
│  Esquema: public                                                 │
│  Uso: Registro, admin, ver planes disponibles                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  URLs de TENANT (config/urls_tenant.py)                         │
│  Dominio: http://hotelparaiso.localhost:8000                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  /api/hoteles/             → HotelViewSet                       │
│  /api/usuarios/            → UserViewSet                        │
│  /api/reservas/            → ReservaViewSet                     │
│  /api/mi-suscripcion/      → MiSuscripcionViewSet               │
│                                                                   │
│  Acceso: Con tenant específico, requiere autenticación          │
│  Esquema: hotelparaiso (automático por TenantMainMiddleware)   │
│  Uso: Operaciones del día a día del hotel                       │
│                                                                   │
│  /api/mi-suscripcion/actual/        → Ver MI suscripción        │
│  /api/mi-suscripcion/estadisticas/  → Ver MI uso/límites        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔑 Conceptos Clave Visuales

### Schema Context

```python
# Por defecto, estás en el esquema del tenant
Hotel.objects.all()  # Lee de esquema "hotelparaiso"

# Para acceder al esquema público
with schema_context("public"):
    Plan.objects.all()  # Lee de esquema "public"
```

### Middleware vs Manual

```python
# ❌ MAL - Acceder sin middleware
def mi_vista(request):
    tenant = Tenant.objects.get(schema_name='hotelparaiso')
    with schema_context("public"):
        suscripcion = Suscripcion.objects.filter(tenant=tenant).first()

# ✅ BIEN - Usar lo que carga el middleware
def mi_vista(request):
    suscripcion = request.suscripcion  # Ya lo cargó el middleware
```

### Permisos en cascada

```python
permission_classes = [EscrituraPermitida, DentroDeCuota]
#                     ↓                    ↓
#                  Valida primero      Valida segundo
#                  (suscripción)       (límites)
```
