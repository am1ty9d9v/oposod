import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from redis import StrictRedis

from accounts.forms import SignUpForm, SignInForm, PasswordForgotForm, \
    PasswordResetForm, PasswordChangeForm, ResendActivationEmailForm
from accounts.models import PasswordForgot, RegistrationProfile
from oposod.settings import RANDOM_CHARS, SITE
from users.models import Profile, PrivacySettings, ProfilePhoto
from utils.misc import send_html_mail, activation_key_generator


def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():

        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user_obj = User.objects.create(
            first_name=first_name.title(),
            last_name=last_name.title(),
            username=username,
            email=email,
            date_joined=datetime.datetime.now(),
            is_active=False,
            password=make_password(password),
            is_superuser=False,
            is_staff=False,
        )

        profile = Profile(user=user_obj,
                          dob=form.cleaned_data['dob'],
                          sex=form.cleaned_data['sex'],
                          last_edited_on=datetime.datetime.now(),
                          )
        profile.save()

        PrivacySettings.objects.create(user=user_obj,
                                       friends_visibility='F',
                                       cover_photos_visibility='F',
                                       profile_photos_visibility='F',
                                       daily_photos_visibility='F',
                                       stories_visibility='F',
                                       calendar_visibility='F',
                                       )
        ProfilePhoto.objects.create(user=user_obj,
                                    profile_photo='profile_photo/default_avatar.jpg',
                                    cropping='',
                                    is_set=True,
                                    key='123456789',
                                    uploaded_on=datetime.datetime.now())

        # Sending the confirmation email here.
        try:
            ACTIVATION_KEY = activation_key_generator(20,
                                                      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdegfhijklmnopqrstuvwxyz1234567890")
            subject = 'Oposod.com: User %s creation information.' % (username)
            html_content = '''<div style="border: 1px solid #ddd; background: #000; padding: 30px; font-size: 50px; font-family: 'Ubuntu'">
                            <p>Hello %s . You have successfully registered your account on oposod.com
                            . To proceed further, you need to verfiy your email id.</p>
                            <p>Please follow this link %s/account/activation/%s</p>
                            </div>''' % (username, SITE, ACTIVATION_KEY)
            recipient_list = [email]

            send_html_mail(subject, html_content, recipient_list)

            rp = RegistrationProfile(user=user_obj, activation_key=ACTIVATION_KEY)
            rp.save()

        except Exception, e:
            return render(request, '404_error.html', {
                'msg': 'There is some error in sending the email. The error is: %s' % e
            })

        messages.info(request,
                      'You have successfully registered, please activate your account from your email before signing in.')
        return HttpResponseRedirect(reverse('signin'))

    return render(request, 'accounts/signup.html', {
        'form': form,
    })


def signin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    form = SignInForm(request.POST or None)
    if form.is_valid():
        username_or_email = form.cleaned_data['username_or_email']
        password = form.cleaned_data['password']
        user_obj = None
        try:
            user_obj = User.objects.get(username=username_or_email)
        except:
            user_obj = User.objects.get(email=username_or_email)

        if user_obj:
            if check_password(password, user_obj.password):
                user = authenticate(username=user_obj.username, password=password)
                if user:
                    if user.is_active:
                        login(request, user)
                        request.session['username'] = user_obj.username
                        # Append the user to online users set in redis.
                        # Also create a notifications object which will be used
                        # to initiate and send notifications
                        redis_obj = StrictRedis(db=9)
                        redis_obj.sadd('online:users', user_obj.username)
                        next = request.GET.get('next', '')
                        if next:
                            return HttpResponseRedirect(next)
                        else:
                            return HttpResponseRedirect(reverse('profile', args=(str(user_obj.username),)))

                else:
                    messages.info(request, 'Please activate your account first.')
                    return HttpResponseRedirect(reverse('accounts.views.signin.'))
    return render(request, 'accounts/signin.html', {
        'form': form,
    })


def reset_password_ask_email_page(request):
    form = PasswordForgotForm(request.POST or None)
    if form.is_valid():
        print 'form valid: ', form.is_valid()
        email = form.cleaned_data['email']
        print 'email: ', email
        try:
            user_obj = get_object_or_404(User, email=email)
            print user_obj
        except:
            user_obj = None

        if user_obj:
            token = activation_key_generator(6, RANDOM_CHARS)
            print 'token: ', token

            pf_obj = PasswordForgot.objects.filter(user=user_obj)
            if pf_obj:
                pf_obj.delete()
                PasswordForgot.objects.create(user=user_obj, token=token)
            else:
                PasswordForgot.objects.create(user=user_obj, token=token)
            subject = 'Password reset request for %s' % user_obj.email
            html_content = '''
                <p>Hi,</p>
                <p>You have recently requested a password reset for your OPOSOD account.</p>
                Please use this token to reset.
                <p>%s</p>
            ''' % token
            recipient_list = [email]
            try:
                send_html_mail(subject, html_content, recipient_list)
            except Exception, e:
                print 'error in sending email: %s' % e

            messages.info(request,
                          'An email with the token has been send to the given email with a token. Enter that token here to proceed further')
            return HttpResponseRedirect(reverse('accounts.views.reset_password_do_reset_password_page'))
        else:
            print 'no user'
    else:
        print 'some error in form'

    return render(request, 'accounts/reset_password_ask_email_page.html', {
        'form': form,
    })


def reset_password_do_reset_password_page(request):
    form = PasswordResetForm(request.POST or None)
    if form.is_valid():
        token = form.cleaned_data['token']
        pass1 = form.cleaned_data['pass1']
        # pass2 = form.cleaned_data['pass2']

        password_forgot_obj = get_object_or_404(PasswordForgot, token=token)
        User.objects.filter(id=password_forgot_obj.user_id).update(password=make_password(pass1))
        PasswordForgot.objects.filter(token=token).delete()
        messages.info(request, 'You have successfully reset your password, can login now.')
        return HttpResponseRedirect(reverse('accounts.views.signin'))
    return render(request, 'accounts/reset_password_do_reset_password_page.html', {
        'form': form,
    })


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        new_password = form.cleaned_data['new_password']
        User.objects.filter(id=request.user.id).update(password=make_password(new_password))
        messages.info(request, 'Your password has been change sucessfully.')
        return HttpResponseRedirect(reverse('accounts.views.change_password'))

    return render(request,
                  'accounts/change_password.html', {
                      'form': form,
                  }, )


def signout(request):
    # Remove user from the set online:users
    redis_obj = StrictRedis(db=9)
    redis_obj.srem('online:users', request.user.username)

    logout(request)

    return HttpResponseRedirect('/')


def activate(request, activation_key):
    '''
        If the user has clicked the email link send to his email, then it is considered
        that the email id is used while registartion is valid and hence his profile
        is set to activated.
        If he fails to verfiy his email id in a given limited time, then his accounts details
        will be removed form the database by an automated crontab script.
    '''
    try:
        rp1 = get_object_or_404(RegistrationProfile, activation_key=activation_key)
    except:
        rp1 = None
        return HttpResponseRedirect('/404')
    try:
        user_obj = User.objects.get(id=rp1.user_id)
    except:
        return HttpResponseRedirect('/404')

    if rp1 and not user_obj.is_active:
        # User.objects.filter(id=rp1.user_id).update(is_active=True)
        user_obj.is_active = True
        user_obj.save()
        messages.info(request, 'Your account is sucessfully activated.')
        return HttpResponseRedirect('/signin/')
    else:
        return HttpResponseRedirect('/404')


def resend_activation_email(request):
    form = ResendActivationEmailForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        user_obj = get_object_or_404(User, email=email)
        rp_obj = get_object_or_404(RegistrationProfile, user=user_obj)
        subject = 'Resending email activation on request'
        html_content = '''<div style="border: 1px solid #ddd; background: #000; padding: 30px; font-size: 50px; font-family: 'Ubuntu'">
                        <p>Hello, </p>
                        <p>As per you request we are sending you the activation email 
                        again
                        . To proceed further, you need to to click the following link
                        to verfiy your email id.</p>
                        <p>Please follow this link %s/account/activation/%s</p>
                        </div>''' % (SITE, rp_obj.activation_key)
        recipient_list = [email]
        try:
            send_html_mail(subject, html_content, recipient_list)
        except Exception, e:
            print 'ERROR IN SENDING EMAILS: %S' % e
        messages.info(request, 'Email has been successfully sent.')
        return HttpResponseRedirect(reverse('accounts.views.signin'))
    return render(request, 'accounts/resend_actvation_email.html', {
        'form': form,
    })
