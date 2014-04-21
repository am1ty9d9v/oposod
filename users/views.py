from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from oposod.settings import MEDIA_ROOT, IMAGE_SIZE_DAILY_PHOTO, \
  MEDIA_URL

from users.forms import EditCoverPhotoForm, EditProfilePhotoForm, \
    EditProfileForm, UploadNewStoryForm, WriteStatusForm, \
    EditPrivacyForm, WriteStoryForm, WriteTestimonialForm
from users.models import CoverPhoto, ProfilePhoto, Profile, FriendRequest, \
    Friends, DailyPhoto, Status, Comments, Likes, PrivacySettings, Testimonials
from utils import misc
from utils.privacy_decorators import visibility_of_daily_photos, \
    visibility_of_friends, visibility_of_stories,visibility_of_profile_photos, \
    visibility_of_cover_photos
from django_facebook.models import FacebookProfile
from django_facebook.decorators import facebook_required
from utils.misc import share_photos

# Python imports
from redis import StrictRedis
from re import findall, sub as resub
from time import time
import thread
import datetime
import json
import urllib2



# @login_required
def profile(request, username):
    username = username.lower()
    try:
        user_obj = get_object_or_404(User, username = username)
    except:
        user_obj = None
    if user_obj:
        name = str(user_obj.first_name.title()) + " " + str(user_obj.last_name.title())
    else:
        return HttpResponseRedirect('/404')
    try:
        cover_photo_obj = CoverPhoto.objects.filter(user = user_obj).order_by('id').reverse()[0]
    except:
        cover_photo_obj = None
    try:
        profile_photo_obj = ProfilePhoto.objects.filter(user = user_obj).order_by('id').reverse()[0]
    except:
        profile_photo_obj = None
    try:
        profile_obj = get_object_or_404(Profile, user = user_obj)
    except:
        profile_obj = None
    try:
        status_obj = Status.objects.filter(user = get_object_or_404(User, username = username)).reverse()[0]
    except:
        status_obj = None
    if request.user.is_authenticated():
        try:
            send_fr_obj = FriendRequest.objects.get(sender = request.user,
                recipient = get_object_or_404(User, username = username))

        except:
            send_fr_obj = None


        try:
            received_fr_obj = FriendRequest.objects.get(
                    sender = get_object_or_404(User, username = username),
            recipient = request.user)

        except:
            received_fr_obj = None
    else:
        send_fr_obj = None
        received_fr_obj = None
    print 'send obj', send_fr_obj
    print 'received_fr_obj', received_fr_obj
    if request.method == 'POST':
        form = WriteStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            Status.objects.create(user = request.user, status = status)
            return HttpResponseRedirect(reverse('users.views.profile', args = (request.user.username,)))
    else:
        form = WriteStatusForm()
        print form

    return render(request, 'users/profile.html', {
        'name': name,
        'username': username,
        'cover_photo_obj': cover_photo_obj,
        'profile_photo_obj': profile_photo_obj,
        'profile_obj': profile_obj,
        'send_fr_obj': send_fr_obj,
        'received_fr_obj': received_fr_obj,
        'status_obj': status_obj,
        'form': form,
        'user_obj': user_obj,
    })

@login_required
def edit_cover_photo(request):
    if request.user.is_authenticated():

        user_obj = request.user
        form = EditCoverPhotoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            choose_cover_photo = request.FILES['choose_cover_photo']

            cover_photo_obj = CoverPhoto()
            cover_photo_obj.user = user_obj
            cover_photo_obj.cover_photo = choose_cover_photo
            cover_photo_obj.cover_photo_path = 'cover_photos/%s' % user_obj.username
            cover_photo_obj.uploaded_on = datetime.datetime.now()
            cover_photo_obj.key = cover_photo_obj.key_generate
            cover_photo_obj.save()

            cover_photo_obj.cover_photo = misc.save_progressive_image(
                cover_photo_obj.cover_photo)
            cover_photo_obj.save()

            # resizing with ratio maintained.
            misc.image_resize(MEDIA_ROOT + '/' + str(cover_photo_obj.cover_photo), '280x280', maintain_ratio = True)
            return HttpResponseRedirect('/%s' % user_obj.username)

    return render(request, 'users/edit_cover_photo.html', {
        'form': form,
    })


