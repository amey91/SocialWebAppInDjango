# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction 
from django.http import HttpResponse, Http404, HttpResponseRedirect

from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail

from django.core.mail import EmailMessage

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import *
from django.core import serializers
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder

import random
import hashlib
import json
from django.utils import simplejson

from moneyclub.models import *
from moneyclub.forms import *

from mysite.settings import *


import ystockquote


@login_required
@transaction.commit_on_success
def view_profile(request):
    errors = []
    context = {}
    profile = []
    try:
        profile_to_edit = UserProfile.objects.get(user=request.user) 
        if not profile_to_edit.profilepicture:
            print "no_pic"
            context['no_pic']="T"
        profile = ProfileForm(instance=profile_to_edit)

    except ObjectDoesNotExist:
        errors.append('Profile not found. Create your profile.')
        profile = ProfileForm()
        context['no_pic']= 1

    context['profile'] = profile
    context['errors'] = errors

    return render(request, 'moneyclub/profile.html',context)


@login_required
@transaction.commit_on_success
def view_profile1(request,uname):
    errors = []
    context = {}
    try:
        u=User.objects.get(username=uname)
        profile= UserProfile.objects.get(user=u) 
        context = {'profile': profile, 'errors': errors}
        return render(request, 'moneyclub/profile.html',context)

    except ObjectDoesNotExist:
        errors.append('Sorry, Profile not found. ')
        context['errors']=errors
        return render(request, 'moneyclub/profile.html',context)   


@login_required
@transaction.commit_on_success
def save_profile(request):
    errors = []
    context = {}
    profile = []
    try:
        profile = UserProfile.objects.get(user = request.user)
        print "save_profile: profile found"
    except ObjectDoesNotExist:
        profile = UserProfile(user=request.user,first_name='',last_name='')

    if request.method == 'GET':
        context = {'profile': profile, 'errors': errors}
        return render(request, 'moneyclub/profile.html',context)
    # Creates or Updates a profile
    profileform = ProfileForm(request.POST, request.FILES, instance=profile)
    
    if  not profileform.is_valid():
        context['profile'] = profileform
        context['no_pic'] = True
        return render(request, 'moneyclub/profile.html',context)
    
    profileform.save();
    context = {'profile': profileform, 'errors': errors}


    return HttpResponseRedirect(reverse('profile'),context)

@login_required
def visit_user(request, user_id):
    errors = []
    context = {}

    profile = []
    try:
        user_to_visit = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        errors.append('User not found')
        return HttpResponseRedirect(reverse('homepage'))

    try:
        profile = UserProfile.objects.get(user=user_id)
         
        #profile = ProfileForm(instance=profile)
    except ObjectDoesNotExist:
        context['no_pic']="T"
        

    posts = Post.objects.filter(user = user_to_visit)
    for post in posts:
        if post.articleType ==1:
            post = post.article
        else:
            post = post.event
    events = Event.objects.filter(user = user_to_visit)


    member = Member.objects.get(user=request.user)
    memberships = GroupMembership.objects.filter(user=user_to_visit)
    score = 0
    for membership in memberships:
        score = score + membership.points
    groups = [membership.group for membership in memberships]

    context['visitee'] = user_to_visit
    context['articles'] = posts
    context['events'] = events
    context['score'] = score
    context['member'] = member
    context['groups'] = groups
    context['profile'] = profile
    context['errors'] = errors
    return render(request, 'moneyclub/visitpage.html', context)

@login_required
def get_photo(request, id):
    print "call get_photo"
    profile = get_object_or_404(UserProfile, user_id=id)
    if not profile.profilepicture:
        print "photo not found"
        raise Http404
    print "photo found"
    content_type = guess_type(profile.profilepicture.name)
    return HttpResponse(profile.profilepicture, mimetype=content_type)

@login_required
@transaction.commit_on_success
def reset_password(request):
    context = {}

    if request.method == 'GET':
        context ['form'] = ResetPasswordForm()
        return render(request, 'moneyclub/reset-password.html', context)

    form = ResetPasswordForm(data=request.POST, user=request.user)
    context ['form'] = form

    if not form.is_valid():
        return render(request, 'moneyclub/reset-password.html', context)

    password = form.cleaned_data['new_password']
    user = get_object_or_404(User, id=request.user.id)
    
    user.set_password(password)
    user.save()
    
    return HttpResponseRedirect(reverse('reset_password'),context)
    

@login_required
@transaction.commit_on_success
def reset_password_by_email(request):
    user = get_object_or_404(User, id=request.user.id)

    hash_pwd = hashlib.sha256(user.password.split('$')[2])
    salt = str(random.random())
    hash_pwd.update(salt)
    new_password = hash_pwd.hexdigest()[:8]
    print (new_password)
    user.set_password(new_password)
    user.save()

    token = default_token_generator.make_token(user)


    email_body = """
Your password has been reset: 
    %s

Please click the link below to verify your email address and complete 
the resetting process with the new_password given, and reset your password
as soon as possible:

  http://%s%s
""" % (new_password, request.get_host(), 
       reverse('confirm_reset_password', args=(user.username, token)))

    email = EmailMessage(subject="Verify your email address",
              body= email_body,
              from_email=settings.EMAIL_HOST_USER,
              to=[user.email])
    
    email.send()

    context = {}
    context['email'] = user.email
    return render(request, 'moneyclub/reset-password-needs-confirmation.html', context)

