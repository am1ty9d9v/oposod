from django.conf.urls import url
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    url(r'^signup/$', signup, name='signup'),
    url(r'^signin/$', signin, name='signin'),
    url(r'^signout/$', signout, name='signout'),
    url(r'^join-oposod/$', TemplateView.as_view(template_name='accounts/join_us.html'), name='join_us'),
    url(r'request/reset-password/',
        reset_password_ask_email_page,
        name='reset_password'),

    url(r'do/reset-password/$',
        reset_password_do_reset_password_page,
        name='do_reset_password'),

    url(r'^change-password/$', change_password, name='change_password'),
    url(r'^account/activation/(?P<activation_key>\w+)/$', activate, name='activate'),
    url(r'resend-activation-email/$',
        resend_activation_email,
        name='resend_activation_email'),
]
