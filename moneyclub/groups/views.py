from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from moneyclub.models import *
from moneyclub.forms import *
from django.db import transaction 
from django.http import HttpResponse, HttpResponseRedirect, Http404
import operator
import json
from django.utils import simplejson

from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail


from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import *

from moneyclub.ystockquote import *

@login_required
def get_photo_group(request, id):
    entry = get_object_or_404(Group, id=id)
    if not entry.picture:
        raise Http404
    content_type = guess_type(entry.picture.name)
    return HttpResponse(entry.picture, mimetype=content_type)

@login_required
def get_photo_article(request, id):
    entry = get_object_or_404(Article, id=id)
    if not entry.picture:
        raise Http404
    content_type = guess_type(entry.picture.name)
    return HttpResponse(entry.picture, mimetype=content_type)

@login_required
def club_home(request,id):
    context = {}    

    try:
        g=Group.objects.get(id=id);
    except ObjectDoesNotExist:
        HttpResponseRedirect(reverse('homepage'))

    memberships = GroupMembership.objects.filter(group = id)
    score = 0
    for membership in memberships:
        score = score + membership.points
    
    #all the keywords for the group to be display4ed in separate blocks.
    str1= g.keywords
    context['keywords'] =str1.split(",")
    context['group'] = g
    
    #all the articles of the group
    all_articles = []
    articles = Post.objects.filter(groupId=g)
    for article in articles:
        if article.articleType == 1:
            article = article.article
            all_articles.append(article)
        else:
            article = article.event
            all_articles.append(article)
    context['articles'] = all_articles
    
    stocks= g.group_stock.all()

    events = Event.objects.filter(groupId = g)
    context['events'] = events
    
    context['stocks']=stocks
    context['score'] = score
    context['group_owner'] = g.owner
    is_member = False
    try:
        member = GroupMembership.objects.get(user=request.user, group = g)
        is_member = True
    except:
        pass

    context['is_member'] = is_member
    #all members of the group arranged by decreasing number of points
    m = GroupMembership.objects.filter(group=g).order_by('-points').exclude(user=g.owner)
    context['members'] = m[:5]
    if len(m) > 5:
        context['more_members_count'] = len(m) - 5
        context['more_members'] = "yup"
    return render(request, 'moneyclub/group_home_page.html', context) 

@login_required   
def club_create(request):
    return render(request, 'moneyclub/create_moneyclub.html',{})
    
@login_required
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


@login_required
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
        

@login_required
@transaction.commit_on_success  
def add_members(request):
    context={}
    if request.method=="GET":
        add_members_generic(request)
    if not 'email' in request.POST or not request.POST['email'] or request.method=="GET":
        add_members_generic(request)
    
    try:
        grp_name = Group.objects.get(name=request.POST['select_group'])
    except:
        grp_name="!none"
    
    #see if a username is entered and user exists
    try:
            u=User.objects.get(username=request.POST['email'])
            
            #check if already invited
            try:
                i = Invite.objects.get(groupId=grp_name,theInvitedOne=u)
                context['message']= "user already invited"
                return render(request, 'moneyclub/adduser_success.html', {'message':'User already invited to money club!'})
            except:
                pass               
            
            #if not invited
            i=Invite(groupId=grp_name,invitedBy=request.user,theInvitedOne=u)
            context['message'] = "User invited"
            i.save()
            return render(request, 'moneyclub/adduser_success.html', {'message':'User invited to money club!'})
        
    except:
            pass
        
    ###if email entered
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
You have an invite from the group %s 
Please click the link below to
verify your email address and complete the registration of your account:

  http://%s
