from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from moneyclub.models import *
from moneyclub.forms import *
from django.db import transaction 
from django.http import HttpResponse, HttpResponseRedirect, Http404

import json
from django.utils import simplejson

from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import *

import ystockquote


def get_photo_group(request, id):
    entry = get_object_or_404(Group, id=id)
    if not entry.picture:
        raise Http404
    content_type = guess_type(entry.picture.name)
    return HttpResponse(entry.picture, mimetype=content_type)

def get_photo_article(request, id):
    entry = get_object_or_404(Article, id=id)
    if not entry.picture:
        raise Http404
    content_type = guess_type(entry.picture.name)
    return HttpResponse(entry.picture, mimetype=content_type)


def club_home(request,id):
    context = {}    

    
    g=Group.objects.get(id=id);
    
    #all the keywords for the group to be display4ed in separate blocks.
    str1= g.keywords
    context['keywords'] =str1.split(",")
    context['group'] = g
    
    #all the articles of the group
    articles = Article.objects.filter(groupId=g)
    
    stocks= g.group_stock.all()

    context['articles']=articles
    context['stocks']=stocks
    context['group_owner'] = g.owner
    #all members of the group arranged by decreasing number of points
    m = GroupMembership.objects.filter(group=g).order_by('-points').exclude(user=g.owner)
    context['members'] = m[:5]
    if len(m) > 5:
        context['more_members_count'] = len(m) - 5
        context['more_members'] = "yup"
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
    try: 
        if len(Group.objects.filter(name__iexact=request.POST['name'])) > 0:
            print 'Group name is already taken.'
            errors.append('Group name is already taken.')
    except ObjectDoesNotExist:
        return render(request, 'moneyclub/error.html', context)
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

    g=form.save()
    #add group creator to the group
    membership = GroupMembership(user=request.user, group=g, is_admin=True)
    membership.save()
    print "group saved"
    print "group name:"+g.name
    print "group id:"+str(g.id)
    
    #print success 
    context['group'] = g
    context['message'] = "Group Created Successfully!"
    context['create_group'] = "true"
    return render(request, 'moneyclub/success.html', context)
    
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
    if not request.POST:
        return render(request, 'moneyclub/view_group_members2.html', {'error':"This "})
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
    try:
        u=User.objects.get(id=id2)
        g=Group.objects.get(id=id1)
        
        # check if user who sent request is owner of group
        if not g.owner==request.user:
            return render(request, 'moneyclub/errors.html', {'errors':"Invalid Access"}) 
          
        b=GroupMembership.objects.get(user=u,group=g)
        b.blocked=1
        b.save()
        #return members of the group
        members=GroupMembership.objects.filter(group=g).order_by('-points')
        return render(request, 'moneyclub/view_group_members2.html', {'members':members})
    except:
        return render(request, 'moneyclub/errors.html', {'errors':"Object not found"})


@transaction.commit_on_success   
def unblock_member(request,id1,id2):
    try:
        u=User.objects.get(id=id2)
        g=Group.objects.get(id=id1)
        
        # check if user who sent request is owner of group
        if not g.owner==request.user:
            return render(request, 'moneyclub/errors.html', {'errors':"Invalid Access"}) 
          
        b=GroupMembership.objects.get(user=u,group=g)
        b.blocked=0
        b.save()
        #return members of the group
        members=GroupMembership.objects.filter(group=g).order_by('-points')
        return render(request, 'moneyclub/view_group_members2.html', {'members':members})
    except:
        return render(request, 'moneyclub/errors.html', {'errors':"Object not found"})


def get_group_description(request,id1):
    g=Group.objects.get(id=id1)
    return render(request, 'moneyclub/group_home_page.html', {'group':g})

@login_required
def article(request,articleID):
    errors=[]
    context = {}

    try:
        article = Article.objects.get(id=articleID)
        group = article.groupId
        
    except ObjectDoesNotExist:
        errors.append('Article not found')

    context['article']=article
    context['group'] = group
    context['errors'] = errors

    return render(request, 'moneyclub/article.html', context)




@login_required
@transaction.commit_on_success
def post_article(request):
    errors = []
    context = {}
       
    #if request.method=='GET':
    #       return render(request, 'moneyclub/post_articles.html', context)
    #check for missing fields
    #if not 'description' in request.POST or not request.POST['description']:
    #    errors.append('description is required')
        
    #check if poster is a member of the group
    if not 'group_id' in request.POST or not request.POST['group_id']:
        
        errors.append('Not a group specified')
        context['errors'] = errors
        context['status'] = 'failure'

        #return render(reverse('homepage'), context)
        return HttpResponse(request, context, mimetype='application/json')
    groupID = request.POST['group_id']
    group1=Group.objects.get(id=groupID)
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        
        errors.append('You are not a member of the given group.')
        context['errors'] = errors
        context['status'] = 'failure'
        #return HttpResponseRedirect(reverse('grouphomepage', args=(group1.id,)), context)
        return HttpResponse( context, mimetype='application/json')
   
    
    new_entry = Article(groupId =group1,user=request.user,articleType=1)
    #new_entry.save()
    form = CreateArticleForm(request.POST, request.FILES, instance=new_entry   )

    print "request files:"
    print request.FILES

    if not form.is_valid():
        
        errors.append('Invalid form')
        context['errors'] = errors
        context['stat'] = 'failure'
        context['form'] = form
        #return HttpResponseRedirect(reverse('grouphomepage', args=(group1.id,)), context)
        return HttpResponse( context, mimetype='application/json')

   
    article = form.save()
    
    print article.content
    print article.articleType
    print article.picture
    #context['article'] = article
    context['article_id'] = article.id
    #context['group'] = group1

    
    #print this on the user page-> feedback that article has been created
    context['stat'] = 'success'
    context['success'] = True
