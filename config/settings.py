from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env.str("SECRET_KEY", default="secretos") #type:ignore

DEBUG = env.bool("DEBUG", default=True) #type:ignore

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"]) #type:ignore
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("PGDATABASE", default="hotel_cad_bd"),#type:ignore
        "USER": env("PGUSER", default="postgres"),#type:ignore
        "PASSWORD": env("PGPASSWORD", default="admin"),#type:ignore
        "HOST": env("PGHOST", default="127.0.0.1"),#type:ignore
        "PORT": env("PGPORT", default="5433"),#type:ignore
    }
}

# Application definition
SHARED_APPS = [
    'django_tenants',
    'core',
    'django.contrib.contenttypes',
    #'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.admin',
    'rest_framework',
    
]
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'apps.usuarios',  # your tenant-specific apps
    'django.contrib.admin',
    'apps.hoteles',
    'apps.habitaciones',
]


INSTALLED_APPS = list(dict.fromkeys(SHARED_APPS + TENANT_APPS))
TENANT_MODEL = "core.Tenant"
TENANT_DOMAIN_MODEL = "core.Domain"

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)


MIDDLEWARE = [
    "django_tenants.middleware.TenantMainMiddleware",
    'config.middleware.middleware_force_urlconf.ForcetenantUrlconfMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "config.urls_public"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"
TENANT_URLCONF = "config.urls_tenant"

AUTH_USER_MODEL = "usuarios.User"


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
