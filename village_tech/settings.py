"""Django settings for Village Tech."""
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,.vercel.app"
    ).split(",")
    if host.strip()
]

# Vercel runs behind a TLS proxy — trust the X-Forwarded-Proto header so Django
# generates correct https:// absolute URLs (matters for CSRF and redirects).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Trust any subdomain on vercel.app for CSRF POSTs.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "https://*.vercel.app,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # local
    "customers",
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

ROOT_URLCONF = "village_tech.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "customers.context_processors.brand",
            ],
        },
    },
]

WSGI_APPLICATION = "village_tech.wsgi.application"

# Database: use DATABASE_URL (Postgres / Neon) when present, otherwise fall
# back to the local SQLite file. This keeps local development unchanged while
# production on Vercel reads the Neon connection string from an env var.
_DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if _DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            _DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Non-manifest variant: still compressed, but falls back gracefully if a
# referenced asset is missing — manifest mode hard-500s on first deploy if
# `collectstatic` hasn't run.
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Don't leak query strings (which may carry the masked phone) to outbound links.
SECURE_REFERRER_POLICY = "same-origin"

# Single shared password that gates /customer/. Override in .env for production.
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "jeeva9600")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Brand info — surfaced in templates via the customers.context_processors.brand processor.
VILLAGE_TECH_PHONE = "9600877537"
VILLAGE_TECH_BRAND = "Village Tech"
