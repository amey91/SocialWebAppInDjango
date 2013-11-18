from django.conf.urls import patterns, include, url

# Generates the routes for the Controller.
# Typical use is a regular expression for a URL pattern, and then the
# action to call to process requests for that URL pattern.
urlpatterns = patterns('',
    #url(r'^temp', 'moneyclub.groups.views.temp'),
    url(r'^$', 'moneyclub.groups.views.menu'),
    url(r'^home', 'moneyclub.groups.views.club_home'),
    url(r'^club_create_submit', 'moneyclub.groups.views.club_create_submit'),
    url(r'^club_create', 'moneyclub.groups.views.club_create'),
    url(r'^get_photo_group/(?P<id>\d+)/$', 'moneyclub.groups.views.get_photo_group'),
    url(r'^add_members_generic', 'moneyclub.groups.views.add_members_generic'),
    url(r'^add_members/$', 'moneyclub.groups.views.add_members'),
    
    url(r'^view_group_members2/$', 'moneyclub.groups.views.view_group_members2'),
    url(r'^view_group_members1/$', 'moneyclub.groups.views.view_group_members1'),
    url(r'^block_member/(?P<id1>\d+)/(?P<id2>\d+)/$', 'moneyclub.groups.views.block_member'),
    url(r'^get_group_description/(?P<id1>\d+)/$', 'moneyclub.groups.views.get_group_description'),
    url(r'^post_article/(?P<groupID>\d+)/$', 'moneyclub.groups.views.post_article', name="post_article"),
    url(r'^add_comment_on_article/(?P<groupID>\d+)/(?P<articleID>\d+)/$', 'moneyclub.groups.views.add_comment_on_article'),

    url(r'^member-management/(?P<groupID>\d+)/$', 'moneyclub.groups.views.member_management', name='member_management'),
    #url(r'^profile/(?P<uname>\w+)/$', 'grumblr.profile.views.profile1'),
	#url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'grumblr/signin.html'}),
    # Route to logout a user and send them back to the login page
    #url(r'^logout$', 'django.contrib.auth.views.logout_then_login'),
    #url(r'^becomefollower/(?P<uname>\w+)/$', 'grumblr.views.becomefollower1'),
    #url(r'^add_comment_redirect/(?P<commentid>\d+)/$', 'grumblr.views.add_comment_redirect'),
    #url(r'^add_comment/(?P<commentid>\d+)/$', 'moneyclub.views.add_comment'),
    #url(r'^grumblquantity/(?P<uname>\w+)/$', 'grumblr.views.somebodysgrumbls'),
       
)
