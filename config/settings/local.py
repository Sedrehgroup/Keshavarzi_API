import os

from config.settings.base import *

DEBUG = True
SECRET_KEY = 'django-insecure-b7hk#h553q$c72$#1zuyp=l1(o$($r#3+kpo69&6h!vjig$4w5'
ALLOWED_HOSTS = ['95.216.55.238']

CELERY_BROKER_URL = "amqp://rabbitmq"
INSTALLED_APPS.append('rest_framework')

GEOSERVER = {
    'HOST': 'geoserver',
    'IP': 'localhost',
    'USERNAME': 'sedreh',
    'PASSWORD': 'ABcd1234!@',
    'WORKSPACE': 'zamin2',
    'NAMESPACE': 'localhost',
    'MEDIA_ROOT': 'media/geoserver/',
    'RASTER_URL': os.path.join(BASE_DIR, 'images'),
    'GEOSERVER_URL': '/opt/geoserver/data_dir',
    'PORT': 8080
}
INSTALLED_APPS += [
    # 'debug_toolbar',
]
# MIDDLEWARE.insert(0,'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = [
    "127.0.0.1:8000",
    "0.0.0.0:8000",
    "api_django"
]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Keshavarzi',
    'DESCRIPTION': 'Created by Sedreh group',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
    },
}
SWAGGER_SETTINGS = {
    'LOGIN_URL': 'token_obtain_pair',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
