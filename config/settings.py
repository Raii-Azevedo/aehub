# ========================
# JAZZMIN (Admin UI)
# ========================
JAZZMIN_SETTINGS = {
    "site_title": "AE Hub Admin",
    "site_header": "AE Knowledge Hub",
    "site_brand": "AE Hub",
    "site_logo": "images/logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/favicon.png",
    "welcome_sign": "Welcome to the AE Hub Admin",
    "copyright": "Artefact Analytics Engineering",
    "search_model": ["auth.user"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "core"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": False,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-purple",
    "accent": "accent-purple",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-purple",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

"""
Django settings for myport project.
"""

import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECURITY
# ========================

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    "aertefact.up.railway.app",
    ".railway.app",
    "localhost",
    "127.0.0.1",
]

# Railway / Proxy HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG


# ========================
# APPLICATIONS
# ========================

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',

# ESSENCIAL
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
# ========================
# MIDDLEWARE
# ========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'core.middleware.UserRoleMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
]


ROOT_URLCONF = 'config.urls'


# ========================
# TEMPLATES
# ========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# ========================
# DATABASE
# ========================

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("🚨 DATABASE_URL não configurada no Railway")

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# ========================
# PASSWORD VALIDATION
# ========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# INTERNATIONALIZATION
# ========================

LANGUAGE_CODE = 'pt-br'

LANGUAGES = [
    ('pt-br', 'Português (Brasil)'),
    ('en', 'English'),
    ('es', 'Español'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_TZ = False


# ========================
# STATIC FILES
# ========================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ========================
# MEDIA FILES
# ========================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ========================
# DEFAULT PK
# ========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ========================
# AUTH
# ========================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/novidades/'  # What's New is the HUB's home/entry point
LOGOUT_REDIRECT_URL = '/login/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
            'key': ''
        }
    }
}


# ========================
# CSRF (CORRIGIDO)
# ========================

CSRF_TRUSTED_ORIGINS = [
    "https://aertefact.up.railway.app",
]


# ========================
# SESSION & SECURITY
# ========================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 7  # 7 dias

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


# ========================
# EMAIL (Railway env vars — same convention as DATABASE_URL / GOOGLE_OAUTH_*)
# ========================
# In DEBUG with no SMTP host configured, fall back to the console backend so local
# development/testing never needs real credentials — emails just print to stdout.
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')

if os.environ.get('EMAIL_BACKEND'):
    EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
elif EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'AE Knowledge Hub <no-reply@artefact.com>')

# Absolute base URL used to build links inside emails (relative URLs don't work in email clients).
SITE_URL = os.environ.get('SITE_URL', 'https://aertefact.up.railway.app')


# ========================
# NEWSLETTER — "What's New" (see docs/newsletter_setup.md)
# ========================
NEWSLETTER_PERIOD_DAYS = int(os.environ.get('NEWSLETTER_PERIOD_DAYS', '15'))

# Phase 1 safety switch. While True, the newsletter ONLY goes to NEWSLETTER_TEST_RECIPIENTS,
# no matter how many people exist in AllowedEmail. Once Raissa approves the design, set
# NEWSLETTER_TEST_MODE=False in Railway and it automatically switches to every email in
# AllowedEmail — no code change needed.
NEWSLETTER_TEST_MODE = os.environ.get('NEWSLETTER_TEST_MODE', 'True') == 'True'
NEWSLETTER_TEST_RECIPIENTS = [
    e.strip() for e in os.environ.get('NEWSLETTER_TEST_RECIPIENTS', 'raissa.azevedo@artefact.com').split(',')
    if e.strip()
]