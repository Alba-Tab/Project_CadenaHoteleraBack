# 📬 GUÍA COMPLETA DE POSTMAN - API DE BACKUPS

## 🔧 CONFIGURACIÓN INICIAL

### Variables de Entorno (Environment)
Crea un environment en Postman con estas variables:

```
BASE_URL = http://noelhoel.localhost:8000
# O también puedes usar:
# BASE_URL = http://hoteltajibo.localhost:8000
```

---

## 🔐 AUTENTICACIÓN (Si es necesario)

Si tu API requiere autenticación JWT, primero obtén el token:

### 1. Obtener Token de Acceso

**Endpoint:**
```
POST {{BASE_URL}}/api/token/
```

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

**Respuesta esperada:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Guardar el token:** Copia el valor de `access` y úsalo en los siguientes requests.

---

## 📋 ENDPOINTS DE BACKUPS

### 1️⃣ LISTAR TODOS LOS BACKUPS

**Endpoint:**
```
GET {{BASE_URL}}/api/backups/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json
```

**Query Parameters (Opcionales):**
```
?tipo=manual
?estado=ok
?backup_type=full
```

**Ejemplos:**
```
GET {{BASE_URL}}/api/backups/
GET {{BASE_URL}}/api/backups/?tipo=manual
GET {{BASE_URL}}/api/backups/?estado=ok
GET {{BASE_URL}}/api/backups/?backup_type=full
```

**Respuesta esperada (200 OK):**
```json
[
  {
    "id": 1,
    "tenant": null,
    "tenant_nombre": null,
    "tenant_schema": null,
    "archivo": "backups/full/full_backup_20251029_123456.sql",
    "tipo": "manual",
    "tipo_display": "Manual",
    "backup_type": "full",
    "backup_type_display": "Completo",
    "fecha": "2025-10-29T12:34:56Z",
    "tamano_bytes": 5453824,
    "tamano_mb": 5.2,
    "duracion_segundos": 3,
    "estado": "ok",
    "mensaje": "Backup exitoso. Tamaño: 5.20 MB"
  }
]
```

---

### 2️⃣ CREAR BACKUP COMPLETO (FULL)

**Endpoint:**
```
POST {{BASE_URL}}/api/backups/crear-backup-full/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "tipo": "manual"
}
```

**Opciones de tipo:**
- `"manual"` - Backup manual
- `"auto_daily"` - Automático diario
- `"auto_weekly"` - Automático semanal
- `"auto_monthly"` - Automático mensual

**Respuesta esperada (201 Created):**
```json
{
  "id": 2,
  "tenant": null,
  "tenant_nombre": null,
  "tenant_schema": null,
  "archivo": "backups/full/full_backup_20251029_143022.sql",
  "tipo": "manual",
  "tipo_display": "Manual",
  "backup_type": "full",
  "backup_type_display": "Completo",
  "fecha": "2025-10-29T14:30:22Z",
  "tamano_bytes": 5623000,
  "tamano_mb": 5.36,
  "duracion_segundos": 4,
  "estado": "ok",
  "mensaje": "Backup exitoso. Tamaño: 5.36 MB"
}
```

---

### 3️⃣ CREAR BACKUP DE TENANTS

**Endpoint:**
```
POST {{BASE_URL}}/api/backups/crear-backup-tenants/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json
```

**Body (JSON) - Todos los tenants:**
```json
{
  "tipo": "manual"
}
```

**Body (JSON) - Tenant específico:**
```json
{
  "tipo": "manual",
  "schema": "hotel_tajibo"
}
```

**Respuesta esperada (201 Created):**
```json
{
  "mensaje": "Backups de tenants creados exitosamente",
  "total": 2,
  "exitosos": 2,
  "fallidos": 0,
  "resultados": [
    {
      "tenant": "Hotel Tajibo",
      "schema": "hotel_tajibo",
      "estado": "ok",
      "archivo": "backups/tenant/hotel_tajibo_20251029_143500.sql",
      "tamano_mb": 2.1,
      "mensaje": "Backup exitoso"
    },
    {
      "tenant": "Noel Hotel",
      "schema": "noelhotel",
      "estado": "ok",
      "archivo": "backups/tenant/noelhotel_20251029_143502.sql",
      "tamano_mb": 1.8,
      "mensaje": "Backup exitoso"
    }
  ]
}
```

---

### 4️⃣ OBTENER ESTADÍSTICAS

**Endpoint:**
```
GET {{BASE_URL}}/api/backups/estadisticas/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
```

**Respuesta esperada (200 OK):**
```json
{
  "total_backups": 5,
  "total_size_bytes": 27459584,
  "total_size_mb": 26.18,
  "backups_exitosos": 5,
  "backups_fallidos": 0,
  "ultimo_backup": {
    "id": 5,
    "fecha": "2025-10-29T14:35:00Z",
    "tipo_display": "Manual",
    "backup_type_display": "Completo"
  },
  "backup_mas_antiguo": {
    "id": 1,
    "fecha": "2025-10-27T00:06:42Z",
    "tipo_display": "Manual",
    "backup_type_display": "Completo"
  }
}
```

---

### 5️⃣ OBTENER CONFIGURACIÓN

**Endpoint:**
```
GET {{BASE_URL}}/api/backups/configuracion/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
```

**Respuesta esperada (200 OK):**
```json
{
  "enabled": true,
  "frequency": "daily",
  "time": "03:00",
  "retention_days": 7,
  "storage": "local"
}
```

---

### 6️⃣ DESCARGAR BACKUP

**Endpoint:**
```
GET {{BASE_URL}}/api/backups/{id}/descargar/
```

**Ejemplo:**
```
GET {{BASE_URL}}/api/backups/1/descargar/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
```

