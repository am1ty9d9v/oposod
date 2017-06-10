import operator
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from calendar import monthrange
from oposod.settings import SITE
from users.models import DailyPhoto, Friends, FeedView
from utils.privacy_decorators import visibility_of_calendar


@csrf_exempt
def index(request):
    dp_dict = {}
    score = {}
    if request.user.is_authenticated():
        try:
            fr_obj = get_object_or_404(Friends, user=request.user)
        except:
            fr_obj = None
        if fr_obj:
            for friend_i in fr_obj.list_of:
                dp_obj = DailyPhoto.objects.filter(is_public=True,
                                                   user=get_object_or_404(User, id=friend_i))
                if dp_obj:

                    for i in dp_obj:
                        dp_dict[i.id] = i
                        # break
                    score = {}
                    for dp in dp_obj:
                        try:
                            score[dp.id] = dp.likes_set.get(user=request.user).rating
                        except:
                            score[dp.id] = 0

    try:
        feed_view_obj = FeedView.objects.get(user=request.user)
    except:
        feed_view_obj = None

    if feed_view_obj and feed_view_obj.view == 'ICON':
        sorted_dp_dict = sorted(dp_dict.iteritems(), key=operator.itemgetter(0), reverse=True)
        return render(request, 'home/index_icon.html', {

            'score': score,
            'sorted_dp_dict': sorted_dp_dict,
        })
    else:
        sorted_dp_dict = sorted(dp_dict.iteritems(), key=operator.itemgetter(0), reverse=True)[0:10]
        return render(request, 'home/index.html', {

            'score': score,
            'sorted_dp_dict': sorted_dp_dict,
        })


def show_more_index(request, dp_id):
    html = ''
    dp_id = int(dp_id)
    dp_dict = {}
    score = {}
    if request.user.is_authenticated():
        try:
            fr_obj = get_object_or_404(Friends, user=request.user)
        except:
            fr_obj = None
        if fr_obj:
            for friend_i in fr_obj.list_of:
                dp_obj = DailyPhoto.objects.filter(id__lt=dp_id, id__gte=int(dp_id - 10), is_public=True,
                                                   user=get_object_or_404(User, id=friend_i))
                if dp_obj:

                    for i in dp_obj:
                        dp_dict[i.id] = i
                        # break
                    score = {}
                    for dp in dp_obj:
                        try:
                            score[dp.id] = dp.likes_set.get(user=request.user).rating
                        except:
                            score[dp.id] = 0
    # print dict((k, v) for k, v in dp_dict.iteritems())

    sorted_dp_dict = sorted(dp_dict.iteritems(), key=operator.itemgetter(0), reverse=True)[0:10]
    return render(request, 'home/show_more_index.html', {
        'sorted_dp_dict': sorted_dp_dict,
        'SITE': SITE,

    })


def named_month(month_number):
    """
    Return the name of the month, given the number.
    """
    date_tup = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    return date_tup[month_number]


def this_month(request):
    """
    Show calendar of events this month.
    """
    today = datetime.now()
    return calendar(request, today.year, today.month)


@visibility_of_calendar
def calendar(request, username, year=None, month=None, series_id=None):
    """
    Show calendar of events for a given month of a given year.
    ``series_id``
    The event series to show. None shows all event series.

    """
    month_name_list = [datetime.strftime(date(2001, 01 + i, 01), "%B") for i in range(12)]
    year_list = [i for i in xrange(datetime.now().year, 1900, -1)]
    print "Post data: ", request.POST
    if request.POST:
        try:
            month = month_name_list.index(str(request.POST['month'])) + 1
            year = int(request.POST['year'])
        except:
            month = None
            year = None

    if year and month:
        year = int(year)
        month = int(month)
        if year == date.today().year and month > date.today().month:
            print "in if"
            my_month = date.today().month
            my_year = date.today().year
        elif year > date.today().year:
            print "in elif"
            my_month = date.today().month
            my_year = date.today().year
        else:
            print "in else"
            my_year = int(year)
            my_month = int(month)
    else:
        my_month = date.today().month
        my_year = date.today().year
    my_calendar_from_month = datetime(my_year, my_month, 1)
    my_calendar_to_month = datetime(my_year, my_month, monthrange(my_year, my_month)[1])
    user_obj = get_object_or_404(User, username=username)
    my_events = DailyPhoto.objects.filter(user=user_obj, is_public=True,
                                          uploaded_on__gte=my_calendar_from_month).filter(
        uploaded_on__lte=my_calendar_to_month)

    '''
    print my_events
    if series_id:
        my_events = my_events.filter(series=series_id)
    '''

    # Calculate values for the calendar controls. 1-indexed (Jan = 1)
    my_previous_year = my_year
    my_previous_month = my_month - 1
    if my_previous_month == 0:
        my_previous_year = my_year - 1
        my_previous_month = 12
    my_next_year = my_year
    my_next_month = my_month + 1
    if my_next_month == 13:
        my_next_year = my_year + 1
        my_next_month = 1
    my_year_after_this = my_year + 1
    my_year_before_this = my_year - 1
    return render(
        request,
        "cal_template.html", {
            'photo_list': my_events,
            'username': username,
            'user_obj': user_obj,
            'month': my_month,
            'month_name': named_month(my_month),
            'year': my_year,
            'previous_month': my_previous_month,
            'previous_month_name': named_month(my_previous_month),
            'previous_year': my_previous_year,
            'next_month': my_next_month,
            'next_month_name': named_month(my_next_month),
            'next_year': my_next_year,
            'year_before_this': my_year_before_this,
            'year_after_this': my_year_after_this,
            'month_name_list': month_name_list,
            'year_list': year_list,
        },
    )


@login_required
def set_view(request, view_type):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None

    if user_obj and request.is_ajax():
        feed_view_obj, created = FeedView.objects.get_or_create(user=user_obj)
        feed_view_obj.view = view_type
        feed_view_obj.save()

    return HttpResponse('')
