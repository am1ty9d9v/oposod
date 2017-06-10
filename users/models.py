import os
import uuid
import random

from django.contrib.auth.models import User
from django.db import models
from djorm_expressions.models import ExpressionManager
from djorm_pgarray.fields import ArrayField
from image_cropping.fields import ImageRatioField, ImageCropField

from django.conf import settings


class Profile(models.Model):
    user = models.ForeignKey(User)
    sex = models.CharField(max_length=1)
    dob = models.DateField(null=True)
    city = models.CharField(max_length=99, null=True)
    country = models.CharField(max_length=99, null=True)
    description = models.CharField(max_length=255, null=True)
    last_edited_on = models.DateTimeField(null=True)


class Status(models.Model):
    user = models.ForeignKey(User)
    status = models.TextField()
    written_on = models.DateTimeField(auto_now_add=True)


class ProfilePhoto(models.Model):
    user = models.ForeignKey(User, null=True)
    profile_photo = ImageCropField(upload_to='profile_photo/')
    cropping = ImageRatioField('profile_photo', '220x196')
    uploaded_on = models.DateTimeField(null=True)
    is_set = models.BooleanField(default=False)
    key = models.CharField(max_length=90)

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                ProfilePhoto.objects.get(key=key)
            except:
                return key

    class Meta:
        app_label = 'users'


class CoverPhoto(models.Model):
    user = models.ForeignKey(User)
    cover_photo_path = models.TextField()

    def get_upload_path(self, filename):
        try:
            ext = filename.rsplit('.', -1)[-1]
        except:
            ext = 'jpg'
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join(self.cover_photo_path, filename)

    cover_photo = models.ImageField(upload_to=get_upload_path)
    uploaded_on = models.DateTimeField()
    key = models.CharField(max_length=90)

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                CoverPhoto.objects.get(key=key)
            except:
                return key


class DailyPhoto(models.Model):
    user = models.ForeignKey(User)
    photo_path = models.TextField()

    def get_upload_path(self, filename):
        try:
            ext = filename.split('.')[-1]
        except:
            ext = 'jpg'
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join(self.photo_path, filename)

    photo = models.ImageField(upload_to=get_upload_path)
    moods = models.CharField(max_length=20, null=True)
    heading = models.TextField(null=True)
    story = models.TextField(null=True)
    no_of_views = models.CharField(max_length=255)
    uploaded_on = models.DateField(null=True)
    is_public = models.BooleanField(default=False)
    key = models.CharField(max_length=90)

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                DailyPhoto.objects.get(key=key)
            except:
                return key

    def get_absolute_url(self):
        return "%s/%s" % (settings.MEDIA_ROOT, self.photo_path)

    def __unicode__(self):
        return unicode(self.photo_path)

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.photo.storage, self.photo.path
        # Delete the model before the file
        super(DailyPhoto, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)


class OnePhoto(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    daily_photo = models.OneToOneField(DailyPhoto)


class Likes(models.Model):
    user = models.ForeignKey(User)
    daily_photo = models.ForeignKey(DailyPhoto)
    rating = models.PositiveSmallIntegerField(default=0)


class Shares(models.Model):
    user = models.ForeignKey(User)
    daily_photo = models.ForeignKey(DailyPhoto)

    def avg_like_rating(self):
        self.likes_set.a


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='friendrequest_sender')
    recipient = models.ForeignKey(User, related_name='friendrequest_recipient')
    is_accepted = models.BooleanField(default=False)


class Friends(models.Model):
    user = models.ForeignKey(User)
    list_of = ArrayField(dbtype='int')
    objects = ExpressionManager()


class Comments(models.Model):
    user = models.ForeignKey(User)
    dailyphoto = models.ForeignKey(DailyPhoto)
    comment = models.TextField()
    commented_on = models.DateTimeField(auto_now_add=True)


class CommentsByUser(models.Model):
    comments = models.ForeignKey(Comments)
    user = models.ForeignKey(User)


class Notifications(models.Model):
    user = models.ForeignKey(User)
    daily_photo = models.ForeignKey(DailyPhoto)
    is_viewed = models.BooleanField(default=False)
    comments = models.ForeignKey(Comments, null=True)
    likes = models.ForeignKey(Likes, null=True)
    friend_request = models.ForeignKey(FriendRequest, null=True)
    time_of = models.DateTimeField(auto_now_add=True)


class PrivacySettings(models.Model):
    user = models.OneToOneField(User)
    friends_visibility = models.CharField(max_length=1, default='F')
    cover_photos_visibility = models.CharField(max_length=1, default='A')
    profile_photos_visibility = models.CharField(max_length=1, default='F')
    daily_photos_visibility = models.CharField(max_length=1, default='F')
    stories_visibility = models.CharField(max_length=1, default='F')
    calendar_visibility = models.CharField(max_length=1, default='F')
    who_can_comment_on_photos = models.CharField(max_length=1, default='F')
    who_can_like_photos = models.CharField(max_length=1, default='F')
    is_sharing_of_photos_on_fb = models.CharField(max_length=1, default='N')


class Testimonials(models.Model):
    user = models.ForeignKey(User, related_name='testimonials_user')
    author = models.ForeignKey(User, related_name='testimonials_author')
    testimonial = models.TextField()
    written_on = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=90)

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                Testimonials.objects.get(key=key)
            except:
                return key


class FeedView(models.Model):
    user = models.ForeignKey(User)
    view = models.CharField(max_length=4)
