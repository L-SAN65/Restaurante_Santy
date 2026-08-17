"""
Santy POS - Django settings.

Configurado para Supabase (PostgreSQL en la nube), Vercel deployment,
zona horaria operativa UTC-5 y aplicaciones modulares por dominio.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "django-insecure-santy-pos-dev-only"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1", "testserver", ".vercel.app"]),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "channels",
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

ASGI_APPLICATION = "santy.asgi.application"
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
# Archivos estáticos
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Crispy forms (Tailwind theme)
# ---------------------------------------------------------------------------

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# ---------------------------------------------------------------------------
# Channels (realtime KDS y estados de mesa)
# ---------------------------------------------------------------------------

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"