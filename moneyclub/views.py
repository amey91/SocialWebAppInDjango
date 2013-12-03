from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from moneyclub.models import *
from moneyclub.forms import *
from django.db import transaction 
from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import *

#from mysite import settings


def group_home(request):
    context = {}
    keywords = {}
    
    
    g=Group.objects.get(id=1);
    context['group_name'] = g.name
    context['description'] = g.description
    context['keywords'] = g.keywords
    
    return render(request, 'moneyclub/group_home_page.html', context)
    
def create_group(request):
    #setup variables
    errors = []
    context = {}
        
    #check for missing fields
    if not 'group_name' in request.POST or not request.POST['group_name']:
        errors.append('Group Name is required')
    if not 'description' in request.POST or not request.POST['description']:
        errors.append('A short group description is required.')
        
    name=request.POST['group_name']
    #changetouser CHANGE
    owner = "Myself"#request.POST['owner']
    description = request.POST['description']
    keywords = request.POST['keywords']
    g = Group(name=name,owner=owner,description=description,keywords=keywords)
    g.save()
    return render(request, 'moneyclub/group_create_successful.html', {})

@login_required
def home(request):
    errors = []
    context = {}
    all_articles=[]
    profile = []
    member = []
    groups = []
    try:

        profile = UserProfile.objects.get(user=request.user) 

    except ObjectDoesNotExist:
        errors.append('Profile not found. Create your profile.')
        context['no_pic']="T"
    print request.user.username
    score = 0
    try:
        member = Member.objects.get(user=request.user)
        memberships = GroupMembership.objects.filter(user=request.user)
        
        for membership in memberships:
            score = score + membership.points
        groups = [membership.group for membership in memberships]
    except ObjectDoesNotExist:
        pass
    # no groups as of now.
    if len(groups)==0:
        context['no_groups'] = "true"
    stocks = UserStockOfInterest.objects.filter(user=request.user)
    articles = Post.objects.filter(user=request.user)
    for article in articles:
        if article.articleType == 1:
            article = article.article
            all_articles.append(article)
        else:
            article = article.event
            all_articles.append(article)
    context['articles'] = all_articles

    context['events'] = Event.objects.filter(user=request.user)
    if len(context['articles'])==0:
        context['no_article'] = "T"
    context['score'] =score
    context['member'] = member
    context['groups'] = groups
    context['profile'] = profile
    context['stocks'] = stocks
    context['errors'] = errors
    return render(request, 'moneyclub/index.html', context)




def register(request):
    print "register called"
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'moneyclub/signup.html', context)

    errors = []
    context['errors'] = errors

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        print 'form is not valid'
        return render(request, 'moneyclub/signup.html', context)

    # If we get here the form data was valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'])
    new_user.is_active = False
    new_user.save()
    
    token = default_token_generator.make_token(new_user)

    
    email_body = """
Welcome to the MoneyClub.  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))


    email = EmailMessage(subject="Verify your email address",
              body= email_body,
              from_email=settings.EMAIL_HOST_USER,
              to=[new_user.email])
    
    email.send()


    context['email'] = form.cleaned_data['email']
    return render(request, 'moneyclub/needs-confirmation.html', context)

    
@transaction.commit_on_success
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    try:
        member = Member.objects.get(user=user)
    except ObjectDoesNotExist:
        member = Member(user=user)
        member.save()
    return render(request, 'moneyclub/confirmed.html', {})

