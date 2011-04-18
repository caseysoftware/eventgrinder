from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import cache_page

from eventsite import site_required
from eventsite.models import Eventsite
import events.models
from pytz.gae import pytz
from datetime import datetime, timedelta, time
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import parse
import vobject, os
from events.models import Event


from itertools import chain

import logging

utc=pytz.timezone('UTC')

from google.appengine.api.users import get_current_user
from google.appengine.api import memcache

@cache_page(60 * 60)	
@site_required
def ical(request, tag=None):
    if request.site.hostnames:
        host= request.site.hostnames[0]
    else:
        host=request.site.key().id_or_name()
    cal = cal = vobject.iCalendar()
    if tag:
        cal.add('X-WR-CALNAME').value="%s on %s"% (tag,request.site.name)
    else:
        cal.add('X-WR-CALNAME').value=request.site.name
    start=utc.localize(datetime.utcnow()).astimezone(request.site.tz).date()
    end=start+relativedelta(days=120, weekday=SU(+1))
    continuing=Event.all().filter('status = ', 'approved').filter('multiday =', True).filter('continues =', str(start))
    events_soon=Event.all().filter('status = ', 'approved').order('local_start').filter('local_start >= ', start).filter('local_start < ', end)
    if tag:
        continuing=continuing.filter('tags = ', tag)
        events_soon=events_soon.filter('tags = ', tag)
    
    
    for event in chain(continuing,events_soon):
        vevent=cal.add('vevent')
        vevent.add('summary').value=event.title
        vevent.add('dtstart').value=utc.localize(event.start)
        vevent.add('dtend').value=utc.localize(event.end)
        if event.link: 
            vevent.add('url').value=event.link
            
        if event.description: 
            vevent.add('description').value=event.description
        elif event.link:
            vevent.add('description').value="details at: %s" % event.link
            
        if event.location:vevent.add('location').value=event.location
        vevent.add('uid').value="%s@%s" %(str(event.key()), host)
    response= HttpResponse(cal.serialize(), mimetype='text/calendar')
    if tag:
        response['Content-Disposition'] = 'attachment; filename=%s_%s.ics'% (tag,request.site.slug)
    else:
        response['Content-Disposition'] = 'attachment; filename=%s.ics'% request.site.slug
    
    response['Cache-Control']="public; max-age=3600;"
    return response
    


def jumpto(request):
    datestring=request.POST.get('jumptodate')
    
    try:
        parsed_day=parse(datestring)
        preceeding_monday=parsed_day+relativedelta(weekday=MO(-1))
        if preceeding_monday != parsed_day:
            href="/week-of/%s#%s" %(preceeding_monday.strftime("%Y-%m-%d"),parsed_day.strftime("%Y-%m-%d"))
        else:
            href="/week-of/%s" %(preceeding_monday.strftime("%Y-%m-%d"))
    except:
        return HttpResponseRedirect('/')
        
    return HttpResponseRedirect(href)


@site_required
def week_of_index(request, datestring=None, format=None):

    parsed_day=parse(datestring).date()
    start=parsed_day+relativedelta(weekday=MO(-1))
    begin_next_week=start+relativedelta(days=1, weekday=MO(+1))
    end=start+relativedelta(weekday=SU)
    continuing=Event.all().filter('status = ', 'approved').filter('continues =', str(start)).filter('local_start < ', start).fetch(150)
    events_soon=Event.all().filter('status = ', 'approved').order('local_start').filter('local_start >= ', start).filter('local_start < ', begin_next_week).fetch(150)
    
    if format == 'newsletter': 
        template='eventsite/newsletter.html'
    else:
        template='eventsite/week.html'

    return render_to_response(template, locals(), context_instance=RequestContext(request))
        




@cache_page(60 * 10)
@site_required
def front_page(request, tag=None):
    start=request.site.today
    logging.warning("rendering front page of %s starting %s" % (request.site.name, request.site.today+request.site.tz.utcoffset(request.site.tz)))
    upcoming=Event.all().filter('status = ', 'approved').order('local_start').filter('local_start >= ', start).fetch(30)
    
    #upcoming=[event for event in upcoming if 
    response= render_to_response('eventsite/front-page.html', locals(), context_instance=RequestContext(request)) 
    response['Cache-Control']="public; max-age=300;"
    return response
      



