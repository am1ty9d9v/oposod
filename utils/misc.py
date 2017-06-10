import random
import string
import threading
import time
from shlex import split as shlex_split
from subprocess import call, check_output
from urllib import urlencode

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.shortcuts import get_object_or_404
from httplib2 import Http
from os import path
from re import sub as resub

from django_facebook.models import FacebookProfile
from oposod.settings import EMAIL_HOST_USER
from users.models import PrivacySettings, DailyPhoto


def image_resize(image_path, new_size, maintain_ratio=False):
    save_dir = path.dirname(image_path)
    new_filename = '%s_%s' % (path.basename(image_path), new_size)
    resize_command = ['convert', "%s" % image_path]
    if not maintain_ratio:
        comm_args = '-resize "%s^" -gravity center  -extent %s "%s/%s"' \
                    % (new_size, new_size, save_dir, new_filename)
    else:
        image_size = check_output(['identify', "%s" % image_path])
        image_size = resub(r'.* ([0-9]+x[0-9]+) .*\n', r'\1', image_size)
        old_x, old_y = image_size.split('x')
        new_x, new_y = new_size.split('x')
        new_y = int((float(old_y) / float(old_x)) * float(new_x))
        new_size = "%sx%d" % (new_x, new_y)
        new_filename = '%s_%s' % (path.basename(image_path), new_x)

        comm_args = '-resize %s^ -gravity center  -extent %s "%s/%s"' \
                    % (new_size, new_size, save_dir, new_filename)

    resize_command.extend(shlex_split(comm_args))
    call(resize_command)


def activation_key_generator(size, chars=string.ascii_uppercase + string.digits):
    """
        It will take two arguments, one is length of the random string generaed
        and the other is the set of characters from which the string has to be
        generated and return the random string.
    """
    return ''.join(random.choice(chars) for x in range(size))


class EmailThread(threading.Thread):
    """
    This class is used to send the emails asynchronously
    to the registered users.
    """

    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, EMAIL_HOST_USER, self.recipient_list)
        msg.content_subtype = "html"
        msg.send()


def send_html_mail(subject, html_content, recipient_list):
    EmailThread(subject, html_content, recipient_list).start()


def save_progressive_image(photo, is_daily_photo=True):
    orig_photo_path = "%s/%s" % (settings.MEDIA_ROOT, photo)
    new_photo = "%s_prs.jpg" % str(photo).split('.')[0]
    new_photo_path = "%s/%s" % (settings.MEDIA_ROOT, new_photo)
    print "photo: ", photo
    print "new photo: ", new_photo
    print "orig_photo_path: ", orig_photo_path

    # TODO: Change the max res of both daily_photo and cover_photo
    if is_daily_photo:
        convert_command = "convert -resize '1280x720>' -interlace Plane %s %s" % (
            orig_photo_path, new_photo_path)
    else:
        convert_command = "convert -resize '1280x720>' -interlace Plane %s %s" % (
            orig_photo_path, new_photo_path)

    try:
        call(shlex_split(convert_command))
    except:
        return photo
    return new_photo


def share_photos(request, new_photo_id):
    time.sleep(30)
    user_obj = request.user
    try:
        ps_obj = get_object_or_404(PrivacySettings, user=user_obj)
        if ps_obj.is_sharing_of_photos_on_fb == "Y":
            fb_profile_obj = get_object_or_404(FacebookProfile, user=user_obj)
            access_token = fb_profile_obj.access_token
            facebook_id = fb_profile_obj.facebook_id
            facebook_url = "https://graph.facebook.com/%s/feed" % facebook_id
            share_url = "%s/%s/daily-photo/%s" % (
                settings.SITE, request.user.username,
                get_object_or_404(DailyPhoto, id=new_photo_id).key)

            h = Http()
            data = dict(access_token=access_token, link=share_url)
            resp, content = h.request(facebook_url, "POST", urlencode(data))
            print "Resp", resp
            print "Content", content

    except Exception, e:
        print 'There is error in posting this photo. %s' % e
