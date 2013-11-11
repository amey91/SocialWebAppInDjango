from django import forms

from django.contrib.auth.models import User

from models import *



class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude=('owner','datetime')
        widgets={'picture' : forms.FileInput() }
        
class UserProfileForm(forms.ModelForm):
    picture = forms.ImageField(error_messages={'required': 'Please select a picture!'})
    class Meta:
        model = UserProfile
        exclude = ('user',)
        widgets = {'picture' : forms.FileInput() }
    
    