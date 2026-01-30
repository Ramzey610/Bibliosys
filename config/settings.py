"""
Configuration de Django pour le projet Bibliothèque
"""
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Lire la clé secrète depuis les variables d'environnement (sécurisé en production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production-xxx123456789')

# DEBUG doit être False en production; autoriser override via variable d'environnement pour tests locaux
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes')

# ALLOWED_HOSTS: si DEBUG True -> autoriser tout localement, sinon utiliser la valeur passée via ALLOWED_HOSTS (ex: ".vercel.app")
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    _allowed = os.environ.get('ALLOWED_HOSTS', '.vercel.app')
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps locales
    'accounts.apps.AccountsConfig',
    'library.apps.LibraryConfig',
    'members.apps.MembersConfig',
    'loans.apps.LoansConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise pour servir les fichiers statiques en production (simple et compatible serverless)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Configuration base de données via DATABASE_URL (PostgreSQL en production)
try:
    import dj_database_url
except Exception:
    dj_database_url = None

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and dj_database_url:
    # Connexion recommandée pour production (Postgres)
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
# Sinon, on garde la configuration SQLite pour le développement local (déclarée plus haut)

# WhiteNoise: stockage compressé en production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Auth User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'library:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Messages
MESSAGE_TAGS = {
    'DEBUG': 'debug',
    'INFO': 'info',
    'SUCCESS': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger',
}

# Pagination
PAGINATION_SIZE = 20