**Respuesta esperada:**
- **200 OK** - Archivo `.sql` descargado
- **404 Not Found** - Backup no existe
- **400 Bad Request** - Archivo no encontrado

**En Postman:**
1. Haz clic en "Send"
2. Haz clic en "Save Response" → "Save to a file"
3. Guarda como `backup.sql`

---

### 7️⃣ OBTENER UN BACKUP POR ID

**Endpoint:**
```
GET {{BASE_URL}}/api/backups/{id}/
```

**Ejemplo:**
```
GET {{BASE_URL}}/api/backups/1/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
```

**Respuesta esperada (200 OK):**
```json
{
  "id": 1,
  "tenant": null,
  "tenant_nombre": null,
  "tenant_schema": null,
  "archivo": "backups/full/full_backup_20251029_123456.sql",
  "tipo": "manual",
  "tipo_display": "Manual",
  "backup_type": "full",
  "backup_type_display": "Completo",
  "fecha": "2025-10-29T12:34:56Z",
  "tamano_bytes": 5453824,
  "tamano_mb": 5.2,
  "duracion_segundos": 3,
  "estado": "ok",
  "mensaje": "Backup exitoso. Tamaño: 5.20 MB"
}
```

---

### 8️⃣ ELIMINAR BACKUP

**Endpoint:**
```
DELETE {{BASE_URL}}/api/backups/{id}/
```

**Ejemplo:**
```
DELETE {{BASE_URL}}/api/backups/5/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
```

**Respuesta esperada:**
- **204 No Content** - Eliminado correctamente
- **404 Not Found** - Backup no existe

---

## 🧪 ORDEN DE PRUEBAS RECOMENDADO

### **Paso 1: Verificar que no hay backups**
```
GET {{BASE_URL}}/api/backups/
```
Resultado esperado: `[]` (lista vacía)

---

### **Paso 2: Crear primer backup completo**
```
POST {{BASE_URL}}/api/backups/crear-backup-full/
Body: { "tipo": "manual" }
```
Resultado esperado: Objeto con `id: 1`, `estado: "ok"`

---

### **Paso 3: Listar backups de nuevo**
```
GET {{BASE_URL}}/api/backups/
```
Resultado esperado: Array con 1 elemento

---

### **Paso 4: Crear backups de tenants**
```
POST {{BASE_URL}}/api/backups/crear-backup-tenants/
Body: { "tipo": "manual" }
```
Resultado esperado: `exitosos: 2` (o el número de tenants que tengas)

---

### **Paso 5: Ver estadísticas**
```
GET {{BASE_URL}}/api/backups/estadisticas/
```
Resultado esperado: `total_backups: 3` (1 full + 2 tenants)

---

### **Paso 6: Descargar un backup**
```
GET {{BASE_URL}}/api/backups/1/descargar/
```
Resultado esperado: Archivo `.sql` descargado

---

### **Paso 7: Ver configuración**
```
GET {{BASE_URL}}/api/backups/configuracion/
```
Resultado esperado: `enabled: true`

---

## ❌ POSIBLES ERRORES Y SOLUCIONES

### **404 Not Found**
```json
{
  "detail": "Not found."
}
```
**Solución:**
- Verifica que la URL esté correcta
- Verifica que `apps.backups.urls` esté en `urls_tenant.py`
- Reinicia el servidor Django

---

### **401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Solución:**
- Agrega el header: `Authorization: Bearer TU_TOKEN`
- Obtén un nuevo token si expiró

---

### **500 Internal Server Error**
**Solución:**
- Revisa la consola de Django para ver el error exacto
- Verifica que las carpetas `media/backups/full/` y `media/backups/tenant/` existan
- Verifica que la tabla `backups_backup` exista en la base de datos

---

## 📦 COLECCIÓN DE POSTMAN

Puedes importar esta colección JSON directamente en Postman:

```json
{
  "info": {
    "name": "Backups API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Listar Backups",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{BASE_URL}}/api/backups/",
          "host": ["{{BASE_URL}}"],
          "path": ["api", "backups", ""]
        }
      }
    },
    {
      "name": "Crear Backup Full",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"tipo\": \"manual\"\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/api/backups/crear-backup-full/",
          "host": ["{{BASE_URL}}"],
          "path": ["api", "backups", "crear-backup-full", ""]
        }
      }
    },
    {
      "name": "Crear Backup Tenants",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"tipo\": \"manual\"\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/api/backups/crear-backup-tenants/",
          "host": ["{{BASE_URL}}"],
          "path": ["api", "backups", "crear-backup-tenants", ""]
        }
      }
    },
    {
      "name": "Estadísticas",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{BASE_URL}}/api/backups/estadisticas/",
          "host": ["{{BASE_URL}}"],
          "path": ["api", "backups", "estadisticas", ""]
        }
      }
    },
    {
      "name": "Configuración",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{BASE_URL}}/api/backups/configuracion/",
          "host": ["{{BASE_URL}}"],
          "path": ["api", "backups", "configuracion", ""]
        }
      }
    }
  ]
}
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de probar en Postman:

- [ ] Django corriendo: `python manage.py runserver`
- [ ] URLs configuradas en `urls_tenant.py`
- [ ] Carpetas creadas: `media/backups/full/` y `media/backups/tenant/`
- [ ] Tabla migrada: `python manage.py migrate backups`
- [ ] Al menos 1 tenant creado (ejemplo: hotel_tajibo, noelhotel)

---

**Fecha:** 29 de octubre de 2025  
**Proyecto:** Sistema de Backups - Cadena Hotelera  
**Backend:** Django + django-tenants  
**Base de datos:** PostgreSQL
