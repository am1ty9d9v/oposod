from django.db import models
from django.contrib.auth.models import User

class PasswordForgot(models.Model):
    user = models.ForeignKey(User, unique = True)
    token = models.CharField(max_length = 6)
    token_sent_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "User Id: {user}\nToken: {token}".format(
               user = self.user, token = self.token)

class RegistrationProfile(models.Model):
    user = models.ForeignKey(User, unique = True)
    activation_key = models.CharField(max_length = 255)
    registered_on = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return "User Id: {user_id}\nActivation Key: {activation_key}".format(
               user_id = self.user_id, activation_key = self.activation_key)