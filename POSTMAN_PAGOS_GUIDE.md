# 🧪 Guía de Pruebas en Postman - Módulo Pagos

## 📋 Requisitos Previos

### 1. **Aplicar las Migraciones**
```bash
python manage.py migrate pagos
```

### 2. **Crear Datos de Prueba (RECOMENDADO)**
```bash
# Esto creará pagos de ejemplo
python manage.py seed_pagos
```

### 3. **Configurar el Tenant**
Asegúrate de tener un tenant creado y usar su dominio en las peticiones.

---

## 🌐 Configuración Base de Postman

### Variables de Entorno (Recomendado)
Crea estas variables en Postman:

| Variable | Valor Ejemplo |
|----------|---------------|
| `base_url` | `http://tajibo.localhost:8000` |
| `api_path` | `api/pagos` |
| `token` | `tu_token_jwt_aqui` (si usas autenticación) |

---

## 🔥 Endpoints Disponibles

### Base URL de Pagos
```
http://tajibo.localhost:8000/api/pagos/
```

---

## 📝 1. CREAR UN PAGO (POST)

### Endpoint
```
POST {{base_url}}/{{api_path}}/
```

### Headers
```
Content-Type: application/json
Authorization: Bearer {{token}}  # Si usas JWT
```

### Body (JSON) - Ejemplo Básico
```json
{
    "estado": "pendiente",
    "fecha_pago": "2025-10-17",
    "metodo": "tarjeta de credito",
    "monto": "250.00",
    "referencia": "TXN-2025-001",
    "folio_estancia": 1
}
```

### Body (JSON) - Sin Folio (Opcional)
```json
{
    "estado": "completado",
    "fecha_pago": "2025-10-17",
    "metodo": "efectivo",
    "monto": "150.50",
    "referencia": "CASH-2025-001"
}
```

### Respuesta Esperada (201 Created)
```json
{
    "id": 1,
    "estado": "pendiente",
    "estado_display": "Pendiente",
    "fecha_pago": "2025-10-17",
    "metodo": "tarjeta de credito",
    "monto": "250.00",
    "referencia": "TXN-2025-001",
    "folio_estancia": 1,
    "created_at": "2025-10-17T10:30:00Z",
    "updated_at": "2025-10-17T10:30:00Z"
}
```

---

## 📖 2. LISTAR TODOS LOS PAGOS (GET)

### Endpoint
```
GET {{base_url}}/{{api_path}}/
```

### Headers
```
Authorization: Bearer {{token}}  # Si usas JWT
```

### Respuesta Esperada (200 OK)
```json
[
    {
        "id": 1,
        "estado": "completado",
        "estado_display": "Completado",
        "fecha_pago": "2025-10-17",
        "metodo": "efectivo",
        "monto": "150.00",
        "referencia": "CASH-001",
        "folio_estancia": 1,
        "created_at": "2025-10-17T10:00:00Z",
        "updated_at": "2025-10-17T10:00:00Z"
    },
    {
        "id": 2,
        "estado": "pendiente",
        "estado_display": "Pendiente",
        "fecha_pago": "2025-10-17",
        "metodo": "tarjeta de credito",
        "monto": "250.00",
        "referencia": "TXN-002",
        "folio_estancia": 2,
        "created_at": "2025-10-17T11:00:00Z",
        "updated_at": "2025-10-17T11:00:00Z"
    }
]
```

---

## 🔍 3. OBTENER UN PAGO POR ID (GET)

### Endpoint
```
GET {{base_url}}/{{api_path}}/1/
```

### Headers
```
Authorization: Bearer {{token}}  # Si usas JWT
```

### Respuesta Esperada (200 OK)
```json
{
    "id": 1,
    "estado": "completado",
    "estado_display": "Completado",
    "fecha_pago": "2025-10-17",
    "metodo": "efectivo",
    "monto": "150.00",
    "referencia": "CASH-001",
    "folio_estancia": 1,
    "created_at": "2025-10-17T10:00:00Z",
    "updated_at": "2025-10-17T10:00:00Z"
}
```

---

## ✏️ 4. ACTUALIZAR UN PAGO (PUT/PATCH)

### Endpoint (PUT - Actualización Completa)
```
PUT {{base_url}}/{{api_path}}/1/
```

