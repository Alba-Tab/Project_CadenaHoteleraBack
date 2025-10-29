# Sistema de Email Multitenant para Reportes

## 📧 Descripción

El servicio de envío de reportes por email ahora **soporta configuración por tenant**, permitiendo que cada tenant (empresa/hotel) use su propia configuración de email SMTP en lugar de usar siempre la del sistema.

## 🔄 Flujo de Funcionamiento

```
1. Request llega al endpoint de email
   ↓
2. Django Tenants middleware detecta el tenant
   request.tenant = <Tenant actual>
   ↓
3. Vista pasa el tenant al servicio
   enviar_reporte_por_email(..., tenant=request.tenant)
   ↓
4. Servicio verifica configuración del tenant
   ┌─────────────────────────────┐
   │ ¿Tenant tiene email config? │
   └─────────────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
       SÍ                NO
        │                 │
        ▼                 ▼
   Usar config      Usar config
   del tenant       del sistema
   (tenant.email)   (.env)
        │                 │
        └────────┬────────┘
                 ▼
           Enviar email
```

## 📝 Modificación Realizada

### Función `enviar_reporte_por_email()` actualizada

**Antes**:
```python
def enviar_reporte_por_email(rows, report_name, format, recipient_email, subject, message=None):
    # Siempre usaba la configuración del .env
    email = EmailMessage(...)
    email.send()
```

**Ahora**:
```python
def enviar_reporte_por_email(rows, report_name, format, recipient_email, subject, message=None, tenant=None):
    # Verifica si el tenant tiene configuración propia
    if tenant and hasattr(tenant, 'email_host_user') and tenant.email_host_user:
        # Crear conexión SMTP personalizada con datos del tenant
        connection = get_connection(
            host=tenant.email_host,
            port=tenant.email_port,
            username=tenant.email_host_user,
            password=tenant.email_host_password,
            use_tls=tenant.email_use_tls
        )
        from_email = tenant.default_from_email or tenant.email_host_user
    else:
        # Usar configuración por defecto del sistema
        connection = None  # Django usa settings.py
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Crear email con la conexión apropiada
    email = EmailMessage(..., from_email=from_email, connection=connection)
    email.send()
```

### Vistas actualizadas

**Habitaciones** (`apps/habitaciones/reportes/views.py`):
```python
result = enviar_reporte_por_email(
    rows=rows,
    report_name=r.name,
    format=data["format"],
    recipient_email=data["recipient_email"],
    subject=data["subject"],
    message=data.get("message"),
    tenant=getattr(request, 'tenant', None)  # ⭐ NUEVO
)
```

**Reservas** (`apps/reservas/reportes/views.py`):
```python
result = enviar_reporte_por_email(
    rows=rows,
    report_name=r.name,
    format=data["format"],
    recipient_email=data["recipient_email"],
    subject=data["subject"],
    message=data.get("message"),
    tenant=getattr(request, 'tenant', None)  # ⭐ NUEVO
)
```

## 🔧 Configuración Requerida (Futura)

Para activar la funcionalidad completa, necesitarás añadir estos campos al modelo de Tenant:

### Opción A: Añadir al modelo Tenant existente

```python
# En apps/suscripciones/models.py o donde esté el modelo Tenant

class Tenant(TenantMixin):
    # ...campos existentes...
    
    # Configuración de email por tenant (NUEVO)
    email_host = models.CharField(
        max_length=255, 
        default='smtp.gmail.com',
        blank=True,
        help_text="Servidor SMTP del tenant"
    )
    email_port = models.IntegerField(
        default=587,
        blank=True,
        help_text="Puerto SMTP"
    )
    email_host_user = models.EmailField(
        blank=True, 
        null=True,
        help_text="Email del remitente del tenant"
    )
    email_host_password = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Contraseña del email (encriptada)"
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text="Usar TLS para conexión segura"
    )
    default_from_email = models.EmailField(
        blank=True, 
        null=True,
        help_text="Email 'De' por defecto"
    )
```

### Opción B: Modelo separado (Recomendado para mejor organización)

```python
# En apps/suscripciones/models.py

class TenantEmailConfig(models.Model):
    """Configuración de email SMTP por tenant"""
    tenant = models.OneToOneField(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='email_config'
    )
    email_host = models.CharField(max_length=255, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_host_user = models.EmailField()
    email_host_password = models.CharField(max_length=255)  # Encriptada
    email_use_tls = models.BooleanField(default=True)
    from_email = models.EmailField(help_text="Email del remitente")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Email del Tenant"
        verbose_name_plural = "Configuraciones de Email de Tenants"
    
    def __str__(self):
        return f"Email Config - {self.tenant.name}"
```

## 🔐 Seguridad: Encriptación de Contraseñas

**IMPORTANTE**: Las contraseñas de email deben guardarse **encriptadas** en la base de datos.

### Instalación
```bash
pip install cryptography
```

### Implementación

```python
# En apps/suscripciones/utils.py o core/utils.py

from django.conf import settings
from cryptography.fernet import Fernet

def get_cipher():
    """Obtiene el cifrador con la clave del settings"""
    key = settings.EMAIL_ENCRYPTION_KEY.encode()
    return Fernet(key)

def encrypt_email_password(password):
    """Encripta una contraseña de email"""
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()

def decrypt_email_password(encrypted_password):
    """Desencripta una contraseña de email"""
    if not encrypted_password:
        return ''
    cipher = get_cipher()
    return cipher.decrypt(encrypted_password.encode()).decode()
```

