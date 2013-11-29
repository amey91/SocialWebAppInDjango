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
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import *


def group_home(request):
    context = {}
    keywords = {}
    """name = "group 1"
    owner = request.user
    description = "desc"
    keywords = "key11,key2,key3"
    g = Group(name=name,owner=owner,description=description,keywords=keywords)
    g.save()"""
    
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
    try:
        profile = UserProfile.objects.get(user=request.user) 
        profile = ProfileForm(instance=profile)
    except ObjectDoesNotExist:
        errors.append('Profile not found. Create your profile.')
    print request.user.username

    member = Member.objects.get(user=request.user)
    memberships = GroupMembership.objects.filter(user=request.user)
    groups = [membership.group for membership in memberships]
    stocks = UserStockOfInterest.objects.filter(user=request.user)

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

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="erzhuow@andrew.cmu.edu",
              recipient_list=[new_user.email])

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

    member = Member(user=user)
    member.save();
    return render(request, 'moneyclub/confirmed.html', {})

    