@login_required
def edit_profile_photo(request, image_id = None):
    profile_photo_obj = get_object_or_404(ProfilePhoto, user = request.user, key = image_id) if image_id else None
    form = EditProfilePhotoForm(instance = profile_photo_obj)
    user_obj = get_object_or_404(User, username = request.user.username)

    if request.method == 'POST':
        form = EditProfilePhotoForm(request.POST, request.FILES, instance = profile_photo_obj)
        if form.is_valid():
            profile_photo_obj = form.save()
            profile_photo_obj.user = user_obj
            ProfilePhoto.objects.filter(user = request.user).update(is_set = False)
            profile_photo_obj.is_set = True
            profile_photo_obj.uploaded_on = datetime.datetime.now()
            profile_photo_obj.key = profile_photo_obj.key_generate
            profile_photo_obj.save()

            # resizing with ratio maintained.
            misc.image_resize(MEDIA_ROOT + '/' + str(profile_photo_obj.profile_photo), '280x280', maintain_ratio = True)

            return HttpResponseRedirect(reverse('edit_profile_photo', args = (profile_photo_obj.key,)))

    return render(request, 'users/edit_profile_photo.html', {
        'form': form,
        'profile_photo_obj': profile_photo_obj,
    })




@login_required
def edit_profile(request):
    user_obj = request.user
    try:
        profile_obj = get_object_or_404(Profile, user = user_obj)
    except:
        profile_obj = None



    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():

            profile_obj.city = form.cleaned_data['city'].title()
            profile_obj.country = form.cleaned_data['country'].title()
            profile_obj.description = form.cleaned_data['description']
            profile_obj.save()
            user_obj.first_name = form.cleaned_data['first_name'].title()
            user_obj.last_name = form.cleaned_data['last_name'].title()
            user_obj.save()
            messages.info(request, 'Your profile information is saved')
    else:
        form = EditProfileForm(initial = {
            'first_name':user_obj.first_name,
            'last_name': user_obj.last_name,
            'username':user_obj.username,
            'sex':  profile_obj.sex,
            'dob': profile_obj.dob.strftime('%d %b, %Y - %A'),
            'city':  profile_obj.city,
            'country': profile_obj.country,
            'description': profile_obj.description,
            })


    return render(request, 'users/edit_profile.html', {
        'form': form,
    })


@login_required
def settings(request):
    return render(request, 'users/settings.html', {

    })

@visibility_of_friends
def friends(request, username):
    username = username

    user_obj = get_object_or_404(User, username = username)


    fr_obj = FriendRequest.objects.filter(recipient = user_obj,
            is_accepted = False)


    try:
        friends_id_obj = Friends.objects.get(user = user_obj)
        friends_obj_list = []
        for i in friends_id_obj.list_of:
            friends_obj_list.append(get_object_or_404(User, id = i))


        print friends_obj_list
    except:
        friends_obj_list = None
    return render(request, 'users/friends.html', {
        'friends_obj_list': friends_obj_list,
        'fr_obj': fr_obj,
        'username': username,
        'user_obj':user_obj,
    })

@visibility_of_stories
def stories(request, username):
    user_obj = get_object_or_404(User, username = username)
    df_obj = DailyPhoto.objects.filter(user = user_obj, is_public = True).order_by('-id')
    return render(request, 'users/stories.html', {
        'df_obj': df_obj,
        "username": username,
        'user_obj': user_obj,
    })

@login_required
def upload_new_story(request):

    if request.method == 'POST':
        form = UploadNewStoryForm(request.POST, request.FILES)
        if form.is_valid():
            photo = request.FILES['photo']
            dp_obj = DailyPhoto()
            dp_obj.user = request.user
            dp_obj.photo = photo
            dp_obj.photo_path = 'dailyphoto/%s' % request.user.username
            dp_obj.key = dp_obj.key_generate
            dp_obj.save()
            try:
                #save a progressive image of the original and update db entry.
                dp_obj.photo = misc.save_progressive_image(dp_obj.photo)
                dp_obj.save()

                # Code to generate more diff diff
                # sizes of the uploaded photo
                for size in IMAGE_SIZE_DAILY_PHOTO:
                    misc.image_resize(MEDIA_ROOT + '/' + str(dp_obj.photo), size,)

                # resizing with ratio maintained.
                misc.image_resize(MEDIA_ROOT + '/' + str(dp_obj.photo), '280x280', maintain_ratio = True)
                return HttpResponseRedirect(
                    reverse('users.views.uploading_finished', args = (dp_obj.id,)))
            except Exception, e:
                print 'ERROR IN UPLOADING DAILY PHOTO, %s' % e
                dp_obj.delete()
                # messages.error(request, 'Please select only images file')
                # form = UploadNewStoryForm()
    else:
        form = UploadNewStoryForm()
    return render(request, 'users/upload_new_story.html', {
        'upload_photo_form': form,
    })


