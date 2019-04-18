from .common import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4s_sh77)gl1^b!(ag#*ug2se6mx=v1=s8+sqt(7shcvhugf4b-'


# Debug mode
DEBUG = True


# Allowed hosts
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}


# Static and media files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    STATIC_PATH,
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Email
EMAIL_FROM = 'info@hasker.ru'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
