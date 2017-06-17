import datetime
import mimetypes
from datetime import timedelta

import boto
from boto.s3.key import Key
from django.conf import settings


class LazyWrapper(object):
    def __init__(self, func):
        self.func = func

    def __call__(self):
        try:
            return self.value
        except AttributeError:
            self.value = self.func()
            return self.value


conn = LazyWrapper(lambda: boto.connect_s3(
    settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, **{'host': settings.AWS_HOST_NAME}))
bucket = LazyWrapper(lambda: conn().get_bucket(settings.AWS_STORAGE_BUCKET_NAME))


# Set cache declarations to 30 days.


def update_key_metadata(key):
    metadata = key.metadata
    content_type, unused = mimetypes.guess_type(key.name)

    if not content_type:
        content_type = 'text/plain'
    expires = datetime.datetime.utcnow() + timedelta(days=30)
    expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    metadata['Expires'] = expires
    metadata['Content-Type'] = content_type
    metadata['Cache-Control'] = 'max-age=%d, public' % (3600 * 24 * 30)
    key.copy(settings.AWS_STORAGE_BUCKET_NAME, key, metadata=metadata, preserve_acl=True)


def update_key_metadata_nav(k):
    key = bucket().get_key(k)
    metadata = key.metadata
    metadata["content_type"] = 'application/javascript'
    metadata['Content-Encoding'] = "gzip"
    key.copy(settings.AWS_STORAGE_BUCKET_NAME, key, metadata=metadata, preserve_acl=True)


def s3_upload_file(from_file, to_key, acl="private"):
    k = Key(bucket())
    k.key = to_key
    k.set_contents_from_filename(from_file)
    k.set_acl(acl)
    # s3_key_expires(k)
    return True


def s3_download_file(from_key, to_file):
    k = Key(bucket())
    k.key = from_key
    k.get_contents_to_filename(to_file)
    return to_file


def s3_key_lookup(key):
    key_found = bucket().lookup(key)
    return key_found if key_found else None


def s3_bucket_keys(prefix=None):
    return bucket().list(prefix=prefix)


def s3_key_expires(key):
    expires = datetime.datetime.utcnow() + timedelta(hours=12)
    expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    metadata = dict()
    metadata['Expires'] = expires
    metadata['Cache-Control'] = 'max-age=%d, public' % (3600 * 12)
    key.set_metadata('metadata', metadata)
