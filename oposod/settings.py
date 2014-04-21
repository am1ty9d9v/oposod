# Django settings for oposod project.

import os
import socket
#########################################################################
# FACEBOOK LOGIN Settings


BASEDIR = os.path.abspath(os.path.dirname(__file__))


RANDOM_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdegfhijklmnopqrstuvwxyz1234567890'


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    "utils.custom_context_processors.new_friend_request_count",
    'utils.custom_context_processors.settings_variable',
    'utils.custom_context_processors.friends_list',
    'django_facebook.context_processors.facebook',
    'django.core.context_processors.tz',
)
TEMPLATE_DEBUG = DEBUG

IMAGE_SIZE_DAILY_PHOTO = ['200x160', '100x100']
IMAGE_SIZE_PROFILE_PHOTO = ['25x25', '40x40', '170x170', '100x100']
IMAGE_SIZE_COVER_PHOTO = ['']

RESCTRICTED_WORDS = ['home', 'user', 'users', 'homes', 'settings', 'setting',
                     'time', 'money', 'whore', 'porn', 'sex', 'edit',
                     'profile', 'calendars', 'calendar', 'stories', 'story',
                     'signin', 'login', 'signout', 'logout', 'upload', 'video',
                     'photo', 'images', 'photos', 'image', 'oposod', 'browse',
                     'privacy', 'facebook', 'twitter', 'plus', 'admin', 'tit',
                     'request', 'accept', 'cancel', 'reject', 'connect',
                     'disconnect', 'help', 'static', 'media', 'fuck', 'vagina',
                     'penis', 'boobs', 'boob', 'tits', 'breast', 'google']
ADMINS = (
    ('Gurpreet Singh', 'gurpreet.singh@bquobe.com'),
    ('Amit Yadav', 'amityadav@amityadav.in')
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'oposod',
        'USER': 'amit',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Kolkata'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASEDIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qo@@oe(lc_#96asn#!_pzlium(3qzsu4yt=h*rdda8q4g+5x$('

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'oposod.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'oposod.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASEDIR, 'templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    'haystack',

    'bootstrap_toolkit',
    'users',
    'accounts',
    'home',
    'image_cropping',
    'easy_thumbnails',
    'django_extensions',
    'djorm_pgarray',
    'djorm_expressions',
    'django_facebook',
    'open_facebook',

)

from easy_thumbnails.conf import settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS
import django.template
django.template.add_to_builtins('django.templatetags.future')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
