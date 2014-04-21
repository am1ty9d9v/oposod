from django.contrib.auth.models import User
#from django.shortcuts import get_object_or_404
from users.models import FriendRequest
from oposod import settings


def new_friend_request_count(request):
    new_friend_request_count = None
    if request.user.is_authenticated():
        user_obj = request.user
        fr_obj = FriendRequest.objects.filter(recipient=user_obj,
                                              is_accepted=False).count()
        if fr_obj:
            new_friend_request_count = fr_obj
    return {
        'new_friend_request_count': new_friend_request_count,
    }


def settings_variable(request):
    return {
        'SITE': settings.SITE,
    }


def friends_list(request):
    user_obj = request.user
    friends_list = []
    try:
        if user_obj.friends_set.get() != []:
            friends_list = [User.objects.get(id=i).username for i in
                            user_obj.friends_set.get().list_of]
    except:
        pass

    friends_list.append(request.user.username)

    return {
        'friends_list': friends_list,
    }
