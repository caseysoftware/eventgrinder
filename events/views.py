from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages


import logging
from events.forms import EventBasicsForm

from google.appengine.api.users import get_current_user
from account.utility import profile_required, get_current_profile
from eventsite import site_required
from django.core.urlresolvers import reverse
from google.appengine.ext import db
from pytz.gae import pytz

from dateutil import parser
utc=pytz.timezone('UTC')

from datetime import datetime

from sources.models import ICalendarSource
from links.models import Link


@profile_required
def add_series(request):
    account=get_current_user()
    profile=get_current_profile()
    if request.method =='POST':
        form=EventSeriesForm(request.POST)
        if form.is_valid():
            form.save()
            if profile.userlevel < 9:
                messages.add_message(request, messages.INFO, "Thanks for submitting an event! It's in <a href='events/queue/'>the queue</a> and will be reviewed soon")
            else:
                messages.add_message(request, messages.INFO, "Event, added.")
                request.site.expire_assets()
            return redirect(reverse('front-page'))
            
        
    else:        
        form=EventBasicsForm()
    return render_to_response('events/add.html', locals(), context_instance=RequestContext(request))




@profile_required
def add_event(request):
    account=get_current_user()
    profile=get_current_profile()
    if request.method =='POST':
        form=EventBasicsForm(request.POST)
        if form.is_valid():
            form.save()
            if profile.userlevel < 9:
                messages.add_message(request, messages.INFO, "Thanks for submitting an event! It's in <a href='events/queue/'>the queue</a> and will be reviewed soon")
            else:
                messages.add_message(request, messages.INFO, "Event, added.")
                request.site.expire_assets()
            return redirect(reverse('front-page'))
            
        
    else:        
        form=EventBasicsForm()
    return render_to_response('events/add.html', locals(), context_instance=RequestContext(request))
    

@site_required
def event_queue(request):
    
    def save_details(event):
        data=request.POST
        event.title=data['title']
        event.link=data['link'] or None
        event.cost=data['cost'] or None
        tz=request.site.tz
        event.start=tz.localize(parser.parse(data['start']))
        event.end=tz.localize(parser.parse(data['end']))
        
        if request.POST.has_key('tags'): 
            event.tags=[t.strip() for t in request.POST.get("tags","").lower().split(',')]
            
        event.put()
        
    
    
    timezone=pytz.timezone(request.site.timezone)
    pending_events=request.site.event_set.filter('status = ', 'submitted')
    today=utc.localize(datetime.utcnow()).astimezone(timezone).date()
    pending_events_future=pending_events.filter('local_start >=', today).order('local_start').fetch(50)
    if request.method == 'POST' and request.POST.has_key('button'):
        profile=get_current_profile()
        if request.POST['button'] == 'Reject' and (profile.userlevel == 10):
            event_results=request.site.event_set.filter(' __key__ =', db.Key(request.POST['event_key']) )
            event=event_results.get()
            event.status="rejected-%s" % request.POST.get('rejection-reason','unspecified')
            event.put()
            messages.add_message(request, messages.INFO,'Rejected! Feels good, right?')
            
        if request.POST['button'] == 'Save':
            event_results=request.site.event_set.filter(' __key__ =', db.Key(request.POST['event_key']) )
            event=event_results.get()
            if profile.userlevel == 10:
                save_details(event)
                messages.add_message(request, messages.INFO,'%s saved' % event.title)
                
        if request.POST['button'] == 'Approve':
            event_results= request.site.event_set.filter(' __key__ =', db.Key(request.POST['event_key']) )
            event=event_results.get()
            if profile.userlevel == 10: 
                event.status='approved'
                event.approved_by=profile
                event.approved_on=datetime.now()
                save_details(event)
                messages.add_message(request, messages.INFO,'%s approved' % event.title)
                
        if request.POST['button'] == 'Back to queue':  
              event_results= request.site.event_set.filter(' __key__ =', db.Key(request.POST['event_key']) )
              event=event_results.get()   
              if profile.userlevel == 10: 
                  event.status='submitted'
                  event.approved_by=None
                  event.approved_on=None
                  save_details(event)
                  messages.add_message(request, messages.INFO,'%s sent back' % event.title)
        request.site.expire_assets()
        if request.POST.has_key('return'):return HttpResponseRedirect(request.POST['return'])
        
    
    pending_events=request.site.event_set.filter('status = ', 'submitted')
    has_pending_sources=submitted_icals=ICalendarSource.all().filter('status =', 'submitted').get()
    has_pending_links=Link.all().filter('status =','submitted').get()
    return render_to_response('events/queue.html', locals(), context_instance=RequestContext(request))
    