#    context['errors']=errors

    context['redirect'] = '/moneyclub/groups/article/%d' % article.id
    return HttpResponseRedirect(reverse('article', args=(article.id,)), context)
    #return HttpResponse(json.dumps(context), mimetype='application/json')
    

@login_required
@transaction.commit_on_success
def start_event(request):
    errors = []
    context = {}
    
    print "start_event"
    if request.method=='GET':
        print "not post`"
        return render(request, 'moneyclub/post_articles.html', context)

    if not 'group_id' in request.POST or not request.POST['group_id']:
        print 'Not a group specified'
        errors.append('Not a group specified')
        context['errors'] = errors
        context['status'] = 'failure'
        return HttpResponse(context, mimetype='application/json')

    groupID = request.POST['group_id']
    group1=Group.objects.get(id=groupID)
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        errors.append('You are not a member of the given group.')
        context['errors'] = errors
        context['status'] = 'failure'
        return HttpResponse( context, mimetype='application/json')
   
    
    new_entry = Event(groupId =group1,user=request.user,articleType=2)
    #new_entry.save()
    form = CreateEventForm(request.POST, instance=new_entry   )
    if not form.is_valid():
        print "form not valid"
        errors.append('Invalid form')
        context['errors'] = errors
        context['status'] = 'failure'
        return HttpResponse( context, mimetype='application/json')

    event = form.save()
    print "event saved"
    context['article'] = event
    context['group'] = group1
    context['errors']=errors

    return HttpResponseRedirect(reverse('article', args=(event.id,)), context)
    

    
def add_comment_on_article(request,groupID,articleID):
    errors = []
    context = {}
       
    if request.method=='GET':
        errors.append('Something went wrong.')
        context['errors'] = errors
        return render(request, 'moneyclub/errors.html', context)
    
    #check for missing fields
    if not 'comment' in request.POST or not request.POST['comment']:
        errors.append('description is required')
    
    
    #check if poster is a member of the group
    group1=Group.objects.get(id=groupID)
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        errors.append('You are not a member of the given group.')
        print 'You are not a member of the given group.'
        context['errors'] = errors 
        return render(request, 'moneyclub/errors.html', context)
    
    #check if article belongs to that group
    a=Article.objects.get(id=articleID)
    if a.groupId != group1:
        errors.append('Error matching article to group')
        
    
    if errors:
            context['errors'] = errors
            return render(request, 'moneyclub/errors.html', context) 
    
    comm = request.POST['comment']
    
    #save article
    new_entry = Comment(articleId=a, commentBy=request.user,comment=comm)
    new_entry.save()    
    article = Article.objects.get(id=articleID)
    context['comments'] = Comment.objects.filter(articleId=articleID)
    
    context['article']=article
    context['errors'] = errors    

    return HttpResponseRedirect('/article.html', context)

    
@login_required
def get_all_articles(request):
    a=Article.objects.all()
    return render(request, 'moneyclub/temp.html', {'items':a})


@login_required
def member_management(request, groupID):
    context = {}
    grp=Group.objects.filter(owner=request.user)
    context['groups'] = grp

    return render(request, 'moneyclub/member_management.html',context  );


@login_required
@transaction.commit_on_success
def group_settings(request, groupID):
    errors = []
    context = {}    
    group = []
    group_to_edit = []
    try:
        group_to_edit = Group.objects.get(id=groupID)
        group = CreateGroupForm(instance=group_to_edit)
    except ObjectDoesNotExist:
        errors.append('Group not found!')

       
    if request.method=='GET':
        context['group'] = group_to_edit
        
        return render(request, 'moneyclub/edit_moneyclub.html', context)
    group = CreateGroupForm(request.POST,request.FILES, instance=group_to_edit) 
    
    try:
        g = Group.objects.get(name=request.POST['name']) 
        if g!=group_to_edit:
            errors.append('The name is already taken')
            
        elif group.is_valid():
            group.save()
            return HttpResponseRedirect(reverse('grouphomepage',args=(group_to_edit.id,)),context)
        else:
            errors.append('required fields are missing')
    
    except ObjectDoesNotExist:
        if  group.is_valid():
    
            group.save()

            return HttpResponseRedirect(reverse('grouphomepage',args=(group_to_edit.id,)),context)
        else:
            errors.append('required fields are missing')
    
    context['group'] = group_to_edit
    
    context['errors'] = errors
    return render(request, 'moneyclub/edit_moneyclub.html', context)
    

