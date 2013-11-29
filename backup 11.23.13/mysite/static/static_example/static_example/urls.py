from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^good$', 'app.views.good'),
    url(r'^bad$', 'app.views.bad'),
)