@login_required
def uploading_finished(request, photo_id):
    photo_id = photo_id
    dp_obj = get_object_or_404(DailyPhoto, id = photo_id)
    photo_path = dp_obj.photo
    photo_path = MEDIA_URL + str(photo_path)
    print 'my photo path', photo_path
    return render(request, 'users/uploading_finished.html', {
        'photo_id': photo_id,
        'photo_path': photo_path,
    })


@login_required

def write_story(request):
    if request.user.is_authenticated():
        user_obj = request.user

    profile_obj = get_object_or_404(Profile, user = user_obj)
    year_of_birth = profile_obj.dob.year
    if request.method == 'POST':
        form = WriteStoryForm(request.POST)
        if form.is_valid():
            story = form.cleaned_data['story']

            story_list = story.split('\n')
            # Replacing the newlines with break tag...
            story = '<br>'.join(story_list)

            heading = form.cleaned_data['heading']
            uploaded_on = request.POST.get('datepicker', '')
            moods = request.POST['moods']
            is_public = request.POST.get('public', '')
            is_public = int(is_public)



            dp_obj = DailyPhoto.objects.filter(user=user_obj, uploaded_on=uploaded_on)
            if dp_obj:
                if is_public:
                    for i in dp_obj:
                        i.is_public=False
                        i.save()

            new_photo_id = request.POST.get('new_photo_id', '')

            DailyPhoto.objects.filter(id = new_photo_id).update(
                heading = heading,
                story = story,
                no_of_views = 0,
                moods = moods,
                is_public = True if is_public else False,
                uploaded_on = uploaded_on
            )

            thread.start_new_thread(share_photos, (request, new_photo_id))
            messages.info(request, 'Story uploaded successfully')

            # Set redis keyword for realtime notifications.
            redis_obj = StrictRedis(db=9)
            redis_obj.publish("notifications:%s" % user_obj.username, 1)
            #TODO Save the activity in db.

            return HttpResponseRedirect('/%s/photo-calendar' % user_obj.username)

    else:
        form = WriteStoryForm()

    return render(request, 'users/write_story.html', {
        'write_story_form': form,
        'year_of_birth': year_of_birth,
    })


@login_required
def edit_story(request, dp_id):
    if request.is_ajax():
        story = request.GET.get('do_edit_story', '')
        story = story.strip()
        if story:
            DailyPhoto.objects.filter(id = dp_id).update(story=story)
    else:
        return HttpResponse('ONLY POST...')
    return HttpResponse('')


@login_required
def check_for_taken_date(request, year, month, day):
    if request.user.is_authenticated():
        user_obj = request.user
    date = year + "-" + month + "-" + day

    dp_obj = DailyPhoto.objects.filter(user=user_obj, is_public=True)
    if request.is_ajax():
        if dp_obj:
            for i in dp_obj:

                if str(i.uploaded_on) == date:

                    return HttpResponse('false')

        else:
            return HttpResponse('true')
    else:
        return HttpResponseRedirect('/403')

    return HttpResponse('')


