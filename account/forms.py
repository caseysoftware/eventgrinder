from django import forms
from django.forms.util import ErrorList
from django.template.defaultfilters import slugify

from google.appengine.api.users import get_current_user
from account.utility import profile_required, get_current_profile

from models import Profile
from eventsite import get_site

from html5.forms import URLInput, DateInput, TextInput, EmailInput



class ProfileForm(forms.Form):
    nickname = forms.CharField(max_length=255, help_text="What you want to be known as on the site")
    email=forms.EmailField(required=True, help_text="Where should we send email?", widget=EmailInput)
    subscribe = forms.BooleanField(required=False, help_text="Do you want to get the weekly events email?")
    link=forms.URLField(required=False, help_text="This can be the URL of your blog, twitter page, LinkedIn profile, homepage, or anything else.", 
                        widget=TextInput(attrs={'placeholder':'http://whatever'}))

    def clean(self):
        site=get_site()
        cleaned_data = self.cleaned_data
        nickname = cleaned_data.get("nickname")
        email = cleaned_data.get("email")
        profile=get_current_profile()
        existing_profile_with_slug=site.profile_set.filter('slug =', unicode(slugify(nickname))).get()
        existing_profile_with_email=site.profile_set.filter('email =', email).get()
        if (existing_profile_with_slug != None and existing_profile_with_slug.key() != profile.key()):
                msg = u"Someone else already took that nickname!"
                self._errors["nickname"] = ErrorList([msg])
                del cleaned_data['nickname']
        if (existing_profile_with_email != None and existing_profile_with_email.key() != profile.key()):
                msg = u"Someone has already registered with that email"
                self._errors["email"] = ErrorList([msg])
                del cleaned_data['email']
                
        return super(ProfileForm, self).clean()