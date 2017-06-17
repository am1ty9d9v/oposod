from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

if not settings.DEBUG:
    class StaticStorage(S3BotoStorage):
        location = settings.STATICFILES_LOCATION


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION

    def _normalize_name(self, name):
        return settings.MEDIAFILES_LOCATION + "/" + name