@login_required
def send_friend_request(request, recipient_id):
    if request.is_ajax():
        recipient = get_object_or_404(User, id=recipient_id)
        redis_obj = StrictRedis(db=9)
        try:
            redis_obj.publish('notifications:%s' % recipient.username, 1)
        except Exception, err:
            print err

        fr_obj = None

        try:
            fr_obj = FriendRequest.objects.get(
                sender=request.user, recipient=recipient)
        except:
            fr_obj = FriendRequest.objects.create(
                sender=request.user, recipient=recipient)

        # Also create an entry in redis for this user.
        # PubSub only works if the user is online and subscribed to the live
        # stream
        try:
            # This is creating error;;
            #hmset() takes exactly 3 arguments (10 given)
            redis_obj.hmset(
                'user:notify:%s' % request.user.id,
                'obj_name', fr_obj._meta.object_name,
                'obj_id', fr_obj.id,
                'time_of', int(time()),
                'was_viewed', 'false')
        except:
            pass
    else:
        return HttpResponse('POST ONLY...')

    return HttpResponse('')


@login_required
def accept_friend_request(request, sender_id):
    if request.user.is_authenticated():
        recipient_obj = request.user
    if request.is_ajax():
        try:
            friends_obj_r = Friends.objects.get(user = recipient_obj)
        except:
            friends_obj_r = Friends.objects.create(user = recipient_obj, list_of = [])

        if int(sender_id) not in friends_obj_r.list_of:
            friends_obj_r.list_of.append(int(sender_id))
        friends_obj_r.save()

        try:
            friends_obj_s = Friends.objects.get(user_id = sender_id)
        except:
            friends_obj_s = Friends.objects.create(user = get_object_or_404(User, id = sender_id), list_of = [])

        if int(recipient_obj.id) not in friends_obj_s.list_of:
            friends_obj_s.list_of.append(int(recipient_obj.id))
        friends_obj_s.save()

        FriendRequest.objects.filter(recipient_id = recipient_obj.id,
                sender_id = sender_id).update(is_accepted = True)
    else:
        return HttpResponse('ONLY POST...')


    return HttpResponse('')

@login_required
def cancel_friend_request(request, recipient_id):
    if request.is_ajax():
        fr_obj = FriendRequest.objects.get(sender = request.user,
            recipient = get_object_or_404(User, id = recipient_id))
        if not fr_obj.is_accepted:
            fr_obj.delete()
    else:
        return HttpResponse('POST ONLY...')

    return HttpResponse('')


@login_required
def reject_friend_request(request, sender_id):
    if request.is_ajax():
        FriendRequest.objects.filter(
            sender = get_object_or_404(User, id = sender_id),
            recipient = get_object_or_404(User, id = request.user.id)).delete()
    else:
        return HttpResponse('ONLY POST...')
    return HttpResponse('')


@login_required
def delete_from_friends(request, friend_id):
    if request.is_ajax():
        print 'friend id', friend_id

        # Removing from Friends model.
        # We have to take care of two things in this
        # While removing we need to remove the user from his and the
        # other friends list_of field .

        fr_obj = get_object_or_404(Friends, user = request.user)
        # Have to add some if statement here, as it may generate error.
        #if int(friend_id) in fr_obj.list_of:
        fr_obj.list_of.remove(int(friend_id))
        fr_obj.save()

        fr_obj1 = get_object_or_404(Friends,
            user = get_object_or_404(User, id = friend_id))
        fr_obj1.list_of.remove(int(request.user.id))
        fr_obj1.save()

        # Removing from FriendsRequest model
        try:
            fr_obj = get_object_or_404(FriendRequest,
                sender = get_object_or_404(User, id = request.user.id),
                recipient = get_object_or_404(User, id = friend_id))
            fr_obj.delete()
            print 'removed from first %s', request.user.id
        except:
            fr_obj = get_object_or_404(FriendRequest,
                sender = get_object_or_404(User, id = friend_id),
                recipient = get_object_or_404(User, id = request.user.id))
            fr_obj.delete()
            print 'removed from second %s', request.user.id
    else:
        return HttpResponse('ONLY POST...')
    return HttpResponse('')


@login_required
def status(request):
    return render(request, 'users/status.html', {

    })


@login_required
def write_status(request):
    if request.method == 'POST':
        form = WriteStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            Status.objects.create(user = request.user, status = status)
            return HttpResponseRedirect(reverse('users.views.profile', args = (request.user.username,)))
    else:
        form = WriteStatusForm()

    return render(request, 'users/write_status.html' , {
        'form': form,
    })


