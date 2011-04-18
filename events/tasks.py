from models import Event
from django.http import HttpResponse
from dateutil.parser import parse
from sources.models import ICalendarSource
from google.appengine.api.labs import taskqueue
from dateutil.relativedelta import relativedelta
import logging, traceback
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api.namespace_manager import set_namespace
import namespace_registry
import gdata.calendar

from dateutil.rrule import *





def start_expanding_recurring_events(request):
    try:
        for ns in namespace_registry.all():
            set_namespace(ns.ns)
            taskqueue.add(url='/events/expand_recurring_events/')
        

    except Exception,e:
                logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))        
    return HttpResponse("OK")

def expand_recurring_events(request):
    try:
        cursor=request.POST.get('cursor')
        recurring_events_q=Event.all().filter('repeats_frequency >=', 'MONTHLY').filter('status =', 'approved')
        if cursor:
            recurring_events_q=recurring_events_q.with_cursor(cursor)
        
        events=recurring_events_q.fetch(1)
        if events:
            taskqueue.add(url='/events/expand_recurring_events/', params={'cursor':recurring_events_q.cursor()})
        
        for event in events:
            logging.warning("expanding %s" % event.title)
            if event.repeats_frequency == 'WEEKLY':
                rule=rrule(WEEKLY, dtstart=event.site.today,
                byweekday=event.local_start.weekday(),
                count=5)
                copies=event.copy(rule)
                db.put(copies)
            elif event.repeats_frequency == 'MONTHLY':
                ordinal=event.repeats_setpos
                weekday=(MO,TU,WE,TH,FR,SU)[event.local_start.weekday()](ordinal)
                logging.warning(ordinal)
                rule=rrule(MONTHLY, dtstart=event.site.today, 
                byweekday=weekday(ordinal), 
                count=5,
                wkst=MO)
                copies=event.copy(rule)
                db.put(copies)
        
    except Exception,e:
            logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))        
    return HttpResponse("OK")
    
    
    
    


def parse_one_gdata(request):
    try:
        event_gdata=memcache.get(request.POST['cache_key'])
        memcache.delete(request.POST['cache_key'])
        gevent=gdata.calendar.CalendarEventEntryFromString(event_gdata)
        logging.warning(gevent.id.text)
        key=db.Key(request.POST['ical_key'])
        source=db.get(key)
        event=Event.from_gdata(gevent,source )
    except Exception,e:
        logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
        
    return HttpResponse("OK")
    




def parse_one_event(request):
    try:
        ical=memcache.get(request.POST['cache_key'])
        memcache.delete(request.POST['cache_key'])
        #logging.warning(ical)
        key=db.Key(request.POST['ical_key'])
        source=db.get(key)
        event=Event.from_vcal(ical,source )
    except Exception,e:
        logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
        
    return HttpResponse("OK")
    
