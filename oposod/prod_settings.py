import os
DEBUG = False
AWS_HOST_NAME = 's3.ap-south-1.amazonaws.com'
AWS_STORAGE_BUCKET_NAME = 'oposod-prod'
AWS_ACCESS_KEY_ID = os.getenv("AWSAccessKeyId")
AWS_SECRET_ACCESS_KEY = os.getenv("AWSSecretKey")

# Tell django-storages that when coming up with the URL for an item in S3 storage, keep
# it simple - just use this domain plus the path. (If this isn't set, things get complicated).
# This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
# We also use it in the next setting.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
# This is used by the `static` template tag from `static`, if you're using that. Or if anything else
# refers directly to STATIC_URL. So it's safest to always set it.
STATIC_URL = "http://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

# Tell the staticfiles app to use S3Boto storage when writing the collected static files (when
# you run `collectstatic`).
MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "http://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("db_name"),
        'USER': os.getenv("db_user"),
        'PASSWORD': os.getenv("db_password"),
        'HOST': os.getenv("db_host"),
        'PORT': os.getenv("db_port"),
    }
}

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
