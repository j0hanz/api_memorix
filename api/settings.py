"""Django settings."""

import os
from pathlib import Path

import cloudinary
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = 'DEV' in os.environ
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.herokuapp.com',
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.herokuapp.com',
    'http://localhost:5173',
]

# CORS
CORS_ALLOWED_ORIGINS = [
    'https://*.herokuapp.com',
    'http://localhost:5173',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'dj_rest_auth.registration',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'

# Database configuration
if 'DEV' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'CONN_MAX_AGE': 60,
        }
    }
    print('Development environment')
else:
    DATABASES = {'default': dj_database_url.parse(os.getenv('DATABASE_URL'))}
    DATABASES['default']['CONN_MAX_AGE'] = 60
    print('Production environment')

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_KEY'),
    api_secret=os.getenv('CLOUDINARY_SECRET'),
    secure=True,
)

# Authentication & REST Framework
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'memorix-access-token',
    'JWT_AUTH_REFRESH_COOKIE': 'memorix-refresh-token',
    'USER_DETAILS_SERIALIZER': 'api.serializers.CurrentUserSerializer',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ]
}

# Site configuration
SITE_ID = 1

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# Static
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
