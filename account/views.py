from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from google.appengine.api import users
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.defaultfilters import slugify, striptags
from django.contrib import messages

from google.appengine.api.users import get_current_user, create_login_url
from google.appengine.api.labs import taskqueue

from account.utility import get_current_user, profile_required, get_current_profile
from account.forms import  ProfileForm
from account.models import Profile

from eventsite import site_required, get_site
#from messaging import notice


import os
from datetime import datetime

@site_required
def signin(request):
        if request.method=='POST':
            dest_url=request.POST.get('continue')
            federated_identity=request.POST.get('openid_url')
           
            login_url=create_login_url(dest_url=dest_url, federated_identity=federated_identity)
            return HttpResponseRedirect(login_url)
            
        else:
            dest=request.GET.get('continue', reverse('front-page'))
            google_login_url=create_login_url(dest_url=dest, federated_identity="https://www.google.com/accounts/o8/id")
            yahoo_login_url=create_login_url(dest_url=dest, federated_identity="http://yahoo.com/")
            return(render_to_response('account/signin.html', locals(), context_instance=RequestContext(request)))



def signout(request):
    messages.add_message(request, messages.INFO,"You've signed out. Come back any time!")
    return HttpResponseRedirect('/')
    


def save_profile(profile, form):
    nickname=striptags(form.cleaned_data['nickname'].strip())
    profile.nickname=nickname
    profile.email= form.cleaned_data['email'].strip()
    profile.slug=unicode(slugify(nickname))
    profile.confirmed_at=datetime.now()
    profile.link=form.cleaned_data['link'] or None
    profile.subscribes=form.cleaned_data['subscribe']
    profile.put()
    if profile.subscribes:
        site=get_site()
        chimp=site.chimp
        taskqueue.add(url='/subscriptions/subscribe_email/',
                       params={'apikey': chimp.apikey,
                       'list_id': chimp.listid,
                       'email': form.cleaned_data['email']})



@profile_required
def edit_profile(request):
    profile=get_current_profile()
    if request.method == 'POST': # If the form has been submitted...
        form = ProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            save_profile(profile, form)
            messages.add_message(request, messages.INFO,"Your profile has been saved!")
            return HttpResponseRedirect('/') # Redirect after POST
    
    
    
    current_settings={'nickname':profile.nickname,
                      'email': profile.email,
                      'subscribe':profile.subscribes,
                      'link': profile.link}

    form=ProfileForm(current_settings)
    return(render_to_response('account/edit.html', locals(), context_instance=RequestContext(request)))

def view_profile(request):
    return HttpResponse("not implemented")



@site_required        
def profile_setup(request):
    hostname=os.environ['HTTP_HOST']
    dest=request.GET.get('continue', reverse('front-page'))
    user=get_current_user()
    profile=get_current_profile()
    
    if not profile:
         return HttpResponseRedirect(create_signin_url(reverse('account-edit')))

    if request.method == 'POST': # If the form has been submitted...
        form = ProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            save_profile(profile, form)
            return HttpResponseRedirect(dest) # Redirect after POST
    else:
        form = ProfileForm(initial=profile.profile_details)

    return(render_to_response('account/profile-setup.html', locals(), context_instance=RequestContext(request)))