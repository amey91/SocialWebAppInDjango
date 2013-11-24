from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from moneyclub.models import *
from moneyclub.forms import *
from moneyclub.groups.forms import *
from django.db import transaction 
from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import *


def get_photo_group(request, id):
    entry = get_object_or_404(Group, id=id)
    if not entry.picture:
        raise Http404
    content_type = guess_type(entry.picture.name)
    return HttpResponse(entry.picture, mimetype=content_type)


def club_home(request,id):
    print "club_home called"
    
    context = {}    
 
    
    g=Group.objects.get(id=id);
    
	#all the keywords for the group to be display4ed in separate blocks.
	str1= g.keywords
    context['keywords'] =str1.split(",")
	
	#all the articles of the group
	articles = g.articleofgroup.all()
	context['articles']=articles
	
	#all members of the group arranged by decreasing number of points
	m = GroupMembership.objects.filer(group=g).orderBy(points)
	context['members'] = m
    return render(request, 'moneyclub/group_home_page.html', context)
    
   
def club_create(request):
    return render(request, 'moneyclub/create_moneyclub.html',{})
    
@transaction.commit_on_success
def club_create_submit(request):
    print "club_create called"
    errors = []
    context = {}    
    if request.method=='GET':
            return render(request, 'moneyclub/create_moneyclub.html', context)
    #check for missing fields
    if not 'name' in request.POST or not request.POST['name']:
        print 'Group Name is required'
        errors.append('Group Name is required')
    if not 'description' in request.POST or not request.POST['description']:
        print 'A short group description is required.'
        errors.append('A short group description is required.')
    if len(Group.objects.filter(name__iexact=request.POST['name'])) > 0:
        print 'Group name is already taken.'
        errors.append('Group name is already taken.')
    if errors:
            context['errors']= errors
            return render(request, 'moneyclub/create_moneyclub.html', context)
    
    new_entry = Group(owner=request.user)
    form = CreateGroupForm(request.POST, request.FILES, instance=new_entry )
    
    if not form.is_valid():         
        context['form'] = form
        print "form is not valid"
        return render(request, 'moneyclub/create_moneyclub.html', context)
    
    #if you don't want to use model forms: 
    name=request.POST['name']
    owner = request.user
    description = request.POST['description']
    keywords = request.POST['keywords']
    g = Group(name=name,owner=owner,description=description,keywords=keywords)
    g.save()
    print "group saved"
    print "group name:"+g.name
    print "group id:"+str(g.id)
    """
    form.save()
    errors.append("Group created successfully!")
    context['errors']=errors
    g=Group.objects.get(name=request.POST['name']);
    """
    context['group_name'] = g.name
    context['description'] = g.description
    str1= g.keywords
    context['keywords'] =str1.split(",") 
    context['id']=g.id
    return render(request, 'moneyclub/group_home_page.html', context)

@transaction.commit_on_success
def add_members_generic(request):
    context={}
    grp = Group.objects.filter(owner=request.user)
    if grp.count()>0:
        #if user owns some group
        #get all groups which user owns
        context['group_ids']=grp
        groups = Group.objects.filter(owner=request.user)
        context['groups']=groups
        return render(request, 'moneyclub/adduser.html', context)
    else:
        club_create(request)
        

@transaction.commit_on_success   
def add_members(request):
    context={}
    if request.method=="GET":
        add_members_generic(request)
    if not 'email' in request.POST or not request.POST['email'] or request.method=="GET":
        add_members_generic(request)
        
    #get group name from group id
    grp_name=Group.objects.get(name=request.POST['select_group'])
 
    #User already joined money club       
    if len(User.objects.filter(email=request.POST['email'])) > 0:   
        U=User.objects.get(email=request.POST['email'])
        i=Invite(groupId=grp_name,invitedBy=request.user,theInvitedOne=U)
        g=GroupMembership(user=U,group=grp_name)
        g.save()
        i.save()    
    else:
        email_body = """
You have been invited to Money Club!! :)
You have an invite from the group " """ +grp_name.name +""""
""" 
        send_mail(subject="Invite to a Money Club!",
            message=email_body,
              from_email="invites@grumblr.com",
              recipient_list=[request.POST['email']])
        
    return render(request, 'moneyclub/adduser_success.html', {})
 