@login_required
def get_group_stock(request,group_id):

    print "get_group_stock called"
    context={}
    errors = []
    
    try:
        group = Group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        errors.append('Group not found')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    
    
    stocks = group.group_stock.all()
    
    for stock in stocks:
        allinfo = ystockquote.get_all(stock.stock_name)

        price = allinfo['last_trade_realtime_time']
        stock.price=price if len(price)<6 else price[0:5]

        stock.change=allinfo['change'] if len(allinfo['change'])<6 else allinfo['change'][0:5]
        stock.percent_change=allinfo['change_percent'].strip("\"")
        stock.save()
        
    context={'stocks':stocks}
    
    return render(request, 'xml/stock.xml', context, content_type='application/xml');

@login_required
@transaction.commit_on_success
def add_stock(request):
    context={}
    errors=[]
    group = []
    user = request.user
    print "add stock group"
    if not 'group_id' in request.POST or not request.POST['group_id']:
        print 'group'
        errors.append('Group not specified')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    group_id = request.POST['group_id']
    try:
        group = Group.objects.get(id=group_id)
        print 'found the group'
    except ObjectDoesNotExist:
        errors.append('Group not found')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    # check if the user is admin
    if not is_admin(request.user, group):

        errors.append('You donnot have the authority')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    

    if not 'stock_name' in request.POST or not request.POST['stock_name']:
        errors.append('A stock name is needed')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    stock_name = request.POST['stock_name']
    stockinfo = ystockquote.get_all(stock_name)

    #if UserStockOfInterest.objects.filter(stock_name=stock_name and user==request.user):
    if group.group_stock.filter(stock_name=stock_name):

        errors.append('Stock already added')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(json.dumps(context), mimetype='application/json')
    
    if stockinfo['shares_owned'] =="\"-\"" or stockinfo['shares_owned'] =="N/A":
        errors.append('No matching stock found')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(json.dumps(context), mimetype='application/json')
    print "stock found"
    stock = GroupStockOfInterest(group=group, stock_name=stock_name)
    stock.price=stockinfo['ask_realtime']
    stock.change=stockinfo['change'] if len(stockinfo['change'])<6 else stockinfo['change'][0:5]
    stock.percent_change=stockinfo['change_percent'].strip("\"")
    stock.save()
    context['stock_name']=stock_name
    context['price'] = stock.price
    context['change'] = stock.change
    context['pctchange'] = stock.percent_change
    context['stock_id'] = stock.id
    context['status'] = 'success'
    
    return HttpResponse(json.dumps(context), mimetype='application/json')

@login_required
@transaction.commit_on_success
def delete_stock(request):
    context={}
    errors=[]
    user = request.user
    
    if not 'group_id' in request.POST or not request.POST['group_id']:
        errors.append('Group not specified')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    group_id = request.POST['group_id']
    try:
        group = Group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        errors.append('Group not found')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    # check if the user is admin
    if not is_admin(request.user, group):
        errors.append('You donnot have the authority')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    
    if 'stock_id' in request.POST and request.POST['stock_id']:
        stock_id = request.POST['stock_id']

        try:
            stock_to_delete = GroupStockOfInterest.objects.get(id=stock_id)
            stock_to_delete.delete()
            context['status']='success'
            print 'stock successfully deleted'
            return HttpResponse(json.dumps(context), mimetype='application/json')

        except ObjectDoesNotExist:
            errors.append('delete error!')
            context['status']='failure'
            return HttpResponse(json.dumps(context), mimetype='application/json')
    errors.append('delete error!')
    context['status']='failure'
    
    return HttpResponse(json.dumps(context), mimetype='application/json')

def is_admin(user, group):
    # check whether the user is an admin, who has the authority
    membership = user.groupmembername.get(group=group)
    return membership.is_admin
    

def join_group(request,id1):
    g=Group.objects.get(id=id1)
    
    #check if user is already part of the given group
    if GroupMembership.objects.filter(user=request.user,group=g).count()>0:
        return render(request, 'moneyclub/errors.html', {'errors':"You are already a member."})
    
    #check if already sent the join request
    if Invite.objects.filter(theInvitedOne = request.user, groupId = g).count() > 0:
        return render(request, 'moneyclub/errors.html', {'errors':"You have already sent  join request to this group."})
    
    #send the join request
    i=Invite(groupId = g, invitedBy=request.user, theInvitedOne=request.user)
    i.save()
    
    
    return render(request, 'moneyclub/success.html', {'message':"Request sent to group owner!",'group_join':"TRUE"})
    

def temp(request):
    return render(request, 'moneyclub/simplegraph.html', {})
