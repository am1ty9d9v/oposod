from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',


    
    url(r'', include('htmltest.urls')),
    url(r'', include('accounts.urls')),
    url(r'', include('home.urls')),
    
    url(r'^search-oposod/', include('haystack.urls')),
    url(r'^facebook/', include('django_facebook.urls')), 
    url(r'^accounts/', include('django_facebook.auth_urls')), 
    url(r'', include('users.urls')),

)  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
