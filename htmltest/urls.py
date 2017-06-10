from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^htmltest/index/$', TemplateView.as_view(template_name='htmltest/index.html')),
]
