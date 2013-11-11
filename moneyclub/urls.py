from django.conf.urls import patterns, include, url

# Generates the routes for the Controller.
# Typical use is a regular expression for a URL pattern, and then the
# action to call to process requests for that URL pattern.
urlpatterns = patterns('',
    url(r'^$', 'moneyclub.views.group_home'),
    
    
    
    
    #url(r'^profile/(?P<uname>\w+)/$', 'grumblr.profile.views.profile1'),
	#url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'/moneyclub/login.html'}),
    # Route to logout a user and send them back to the login page
    #url(r'^logout$', 'django.contrib.auth.views.logout_then_login'),
    #url(r'^becomefollower/(?P<uname>\w+)/$', 'grumblr.views.becomefollower1'),
    #url(r'^add_comment_redirect/(?P<commentid>\d+)/$', 'grumblr.views.add_comment_redirect'),
    #url(r'^add_comment/(?P<commentid>\d+)/$', 'moneyclub.views.add_comment'),
    #url(r'^grumblquantity/(?P<uname>\w+)/$', 'grumblr.views.somebodysgrumbls'),
    url(r'^home$', 'moneyclub.views.home'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'moneyclub/welcome.html'}, name='login'),
	url(r'^logout$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^register$', 'moneyclub.views.register'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'moneyclub.views.confirm_registration', name='confirm'),
 
)
