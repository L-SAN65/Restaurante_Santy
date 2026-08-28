"""
Santy POS - Django settings.

Configurado para Supabase (PostgreSQL en la nube), Vercel deployment,
zona horaria operativa UTC-5 y aplicaciones modulares por dominio.
"""

import sys
import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "django-insecure-santy-pos-dev-only"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1", "testserver", ".vercel.app"]),
    SUPABASE_URL=(str, ""),
    AWS_ACCESS_KEY_ID=(str, ""),
    AWS_SECRET_ACCESS_KEY=(str, ""),
    AWS_STORAGE_BUCKET_NAME=(str, ""),
    AWS_S3_REGION_NAME=(str, "us-east-1"),
    AWS_S3_ENDPOINT_URL=(str, ""),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
# DEBUG nunca se activa en Vercel (build + runtime), aunque .env.local diga lo contrario.
DEBUG = env("DEBUG") and os.environ.get("VERCEL") != "1"
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "crispy_forms",
    "crispy_tailwind",
    # Módulos de dominio
    "core.apps.CoreConfig",
    "reservations.apps.ReservationsConfig",
    "billing.apps.BillingConfig",
    "kitchen.apps.KitchenConfig",
    "inventory.apps.InventoryConfig",
    "loyalty.apps.LoyaltyConfig",
    "audit.apps.AuditConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "santy.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "santy.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos (Supabase PostgreSQL)
# ---------------------------------------------------------------------------

import dj_database_url  # noqa: E402

DATABASE_URL = env("DATABASE_URL", default=None)

DATABASES = {
    "default": (
        dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
        if DATABASE_URL
        else {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    )
}

# ---------------------------------------------------------------------------
# Modelo de usuario custom (roles de negocio)
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "core.User"
LOGIN_URL = "core:login"
LOGIN_REDIRECT_URL = "core:dashboard"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------------------
# Regionalización - invariantes de negocio (BDD)
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Panama"  # UTC-5 sin DST (invariante del sistema)
USE_I18N = True
USE_TZ = True

# Formato de moneda USD
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3
DECIMAL_SEPARATOR = "."
THOUSAND_SEPARATOR = ","

# ---------------------------------------------------------------------------
# Archivos estáticos y media (imágenes de platillos)
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
# Vercel filesystem es read-only excepto /tmp — usar /tmp/media en producción
if os.environ.get("VERCEL") == "1":
    MEDIA_ROOT = Path("/tmp/media")
    # Asegurar que exista al arrancar
    try:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
else:
    MEDIA_ROOT = BASE_DIR / "media"

# Los tests no requieren manifest hasheado (evita depender de npm run build).
if "test" in sys.argv:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Supabase Storage (S3-compatible) para imágenes persistentes en Vercel.
# Si tienes bucket configurado, define en Vercel Env: SUPABASE_URL, AWS_ACCESS_KEY_ID,
# AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME. Si no, fallback a filesystem (/tmp en Vercel).
_SUPABASE_URL = env("SUPABASE_URL", default="")
_AWS_BUCKET = env("AWS_STORAGE_BUCKET_NAME", default="")
_AWS_KEY = env("AWS_ACCESS_KEY_ID", default="")
_AWS_SECRET = env("AWS_SECRET_ACCESS_KEY", default="")
_USE_S3 = bool(_SUPABASE_URL and _AWS_BUCKET and _AWS_KEY and _AWS_SECRET)

if _USE_S3:
    # Deriva endpoint S3 si no se provee explícitamente
    _S3_ENDPOINT = env("AWS_S3_ENDPOINT_URL", default="") or f"{_SUPABASE_URL.rstrip('/')}/storage/v1/s3"
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": _AWS_KEY,
                "secret_key": _AWS_SECRET,
                "bucket_name": _AWS_BUCKET,
                "endpoint_url": _S3_ENDPOINT,
                "region_name": env("AWS_S3_REGION_NAME", default="us-east-1"),
                "file_overwrite": False,
                "default_acl": None,
                "querystring_auth": False,  # URLs públicas si bucket es público
                "object_parameters": {"CacheControl": "max-age=86400"},
            },
        },
        "staticfiles": {"BACKEND": STATICFILES_STORAGE},
    }
    # En S3 no hay MEDIA_ROOT local; MEDIA_URL será la URL del bucket
    # Pero mantenemos MEDIA_URL para compatibilidad (no usado por S3)
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": STATICFILES_STORAGE,
        },
    }

# ---------------------------------------------------------------------------
# Crispy forms (Tailwind theme)
# ---------------------------------------------------------------------------

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"