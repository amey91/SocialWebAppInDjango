from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('moneyclub.urls')),
    url(r'^moneyclub/groups/', include('moneyclub.groups.urls')),
    url(r'^moneyclub/member/', include('moneyclub.member.urls')),
    url(r'^static/(.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),

)
