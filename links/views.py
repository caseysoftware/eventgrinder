from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages

from account.utility import get_current_user, profile_required, get_current_profile

from eventsite import site_required


@site_required        
def add(request):
	return(render_to_response('links/add.html', locals(), context_instance=RequestContext(request)))