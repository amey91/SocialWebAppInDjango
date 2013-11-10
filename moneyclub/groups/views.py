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


def get_photo_group(request, id):
    entry = get_object_or_404(Group, id=id)
    print entry
    if not entry.picture:
        raise Http404
    content_type = guess_type(entry.picture.name)
    print content_type
    return HttpResponse(entry.picture, mimetype=content_type)


def club_home(request):
    context = {}    
    """name = "group 1"
    owner = request.user
    description = "desc"
    keywords = "key11,key2,key3"
    g = Group(name=name,owner=owner,description=description,keywords=keywords)
    g.save()"""
    
    g=Group.objects.get(id=6);
    context['group_name'] = g.name
    context['description'] = g.description
    str1= g.keywords
    context['keywords'] =str1.split(",")
    context['id']= g.id
    return render(request, 'moneyclub/group_home_page.html', context)
    
   
def club_create(request):
    return render(request, 'moneyclub/create_moneyclub.html',{})
    
@transaction.commit_on_success
def club_create_submit(request):
    errors = []
    context = {}
    print "hi hello"
    
    if request.method=='GET':
            return render(request, 'moneyclub/create_moneyclub.html', context)
    #check for missing fields
    if not 'name' in request.POST or not request.POST['name']:
        errors.append('Group Name is required')
    if not 'description' in request.POST or not request.POST['description']:
        errors.append('A short group description is required.')
    if len(Group.objects.filter(name__iexact=request.POST['name'])) > 0:
        errors.append('Group name is already taken.')
    if errors:
            context['errors']= errors
            return render(request, 'moneyclub/create_moneyclub.html', context)
    
    new_entry = Group(owner=request.user)
    form = CreateGroupForm(request.POST, request.FILES, instance=new_entry )
    
    if not form.is_valid():         
        context['form'] = form
        return render(request, 'moneyclub/create_moneyclub.html', context)
    '''
    if you don't want to use model forms: 
    name=request.POST['group_name']
    owner = request.user
    description = request.POST['description']
    keywords = request.POST['keywords']
    g = Group(name=name,owner=owner,description=description,keywords=keywords)
    g.save()'''
    
    form.save()
    errors.append("Group created successfully!")
    context['errors']=errors
    g=Group.objects.get(name=request.POST['name']);
    context['group_name'] = g.name
    context['description'] = g.description
    str1= g.keywords
    context['keywords'] =str1.split(",") 
    context['id']=g.id
    return render(request, 'moneyclub/group_home_page.html', context)

def add_members(request,id):
    return render(request, 'moneyclub/adduser.html', {})
    

    