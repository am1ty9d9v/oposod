from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', index, name='home_index'),
    url(r'^show-more-home-feed/(?P<dp_id>\d+)$', show_more_index, name='show_more_index'),
    url(r'^(?P<username>\w+)/photo-calendar/$', calendar, name='calendar'),
    url(r'^(?P<username>\w+)/photo-calendar/(?P<year>\d{4})/(?P<month>\d{1,2})$', calendar,
        name='calendar'),
    url(r'^set/view/(?P<view_type>\w+)', set_view),
]
