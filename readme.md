# 🏨 Guía completa de creación de aplicación Django Multi‑Tenant

## Esta guía detalla los **pasos seguidos para crear la aplicación multi‑tenant** con `django-tenants`, usando un esquema por tenant y usuarios independientes por hotel

# 🤝 Flujo de trabajo con Git (Equipos y Ramas)

Esta guía explica cómo debe trabajar un equipo de desarrollo utilizando
ramas en Git para mantener un flujo limpio y organizado.

## 1️⃣ Estructura recomendada de ramas

-**main** → rama principal, contiene solo código estable y probado.\
 -**develop** → rama de integración donde se unen las nuevas funciones
antes de pasar a producción.\
 -**feature/**nombre-funcionalidad → ramas de trabajo individuales
para nuevas funciones o tareas.\
 -**hotfix/**nombre-fix → correcciones urgentes directamente sobre
main.

---

## 2️⃣ Clonar el repositorio por primera vez

```bash
git clone https://github.com/Alba-Tab/Project_CadenaHoteleraBack
cd Project_CadenaHoteleraBack
git checkout develop
```

---

## 3️⃣ Crear una nueva rama para trabajar

Antes de crear una nueva rama, asegúrate de tener el código actualizado:

```bash
git pull origin develop
git checkout -b feature/nueva-funcionalidad
```

---

## 4️⃣ Guardar y subir tus cambios

```bash
git add .
git commit -m "Descripción clara de los cambios"
git push origin feature/nueva-funcionalidad
```

---

## 5️⃣ Solicitar merge (pull request)

Una vez terminada la tarea:

1. Sube tu rama al repositorio remoto.\
2. En GitHub, crea un _Pull Request_ hacia `develop`.\
3. Espera revisión del equipo antes de hacer merge.

---

## 6️⃣ Actualizar tu entorno

Cada vez que empieces a trabajar o antes de crear una rama nueva:

```bash
git checkout develop
git pull origin develop
```

Si necesitas el último código estable:

```bash
git checkout main
git pull origin main
```

---

## 7️⃣ Trabajar con migraciones (Django)

Si modificas modelos, genera y versiona las migraciones:

```bash
python manage.py makemigrations
git add apps/*core*.py
git commit -m "Agregadas migraciones para [descripción]"
git push
```

---

## ✅ Buenas prácticas

-No trabajar directamente sobre `main`.\
 -Hacer commits pequeños y claros.\
 -Usar nombres de rama descriptivos.\
 -Borrar ramas locales y remotas cuando ya se fusionen.\
 -Hacer `pull` antes de empezar cada jornada.

---

**¡Listo! Tu flujo de trabajo en equipo con Git está configurado y
organizado.**

---

**¡Listo! Tu entorno de desarrollo está configurado y funcionando.** 🎉

---

## 📦 Clonar y configurar el proyecto (Para nuevos desarrolladores)

Si eres un nuevo miembro del equipo y necesitas configurar el proyecto desde cero, sigue estos pasos:

### 1️⃣ Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd CadenaHoteleraBack
```

### 2️⃣ Crear y activar el entorno virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activar en Windows (CMD)
.venv\Scripts\activate

```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=django-insecure-tu-clave-secreta-aqui
DEBUG=True

# Database - Ajusta según tu configuración de PostgreSQL
PGDATABASE=hotel_cad_bd
PGUSER=postgres
PGPASSWORD=tu_password_de_postgres
PGHOST=127.0.0.1
PGPORT=5432
```

> ⚠️ **Importante:** Cambia `PGPASSWORD` por la contraseña real de tu PostgreSQL local.

### 5️⃣ Crear la base de datos en PostgreSQL

Abre `psql` o pgAdmin y ejecuta:

```sql
CREATE DATABASE hotel_cad_bd;
```

O desde la terminal:

```bash
psql -U postgres -c "CREATE DATABASE hotel_cad_bd;"
```

### 6️⃣ Ejecutar migraciones

```bash
# Migrar esquema compartido (público)
python manage.py migrate_schemas --shared
```

### 7️⃣ Crear el tenant público (obligatorio)

```bash
python manage.py shell
```

Dentro de la shell de Python:

```python
from core.models import Tenant, Domain

# Crear tenant público (obligatorio para django-tenants)
public_tenant = Tenant(schema_name="public", name="Public Schema")
public_tenant.save()

exit()
```

### 8️⃣ Crear tu primer hotel (tenant)

Opción A - Desde la shell:

```bash
python manage.py shell
```

```python
from core.models import Tenant, Domain

# Crear el tenant del hotel
hotel = Tenant(schema_name="hotel_sol", name="Hotel Sol")
hotel.save()

# Asociar un dominio al tenant
domain = Domain(domain="hotelsol.localhost", tenant=hotel, is_primary=True)
domain.save()

exit()
```

Opción B - Vía API (si ya tienes el servidor corriendo):

```http
POST http://localhost:8000/api/tenants/
Content-Type: application/json

{
  "name": "Hotel Sol",
  "schema_name": "hotel_sol",
  "domain": "hotelsol.localhost"
}
```

### 9️⃣ Crear superusuario para el tenant

```bash
python manage.py create_tenant_superuser --schema=hotel_sol
```

Ingresa los datos solicitados:

- Username
- Email
- Password

### 🔟 Configurar hosts local

Para acceder mediante subdominios, edita el archivo hosts:

**Windows:**

```shell
C:\Windows\System32\drivers\etc\hosts
```

**Linux/Mac:**

```shell
/etc/hosts
```

Añade al final del archivo:

```shell
127.0.0.1 hotelsol.localhost
```

### 1️⃣1️⃣ Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

### 1️⃣2️⃣ Probar el acceso

Abre tu navegador en:

- **Esquema público:** `http://localhost:8000/`
- **Hotel Sol (tenant):** `http://hotelsol.localhost:8000/`
- **Admin Hotel Sol:** `http://hotelsol.localhost:8000/admin/`

---

## 🐛 Solución de problemas comunes

### Error de autenticación PostgreSQL

```shell
FATAL: la autentificación password falló para el usuario «postgres»
```

**Solución:** Verifica que la contraseña en el archivo `.env` coincida con la de tu PostgreSQL. Puedes cambiar la contraseña de postgres con:

```bash
psql -U postgres
ALTER USER postgres PASSWORD 'nueva_password';
```

### Error: "No module named 'psycopg'"

**Solución:** Instala las dependencias:

```bash
pip install psycopg[binary]
```

### Error: "Tenant matching query does not exist"

**Solución:** Asegúrate de haber creado el tenant público y el dominio:

```bash
python manage.py shell
# ... (ejecuta el código del paso 7)
```

### El subdominio no funciona

**Solución:**

1. Verifica que el archivo hosts esté guardado correctamente
2. Limpia la caché DNS: `ipconfig /flushdns` (Windows)
3. Reinicia el navegador

---

## **Guia para la creacion de proyecto desde cero**

## 🚀 Instalación de dependencias

```bash
python -m pip install "Django==5.2.*" djangorestframework "psycopg[binary]" django-tenants django-environ djangorestframework-simplejwt
```

---

## ⚙️ Creación del proyecto base

```bash
django-admin startproject config .
python manage.py startapp core
```

Crea los modelos de `Tenant` y `Domain` dentro de `core/models.py`, y configura `settings.py` con las variables `SHARED_APPS`, `TENANT_APPS`, `DATABASE_ROUTERS`, `MIDDLEWARE`, etc.

---

## 👥 Creación de la app de usuarios

```bash
python manage.py startapp usuarios apps/usuarios
```

> Al crear una app, recuerda en `apps.py` definir correctamente el nombre:

```python
name = "apps.usuarios"
```

Luego crea tu modelo de usuario en `apps/usuarios/models.py`:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
```

Agrega también las rutas `urls_public.py` y `urls_tenant.py`.

---

## 🧱 Migraciones iniciales

```bash
python manage.py makemigrations
python manage.py migrate_schemas --shared  # Migra el esquema público
```

---

## 🏨 Crear tenants desde la shell

```bash
python manage.py shell
```

```python
from core.models import Tenant, Domain
pub = Tenant(schema_name="public", name="Main"); pub.save()
c = Tenant(schema_name="hotel_sol", name="Hotel Sol"); c.save()
d = Domain(domain="hotelsol.localhost", tenant=c, is_primary=True); d.save()
```

Esto crea físicamente el esquema `hotel_sol` y aplica migraciones dentro de él.

---

## 📡 Creación de tenants vía API (alternativa)

También puedes crear tenants con un **POST HTTP** desde Postman o tu frontend:

```http
POST /api/tenants/
Content-Type: application/json

{
  "name": "Hotel Sol",
  "schema_name": "hotel_sol",
  "domain": "hotelsol.localhost"
}
```

---

## 👤 Crear un superusuario dentro del tenant

### Opción 1 — Manual desde shell

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(username="admin", email="admin@sol.com", password="12345")
```

### Opción 2 — Comando directo

```bash
python manage.py create_tenant_superuser --schema=hotel_sol
```

---

## ▶️ Ejecutar el servidor

```bash
python manage.py runserver
```

Visita:

```shell
http://hotelsol.localhost:8000/
```

---

## 🌐 Agregar el subdominio local

Edita el archivo de hosts en Windows:

```shell
C:\Windows\System32\drivers\etc\hosts
```

Agrega al final:

```shell
127.0.0.1 hotelsol.localhost
```

Esto permitirá acceder mediante el subdominio `http://hotelsol.localhost:8000/`.

---

## ⚠️ Migraciones seguras (recomendado)

```text
1) makemigrations
2) migrate_schemas --shared
3) Ventana de mantenimiento corta
4) migrate_schemas para todos los tenants o --schema=<name> para pruebas canary
5) Observar errores y aplicar rollback si es necesario
```

---

## ✅ Resultado final

- Esquema `public`: tablas globales y registro de tenants (`core_tenant`, `core_domain`)
- Esquema `hotel_sol`: tablas propias del tenant (`usuarios_user`, `auth_*`, `admin_*`, etc.)
- Aislamiento completo por subdominio (`hotelsol.localhost`)

---

**Proyecto funcional y listo para extender con nuevos tenants o servicios.**

---

## 📚 Estructura del proyecto

```shell
CadenaHoteleraBack/
├── .venv/                  # Entorno virtual (NO en Git)
├── apps/
│   └── usuarios/          # App de usuarios por tenant
├── config/                # Configuración de Django
│   ├── settings.py       # Configuración principal
│   ├── urls.py           # URLs principales
│   ├── urls_public.py    # URLs del esquema público
│   └── urls_tenant.py    # URLs de los tenants
├── core/             # Modelos de tenants
├── .env                   # Variables de entorno (NO en Git)
├── .gitignore            # Archivos ignorados por Git
├── db.sqlite3            # Base de datos SQLite (NO en Git)
├── manage.py             # Script de gestión de Django
├── readme.md             # Este archivo
└── requirements.txt      # Dependencias del proyecto
```
