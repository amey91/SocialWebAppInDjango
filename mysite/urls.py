from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', 'moneyclub.groups.views.club_home', name='default'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^moneyclub/groups/', include('moneyclub.groups.urls')),
	
)

