from pathlib import Path
import os

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = None
DEBUG = True
ALLOWED_HOSTS = []

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis'
]
LOCAL_APPS = [
    "users.apps.UsersConfig",
    "regions.apps.RegionsConfig",
    "notes.apps.NotesConfig",
]
THIRD_PARTY_APPS = [
    'rest_framework_simplejwt',
    "django_celery_beat"
]
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DATABASE"),
        "USER": os.getenv("POSTGRES_USERNAME"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://default:{os.getenv('REDIS_PASSWORD')}@redis:{os.getenv('REDIS_PORT_NUMBER')}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "sedreh"
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ADMINS = [
    ('Hossein Shayesteh', 'shayestehhs1@gmail.com'),
    # ('Sedreh', 'info@sedreh.ir')
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': "CRITICAL",
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file_request': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / "logs" / 'debug_request.log',
        },
        'file_django': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / "logs" / 'debug_django.log',
        },
        'file_cache_tools': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / "logs" / 'cache_tools.log',
        },
        'file_celery': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / "logs" / 'debug_celery.log',
            'formatter': 'standard',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', "file_django", "mail_admins"],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file_request'],
            'propagate': False,
        },
        'celery_tasks': {
            'handlers': ['console', "file_celery"],
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file_cache_tools', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

CELERY_BEAT_SCHEDULE = {
    "get_new_images": {
        "task": "regions.tasks.get_new_images",
        "schedule": crontab(day_of_week="fri", hour="3", minute="30"),
    },
}

MAXIMUM_DOWNLOAD_IMAGE_PER_TASK = 3