@visibility_of_daily_photos
def browse_daily_photo_single_lightbox(request, username, photo_id = None):
    username = username

    try:
        user_obj = get_object_or_404(User, username = username)
    except:
        user_obj = None
    dailyphoto_obj_single = None

    comments_obj = None
    next_photo = ["disabled", "#"]
    prev_photo = ["disabled", "#"]
    friends_dict = {}
    friends_id_list = None

    if user_obj:

        if photo_id:

            dailyphoto_obj_single = get_object_or_404(DailyPhoto, user = user_obj, key = photo_id, is_public = True)
            dailyphoto_obj_single.no_of_views = int(dailyphoto_obj_single.no_of_views) + 1
            dailyphoto_obj_single.save()
            comments_obj = Comments.objects.filter(
                    dailyphoto = get_object_or_404(DailyPhoto, key = photo_id))

            # Pagination
            photo_list = list(DailyPhoto.objects.filter(user = user_obj, is_public = True).order_by('uploaded_on'))
            curr_page_number = photo_list.index(dailyphoto_obj_single)
            last_page_number = len(photo_list) - 1

            if last_page_number == 0:
                next_photo = ['disabled', '#']
                prev_photo = ['disabled', '#']
            else:
                if curr_page_number == last_page_number:
                    next_photo = ['active', photo_list[0].key]
                    prev_photo = ['active', photo_list[curr_page_number - 1].key]
                elif curr_page_number == 0:
                    next_photo = ['active', photo_list[curr_page_number + 1].key]
                    prev_photo = ['active', photo_list[-1].key]
                else:
                    next_photo = ['active', photo_list[curr_page_number + 1].key]
                    prev_photo = ['active', photo_list[curr_page_number - 1].key]

            # Get list of friends for commenting
            logged_in_user = request.user


            try:
                friends_id_list = logged_in_user.friends_set.get().list_of
                for friend_id in friends_id_list:
                    username = User.objects.get(id = friend_id).username

                    friends_dict[username] = {"url": "/%s/" % username}
            except Exception, err:
                print "pass statement ", err


    score = {}
    likes_count = 0
    try:
        score[dailyphoto_obj_single.id] = dailyphoto_obj_single.likes_set.get(user = request.user).rating
    except:
        pass

    try:
        likes_count = dailyphoto_obj_single.likes_set.all().aggregate(Sum('rating'))['rating__sum']
        if likes_count is None:
            likes_count = 0
    except:
        likes_count = 0


    return render(request, 'users/browse_daily_photo_single_lightbox.html', {
        'dailyphoto_obj_single': dailyphoto_obj_single,
        'comments_obj': comments_obj,
        'username': username,
        'user_obj': user_obj,
        'score': score,
        'likes_count': likes_count,
        'next_photo': next_photo,
        'prev_photo': prev_photo,
        'friends_dict': json.dumps(friends_dict),
        'friends_id_list': friends_id_list,
    })



@visibility_of_daily_photos
def browse_daily_photo_single(request, username, photo_id = None):
    username = username

    try:
        user_obj = get_object_or_404(User, username = username)
    except:
        user_obj = None
    dailyphoto_obj_single = None

    comments_obj = None
    next_photo = ["disabled", "#"]
    prev_photo = ["disabled", "#"]
    friends_dict = {}
    friends_id_list = None

    if user_obj:

        if photo_id:

            dailyphoto_obj_single = get_object_or_404(DailyPhoto, user = user_obj, key = photo_id, is_public = True)
            dailyphoto_obj_single.no_of_views = int(dailyphoto_obj_single.no_of_views) + 1
            dailyphoto_obj_single.save()
            comments_obj = Comments.objects.filter(
                    dailyphoto = get_object_or_404(DailyPhoto, key = photo_id))

            # Pagination
            photo_list = list(DailyPhoto.objects.filter(user = user_obj, is_public = True).order_by('uploaded_on'))
            curr_page_number = photo_list.index(dailyphoto_obj_single)
            last_page_number = len(photo_list) - 1

            if last_page_number == 0:
                next_photo = ['disabled', '#']
                prev_photo = ['disabled', '#']
            else:
                if curr_page_number == last_page_number:
                    next_photo = ['active', photo_list[0].key]
                    prev_photo = ['active', photo_list[curr_page_number - 1].key]
                elif curr_page_number == 0:
                    next_photo = ['active', photo_list[curr_page_number + 1].key]
                    prev_photo = ['active', photo_list[-1].key]
                else:
                    next_photo = ['active', photo_list[curr_page_number + 1].key]
                    prev_photo = ['active', photo_list[curr_page_number - 1].key]

            # Get list of friends for commenting
            logged_in_user = request.user


            try:
                friends_id_list = logged_in_user.friends_set.get().list_of
                for friend_id in friends_id_list:
                    username = User.objects.get(id = friend_id).username

                    friends_dict[username] = {"url": "/%s/" % username}
            except Exception, err:
                print "pass statement ", err


    score = {}
    likes_count = 0
    try:
        score[dailyphoto_obj_single.id] = dailyphoto_obj_single.likes_set.get(user = request.user).rating
    except:
        pass

    try:
        likes_count = dailyphoto_obj_single.likes_set.all().aggregate(Sum('rating'))['rating__sum']
        if likes_count is None:
            likes_count = 0
    except:
        likes_count = 0


    return render(request, 'users/browse_daily_photo_single.html', {
        'dailyphoto_obj_single': dailyphoto_obj_single,
        'comments_obj': comments_obj,
        'username': username,
        'user_obj': user_obj,
        'score': score,
        'likes_count': likes_count,
        'next_photo': next_photo,
        'prev_photo': prev_photo,
        'friends_dict': json.dumps(friends_dict),
        'friends_id_list': friends_id_list,
    })

