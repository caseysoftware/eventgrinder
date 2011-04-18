import logging, os

from google.appengine.api import users
from google.appengine.api.users import get_current_user, create_login_url
from google.appengine.ext.db import Query

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

#from messaging import notice

from eventsite import get_site, site_required

from models import Profile	



def get_current_profile():
    site=get_site()
    user=get_current_user()
    if not site: return None
    if not user: return None
    profile=Profile.get_or_insert(site.slug+user.user_id(), user=user, site=site, subscribes=False)
    return profile
	
def create_signin_url(dest='/'):
    return reverse('account-signin')+'?continue='+dest
    

def create_profile_confirm_url(dest='/'):
    return reverse('profile-setup')+'?continue='+dest
    

    
    
def profile_required(func):
    def replacement_view(request, *args, **kwargs):
        site=get_site()
        
        user=get_current_user()
        if user and not site:
            return func(request, *args, **kwargs)

        if not user: 
            return redirect(create_signin_url(request.get_full_path()))
            
        profile=get_current_profile()
        if not profile.confirmed_at:
            return redirect(create_profile_confirm_url(request.get_full_path()))
        request.site= site
        request.profile=profile
        return func(request, *args, **kwargs)

    return site_required(replacement_view)


def admin_required(func):
        def replacement_view(request, *args, **kwargs):
            g_user=users.get_current_user()
            if not users.is_current_user_admin(): 
                
                return redirect(create_signin_url(dest=request.get_full_path()))


            return func(request, *args, **kwargs)

        return profile_required(replacement_view)

def userlevel_required(level):
    def replacement_decorator(func):
        def replacement_view(request, *args, **kwargs):
            profile=get_current_profile()
            if not (users.is_current_user_admin() or profile.userlevel >= level):
                messages.add_message(request, messages.INFO,"You don't have access to that page")
                return HttpResponseRedirect('/')



            return func(request, *args, **kwargs)

        return profile_required(replacement_view)
    return replacement_decorator

def create_logout_url(dest):
    return aeoid.users.create_logout_url(dest)



def profile_for_user(user, keys_only=False):
    q=Query(Profile, keys_only=keys_only).filter('user =', user)
    return q.fetch(1)[0]

