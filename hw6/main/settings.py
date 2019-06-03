from datetime import timedelta
import os
from pathlib import Path
import sys

from django.urls import reverse_lazy


# Project version
VERSION = '1.0.0'


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')


# Debug mode
DEBUG = os.getenv('DEBUG') == 'True'
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent.parent


# Allowed hosts
ALLOWED_HOSTS = [
    '0.0.0.0',
    '127.0.0.1',
    'localhost',
    'backend',
    'nginx',
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'django.contrib.postgres',
    'rest_framework',
    'rest_framework.authtoken',

    'api',
    'question',
    'user',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'main.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
        'OPTIONS': {
            'options': '-c search_path=public',
        },
        'TEST': {
            'NAME': os.getenv('POSTGRES_DB'),
            'CREATE_DB': False,
        }
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
AUTH_USER_MODEL = 'user.User'


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = False
USE_TZ = False
DATE_FORMAT = 'd.m.Y'
DATETIME_FORMAT = 'd.m.Y H:i:s'


# Static and media files (CSS, JavaScript, Images)
STATIC_URL = '/staticfiles/'
if DEBUG:
    STATIC_PATH = BASE_DIR.joinpath('staticfiles')
    STATIC_PATH.mkdir(exist_ok=True)
    STATICFILES_DIRS = (
        STATIC_PATH,
    )
else:
    STATIC_ROOT = BASE_DIR.joinpath('staticfiles')
    STATIC_ROOT.mkdir(exist_ok=True)

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = BASE_DIR.joinpath('mediafiles')
MEDIA_ROOT.mkdir(exist_ok=True)


# Urls
INDEX_URL = 'question_list'
LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy(INDEX_URL)


# Pagination
QUESTION_PER_PAGE = 20
ANSWER_PER_PAGE = 30
TRENDING_PER_PAGE = 20


# REST Framework
CSRF_COOKIE_NAME = 'csrftoken'
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-disposition',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    '127.0.0.1:8000',
    'localhost:8080',
    '127.0.0.1:8080',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DATETIME_FORMAT': '%d.%m.%Y %H:%M',
    'DATE_INPUT_FORMATS': ['%d.%m.%Y', 'iso-8601', '%Y-%m-%dT%H:%M:%S.%fZ'],
    # 'UPLOADED_FILES_USE_URL': False,
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(days=90),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=90),
}


# Email
EMAIL_FROM = 'info@hasker.ru'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
elif TESTING:
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/hasker-emails'
