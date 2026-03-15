import os
import sys
from pathlib import Path
from decouple import config
import dj_database_url

# === CORREÇÃO PARA PYTHON 3.13 (audioop) ===
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
        sys.modules["audioop"] = audioop
    except ImportError:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-key')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,.railway.app').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'separator',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Sempre o primeiro
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'audio_project.urls'

# === BLOCO REESTABELECIDO (Resolve o erro admin.E403) ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'audio_project.wsgi.application'

# === BANCO DE DADOS (Correção TCP_AOFAILURE) ===
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# === CORS & SEGURANÇA ===
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    'https://audio-splitter-frontend.vercel.app',
    'https://*.railway.app'
]

# === ARQUIVOS ESTÁTICOS E MÍDIA ===
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# === LIMITES E PROXY ===
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# === CELERY & REDIS ===
# Pega a URL do Redis das variáveis de ambiente do Railway
redis_url = config('REDIS_URL', default=None)

if redis_url:
    # Garante que o Celery use a URL capturada
    CELERY_BROKER_URL = redis_url
    CELERY_RESULT_BACKEND = redis_url
else:
    # Opcional: Caso o Redis não esteja configurado (evita que o app quebre no build)
    CELERY_BROKER_URL = None
    CELERY_RESULT_BACKEND = None
    
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'