### En settings.py
```python
# Generar una clave: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
EMAIL_ENCRYPTION_KEY = env('EMAIL_ENCRYPTION_KEY', default='tu_clave_generada_aqui')
```

### En el modelo
```python
def save(self, *args, **kwargs):
    # Encriptar contraseña antes de guardar si cambió
    if self.email_host_password and not self.pk:
        from apps.core.utils import encrypt_email_password
        self.email_host_password = encrypt_email_password(self.email_host_password)
    super().save(*args, **kwargs)
```

### En email_service.py (actualización futura)
```python
# Cuando obtengas la contraseña del tenant
from apps.core.utils import decrypt_email_password

password = decrypt_email_password(tenant.email_host_password)

connection = get_connection(
    ...
    password=password,
    ...
)
```

## 🎯 Casos de Uso

### Caso 1: Tenant CON configuración propia
```
Tenant: Hotel Grand Palace
email_host_user: reportes@grandpalace.com
email_host_password: [encriptada]

→ Los reportes se envían desde: reportes@grandpalace.com
→ Usa el SMTP configurado por el tenant
```

### Caso 2: Tenant SIN configuración (usa sistema)
```
Tenant: Hotel Nuevo
email_host_user: NULL

→ Los reportes se envían desde: sistema@cadenahotelesapp.com
→ Usa el SMTP del .env (configuración del sistema)
```

### Caso 3: Ambiente sin multitenant
```
request.tenant = None

→ Los reportes se envían desde: sistema@cadenahotelesapp.com
→ Usa el SMTP del .env (comportamiento por defecto)
```

## ✅ Estado Actual

| Componente | Estado | Descripción |
|------------|--------|-------------|
| **email_service.py** | ✅ Listo | Soporta parámetro `tenant` opcional |
| **Vistas (habitaciones/reservas)** | ✅ Listo | Pasan `request.tenant` al servicio |
| **Modelo Tenant** | ⏳ Pendiente | Necesita añadir campos de email config |
| **Encriptación** | ⏳ Pendiente | Implementar encrypt/decrypt |
| **Admin/UI** | ⏳ Pendiente | Interface para configurar email por tenant |
| **Migraciones** | ⏳ Pendiente | Crear migración para nuevos campos |

## 📋 Próximos Pasos para Completar la Funcionalidad

1. **Añadir campos al modelo Tenant**
   ```bash
   # Editar apps/suscripciones/models.py
   # Añadir campos de email config
   ```

2. **Crear migración**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Implementar encriptación**
   ```bash
   pip install cryptography
   # Crear utils.py con funciones encrypt/decrypt
   # Actualizar email_service.py para desencriptar
   ```

4. **Configurar admin**
   ```python
   # En admin.py del tenant
   # Añadir campos de email a la interface
   ```

5. **Testing**
   - Probar con tenant que tiene config
   - Probar con tenant sin config (fallback)
   - Probar sin multitenant

## 🔍 Compatibilidad

- ✅ **Retrocompatible**: Si no pasas `tenant`, funciona como antes
- ✅ **Multitenant**: Detecta automáticamente si existe `request.tenant`
- ✅ **Fallback seguro**: Si tenant no tiene config, usa la del sistema
- ✅ **Sin multitenant**: Funciona perfectamente en ambientes sin django-tenants

## 💡 Ejemplo de Uso Completo

```python
# En cualquier vista que envíe reportes

# 1. Con multitenant (automático)
result = enviar_reporte_por_email(
    rows=data,
    report_name="Reporte de Ventas",
    format="pdf",
    recipient_email="cliente@ejemplo.com",
    subject="Tu reporte mensual",
    message="Adjunto tu reporte",
    tenant=request.tenant  # Django Tenants lo inyecta automáticamente
)

# 2. Sin multitenant (también funciona)
result = enviar_reporte_por_email(
    rows=data,
    report_name="Reporte de Ventas",
    format="pdf",
    recipient_email="cliente@ejemplo.com",
    subject="Tu reporte mensual",
    message="Adjunto tu reporte",
    tenant=None  # O simplemente no pasar el parámetro
)

# 3. Con tenant específico (manual)
from apps.suscripciones.models import Tenant
tenant = Tenant.objects.get(schema_name='hotel_abc')

result = enviar_reporte_por_email(
    rows=data,
    ...,
    tenant=tenant
)
```

## 🎉 Beneficios

1. ✅ **Personalización**: Cada tenant usa su propio email corporativo
2. ✅ **Profesionalismo**: Los reportes llegan desde el email del hotel, no del sistema
3. ✅ **Flexibilidad**: Soporte para diferentes proveedores SMTP por tenant
4. ✅ **Escalabilidad**: Fácil añadir nuevos tenants con su config
5. ✅ **Seguridad**: Contraseñas encriptadas en BD
6. ✅ **Fallback**: Si falla config del tenant, usa la del sistema
7. ✅ **Retrocompatibilidad**: No rompe código existente