### Headers
```
Content-Type: application/json
Authorization: Bearer {{token}}  # Si usas JWT
```

### Body (JSON)
```json
{
    "estado": "completado",
    "fecha_pago": "2025-10-17",
    "metodo": "transferencia bancaria",
    "monto": "300.00",
    "referencia": "TRANSFER-2025-001",
    "folio_estancia": 1
}
```

### Endpoint (PATCH - Actualización Parcial)
```
PATCH {{base_url}}/{{api_path}}/1/
```

### Body (JSON) - Solo cambiar estado
```json
{
    "estado": "completado"
}
```

### Respuesta Esperada (200 OK)
```json
{
    "id": 1,
    "estado": "completado",
    "estado_display": "Completado",
    "fecha_pago": "2025-10-17",
    "metodo": "transferencia bancaria",
    "monto": "300.00",
    "referencia": "TRANSFER-2025-001",
    "folio_estancia": 1,
    "created_at": "2025-10-17T10:00:00Z",
    "updated_at": "2025-10-17T12:30:00Z"
}
```

---

## 🗑️ 5. ELIMINAR UN PAGO (DELETE)

### Endpoint
```
DELETE {{base_url}}/{{api_path}}/1/
```

### Headers
```
Authorization: Bearer {{token}}  # Si usas JWT
```

### Respuesta Esperada (204 No Content)
Sin contenido en el body, solo status 204.

---

## 🔎 6. FILTROS Y BÚSQUEDAS

### Filtrar por Estado
```
GET {{base_url}}/{{api_path}}/?estado=completado
```

**Valores posibles:** `pendiente`, `completado`, `fallido`

### Filtrar por Método
```
GET {{base_url}}/{{api_path}}/?metodo=efectivo
```

### Filtrar por Folio de Estancia
```
GET {{base_url}}/{{api_path}}/?folio_estancia=1
```

### Búsqueda (Search)
```
GET {{base_url}}/{{api_path}}/?search=TXN
```
Busca en: `metodo`, `estado`, `referencia`

### Ordenamiento
```
# Ordenar por fecha de pago ascendente
GET {{base_url}}/{{api_path}}/?ordering=fecha_pago

# Ordenar por fecha de pago descendente
GET {{base_url}}/{{api_path}}/?ordering=-fecha_pago

# Ordenar por monto ascendente
GET {{base_url}}/{{api_path}}/?ordering=monto

# Múltiples ordenamientos
GET {{base_url}}/{{api_path}}/?ordering=-fecha_pago,monto
```

### Combinación de Filtros
```
GET {{base_url}}/{{api_path}}/?estado=completado&metodo=efectivo&ordering=-fecha_pago
```

---

## ⚠️ 7. VALIDACIONES Y ERRORES

### Error: Monto Negativo o Cero
**Request:**
```json
{
    "estado": "pendiente",
    "fecha_pago": "2025-10-17",
    "metodo": "efectivo",
    "monto": "0.00",
    "referencia": "TEST-001"
}
```

**Response (400 Bad Request):**
```json
{
    "monto": [
        "El monto debe ser mayor a cero."
    ]
}
```

### Error: Fecha Futura
**Request:**
```json
{
    "estado": "pendiente",
    "fecha_pago": "2026-10-17",
    "metodo": "efectivo",
    "monto": "100.00",
    "referencia": "TEST-002"
}
```

**Response (400 Bad Request):**
```json
{
    "fecha_pago": [
        "La fecha de pago no puede ser futura."
    ]
}
```

### Error: Folio No Existe
**Request:**
```json
{
    "estado": "pendiente",
    "fecha_pago": "2025-10-17",
    "metodo": "efectivo",
    "monto": "100.00",
    "referencia": "TEST-003",
    "folio_estancia": 9999
}
```

**Response (400 Bad Request):**
```json
{
    "folio_estancia": [
        "El folio de estancia no existe."
    ]
}
```

---

## 🧪 8. CASOS DE PRUEBA RECOMENDADOS

### ✅ Test 1: Crear Pago Básico
- Método: POST
- Estado esperado: 201 Created
- Verificar: Todos los campos se guardan correctamente

### ✅ Test 2: Crear Pago Sin Folio
- Método: POST
- Body sin `folio_estancia`
- Estado esperado: 201 Created

