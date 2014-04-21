from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^signup/$', 'accounts.views.signup', name='signup'),
    url(r'^signin/$', 'accounts.views.signin', name='signin'),
    url(r'^signout/$', 'accounts.views.signout', name='signout'),
    url(r'^join-oposod/$', TemplateView.as_view(template_name='accounts/join_us.html'), name='join_us'),
    url(r'request/reset-password/',
         'accounts.views.reset_password_ask_email_page', 
            name='reset_password'),

    url(r'do/reset-password/$',
         'accounts.views.reset_password_do_reset_password_page', 
            name='do_reset_password'),

    url(r'^change-password/$', 'accounts.views.change_password', name='change_password'),
    url(r'^account/activation/(?P<activation_key>\w+)/$', 'accounts.views.activate', name='activate'),
    url(r'resend-activation-email/$',
            'accounts.views.resend_activation_email',
                name = 'resend_activation_email'),
)
