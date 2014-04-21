from django import forms
from image_cropping.widgets import ImageCropWidget
from users.models import ProfilePhoto
from bootstrap_toolkit.widgets import  BootstrapUneditableInput


class EditCoverPhotoForm(forms.Form):
    choose_cover_photo = forms.ImageField()

class EditProfilePhotoForm(forms.ModelForm):
    class Meta:

        widgets = {
            'profile_photo': ImageCropWidget,
        }
        model = ProfilePhoto
        exclude = ['user', 'profile_photo_path', 'uploaded_on', 'is_set', 'key']


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length = 30)
    last_name = forms.CharField(max_length = 30)
    

    
    dob = forms.DateField(
                            widget = forms.TextInput(attrs =
                            {
                                'id':'datepicker',
                                'disabled':'disabled',
                            }
                            ), required = False
                            )
    city = forms.CharField(max_length = 99, required = False)
    country = forms.CharField(max_length = 99, required = False)
    description = forms.CharField(label = 'I believe in...', max_length = 140, required = False)


class UploadNewStoryForm(forms.Form):

    photo = forms.FileField()

    


class WriteStoryForm(forms.Form):
    heading = forms.CharField(label = '', max_length = 100,
                              widget = forms.TextInput(attrs =
                            {
                                'placeholder':'Heading',
                            }
                            ),)
    story = forms.CharField(label = '', widget = forms.Textarea(attrs = {'cols': 40, 'rows': 10, 'placeholder':'Write story here...'}))

    

class WriteStatusForm(forms.Form):
    status = forms.CharField(label='', max_length=155,
                            widget = forms.TextInput(attrs =
                            {
                                'placeholder': 'Update Status',
                            }))


class DoCommentForm(forms.Form):
    comment = forms.CharField(max_length = 160,
                            widget = forms.TextInput(attrs =
                            {
                                'id':'do_comment',
                                'style': 'width: 500px;float:right;margin-top:-40px;',
                                'placeholder': 'Add comment...',
                            }
                            ))



class EditPrivacyForm(forms.Form):
    
    choices = [('A', 'Everyone'), ('F', 'Only connection'), ('N', 'Only me')]
    friends_visibility = forms.ChoiceField(label = 'Your connection list visible to ', choices = choices, required = False)
    cover_photos_visibility = forms.ChoiceField(label = 'Your cover photos visible to ', choices = choices, required = False)
    profile_photos_visibility = forms.ChoiceField(label = 'Your profile photos visible to ', choices = choices, required = False)
    daily_photos_visibility = forms.ChoiceField(label = 'Your daily photos visible to ', choices = choices, required = False)
    stories_visibility = forms.ChoiceField(label = 'Your stories visible to ', choices = choices, required = False)
    calendar_visibility = forms.ChoiceField(label = 'Your calendar visible to ', choices = choices, required = False)
    who_can_comment_on_photos = forms.ChoiceField(label = 'Who can comment on your photos ', choices = choices, required = False)
    who_can_like_photos = forms.ChoiceField(label = 'Who can likes your photos ', choices = choices, required = False)
    #is_sharing_of_photos_on_fb = forms.ChoiceField(label = 'Share automatically your daily photos on facebook ', choices = sharing_choices, required = False)


class WriteTestimonialForm(forms.Form):
    testimonial = forms.CharField(label="Write testimonial", widget = forms.Textarea(attrs = {'rows':10, 'cols':30}))
