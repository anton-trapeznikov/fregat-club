import json
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-tv@vubbyb#v5q=-)f*_38b_r2ht@re0#l4&!96m&85)^!rrb%o'
SESSION_COOKIE_DOMAIN = None
DEBUG = False

ALLOWED_HOSTS: tuple = ('localhost', 'fregat-club.ru', 'fregat-club.na4u.ru')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.joinpath('www/static')
STATICFILES_DIRS = (BASE_DIR.joinpath('static'), )

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.joinpath('www/media')

json_config_path = BASE_DIR.joinpath('fregat/local_settings.json')
if json_config_path.is_file():
    with open(json_config_path) as f:
        json_config = json.loads(f.read())
        for param, value in json_config.items():
            setattr(sys.modules[__name__], param, value)

if isinstance(MEDIA_ROOT, str):
    MEDIA_ROOT = Path(MEDIA_ROOT)

if isinstance(STATIC_ROOT, str):
    STATIC_ROOT = Path(STATIC_ROOT)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mdeditor',
    'compressor',
    'fregat.apps.FregatConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fregat.middleware.RedirectMiddleware',
    'fregat.middleware.FrontDataMiddleware',
]

ROOT_URLCONF = 'fregat.urls'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (BASE_DIR.joinpath('templates'), ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fregat.processors.settings_processor',
                'fregat.processors.main_menu_processor',
                'fregat.processors.canonical_processor',
                'fregat.processors.front_data_processor',
                'fregat.processors.teasers_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'fregat.wsgi.application'

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

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = 'SAMEORIGIN'

MDEDITOR_CONFIGS = {
    'default':{
        'width': '90%',
        'height': 500,
        'toolbar': [
            "bold", "del", "italic", "|", "h2", "h3", "h4", "|",
            "list-ul", "list-ol", "|",
            "link", "image", "table", "html-entities", "|",
            "help", "info",
        ],
        'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
        'image_folder': 'uploads',
        'theme': 'default',
        'preview_theme': 'default',
        'editor_theme': 'default',
        'toolbar_autofixed': True,
        'search_replace': True,
        'emoji': False,
        'tex': True,
        'flow_chart': False,
        'sequence': True,
        'watch': True,
        'lineWrapping': True,
        'lineNumbers': True,
        'language': 'en'
    }

}

COMPRESS_ENABLED = not DEBUG
COMPRESS_OUTPUT_DIR = 'compress'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]

if DEBUG:
    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        }
    }