def view_group_members2(request):
    context={}
    print request.POST['select_group']
    if request.method=="GET":
        view_group_members1(request)
    if not 'select_group' in request.POST or not request.POST['select_group']:
        view_group_members1(request)
    g=Group.objects.get(name=request.POST['select_group'])
    members=GroupMembership.objects.filter(group=g).order_by('-points')        
    return render(request, 'moneyclub/view_group_members2.html', {'members':members})


def view_group_members1(request):
    grp=Group.objects.filter(owner=request.user)
    #owns no groups
    if grp.count()==0:
        return render(request, 'moneyclub/create_moneyclub.html', {})
    return render(request, 'moneyclub/view_group_members1.html', {'groups':grp})
        
            
def menu(request):
    return render(request, 'moneyclub/Menu.html', {})


@transaction.commit_on_success   
def block_member(request,id1,id2):
    u=User.objects.get(id=id2)
    g=Group.objects.get(id=id1)
    b=GroupMembership.objects.get(user=u,group=g)
    b.blocked=1
    b.save()
    return render(request, 'moneyclub/menu.html', {})

def get_group_description(request,id1):
    g=Group.objects.get(id=id1)
    return render(request, 'moneyclub/group_home_page.html', {'group':g})


  
def post_article(request,groupID):
    errors = []
    context = {}
       
    """if request.method=='GET':
            return render(request, 'moneyclub/post_articles.html', context)
    #check for missing fields
    if not 'description' in request.POST or not request.POST['description']:
        errors.append('description is required')
    """
    
    #check if poster is a member of the group
    group1=Group.objects.get(id=groupID)
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        errors.append('You are not a member of the given group.')
        
    if errors:
        print errors
        context['errors']= errors
        return render(request, 'moneyclub/post_article.html', context) 
    desc="hello worldasdasdaasd"
    new_entry = Article(groupId =group1,user=request.user,articleType=2,description=desc)
    #new_entry.save()
    article = CreateArticleForm(request.POST, request.FILES, instance=new_entry   )
    if not article.is_valid():         
        context['article'] = article
        return render(request, 'moneyclub/article.html', context)
    article.save()

    context['article'] = article
    context['group'] = group1
    user = request.user
    context['user'] = user
    
    #print this on the user page-> feedback that article has been created
     
    context['errors']=errors
    g=group1
    context['group_name'] = g.name
    context['description'] = g.description
    str1= g.keywords
    context['keywords'] =str1.split(",") 
    context['id']=g.id
    return render(request, 'moneyclub/article.html', context)

    
def add_comment_on_article(request,groupID,articleID):
    errors = []
    context = {}
       
    """if request.method=='GET':
            return render(request, 'moneyclub/post_articles.html', context)
    #check for missing fields
    if not 'comment' in request.POST or not request.POST['comment']:
        errors.append('description is required')
    """
    
    #check if poster is a member of the group
    group1=Group.objects.get(id=groupID)
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        errors.append('You are not a member of the given group.')
        return render(request, 'moneyclub/nopage1.html', context)
    
    #check if article belongs to that grou[
    a=Article.objects.get(id=articleID)
    if a.groupId != group1:
        errors.append('Error matching article to group')
        return render(request, 'moneyclub/nopage2.html', context)
        
    if errors:
            context['errors']= errors
            #?? doubt where to derirect
            return render(request, 'moneyclub/nopage3.html', context) 
    
     #??? doubt change comm from request
    comm = "comm"
    
    #comm = request.POST['comment']
    new_entry = Comment(articleId=a, commentBy=request.user,comment=comm)
    new_entry.save()
    
    
    #print this on the user page-> feedback that article has been created
    errors.append("Group created successfully!")
    context['errors']=errors
    g=group1
    context['group_name'] = g.name
    context['description'] = g.description
    str1= g.keywords
    context['keywords'] =str1.split(",") 
    context['id']=g.id
    return render(request, 'moneyclub/group_home_page.html', context)

    

def get_all_articles(request):
    a=Article.objects.all()
    return render(request, 'moneyclub/temp.html', {'items':a})

def member_management(request, groupID):
    context = {}
    grp=Group.objects.filter(owner=request.user)
    context['groups'] = grp

    return render(request, 'moneyclub/member_management.html',context  );

    
