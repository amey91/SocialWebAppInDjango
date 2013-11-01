from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
from test.test_imageop import MAX_LEN
# Create your models here.

    

class Group(models.Model):
    name=models.CharField(max_length=30)
    owner = models.ForeignKey(User,blank=False,related_name="groupowner")
    description = models.CharField(max_length=10000)
    keywords = models.CharField(max_length=900)
    datetime=models.DateTimeField(auto_now_add='true')
    
    def __unicode__(self):
        return self.name
    
    
class Invite(models.Model):
    groupId = models.ForeignKey(Group, blank=False,related_name="idofgroup")
    invitedBy = models.ForeignKey(User, blank=False,related_name="invitedBy")
    theInvitedOne = models.ForeignKey(User, blank= False,related_name="onewhoisinvited")
    datetime=models.DateTimeField(auto_now_add='true')
    
class Article(models.Model):
    groupId = models.ForeignKey(Group, blank=False,related_name="articleofgroup")
    user=models.ForeignKey(User, blank=False,related_name="articleby")
    type = models.IntegerField(default=0)
    description = models.CharField(max_length=400,blank=True)
    picture = models.ImageField(upload_to="article_pics", blank=True)
    datetime=models.DateTimeField(auto_now_add='true')
    
    def __unicode__(self):
        return self.description;
    
class Comment(models.Model):
    articleId=models.ForeignKey(Article, related_name="comment_for_article")
    commentBy=models.ForeignKey(User,related_name="commentbyuser")
    comment=models.CharField(max_length=100)
    datetime=models.DateTimeField(auto_now_add='true')
    
    def __unicode__(self):
        return self.comment
    
class GroupMembership(models.Model):
    user=models.ForeignKey(User, blank=False,related_name="groupmembername")
    group=models.ForeignKey(Group, blank=False, related_name="groupname")
    points = models.IntegerField(default=0)    
    datetime=models.DateTimeField(auto_now_add='true')

    def __unicode__(self):
        return self.group
    
class UserProfile(models.Model):
    user=models.ForeignKey(User,blank=False,related_name="usernameformember")
    profilepicture = models.ImageField(upload_to="profile_pics", blank=True)
    total_points = models.IntegerField(default=0)
    level=models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.username