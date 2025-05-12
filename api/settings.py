"""Django settings."""

import os
from datetime import timedelta
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
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://[^.]+\.herokuapp\.com$',
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# Application definition
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
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'dj_rest_auth.registration',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'users',
    'memorix',
]

SITE_ID = 1

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
    'allauth.account.middleware.AccountMiddleware',
]

# URL configuration
ROOT_URLCONF = 'api.urls'
WSGI_APPLICATION = 'api.wsgi.application'

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Authentication settings
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

# Disable email verification
ACCOUNT_EMAIL_VERIFICATION = 'none'

# REST Framework configuration
# https://www.django-rest-framework.org/api-guide/settings/#settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# Rest Auth configuration
# https://django-rest-auth.readthedocs.io/en/latest/index.html
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'USER_DETAILS_SERIALIZER': 'api.serializers.CurrentUserSerializer',
}

# JWT settings for REST Auth
REST_AUTH_SERIALIZERS = {
    'JWT_SERIALIZER': 'api.serializers.PublicJWTSerializer',
}

# JWT settings
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/index.html
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'BLACKLIST_AFTER_ROTATION': True,
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_KEY'),
    api_secret=os.getenv('CLOUDINARY_SECRET'),
    secure=True,
)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
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
        'level': 'INFO',
    },
}
