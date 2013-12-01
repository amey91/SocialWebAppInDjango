from django import forms
from django.forms.util import ErrorList

from django.contrib.auth.models import User
import hashlib

from moneyclub.models import *

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude=('owner','datetime')
        widgets={'picture' : forms.FileInput() }

class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ('user','groupId','datetime','articleType' )
        widgets = {'picture' : forms.FileInput(), 'articleType':forms.HiddenInput()}

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('user','groupId','datetime','articleType' )
       


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length = 20,
                                widget = forms.TextInput(attrs={'class':'form-control',\
                                    'placeholder':'Username', 'autofocus':'on'}))
    email = forms.EmailField(max_length=200,
                                widget = forms.TextInput(attrs={'class':'form-control',\
                                    'placeholder':'Email', 'autofocus':'on'}))
    password1 = forms.CharField(max_length = 200, 
                                label='Password', 
                                widget = forms.PasswordInput(attrs={'class':'form-control',\
                                    'placeholder':'Password', 'autofocus':'on'}))
    password2 = forms.CharField(max_length = 200, 
                                label='Confirm password',  
                                widget = forms.PasswordInput(attrs={'class':'form-control',\
                                    'placeholder':'Confirm Password', 'autofocus':'on'}))


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(max_length = 200, 
                                label='Old Password', 
                                widget = forms.PasswordInput(attrs={'class':'form-control',\
                                    'placeholder':'Old Password', 'autofocus':'on'}))
    new_password = forms.CharField(max_length = 200, 
                                label='Password', 
                                widget = forms.PasswordInput(attrs={'class':'form-control',\
                                    'placeholder':'New Password', 'autofocus':'on'}))
    con_password = forms.CharField(max_length = 200, 
                                label='Confirm password',  
                                widget = forms.PasswordInput(attrs={'class':'form-control',\
                                    'placeholder':'Confirm Password', 'autofocus':'on'}))

    '''
    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm,self).__init__(*args,**kwargs)
        '''

    def __init__(self, user=None, *args, **kwargs):
        super(ResetPasswordForm,self).__init__(*args,**kwargs)
        if user is not None:
            self._user = user
        

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(ResetPasswordForm, self).clean()

        password = self._user.password
        print "old password: "+password 
        
        email = self._user.email

        # Confirms that the two password fields match
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        con_password = cleaned_data.get('con_password')
        print "input password: "+ str(old_password)
        if not self._user.check_password(old_password):
            raise forms.ValidationError("Password does not match old password.")
        
        if new_password and con_password and new_password != con_password:
            raise forms.ValidationError("New passwords did not match.")


        # We must return the cleaned data we got from our parent.
        return cleaned_data



class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', )
        widgets = {'picture' : forms.FileInput() }
    def clean(self):
        
        if 'birthdate' in self._errors:
            print 'birthdate invalid'
            self._errors['birthdate'] = self.error_class(["Valid form: YYYY-mm-dd"])
            raise forms.ValidationError("YYYY-mm-dd")
        return self.cleaned_data   