""" % (grp_name.name, request.get_host())

        email = EmailMessage(subject="Invite to a Money Club!",
              body= email_body,
              from_email=settings.EMAIL_HOST_USER,
              to=[request.POST['email']])
        
        email.send()
        
    return render(request, 'moneyclub/adduser_success.html', {})
 

@login_required
def view_group_members2(request):
    context={}
    if not request.POST:
        return render(request, 'moneyclub/view_group_members2.html', {'error':"This "})
    print request.POST['select_group']
    
    
    
    
    if request.method=="GET":
        view_group_members1(request)
    if not 'select_group' in request.POST or not request.POST['select_group']:
        view_group_members1(request)
    try:
        g=Group.objects.get(name=request.POST['select_group'])
        #check if user owns this group
        if not g.owner==request.user:
            context['errors']="Privilege restriction. You cannot access the page. Sorry."
            return render(request, 'moneyclub/errors.html', context)
        
        members=GroupMembership.objects.filter(group=g).order_by('-points') 
        return render(request, 'moneyclub/view_group_members2.html', {'members':members})
    except:
        context['errors']="Group does not exist"
        return render(request, 'moneyclub/errors.html', context)
    
    
    
    
    

@login_required
def view_group_members1(request):
    
    grp=Group.objects.filter(owner=request.user)
    #owns no groups
    if grp.count()==0:
        return render(request, 'moneyclub/create_moneyclub.html', {})
    return render(request, 'moneyclub/view_group_members1.html', {'groups':grp})
        

@login_required
def only_view_group_members(request,grpId):
    context ={}
    errors=[]
    context['errors']=errors
    try:
        grp=Group.objects.get(id=grpId)
    except:
        errors.append("Group does not exist")
        return render(request, 'moneyclub/errors.html', context)
    members=GroupMembership.objects.filter(group=grp).order_by('-points') 
    context['members']=members
    
    #get group data
    memberships = GroupMembership.objects.filter(user=request.user)    
    groups = [membership.group for membership in memberships]
    context['groups'] = groups
    
    # no groups as of now.
    if len(groups)==0:
        context['no_groups'] = "true"
        
    
    #get stock data
    stocks = UserStockOfInterest.objects.filter(user=request.user)
    
    
    
    context['stocks'] = stocks
    context['errors'] = errors
    
    
    return render(request, 'moneyclub/only_view_group_members.html', context)
    

@login_required
def menu(request):
    return render(request, 'moneyclub/Menu.html', {})


@login_required
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


@login_required
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

@login_required
@transaction.commit_on_success
def get_group_description(request,id1):
    try:
        g=Group.objects.get(id=id1)
    except:
        return render(request, 'moneyclub/errors.html', {'errors':"No group found."})
    return g.description

@login_required
@transaction.commit_on_success
def article(request,articleID):
    errors=[]
    context = {}
    deletable = []
    try:
        article = Post.objects.get(id=articleID)
        if article.articleType==1:
            article = article.article
            #print "this is an article"
        else :
            article = article.event
            #print "this is an event"
        group = article.groupId
        
    except ObjectDoesNotExist:
        errors.append('Article not found')
        context['errors'] = errors
        return render(request, '/moneyclub/errors.html',context)
    if article.user == request.user or is_admin(request.user, group):
        deletable=True

    comments = article.comment_for_article.all()
    context['comments'] = comments
    context['article']=article
    context['group'] = group
    context['errors'] = errors
    context['upvote'] = len(article.article_upvote.all())
    context['downvote'] = len(article.article_downvote.all())
    context['deletable'] = deletable
   
    return render(request, 'moneyclub/article.html', context)


@login_required
@transaction.commit_on_success
def delete_post(request, article_id):
    errors = []
    context = {}
    group = []
    try:
        article_to_delete = Post.objects.get(id=article_id)
        group = article_to_delete.groupId
        composer = article_to_delete.user
        membership = GroupMembership.objects.get(user=composer, group = group)
        membership.points = membership.points-10
        membership.save()
        article_to_delete.delete()
    except ObjectDoesNotExist:
        errors.append('delete failed')
        context['errors']= errors
        return render(request, '/moneyclub/errors.html',context)
    if not group:
        errors.append('group not found')
        context['errors']= errors
        return render(request, '/moneyclub/errors.html',context)
    return HttpResponseRedirect(reverse('grouphomepage', args=(group.id,)), context)


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
        return render(request, 'moneyclub/errors.html', context)
    groupID = request.POST['group_id']
    
    try:
        group1=Group.objects.get(id=groupID)
        
    except:
        return render(request, 'moneyclub/errors.html', {'errors':"error finding Group."})
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        
        errors.append('You are not a member of the given group.')
        context['errors'] = errors
        context['status'] = 'failure'
        #return HttpResponseRedirect(reverse('grouphomepage', args=(group1.id,)), context)
        return render(request, 'moneyclub/errors.html', context)
   
    
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
        return render(request, 'moneyclub/errors.html', context)

   
    article = form.save()
    try:
        member = GroupMembership.objects.get(user = request.user, group = group1)
        member.points = member.points + 10
        member.save()
    except:
        pass
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
        errors.append('this is not a post request')
        context['errors'] = errors
        context['stat'] = 'failure'
        HttpResponse(json.dumps(context), mimetype='application/json')

    if not 'group_id' in request.POST or not request.POST['group_id']:
        print 'Not a group specified'
        errors.append('Not a group specified')
        context['errors'] = errors
        context['stat'] = 'failure'
        HttpResponse(json.dumps(context), mimetype='application/json')

    groupID = request.POST['group_id']
    try:
        group1=Group.objects.get(id=groupID)
    except:
        return render(request, 'moneyclub/errors.html', {'errors':"Error handling groups"})
    group_list=GroupMembership.objects.filter(group=group1).values_list('user', flat=True)
    if request.user.id not in group_list:
        errors.append('You are not a member of the given group.')
        context['errors'] = errors
        context['stat'] = 'failure'
        return HttpResponse(json.dumps(context), mimetype='application/json')
   
    
    new_entry = Event(groupId =group1,user=request.user,articleType=2)
    #new_entry.save()
    form = CreateEventForm(request.POST, instance=new_entry   )
    if not form.is_valid():
       
        errors.append('Invalid form')
        context['errors'] = errors
        context['stat'] = 'failure'
        return HttpResponse(json.dumps(context), mimetype='application/json')

    event = form.save()
    try:
        member = GroupMembership.objects.get(user = request.user, group = group1)
        member.points = member.points + 10
        member.save()
    except:
        pass
    context['stat'] = 'success'
    context['redirect'] =  "/moneyclub/groups/article/%s" % event.id

    return HttpResponse(json.dumps(context), mimetype='application/json')


@login_required
@transaction.commit_on_success

def add_comment_on_article(request,groupID,articleID):
    errors = []
    context = {}
       
    if request.method=='GET':
        errors.append('Not a post.')
        context['errors'] = errors
        context['stat'] = 'failure'
        return HttpResponse(json.dumps(context), mimetype='application/json')
    
    #check for missing fields
    if not 'comment' in request.POST or not request.POST['comment']:
        errors.append('comment is required')
        context['errors'] = errors
        context['stat'] = 'failure'
        return HttpResponse( json.dumps(context), mimetype='application/json')
    
    try:
        article = Post.objects.get(id=articleID)
    except ObjectDoesNotExist:
        errors.append('article not found')
        context['errors'] = errors
        context['stat'] = 'failure'
        return HttpResponse( json.dumps(context), mimetype='application/json')
    
    #check if poster is a member of the group and is not blocked
    try:
        group1=Group.objects.get(id=groupID)

        group_list=GroupMembership.objects.filter(group=group1, blocked=0).values_list('user', flat=True)
        
        
    except ObjectDoesNotExist:
        errors.append('group not found')
        context['errors'] = errors
        context['stat'] = 'failure'
        return HttpResponse( json.dumps(context), mimetype='application/json')
    if request.user.id not in group_list:
        errors.append('You are not a member of the given group, or are blocked.')
        context['errors'] = errors 
        context['stat'] = 'failure'
        return HttpResponse( json.dumps(context), mimetype='application/json')
        
    
    #check if article belongs to that group
    
    try:
        a=Post.objects.get(id=articleID)
        if a.articleType==1:
            a = a.article
        else :
            a = a.event
        
    except ObjectDoesNotExist:
        errors.append('Article not found')
        context['stat'] = 'failure'
        context['errors'] = errors
        return HttpResponse(json.dumps(context), mimetype='application/json')

    if a.groupId != group1:
        errors.append('Error matching article to group')
        context['stat'] = 'failure'
        context['errors'] = errors
        return HttpResponse( json.dumps(context), mimetype='application/json')
        
   
    comm = request.POST['comment']
    print a
    #save article
    new_entry = Comment(articleId=a, commentBy=request.user,comment=comm)
    new_entry.save()

    
    #context['comments'] = Comment.objects.filter(articleId=articleID)    
    #context['article']=article
    #context['errors'] = errors    
    print articleID
    context['stat'] = 'success'
    context['redirect'] =  "/moneyclub/groups/article/%s" % articleID


    return HttpResponse(json.dumps(context), mimetype='application/json')


@login_required
def get_all_articles(request):
    a=Article.objects.all()
    return render(request, 'moneyclub/temp.html', {'items':a})


@login_required
def member_management(request, groupID):
    context = {}
    grp=Group.objects.filter(owner=request.user)
    context['groups'] = grp
    context['joined_groups'] = GroupMembership.objects.filter(user=request.user) 

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
        allinfo = get_all(stock.stock_name)

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
    

    if not 'stock_name' in request.POST or not request.POST['stock_name']:
        errors.append('A stock name is needed')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    stock_name = request.POST['stock_name']
    stockinfo = get_all(stock_name)

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

@login_required
def is_admin(user, group):
    # check whether the user is an admin, who has the authority

    try:
        #membership = user.groupmembername.get(group=group)
        membership = GroupMembership.get(user=user, group=group)
        return membership.is_admin
    except:
        return render('moneyclub/errors.html', {'errors':"Error resolving admininstrator status. Is_Admin?"})
    
    
@login_required
@transaction.commit_on_success
def join_group(request,id1):
  try:
    g=Group.objects.get(id=id1)
    
    #check if user is already part of the given group
    if GroupMembership.objects.filter(user=request.user,group=g).count()>0:
        return render(request, 'moneyclub/errors.html', {'errors':"You are already a member."})
    
    gm = GroupMembership(user=request.user,group=g)
    gm.save()
        
    
    return render(request, 'moneyclub/success.html', {'message':"Request sent to group owner!",'group_join':"TRUE"})
  except:
    return render(request, 'moneyclub/errors.html', {'errors':"Joining group action not allowed for this group."})
    
@login_required
def newsfeed(request):
    context = {}
    errors = []
    
    all_articles= [] 
    events = []
    context['errors']= errors
    
    

    #find the groups the user has joined
    gm=GroupMembership.objects.filter(user=request.user)
    a= "yup" 
    print "YYY"
    #get all memberships
    for membership in gm:
         
        a = Post.objects.filter(groupId=membership.group).order_by('-datetime')[0:5]
        
        #assign type
        for item in a:
            if item.articleType==1:
                item=item.article
                all_articles.append(item)
                print " article "
            else:
                item=item.event
                all_articles.append(item)
                print " event "
        
    
    context['articles'] = all_articles
      
    
    #reused from home
    memberships = GroupMembership.objects.filter(user=request.user)
    score = 0
    for membership in memberships:
        score = score + membership.points
        
    
    groups = [membership.group for membership in memberships]
    # no groups as of now.
    if len(groups)==0:
        context['no_groups'] = "true"
    context['groups'] = groups  
    context['events'] = events
    try:

        profile = UserProfile.objects.get(user=request.user) 
        if not profile.profilepicture:
            context['no_pic']="T"
    except ObjectDoesNotExist:
        errors.append('Profile not found. Create your profile.')
        context['no_pic']="T"
    print request.user.username
    try:
        member = Member.objects.get(user=request.user)
        
        memberships = GroupMembership.objects.filter(user=request.user)
        
        stocks = UserStockOfInterest.objects.filter(user=request.user)

        print "amey"
        context['events'] = Event.objects.filter(user=request.user)
        print "amey2"
        if len(context['articles'])==0:
            context['no_article'] = "T"
        context['score'] =score
        context['member'] = member
        context['groups'] = groups
        context['stocks'] = stocks
        context['errors'] = errors
        print "amey3"
        return render(request, 'moneyclub/newsfeed.html', context)
    except:
        print "amey4"
        return render(request, 'moneyclub/errors.html', {'errors':"Error while resolving database query.."})


@login_required
def temp(request):
    return render(request, 'moneyclub/temp.html', {})

@login_required
def findgroups(request):
    context ={}
    sorted_groups= []
    
    grps= Group.objects.all().order_by('id')
    
    for grp in grps:
        memberships = GroupMembership.objects.filter(group=grp)
        score = 0.0
        for membership in memberships:
            score = score + membership.points

        
        context[grp] = score
    
    sorted_x = sorted(context.iteritems(), key=operator.itemgetter(1))
    i=1
    for item in sorted_x:
        sorted_groups.append(sorted_x[len(sorted_x)-i])
        i+=1   
    
    
    context['groups'] = sorted_groups
    
    context['new_groups'] = Group.objects.all().order_by('-id')[0:5]
    print context['new_groups']
    return render(request, 'moneyclub/findgroups.html', context)
        


@login_required
@transaction.commit_on_success
def general_data_to_be_included_in_requests(request):
    context = {}
    errors= []
    
    #get group data
    memberships = GroupMembership.objects.filter(user=request.user)    
    groups = [membership.group for membership in memberships]
    context['groups'] = groups
    
    # no groups as of now.
    if len(groups)==0:
        context['no_groups'] = "true"
        
    #get stock data
    stocks = UserStockOfInterest.objects.filter(user=request.user)   
    context['stocks'] = stocks
    
    context['errors'] = errors
    return context

@login_required
def view_invites(request):
    try:
        i=Invite.objects.filter(theInvitedOne=request.user)
        return render(request, 'moneyclub/view_invites.html', {'invites':i})
    except:
        return render(request, 'moneyclub/errors.html', {'errors':"Error while returning invites"})

@login_required
@transaction.commit_on_success
def accept_invites(request,id1):
    context = {}
    errors= []
    
    #get group data
    memberships = GroupMembership.objects.filter(user=request.user)    
    groups = [membership.group for membership in memberships]
    context['groups'] = groups
    
    # no groups as of now.
    if len(groups)==0:
        context['no_groups'] = "true"
        
    #get stock data
    stocks = UserStockOfInterest.objects.filter(user=request.user)   
    context['stocks'] = stocks
    
    context['errors'] = errors
    try:
        #check if user is actually invited
        g=Group.objects.get(id=id1)
        print "a"
        i=Invite.objects.filter(theInvitedOne=request.user,groupId=g)
        print "b"
        if not i:
            return render(request, 'moneyclub/errors.html', {'errors':"You are not invited to the group"})
            print "c"
        
        #check if already a member
        print "k"
        member= GroupMembership.objects.filter(user=request.user,group=g)
        print "m"
        if GroupMembership.objects.filter(user=request.user,group=g).count() >1:
            return render(request, 'moneyclub/errors.html', {'errors':"Error in Db"})
            
            
        print "d"
        if member:
            i.delete()
            print "e"
            return render(request, 'moneyclub/errors.html', {'errors':"You are already a member"})
        
        
        else:
            gm=GroupMembership(user=request.user,group=g)
            print "f"
            gm.save()
            return club_home(request,id1)
    except:
        print "g"
        return render(request, 'moneyclub/errors.html', {'errors':"Cannot accept invites at this time"})
    
    
    