### ✅ Test 3: Listar Todos los Pagos
- Método: GET
- Estado esperado: 200 OK
- Verificar: Array de pagos

### ✅ Test 4: Obtener Pago Individual
- Método: GET con ID
- Estado esperado: 200 OK

### ✅ Test 5: Actualizar Estado
- Método: PATCH
- Cambiar estado de "pendiente" a "completado"
- Estado esperado: 200 OK

### ✅ Test 6: Filtrar por Estado
- Método: GET con query param `?estado=completado`
- Estado esperado: 200 OK
- Verificar: Solo pagos completados

### ✅ Test 7: Buscar por Referencia
- Método: GET con query param `?search=TXN`
- Estado esperado: 200 OK
- Verificar: Pagos con "TXN" en referencia

### ✅ Test 8: Validar Monto Cero
- Método: POST con monto 0
- Estado esperado: 400 Bad Request

### ✅ Test 9: Validar Fecha Futura
- Método: POST con fecha futura
- Estado esperado: 400 Bad Request

### ✅ Test 10: Eliminar Pago
- Método: DELETE
- Estado esperado: 204 No Content

---

## 🎯 9. DATOS DE PRUEBA SUGERIDOS

### Métodos de Pago Comunes
- `efectivo`
- `tarjeta de credito`
- `tarjeta de debito`
- `transferencia bancaria`
- `paypal`
- `qr`

### Estados
- `pendiente` - Pago en proceso
- `completado` - Pago exitoso
- `fallido` - Pago rechazado

### Referencias de Ejemplo
- `TXN-2025-001`
- `CASH-17OCT-001`
- `CARD-123456`
- `TRANSFER-BOL-001`

---

## 🚀 10. COMANDOS ÚTILES

### Crear Datos de Prueba
```bash
python manage.py seed_pagos
```

### Ver Pagos en Admin
```
http://tajibo.localhost:8000/admin/pagos/pago/
```

### Ver Estructura de URLs
```bash
python manage.py show_urls | grep pago
```

---

## 📦 11. COLECCIÓN DE POSTMAN (JSON)

Puedes importar esta colección a Postman:

```json
{
    "info": {
        "name": "Pagos API - Hotel Cadena",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Crear Pago",
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
                    "raw": "{\n    \"estado\": \"pendiente\",\n    \"fecha_pago\": \"2025-10-17\",\n    \"metodo\": \"tarjeta de credito\",\n    \"monto\": \"250.00\",\n    \"referencia\": \"TXN-2025-001\",\n    \"folio_estancia\": 1\n}"
                },
                "url": {
                    "raw": "{{base_url}}/{{api_path}}/",
                    "host": ["{{base_url}}"],
                    "path": ["{{api_path}}", ""]
                }
            }
        },
        {
            "name": "Listar Pagos",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/{{api_path}}/",
                    "host": ["{{base_url}}"],
                    "path": ["{{api_path}}", ""]
                }
            }
        },
        {
            "name": "Obtener Pago por ID",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/{{api_path}}/1/",
                    "host": ["{{base_url}}"],
                    "path": ["{{api_path}}", "1", ""]
                }
            }
        },
        {
            "name": "Actualizar Pago (PATCH)",
            "request": {
                "method": "PATCH",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"estado\": \"completado\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/{{api_path}}/1/",
                    "host": ["{{base_url}}"],
                    "path": ["{{api_path}}", "1", ""]
                }
            }
        },
        {
            "name": "Eliminar Pago",
            "request": {
                "method": "DELETE",
                "url": {
                    "raw": "{{base_url}}/{{api_path}}/1/",
                    "host": ["{{base_url}}"],
                    "path": ["{{api_path}}", "1", ""]
                }
            }
        },
        {
            "name": "Filtrar por Estado",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/{{api_path}}/?estado=completado",
                    "host": ["{{base_url}}"],
                    "path": ["{{api_path}}", ""],
                    "query": [
                        {
                            "key": "estado",
                            "value": "completado"
                        }
                    ]
                }
            }
        }
    ]
}
```

---

## ✨ Resumen

**Tu módulo de Pagos está listo para:**
- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Filtros por estado, método y folio
- ✅ Búsqueda por texto
- ✅ Ordenamiento flexible
- ✅ Validaciones robustas
- ✅ Relación con FolioEstancia

**¡Listo para probar en Postman!** 🚀
