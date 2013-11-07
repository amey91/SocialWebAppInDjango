from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from moneyclub.models import *
#from moneyclub.forms import *
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
    