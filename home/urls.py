from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
	
	url(r'^$', 'home.views.index', name='home_index'),
	url(r'^show-more-home-feed/(?P<dp_id>\d+)$', 'home.views.show_more_index', name = 'show_more_index'),
	url(r'^(?P<username>\w+)/photo-calendar/$', 'home.views.calendar', name='calendar'),
	url(r'^(?P<username>\w+)/photo-calendar/(?P<year>\d{4})/(?P<month>\d{1,2})$', 'home.views.calendar', name='calendar'),
	url(r'^set/view/(?P<view_type>\w+)', 'home.views.set_view')	,
)