@transaction.commit_on_success
def confirm_reset_password_by_email(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    return reset_password(request)

@login_required
def search(request):
    errors = []
    
    query = request.POST['query']
    query = query.lower()
    groups = Group.objects.all()
    users = User.objects.all()
    this_user = User.objects.get(id=request.user.id)
    
    groups_retrieved = []
    users_retrieved = []



    # Retrieve grumbler if his name matching the query
    for user in users:
        username = user.username.lower()
        if query in username:
            users_retrieved.append(user) 
    if len(users_retrieved)==0:
        errors.append('No users match the query.')
    # Retrieve grumbl if the users have an grumbl matching the query

    for group in groups:
        groupname = group.name.lower()
        if query in groupname :
            groups_retrieved.append(group) 
    if len(groups_retrieved)==0:
        errors.append('No groups match the query.')

    
    context = {'groups_retrieved' : groups_retrieved,\
                'users_retrieved' : users_retrieved, 'errors': errors}
    return render(request, 'moneyclub/search_results.html', context)



@login_required
def get_user_stock(request):
    print "get_user_stock called"
    errors = []
    """
    stock = UserStockOfInterest(user=request.user, stock_name='GOOG')
    stock.save()
    print "stock saved"
    """
    stocks = UserStockOfInterest.objects.filter(user=request.user)
    
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
    user = request.user

    if not 'stock_name' in request.POST or not request.POST['stock_name']:
        errors.append('A stock name is needed')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(request, context, mimetype='application/json')
    stock_name = request.POST['stock_name']
    stockinfo = ystockquote.get_all(stock_name)

    #if UserStockOfInterest.objects.filter(stock_name=stock_name and user==request.user):
    if user.user_stock.filter(stock_name=stock_name):

        errors.append('Stock already added')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(json.dumps(context), mimetype='application/json')
    
    if 'shares_owned' not in stockinfo or stockinfo['shares_owned'] =="\"-\"" or stockinfo['shares_owned'] =="N/A":
        errors.append('No matching stock found')
        context['status'] = 'failure'
        context['errors'] = errors
        return HttpResponse(json.dumps(context), mimetype='application/json')

    
    context['stat'] = 'success'
    context['redirect'] = '/'
    #return HttpResponseRedirect(reverse('homepage'),context)
    return HttpResponse(json.dumps(context), mimetype='application/json')

@login_required
@transaction.commit_on_success
def delete_stock(request):
    context={}
    errors=[]
    if 'stock_id' in request.POST and request.POST['stock_id']:
        stock_id = request.POST['stock_id']

        try:
            stock_to_delete = UserStockOfInterest.objects.get(id=stock_id)
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
@transaction.commit_on_success

def upvote(request):

    context = {}
    errors=[]

    

    if 'article_id' in request.POST and request.POST['article_id']:
        article_id = request.POST['article_id']
        try:
            article_to_vote = Post.objects.get(id=article_id)
        except ObjectDoesNotExist:
            errors.append('article not found!')
            context['status']='failure'
            return HttpResponse(json.dumps(context), mimetype='application/json')
        
        try:
            vote = UpVote.objects.get(user=request.user, article=article_to_vote)    
            errors.append('You can upvote this post only once')
        except ObjectDoesNotExist:
            vote = UpVote(user=request.user, article=article_to_vote)
            vote.save()

            try:
                downvote = DownVote.objects.get(user=request.user, article=article_to_vote)
                downvote.delete()
                context['downvoted'] = True
            except ObjectDoesNotExist:
                context['downvoted'] = False
            try:

                #print 'reward composer'
                # reward the composer
                composer = article_to_vote.user

                member = composer.member
                member.total_points = member.total_points+5
                member.save()
                #print 'reward groups '+str(article_to_vote.groupId)
                group = article_to_vote.groupId
                #print 'group found'
                membership = request.user.groupmembername.get(group=group)
                #print 'membership found'
                membership.points = membership.points+5
                membership.save()

                context['status'] = 'success'
                #print 'upvote successfully'
                return HttpResponse(json.dumps(context), mimetype='application/json')
            except:
                errors.append('UpVote failed')
    context['errors'] = errors
    context['status']='failure'
    
    return HttpResponse(json.dumps(context), mimetype='application/json')

@login_required
@transaction.commit_on_success
def downvote(request):
    context = {}
    errors=[]


    
    if 'article_id' in request.POST and request.POST['article_id']:
        article_id = request.POST['article_id']
        try:
            article_to_vote = Post.objects.get(id=article_id)
        except ObjectDoesNotExist:
            errors.append('article not found!')
            context['status']='failure'
            return HttpResponse(json.dumps(context), mimetype='application/json')
        try:
            vote = DownVote.objects.get(user=request.user , article=article_to_vote)   
            errors.append('You can downvote this post only once')
            
            #print 'vote found'
        except ObjectDoesNotExist:
            vote = DownVote(user=request.user, article=article_to_vote)
            vote.save()
            try:
                upvote = UpVote.objects.get(user=request.user, article=article_to_vote)
                upvote.delete()
                context['upvoted'] = True
            except ObjectDoesNotExist:
                context['upvoted'] = False
            try:
                # downvote the composer
                #print 'reward composer'
                composer = article_to_vote.user

                member = composer.member
                member.total_points = member.total_points-2
                member.save()

                group = article_to_vote.groupId
                membership = request.user.groupmembername.get(group=group)
                membership.points = membership.points-2
                membership.save()
                # penalize the voter
                voter = request.user

                member = voter.member
                member.total_points = member.total_points-1
                member.save()

                group = article_to_vote.groupId
                membership = request.user.groupmembername.get(group=group)
                membership.points = membership.points-1
                membership.save()

                context['status'] = 'success'
                #print 'downvote successfully'
                return HttpResponse(json.dumps(context), mimetype='application/json')
            except:
                errors.append('DownVote failed')
        
    context['status']='failure' 
    

    return HttpResponse(json.dumps(context), mimetype='application/json')

