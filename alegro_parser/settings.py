import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / 'Docker' / '.env')

SECRET_KEY = os.getenv("SECRET_KEY")
SCRAPPINGDOG_API_KEY = os.getenv("SCRAPPINGDOG_API_KEY")
CONCURRENT_REQUESTS = os.getenv("CONCURRENT_REQUESTS")

EXPOERTED_FILE_BASE_PATH = BASE_DIR / 'exports'

DEBUG = os.getenv("DEBUG", default=False) in ('true', 'True', 'TRUE')

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',

    'core_app',

    'django_celery_beat',
    'admin_reorder',
    'rangefilter',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'alegro_parser.urls'

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
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'alegro_parser.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": os.getenv("DATABASE_NAME", default=BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DATABASE_USER", default=""),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", default=""),
        "HOST": os.getenv("DATABASE_HOST", default="localhost"),
        "PORT": os.getenv("DATABASE_PORT", default="5432"),
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_WORKER_HEARTBEAT = 120

ADMIN_REORDER = (
    # Довідник
    {'app': 'core_app', 'label': 'Довідник',
     'models': (
         'core_app.Brand',
         'core_app.Model',
         'core_app.PartGroup',
         'core_app.Part',
         'core_app.Translation',
     )},
    # Парсинг
    {'app': 'core_app', 'label': 'Парсинг',
     'models': (
         'core_app.ParsingLink',
         'core_app.ParsingTask',
         {'model': 'core_app.ApiToken', 'label': "Scrapping Service"},
         'core_app.Advertisement',
     )},
    # Експорт
    {'app': 'core_app', 'label': 'Експорт',
     'models': (
         'core_app.ExportCSV',
         'core_app.ExportFile',
         'core_app.ExportedFile',
     )},
    # Django Auth
    {'app': 'auth', 'label': 'Authentication and Authorization',
     'models': (
         'auth.User',
         'auth.Group',
     )},
    # Django Celery Beat
    {'app': 'django_celery_beat', 'label': 'Periodic Tasks',
     'models': (
         'django_celery_beat.PeriodicTask',
         'django_celery_beat.IntervalSchedule',
         'django_celery_beat.CrontabSchedule',
             'django_celery_beat.ClockedSchedule',
     )},
)