@visibility_of_daily_photos
def browse_daily_photo_all(request, username):
    username = username
    try:
        user_obj = get_object_or_404(User, username = username)
    except:
        user_obj = None

    dailyphoto_obj_all = DailyPhoto.objects.filter(
                user = user_obj, is_public = True).order_by("-id")
    return render(request, 'users/browse_daily_photo_all.html', {
        'dailyphoto_obj_all': dailyphoto_obj_all,

        'username': username,
        'user_obj': user_obj,

    })


@visibility_of_profile_photos
def browse_profile_photos_all(request, username):
    username = username
    try:
        user_obj = get_object_or_404(User, username = username)
    except:
        user_obj = None
    profilephoto_obj_all = ProfilePhoto.objects.filter(
        user = user_obj).order_by("-id")
    return render(request, 'users/browse_profile_photos_all.html', {
        'profilephoto_obj': profilephoto_obj_all,
        'username': username,
        'user_obj': user_obj,
    })


@visibility_of_cover_photos
def browse_cover_photos_all(request, username):
    username = username
    try:
        user_obj = get_object_or_404(User, username = username)
    except:
        user_obj = None
    coverphotos_obj_all = CoverPhoto.objects.filter(
        user = user_obj)
    return render(request, 'users/browse_cover_photos_all.html', {
        'coverphoto_obj': coverphotos_obj_all,
        'username': username,
        'user_obj': user_obj,
    })


def user_profile_info(request, username):
    username = username
    user_obj = get_object_or_404(User, username = username)
    profilephoto_obj = None
    if user_obj:
        profilephoto_obj = get_object_or_404(ProfilePhoto,
            user = user_obj,
            is_set = True)
    return render(request, 'users/user_profile_info.html', {
        "username": username,
        'profilephoto_obj': profilephoto_obj,
        'user_obj': user_obj,
    })


@login_required
@csrf_exempt
def do_comment(request, dailyphoto_id):
    dp_obj = get_object_or_404(DailyPhoto, id=dailyphoto_id)
    
    comment = request.POST.get('do_comment', '')
    comment = comment.strip()
    # Save the comment in DB.
    print "Comment Text: ", comment
    list_of_users_in_comment = [resub(r'\[|\]', r'', name)
                                for name in findall(r'\[[a-z0-9]+\]', comment)]
    for nuser in list_of_users_in_comment:
        print nuser
    if comment:
        Comments.objects.create(user = request.user,
            dailyphoto = get_object_or_404(DailyPhoto, id = dailyphoto_id),
            comment = comment,
            )
        redis_obj = StrictRedis(db=9)
        redis_obj.publish("notifications:%s" % request.user.username, 1)
    return HttpResponseRedirect(reverse('users.views.browse_daily_photo_single', args=(str(dp_obj.user.username),dp_obj.key )))
    

