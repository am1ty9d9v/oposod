from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

if not settings.DEBUG:
    class StaticStorage(S3BotoStorage):
        location = settings.STATICFILES_LOCATION

if not settings.DEBUG:
    class MediaStorage(S3BotoStorage):
        location = settings.MEDIAFILES_LOCATION
