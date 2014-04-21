from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       
    url(r'^htmltest/index/$', TemplateView.as_view(template_name = 'htmltest/index.html')),
)
