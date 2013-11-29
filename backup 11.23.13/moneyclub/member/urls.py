from django.conf.urls import patterns, include, url

# Generates the routes for the Controller.
# Typical use is a regular expression for a URL pattern, and then the
# action to call to process requests for that URL pattern.
urlpatterns = patterns('',
	url(r'^profile$', 'moneyclub.member.views.view_profile'),
    #url(r'^edit-profile$', 'grumblr.views.edit_profile'),
    url(r'^save-profile$', 'moneyclub.member.views.save_profile'),
    url(r'^userphoto/(?P<id>\d+)$', 'moneyclub.member.views.get_photo', name='user-photo'),
    url(r'^reset-password$', 'moneyclub.member.views.reset_password', name='reset_password'),
    url(r'^reset-password-by-email$', 'moneyclub.member.views.reset_password_by_email', name='reset_password_by_email'),
    url(r'^confirm-reset-password-by-email/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'moneyclub.member.views.confirm_reset_password_by_email', name='confirm_reset_password'),
    url(r'^search$', 'moneyclub.member.views.search'),
)