from django.conf.urls import patterns, include, url

# Generates the routes for the Controller.
# Typical use is a regular expression for a URL pattern, and then the
# action to call to process requests for that URL pattern.
urlpatterns = patterns('',
    url(r'^profile$', 'moneyclub.member.views.view_profile', name='profile'),
    url(r'^profile/$', 'moneyclub.member.views.view_profile', name='profile'),
    url(r'^profile/(?P<uname>\w+)/$', 'moneyclub.member.views.view_profile1', name="others_profile"),
    #url(r'^edit-profile$', 'grumblr.views.edit_profile'),
    url(r'^save-profile$', 'moneyclub.member.views.save_profile'),
    
    url(r'^userphoto/(?P<id>\d+)$', 'moneyclub.member.views.get_photo', name='user-photo'),
    url(r'^reset-password$', 'moneyclub.member.views.reset_password', name='reset_password'),
    url(r'^reset-password-by-email$', 'moneyclub.member.views.reset_password_by_email', name='reset_password_by_email'),
    url(r'^confirm-reset-password-by-email/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'moneyclub.member.views.confirm_reset_password_by_email', name='confirm_reset_password'),
    url(r'^search$', 'moneyclub.member.views.search'),
    url(r'^get-stock-info$', 'moneyclub.member.views.get_user_stock'),
    url(r'^add-stock$','moneyclub.member.views.add_stock'),
    url(r'^delete-stock$','moneyclub.member.views.delete_stock'),
    url(r'^upvote$', 'moneyclub.member.views.upvote', name='upvote'),
    url(r'^downvote$', 'moneyclub.member.views.downvote', name='downvote'),

    url(r'^visit-user/(?P<user_id>\d+)$', 'moneyclub.member.views.visit_user', name='visit_user')

)
