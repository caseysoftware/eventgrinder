from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages

from forms import ICalendarEditForm, ICalApprovalForm
from account.utility import profile_required, userlevel_required
from eventsite import site_required
from google.appengine.api.labs import taskqueue
from google.appengine.api.namespace_manager import set_namespace, get_namespace
from datetime import datetime
import logging
import namespace_registry

import simplejson

@profile_required
def add_source(request):
    if request.method == 'POST':
        form=ICalendarEditForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Thanks for submitting an iCal!")
            if request.profile.userlevel < 10 :
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/sources/manage/')
            
        else:
            return render_to_response('sources/add.html', locals(), context_instance=RequestContext(request))
    
    
    form=ICalendarEditForm()
    return render_to_response('sources/add.html', locals(), context_instance=RequestContext(request))
    
@site_required
def sources(request):
    live_icals=request.site.icalendarsource_set.filter('status =', 'approved')
    return render_to_response('sources/index.html', locals(), context_instance=RequestContext(request))
    
    
    
@site_required
def opml(request):
    live_icals=request.site.icalendarsource_set.filter('status =', 'approved')
    response= render_to_response('sources/index.opml', locals(), context_instance=RequestContext(request))
    response['Content-Type']='text/xml'
    return response
    
    
@site_required
def json(request):
    live_icals=request.site.icalendarsource_set.filter('status =', 'approved')
    export=[]
    for source in live_icals:
        export.append(dict(name= source.name, ics=source.ical_href, trusted=source.trusted))
    response=HttpResponse(simplejson.dumps(export))
    response['Content-Type']='application/json'
    return response
    
    
    
@userlevel_required(10)
def manage_sources(request):
    submitted_icals=request.site.icalendarsource_set.filter('status =', 'submitted')
    live_icals=request.site.icalendarsource_set.filter('status =', 'approved')
    return render_to_response('sources/manage.html', locals(), context_instance=RequestContext(request))

@userlevel_required(10)    
def save_ical(request):
    if request.method == 'POST':
        form=ICalApprovalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "saved your change")
            return HttpResponseRedirect('/sources/manage')
            
        else:
            messages.add_message(request, messages.INFO, "something went wrong!")
            return HttpResponseRedirect('/sources/manage')
            
            
def start_fetch_icals(request):
    
    for ns in namespace_registry.all():
        set_namespace(ns.ns)
        logging.warning('namespace: %s'% get_namespace())
        taskqueue.add(url='/sources/fetch/', params={
                                                'started': datetime.now(),
                                                'timestamp': datetime.now().strftime("%Y%m%d%H%M")})
        #logging.warning("started fetch queuing at %s" % datetime.now())
    return HttpResponse("enqueued!")
