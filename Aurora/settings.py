"""
Django settings for Aurora project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's5)xkjl25k5j7a0fn%a=6jv38oid_srpn^(3wo@uv1+s2ml!9h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Tell the toolbar not to adjust your settings automatically
DEBUG_TOOLBAR_PATCH_SETTINGS = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Social Authentication app
    #'social.apps.django_app.default',
    # Widget Tweaks
    'widget_tweaks',
    # Debug toolbar
    #'debug_toolbar',
    # Aurora main application
    'sdn',
)

MIDDLEWARE_CLASSES = (
    # Django defaults
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Debug toolbar
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1')

ROOT_URLCONF = 'Aurora.urls'

WSGI_APPLICATION = 'Aurora.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'aurora',
#         'USER': 'aurora',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '',
#         'OPTIONS': {
#                "init_command": "SET storage_engine=INNODB",
#         }
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aurora',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/Aurora/static/'

MEDIA_ROOT = '/var/www/Aurora/sdn/'

AUTHENTICATION_BACKENDS = (
    #'social.backends.open_id.OpenIdAuth',
    #'social.backends.google.GoogleOpenId',
    #'social.backends.google.GoogleOAuth2',
    #'social.backends.google.GooglePlusAuth',
    #'social.backends.google.GoogleOAuth',
    #'social.backends.twitter.TwitterOAuth',
    #'social.backends.yahoo.YahooOpenId',

    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    # Social auth
    #'social.apps.django_app.context_processors.backends',
    #'social.apps.django_app.context_processors.login_redirect',
)


# URL to redirect user to login
LOGIN_URL = '/Aurora/accounts/login/'
LOGIN_REDIRECT_URL = '/Aurora/'
LOGIN_ERROR_URL = '/Aurora/accounts/login-error/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/www/Aurora/logs/main.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'sdn': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d ' +
                '%(thread)d: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'aurora_cache',
        #'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': 'unix:/tmp/memcached.sock',
        #'LOCATION': '127.0.0.1:11211',
    }
}

# SDN Controller IP address
# Network reachable IP address (usually not 127.0.0.1) so other switches can connect remotelly to your controller
SDN_CONTROLLER = {
    'type': 'floodlight',
    'ip': '10.0.0.1',
    'transport': 'tcp',
}

# Override default settings locally
try:
    from local_settings import *
except ImportError as e:
    pass

