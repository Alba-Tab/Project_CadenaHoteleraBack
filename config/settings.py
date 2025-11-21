from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env.str("SECRET_KEY", default="secretos") #type:ignore

DEBUG = env.bool("DEBUG", default=True) #type:ignore

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS",default=["*"]) #type:ignore
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("PGDATABASE", default="hotel_cad_bd"),#type:ignore
        "USER": env("PGUSER", default="postgres"),#type:ignore
        "PASSWORD": env("PGPASSWORD", default="admin"),#type:ignore
        "HOST": env("PGHOST", default="127.0.0.1"),#type:ignore
        "PORT": env("PGPORT", default="5433"),#type:ignore
        # 🚀 OPTIMIZACIONES DE RENDIMIENTO
        "CONN_MAX_AGE": 600,  # Mantener conexiones por 10 minutos
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # Timeout de 30 segundos para queries
        }
    }
}

# Application definition
SHARED_APPS = [
    'django_tenants',
    'core',
    'django.contrib.contenttypes',
    # 'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.admin',
    'rest_framework',
    'rest_framework_simplejwt',  # ✨ NUEVO
    'corsheaders',
    'apps.backups',  # MOVIDO A SHARED (debe estar en schema public) aqui registra todos los tenant
    'apps.suscripciones',
]
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'apps.usuarios',
    'django.contrib.admin',
    'apps.hoteles',
    'apps.habitaciones',
    'apps.servicios',
    'apps.reservas',
    'apps.folioestancias',
    'apps.fidelizacion',
    'apps.checkinout',
    'apps.pagos',
    'apps.servicios_asociados',
    'apps.configuracion_apariencia',
    'apps.facial_recognition',
    'apps.recomendaciones_ia',  # ML para recomendaciones de precios
    "storages",
    'auditlog',
]


INSTALLED_APPS = list(dict.fromkeys(SHARED_APPS + TENANT_APPS))

# ============================================================================
# CONFIGURACIÓN MULTITENANT basado en headers
# ============================================================================
TENANT_MODEL = "core.Tenant"
# TENANT_DOMAIN_MODEL eliminado - ya no se usa enfoque de dominios

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# Email settings                           django.core.mail.backends.console.EmailBackend
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')#type:ignore
EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.gmail.com')#type:ignore
EMAIL_PORT = env.int('EMAIL_PORT', default=587)#type:ignore
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)#type:ignore
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='brayan.123.bg76@gmail.com')#type:ignore
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')#type:ignore
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)#type:ignore

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    
    "config.middleware.tenant_header_middleware.TenantHeaderMiddleware",
    'apps.suscripciones.middleware.SuscripcionMiddleware',
    
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.middleware_user_audit.JWTActorMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "config.middleware.middleware_auditlog.TenantAuditLogMiddleware",
    
    # Otros
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============================================================================
# CONFIGURACIÓN DE URLs
# ============================================================================
ROOT_URLCONF = "config.urls"  # Archivo principal que delega a django-tenants
PUBLIC_SCHEMA_URLCONF = "config.urls_public"  # URLs para schema 'public'
TENANT_URLCONF = "config.urls_tenant"  # URLs para schemas de tenants

AUTH_USER_MODEL = "usuarios.User"

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-tenant',  # 🏨 Header para identificar el tenant
]

#-------------------------------------------------------------------------------------------------------------------

#-----------------------Arreglos de cors para la nube---------------------------------------
CORS_ALLOW_HEADERS = ['*']  # Permitir todas las cabeceras
CORS_ALLOW_METHODS = ['*']  # Permitir todos los métodos HTTP
CORS_EXPOSE_HEADERS = ['*']  # Exponer todas las cabeceras al cliente
CORS_PREFLIGHT_MAX_AGE = 86400  # Cache de preflight por 24 horas
#-------------------------------------------------------------------------------------------------------------------
# ✨ CONFIGURACIÓN DE JWT
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# 🚀 CONFIGURACIÓN DE CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD CSRF PARA CORS
# ============================================================================
# Orígenes confiables para CSRF
CSRF_TRUSTED_ORIGINS = [    
    'https://albadev.me',
    'http://albadev.me',
    'https://*.albadev.me',  # Todos los subdominios de albadev.me
    'http://*.albadev.me',
    'http://hoteles-front.s3-website.us-east-2.amazonaws.com',
    'https://jgyqzmxg7p.us-east-2.awsapprunner.com',
    'http://localhost:4200',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Permitir cookies cross-domain
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS



# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD CSRF PARA CORS
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="") #type:ignore
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="") #type:ignore
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="si2-hoteles") #type:ignore
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", default="us-east-2")  #type:ignore

# S3 Configuration
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None  # None para buckets con ACLs deshabilitadas (configuración moderna)
AWS_QUERYSTRING_AUTH = False  # No incluir query strings en las URLs
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_VERIFY = True  # Verificar certificados SSL

# Storage backends
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Media files URL
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
MEDIA_ROOT = ''

from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import default_storage

default_storage._wrapped = S3Boto3Storage() # type: ignore

# Firebase Configuration
import os
import json

# Opción 1: Usar archivo JSON local (desarrollo)
FIREBASE_CREDENTIAL_PATH = os.path.join(BASE_DIR, 'firebase', 'project-hotel-af807-firebase-adminsdk-fbsvc-5fca853de0.json')

# Opción 2: Usar variable de entorno con JSON completo (producción)
FIREBASE_CREDENTIALS_JSON = env.str('FIREBASE_CREDENTIALS_JSON', default='') #type:ignore
