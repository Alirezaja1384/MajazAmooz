"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
from collections import OrderedDict
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS',
                       default='127.0.0.1, localhost').replace(' ', '').split(',')

INTERNAL_IPS = config('INTERNAL_IPS',
                      default='127.0.0.1, localhost').replace(' ', '').split(',')

# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'django_bleach',
    'debug_toolbar',
    'django_filters',
    'django_tables2',
    'crispy_forms',
    'tinymce',
    'django_resized',
    'constance',

    # Project apps
    'authentication.apps.AuthenticationConfig',
    'learning.apps.LearningConfig',
    'ajax.apps.AjaxConfig',
    'user.apps.UserConfig',
    'utilities'
]

MIDDLEWARE = [

    # Include the Debug Toolbar middleware as early as possible
    # in the list. However, it must come after any other middleware
    # that encodes the response’s content, such as GZipMiddleware.
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middlewares
    'utilities.middleware.LoginRequiredMiddleware',
    'utilities.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DEFAULT_DATABASE_ENGINE',
                         default='django.db.backends.postgresql_psycopg2'),

        'NAME': config('DEFAULT_DATABASE_NAME', default='MajazAmooz'),
        'USER': config('DEFAULT_DATABASE_USER', default='postgres'),
        'PASSWORD': config('DEFAULT_DATABASE_PASSWORD', default='postgres'),
        'HOST': config('DEFAULT_DATABASE_HOST', default='127.0.0.1'),
        'PORT': config('DEFAULT_DATABASE_PORT', default=5432),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'fa'

TIME_ZONE = 'UTC'

# Used in TimezoneMiddleware
DEFAULT_USER_TZ = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
# Other configurations in production.py/development.py
STATIC_URL = '/static/'
MEDIA_URL = '/media/'


# Custom uSer model
AUTH_USER_MODEL = 'authentication.User'
# Default auto-created primary keys type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND',
                       default='django.core.mail.backends.console.EmailBackend')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=None)
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)


# django-bleach settings
# https://django-bleach.readthedocs.io/en/latest/settings.html

BLEACH_ALLOWED_TAGS = [
    'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'sup',
    'sub', 'code', 'table', 'tbody', 'tr', 'th', 'td'
]

BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style', 'src']

BLEACH_ALLOWED_STYLES = [
    'font-family', 'font-weight', 'font-size', 'font-variant',
    'text-decoration', 'color', 'background-color', 'direction',
    'text-align',
]

BLEACH_ALLOWED_PROTOCOLS = ['http', 'https']

# Strip unknown tags if True, replace with HTML escaped characters if False
BLEACH_STRIP_TAGS = True

# Strip HTML comments, or leave them in.
BLEACH_STRIP_COMMENTS = False

# Deafult form widget
BLEACH_DEFAULT_WIDGET = 'tinymce.widgets.TinyMCE'


# Login url
# https://docs.djangoproject.com/en/3.2/ref/settings/#login-url

LOGIN_URL = '/auth/login'

# Logout required url for LogoutRequiredMixin
LOGOUT_REQUIRED_URL = '/auth/logout_required'

# Login required by url pattern
# Used for LoginRequiredMiddleware
LOGIN_REQUIRED_URLS = [
    r'^/user/(.*)$'
]