@login_required
def edit_comment(request, comment_id):
    if request.is_ajax():
        comment = request.GET.get('do_edit_comment', '')
        comment = comment.strip()
        if comment:
            Comments.objects.filter(id = comment_id).update(comment=comment)
    else:
        return HttpResponse('ONLY POST...')
    return HttpResponse('')






@login_required
def delete_comment(request, comment_id):
    if request.user.is_authenticated():
        #user_obj = request.user
        pass

        if request.is_ajax():
            Comments.objects.filter(id=comment_id).delete()
        else:
            return HttpResponseRedirect('/403')
    else:
        return HttpResponseRedirect('/404')
    return HttpResponse('')



@login_required
@csrf_exempt
def set_rating(request):
    if request.method == 'POST':
        daily_photo = get_object_or_404(DailyPhoto, id = request.POST['dayphotoID'])

        likes_obj = Likes.objects.get_or_create(user = request.user, daily_photo = daily_photo)[0]
        likes_obj.rating = request.POST['score']
        likes_obj.save()

    return HttpResponse(json.dumps({}), content_type = "application/json")


@login_required
def edit_privacy_settings(request):
    ps_obj = get_object_or_404(PrivacySettings, user = request.user)
    if request.method == 'POST':
        form = EditPrivacyForm(request.POST)
        if form.is_valid():
            friends_visibility = form.cleaned_data['friends_visibility']
            cover_photos_visibility = form.cleaned_data['cover_photos_visibility']
            profile_photos_visibility = form.cleaned_data['profile_photos_visibility']
            daily_photos_visibility = form.cleaned_data['daily_photos_visibility']
            stories_visibility = form.cleaned_data['stories_visibility']
            calendar_visibility = form.cleaned_data['calendar_visibility']
            who_can_like_photos = form.cleaned_data['who_can_like_photos']
            who_can_comment_on_photos = form.cleaned_data['who_can_comment_on_photos']


            if daily_photos_visibility == 'N' or daily_photos_visibility == "F":
                is_sharing_of_photos_on_fb = 'N'
            else:
                is_sharing_of_photos_on_fb = ps_obj.is_sharing_of_photos_on_fb


            PrivacySettings.objects.filter(user = request.user).update(
                friends_visibility = friends_visibility,
                is_sharing_of_photos_on_fb = is_sharing_of_photos_on_fb,
                cover_photos_visibility = cover_photos_visibility,
                profile_photos_visibility = profile_photos_visibility,
                daily_photos_visibility = daily_photos_visibility,
                stories_visibility = stories_visibility,
                calendar_visibility = calendar_visibility,
                who_can_comment_on_photos = who_can_comment_on_photos,
                who_can_like_photos = who_can_like_photos,
                )
            messages.info(request, 'Your privacy settings is changed.')
            return HttpResponseRedirect(reverse('users.views.edit_privacy_settings'))

    else:
        form = EditPrivacyForm(initial = {
            'friends_visibility': ps_obj.friends_visibility,
            'cover_photos_visibility': ps_obj.cover_photos_visibility,
            'profile_photos_visibility': ps_obj.profile_photos_visibility,
            'daily_photos_visibility': ps_obj.daily_photos_visibility,
            'stories_visibility': ps_obj.stories_visibility,

            'calendar_visibility': ps_obj.calendar_visibility,
            'who_can_comment_on_photos': ps_obj.who_can_comment_on_photos,
            'who_can_like_photos': ps_obj.who_can_like_photos,
            })
    return render(request, 'users/edit_privacy_settings.html', {
        'form': form,
    })


@login_required
def show_likes_history(request, photo_id):
    #suser_obj = request.user
    likes_obj = Likes.objects.filter(daily_photo = get_object_or_404(DailyPhoto, id=photo_id))
    for i in likes_obj:
        print i.user, i.rating
    return render(request, 'users/show_likes_history.html', {
        'likes_obj': likes_obj,
    })


@login_required
def find_friends(request):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None

    is_user_connected = False
    if user_obj:
        fb_profile_obj = FacebookProfile.objects.filter(user=user_obj)
        if fb_profile_obj:
            for item in fb_profile_obj:
                if item.facebook_id:
                    is_user_connected = True
                else:
                    is_user_connected = False
        else:
            is_user_connected = False
    return render(request, 'users/find_friends.html', {
        'is_user_connected': is_user_connected,
    })


