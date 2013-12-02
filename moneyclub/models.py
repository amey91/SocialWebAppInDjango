from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
# from test.test_imageop import MAX_LEN
# Create your models here.

    

class Group(models.Model):
    name=models.CharField(max_length=30,blank=False)
    owner = models.ForeignKey(User,blank=False,related_name="groupowner")
    description = models.CharField(max_length=10000)
    keywords = models.CharField(max_length=900, blank=True, null=True)
    datetime=models.DateTimeField(auto_now_add='true')
    picture = models.ImageField(upload_to="group_pics", blank=True)
    
    def __unicode__(self):
        return self.name
    
    
class Invite(models.Model):
    groupId = models.ForeignKey(Group, blank=False,related_name="idofgroup")
    # this user has invited someone to the group. He already is a member.
    invitedBy = models.ForeignKey(User, blank=False,related_name="invitedBy")
    # this user will be invited to the group
    theInvitedOne = models.ForeignKey(User, blank= False,related_name="onewhoisinvited")
    datetime=models.DateTimeField(auto_now_add='true')
    
    def __unicode__(self):
        return self.theInvitedOne.username
    
class Post(models.Model):
    #same for both types    
    groupId = models.ForeignKey(Group, blank=False,related_name="%(app_label)s_%(class)s_post")
    #same for both types
    user=models.ForeignKey(User, blank=False,related_name="%(app_label)s_%(class)s_post")
    #articletype = 1 for generic articles
    #articletype = 2 for events
    articleType = models.IntegerField(default=0, blank=True, null=True)
    #same for both types 
    title = models.CharField(max_length=80)
    #date and time of creation 
    #same for both types 
    datetime=models.DateTimeField(auto_now_add='true')
    
    def __unicode__(self):
        return self.title
    class Meta:
        ordering=['-datetime']
        


class Article(Post):
    #same for both types 
    picture = models.ImageField(upload_to="article_pics", blank=True, null=True)

    #picture_url = models.URLField(null=True, blank=True)
    content = models.CharField(max_length=2000, blank=True, null=True)

    
    
class Event(Post):
    #same for both types 
    description = models.CharField(max_length=400,blank=True, null=True)
    #date and time of the actual event
    eventDate = models.DateField()
    eventTime = models.TimeField()
    location = models.CharField(max_length=100)

    
    
    
class Comment(models.Model):
    articleId=models.ForeignKey(Article, related_name="comment_for_article")
    commentBy=models.ForeignKey(User,related_name="commentbyuser")
    comment=models.CharField(max_length=100)
    datetime=models.DateTimeField(auto_now_add='true')
    
    def __unicode__(self):
        return self.comment

    class Meta:
        ordering=['-datetime']

class GroupMembership(models.Model):
    user=models.ForeignKey(User, blank=False,related_name="groupmembername")
    group=models.ForeignKey(Group, blank=False, related_name="groupname")
    points = models.IntegerField(default=0)   
    # 0 == member is NOT blocked
    # 1 == member IS blocked
    blocked = models.IntegerField(default=0)

    points = models.IntegerField(default=0) 
    # type of the member:
    #   False : normal member,
    #   True : admin
    is_admin = models.BooleanField(default=False)
    datetime=models.DateTimeField(auto_now_add='true')

    def __unicode__(self):
        return self.user.username + "  'memberOf'  " + self.group.name 
    
class UserProfile(models.Model):
    user=models.OneToOneField(User,blank=False,related_name="profile")
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birthdate = models.DateField( blank=True, null=True)
    location = models.CharField(max_length=40,blank=True)
    education = models.CharField(max_length=40,blank=True)
    occupation = models.CharField(max_length=80,blank=True)
    profilepicture = models.ImageField(upload_to="profile_pics", blank=True)


    def __unicode__(self):
        return self.user.username

class Member(models.Model):
    user=models.OneToOneField(User,blank=False,related_name="member")
    total_points = models.IntegerField(default=0)
    level=models.IntegerField(default=0)


    def __unicode__(self):
        return self.user.username



class UpVote(models.Model):
    user=models.ForeignKey(User, blank=False, related_name="user_upvote")
    article=models.ForeignKey(Post,blank=False, related_name="article_upvote")

    
class DownVote(models.Model):
    user=models.ForeignKey(User, blank=False, related_name="user_downvote")
    article=models.ForeignKey(Post,blank=False, related_name="article_downvote")



class StockOfInterest(models.Model):
    stock_name=models.CharField(max_length=10)
    price=models.CharField(max_length=10,blank=True,null=True)
    change=models.CharField(max_length=10,blank=True,null=True)
    percent_change=models.CharField(max_length=10,blank=True,null=True)

    def __unicode__(self):
        return self.stock_name
    class Meta:
        abstract = True

class UserStockOfInterest(StockOfInterest):
    user=models.ForeignKey(User,blank=False,related_name="user_stock")

    class Meta:
        app_label = "moneyclub"

class GroupStockOfInterest(StockOfInterest):
    group=models.ForeignKey(Group,blank=False,related_name="group_stock")

    class Meta:
        app_label = "moneyclub"


