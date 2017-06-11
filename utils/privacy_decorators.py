from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from users.models import PrivacySettings, Friends


def visibility_of_daily_photos(function):
    def wrapper(request, *args, **kwargs):
        user_from_url = get_object_or_404(User, username=kwargs['username'])

        if request.user.is_authenticated():
            logged_in_user = request.user
        else:
            logged_in_user = None

        ps_obj_for_user_from_url = get_object_or_404(PrivacySettings, user=user_from_url)

        if ps_obj_for_user_from_url.daily_photos_visibility == 'N':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('/403')

        if ps_obj_for_user_from_url.daily_photos_visibility == 'A':
            return function(request, *args, **kwargs)

        if ps_obj_for_user_from_url.daily_photos_visibility == 'F':

            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:

                    if int(logged_in_user.id) in get_object_or_404(Friends, user=user_from_url).list_of:
                        return function(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('/403')

    return wrapper


def visibility_of_friends(function):
    def wrapper(request, *args, **kwargs):

        user_from_url = get_object_or_404(User, username=kwargs['username'])

        if request.user.is_authenticated():
            logged_in_user = request.user
        else:
            logged_in_user = None

        ps_obj_for_user_from_url = get_object_or_404(PrivacySettings, user=user_from_url)

        if ps_obj_for_user_from_url.friends_visibility == 'N':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('/403')

        if ps_obj_for_user_from_url.friends_visibility == 'A':
            return function(request, *args, **kwargs)

        if ps_obj_for_user_from_url.friends_visibility == 'F':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:

                    if int(logged_in_user.id) in get_object_or_404(Friends, user=user_from_url).list_of:
                        return function(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('/403')

    return wrapper


def visibility_of_stories(function):
    def wrapper(request, *args, **kwargs):

        user_from_url = get_object_or_404(User, username=kwargs['username'])

        if request.user.is_authenticated():
            logged_in_user = request.user
        else:
            logged_in_user = None

        ps_obj_for_user_from_url = get_object_or_404(PrivacySettings, user=user_from_url)

        if ps_obj_for_user_from_url.stories_visibility == 'N':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('/403')

        if ps_obj_for_user_from_url.stories_visibility == 'A':
            return function(request, *args, **kwargs)

        if ps_obj_for_user_from_url.stories_visibility == 'F':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:

                    if int(logged_in_user.id) in get_object_or_404(Friends, user=user_from_url).list_of:
                        return function(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('/403')

    return wrapper


def visibility_of_calendar(function):
    def wrapper(request, *args, **kwargs):

        user_from_url = get_object_or_404(User, username=kwargs['username'])

        if request.user.is_authenticated():
            logged_in_user = request.user
        else:
            logged_in_user = None

        ps_obj_for_user_from_url = get_object_or_404(PrivacySettings, user=user_from_url)

        if ps_obj_for_user_from_url.calendar_visibility == 'N':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('/403')

        if ps_obj_for_user_from_url.calendar_visibility == 'A':
            return function(request, *args, **kwargs)

        if ps_obj_for_user_from_url.calendar_visibility == 'F':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:

                    if int(logged_in_user.id) in get_object_or_404(Friends, user=user_from_url).list_of:
                        return function(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('/403')

    return wrapper


def visibility_of_cover_photos(function):
    def wrapper(request, *args, **kwargs):

        user_from_url = get_object_or_404(User, username=kwargs['username'])

        if request.user.is_authenticated():
            logged_in_user = request.user
        else:
            logged_in_user = None

        ps_obj_for_user_from_url = get_object_or_404(PrivacySettings, user=user_from_url)

        if ps_obj_for_user_from_url.cover_photos_visibility == 'N':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('/403')

        if ps_obj_for_user_from_url.cover_photos_visibility == 'A':
            return function(request, *args, **kwargs)

        if ps_obj_for_user_from_url.cover_photos_visibility == 'F':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:

                    if int(logged_in_user.id) in get_object_or_404(Friends, user=user_from_url).list_of:
                        return function(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('/403')

    return wrapper


def visibility_of_profile_photos(function):
    def wrapper(request, *args, **kwargs):

        user_from_url = get_object_or_404(User, username=kwargs['username'])

        if request.user.is_authenticated():
            logged_in_user = request.user
        else:
            logged_in_user = None

        ps_obj_for_user_from_url = get_object_or_404(PrivacySettings, user=user_from_url)

        if ps_obj_for_user_from_url.profile_photos_visibility == 'N':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('/403')

        if ps_obj_for_user_from_url.profile_photos_visibility == 'A':
            return function(request, *args, **kwargs)

        if ps_obj_for_user_from_url.profile_photos_visibility == 'F':
            if not logged_in_user:
                return HttpResponseRedirect('/403')
            else:
                if logged_in_user.username == user_from_url.username:
                    return function(request, *args, **kwargs)
                else:

                    if int(logged_in_user.id) in get_object_or_404(Friends, user=user_from_url).list_of:
                        return function(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('/403')

    return wrapper