@login_required
def do_find_friends(request):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None
    fb_id_list = []
    friends_on_oposod_list = []
    if user_obj:
        if request.is_ajax():
            fb_profile_obj = FacebookProfile.objects.filter(user=user_obj)
            if fb_profile_obj:
                for item in fb_profile_obj:
                    if item.facebook_id:
                        access_token = item.access_token
                        facebook_id = item.facebook_id
                        url = 'https://graph.facebook.com/%s/friends/?access_token=%s' \
                            % (facebook_id, access_token)

                        data = json.load(urllib2.urlopen(url))
                        for item in data['data']:
                            fb_id_list.append(item['id'])

                        if fb_id_list:
                            for fb_id in fb_id_list:
                                try:
                                    fb_profile_obj = get_object_or_404(FacebookProfile, facebook_id=fb_id)
                                    friends_on_oposod_list.append(fb_profile_obj)
                                except:
                                    pass


                    else:
                        access_token = None
                        facebook_id = None
        else:
            return HttpResponseRedirect('/403')



    return render(request, 'users/do_find_friends.html', {
        'friends_on_oposod_list': friends_on_oposod_list,
    })




def testimonials(request, username, key=None):
    username = username
    testimonial_obj_all = None
    testimonial_obj_single = None
    try:
        user_obj = get_object_or_404(User, username=username)
        if not key:
            testimonial_obj_all = Testimonials.objects.filter(user=user_obj)
        else:
            testimonial_obj_single = get_object_or_404(Testimonials,
                user=user_obj,
                key = key)

    except:
        return HttpResponseRedirect('/404')


    return render(request, 'users/testimonials.html', {
        'testimonial_obj_all': testimonial_obj_all,
        'testimonial_obj_single': testimonial_obj_single,
        'username': username,
        'user_obj': user_obj,
    })


@login_required
def write_testimonial(request, username):
    username = username
    if request.user.is_authenticated():
        author = request.user
    else:
        author = None

    if author:
        form = WriteTestimonialForm(request.POST or None)
        if form.is_valid():
            testimonial = form.cleaned_data['testimonial']
            t_obj = Testimonials()
            t_obj.testimonial = testimonial
            t_obj.author = author
            t_obj.key = t_obj.key_generate
            t_obj.user = get_object_or_404(User, username=username)
            t_obj.save()

            messages.info(request, 'Testimonials successfully submitted.')
            return HttpResponseRedirect(reverse('users.views.write_testimonial', args=(str(username),)))
    return render(request, 'users/write_testimonial.html', {
        'form': form,
        'username': username,
    })


@login_required
def facebook_settings(request):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None
    fb_settings = False
    is_user_connected = False
    if user_obj:
        fb_profile_obj = FacebookProfile.objects.filter(user=user_obj)
        if fb_profile_obj:
            for item in fb_profile_obj:
                if item.facebook_id:
                    is_user_connected = True
                else:
                    is_user_connected = False
        else:
            is_user_connected = False

        ps_obj = get_object_or_404(PrivacySettings, user=user_obj)
        if ps_obj.is_sharing_of_photos_on_fb == 'Y':
            fb_settings = True
        else:
            fb_settings = False
    return render(request, 'users/facebook_settings.html', {
        'is_user_connected': is_user_connected,
        'fb_settings': fb_settings,
    })


@login_required
@facebook_required(scope='publish_actions')
def change_facebook_settings(request):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None

    if user_obj:
        if request.method == 'POST':
            #pass
            option = request.POST['is_sharing_of_photos_on_fb']
            #return HttpResponse(option)
            PrivacySettings.objects.filter(user=user_obj).update(is_sharing_of_photos_on_fb=option,
                daily_photos_visibility="A")
            messages.info(request, 'Your facebook settings is saved.')
            return HttpResponseRedirect(reverse('users.views.facebook_settings'))
        else:
            return HttpResponseRedirect('/403')
    return HttpResponse('Issues are here....')


@login_required
def delete_daily_photo(request, dp_id):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None
    if user_obj and request.is_ajax():
        DailyPhoto.objects.filter(id=dp_id).delete()
    else:
        return HttpResponse('')    
    return HttpResponse('')
