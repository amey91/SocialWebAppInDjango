from django.contrib import admin
from moneyclub.models import *

admin.site.register(Group)
admin.site.register(Invite)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(GroupMembership)
admin.site.register(UserProfile)