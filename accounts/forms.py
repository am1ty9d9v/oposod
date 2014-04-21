from django import forms
from re import search as re_search
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings

from django.utils import timezone

import datetime
from accounts.models import PasswordForgot
from django.utils import timezone
from django.utils.safestring import mark_safe

class SignUpForm(forms.Form):
    first_name = forms.CharField(label="", help_text="",max_length = 40,
     widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label="", help_text="",max_length = 40,
         widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    username = forms.CharField(label="", help_text="",max_length=10,
         widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    
    email = forms.EmailField(label="", help_text="",
         widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    MALE_FEMALE_CHOICE = [('m', 'Male'),
         ('f', 'Female')]
    sex = forms.ChoiceField(choices=MALE_FEMALE_CHOICE, widget=forms.RadioSelect(attrs={'style': 'display:inline'}))
    dob = forms.DateField(label="", 
                            widget=forms.TextInput(attrs=
                            {
                                'id':'datepicker',
                                'placeholder': 'Date of birth'
                            }
                            )
                            )
    password = forms.CharField(label="", help_text="",max_length=255,
                    widget=forms.PasswordInput(attrs=
                        {
                           'placeholder': 'Password'
                        }
                    )
                )

    renter_password = forms.CharField(label="", help_text="",max_length=255,
                        widget=forms.PasswordInput(attrs=
                            {
                                'placeholder': 'Renter password'
                            }
                        )
                    )

    # We are making  a method that starts with the word 'clean' then appended by '_' and the field
    # name . This is used to validate this field for any error.
    def clean_renter_password(self):

        # Getting username and the password
        renter_password = self.cleaned_data.get('renter_password')
        password = self.cleaned_data.get('password')
        username = self.cleaned_data.get('username')

        # Checking length of the passaword. If it is less than 8 chars, then form
        # will throw an error.
        if len(str(renter_password)) < 2:
            raise ValidationError('Password must be greater than 2 characters.')

        # Checking if the user has entered his password same as his username
        if renter_password == username:
            raise ValidationError('Password must be not same as username')


        # Checking if both password match
        if password != renter_password:
            raise ValidationError("Passwords doesn\'t match")
            return renter_password


    # Cleaning username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.strip().lower()
        if len(username) > 20 and len(username) < 2:
            raise ValidationError('Username should be within 2 and 20 characters.')
        if username in settings.RESCTRICTED_WORDS:
            raise ValidationError("Username is not available.")
        # Tests whether a non allowed letter is present
        if re_search('.*[^a-zA-Z0-9_]', username):
            raise ValidationError('Only numbers, underscore(_),  and alphabets allowed.')

        if User.objects.filter(username=username):
            raise ValidationError("Username is already taken")

        return username

    # Cleaning email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email):
            raise ValidationError("Entered email is already taken")
        return email




class SignInForm(forms.Form):
    username_or_email = forms.CharField(label="", help_text="",max_length=40,
         widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(label="", help_text="",max_length=255,
                    widget=forms.PasswordInput(attrs=
                        {
                            'placeholder': 'Password'
                        }
                    )
                )

    # Validating username
    def clean_username_or_email(self):
        username_or_email = self.cleaned_data.get('username_or_email')
        if User.objects.filter(email=username_or_email) or User.objects.filter(username=username_or_email):
            pass
        else:
            raise ValidationError("Username doesn\'t exist")
        if User.objects.filter(email=username_or_email, is_active=True) or User.objects.filter(username=username_or_email, is_active=True):
            pass
        else:
            raise ValidationError(mark_safe("Account not active. <a href='/resend-activation-email'>Send email again<a/>"))
        return username_or_email

    # Validating password
    def clean_password(self):
        password = self.cleaned_data.get('password')

        username_or_email = self.cleaned_data.get('username_or_email')
        user_obj = None
        try:
            user_obj = User.objects.get(username=username_or_email)
        except:
            try:
                user_obj = User.objects.get(email=username_or_email)
            except:
                raise ValidationError('')

        if user_obj:
            if check_password(password, user_obj.password):
                pass
            else:
                raise ValidationError('Password does not match')
        else:
            raise ValidationError('Password does not exist')

        return password





class PasswordForgotForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.TextInput(attrs=
                            {
                                
                                'placeholder': 'Enter your email'
                            }),required=True)

    def clean_email(self):
        email =  self.cleaned_data.get('email')
        try:
            user_obj = User.objects.get(email = email)


        except:
            # Add prompt with link to register on this site
            raise ValidationError(mark_safe('Email is not registered with us. Would you like to <a href="/join-oposod/">register?</a>'))

        if not user_obj.is_active:
            raise ValidationError('Entered email id is already registered with us but is not active.')
        return email

class PasswordResetForm(forms.Form):
    token = forms.CharField(label='', max_length=6, widget=forms.TextInput(attrs=
                        {
                            'placeholder': 'Enter you token here'
                        }
                    ))
    pass1 = forms.CharField(label='', max_length=100, widget=forms.PasswordInput(attrs=
                        {
                            'placeholder': 'Password'
                        }
                    ))
    pass2 = forms.CharField(label='',max_length=100, widget=forms.PasswordInput(attrs=
                        {
                            'placeholder': 'Renter Password'
                        }
                    ))

    def clean(self):

        data = super(PasswordResetForm, self).clean()
        token = data.get('token')
        if token:
            try:
                password_forgot_obj = PasswordForgot.objects.get(token = token)
                if timezone.now() > password_forgot_obj.token_sent_on + datetime.timedelta(1):
                    raise ValidationError("Token has expired.")
            except:
                raise ValidationError('Entered token is not valid')
        else:
            raise ValidationError('Token field is required')

        pass1 = data.get('pass1')
        pass2 = data.get('pass2')

        if pass1 and pass2:

            if pass1 != pass2:
                raise ValidationError('Both passwords are not same')
            
        else:
            raise ValidationError('Passwords fields are required')
        return data


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(label='', max_length=100,widget=forms.PasswordInput(attrs=
                        {
                            'placeholder': 'Current password'
                        }
                    ))
    new_password = forms.CharField(label='', max_length=100, widget=forms.PasswordInput(attrs=
                        {
                            'placeholder': 'New password'
                        }
                    ))
    new_password_again = forms.CharField(label='', max_length=100, widget=forms.PasswordInput(attrs=
                        {
                            'placeholder': 'New password again'
                        }
                    ))

    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        
        data = super(PasswordChangeForm, self).clean()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        new_password_again = data.get('new_password_again')

        if not current_password:
            raise ValidationError('Current  password field is required')

        if not check_password(current_password, self.user.password):
            raise ValidationError('Entered current password is wrong')

        if not new_password and new_password_again:
            raise ValidationError('New password field is required')

        if new_password != new_password_again:
            raise ValidationError('Both new passwords must be same')

        
       
        return data


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email =  self.cleaned_data.get('email')
        try:
            user_obj = User.objects.get(email = email)
        except:
            # TODO
            # add prompt with link to register on this site
            raise ValidationError(mark_safe('Email is not registered with us. <a href="/join-bquobe">Would you like to register?</a>'))

        if user_obj.is_active:
            raise ValidationError("Email id is already active.")

        return email