# Logging configuration
# https://docs.djangoproject.com/en/3.2/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(pathname)s %(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
        },
        'verbose_console': {
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'file_json': {
            'level': 'WARNING',
            'formatter': 'json',
            'class': 'logging.FileHandler',
            'filename': config('LOGGING_FILE_NAME', 'logs.log'),
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file_json'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'file_json'],
            'level': 'INFO',
            'propagate': False,
        },
        'emails': {
            'handlers': ['verbose_console', 'file_json'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}


# django-crispy-forms settings
# https://django-crispy-forms.readthedocs.io/en/latest/
CRISPY_TEMPLATE_PACK = 'bootstrap4'


# django-tinymce settings
# https://django-tinymce.readthedocs.io/en/latest/
TINYMCE_JS_ROOT = 'js/tinymce/'
TINYMCE_JS_URL = os.path.join(STATIC_URL, 'js/tinymce/tinymce.min.js')

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'silver',
    'height': 500,
    'menubar': False,
    'plugins': 'link print preview searchreplace code fullscreen table wordcount',
    'toolbar': 'undo redo | forecolor | bold italic | alignleft aligncenter \
    alignright alignjustify | bold italic underline strikethrough \
    | fontselect fontsizeselect formatselect | table code searchreplace | preview fullscreen',
}

# django_tables2 settings
# https://django-tables2.readthedocs.io/en/latest/
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap4.html'


# django-resized settings
# https://github.com/un1t/django-resized
DJANGORESIZED_DEFAULT_SIZE = [960, 540]
DJANGORESIZED_DEFAULT_QUALITY = 72
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

# django-constance settings
# https://django-constance.readthedocs.io/en/latest/
CONSTANCE_BACKEND = 'constance.backends.redisd.RedisBackend'
CONSTANCE_REDIS_PREFIX = 'constance:majazamooz:'
CONSTANCE_REDIS_CONNECTION = config('CONSTANCE_REDIS_CONNECTION')

CONSTANCE_CONFIG = OrderedDict([

    # Website settings
    ('WEBSITE_KEYWORDS', (
        'آموزش,درسنامه,آزمون,آموزش مجازی,آزمون آنلاین',
        'وبسایت - کلمات کلیدی', str),
     ),

    ('WEBSITE_DESCRIPTION', (
        ('با هم مجازی می آموزیم! مجاز آموز، جامعه ای از دانش آموزان سراسر ایران است که با استفاده'
         ' از فضای آنلاین در هر مکان و زمان به آموزش دسترسی دارند و به یکدیگر آموزش می دهند.'),
        'وبسایت - توضیحات', str),
     ),

    # Learning
    ('LEARNING_TUTORIAL_ARCHIVE_PAGINATE_BY',
     (30, 'آرشیو آموزش ها - تعداد آموزش هر صفحه', int),),

    # User panel
    ('USER_PANEL_PAGINATE_BY', (15, 'پنل کاربری - تعداد آیتم هر صفحه', int),),
    ('USER_PANEL_STATISTICS_LAST_MONTH_COUNT',
     (5, 'پنل کاربری - تعداد ماه های اخیر آمار', int),),

    # Tutorial relations
    ('TUTORIAL_LIKE_SCORE', (5, 'آموزش - امتباز لایک', int),),
    ('TUTORIAL_LIKE_COIN', (5, 'آموزش - سکه لایک', int),),
    ('TUTORIAL_VIEW_SCORE', (1, 'آموزش - امتباز بازدید کاربران', int),),
    ('TUTORIAL_VIEW_COIN', (1, 'آموزش - سکه بازدید کاربران', int),),
    ('TUTORIAL_UPVOTE_SCORE', (0, 'آموزش - امتباز رای موافق', int),),
    ('TUTORIAL_UPVOTE_COIN', (0, 'آموزش - سکه رای موافق', int),),
    ('TUTORIAL_DOWNVOTE_SCORE', (0, 'آموزش - امتباز رای مخالف', int),),
    ('TUTORIAL_DOWNVOTE_COIN', (0, 'آموزش - سکه رای مخالف', int),),

    # Tutorial comment relations
    ('TUTORIAL_COMMENT_LIKE_SCORE', (3, 'دیدگاه آموزش - امتباز لایک', int),),
    ('TUTORIAL_COMMENT_LIKE_COIN', (3, 'دیدگاه آموزش - سکه لایک', int),),
    ('TUTORIAL_COMMENT_UPVOTE_SCORE', (0, 'دیدگاه آموزش - امتباز رای موافق', int),),
    ('TUTORIAL_COMMENT_UPVOTE_COIN', (0, 'دیدگاه آموزش - سکه رای موافق', int),),
    ('TUTORIAL_COMMENT_DOWNVOTE_SCORE', (0, 'دیدگاه آموزش - امتباز رای مخالف', int),),
    ('TUTORIAL_COMMENT_DOWNVOTE_COIN', (0, 'دیدگاه آموزش - سکه رای مخالف', int),),

])
