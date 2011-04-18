from models import ICalendarSource
from django.http import HttpResponse
from dateutil.parser import parse
from google.appengine.api.labs import taskqueue
from datetime import datetime, date, timedelta
from pytz.gae import pytz
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import logging, traceback
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

import gdata.calendar

from vobject.icalendar import stringToDate, stringToDateTime

# DeadlineExceededError can live in two different places 
try: 
  # When deployed 
  from google.appengine.runtime import DeadlineExceededError 
except ImportError: 
  # In the development server 
  from google.appengine.runtime.apiproxy_errors import DeadlineExceededError


utc=pytz.timezone('UTC')



def split_gdata(request):
    try:
        if request.method == 'POST':
            key=db.Key(request.POST.get('ical_key'))
            source=ICalendarSource.get(key)
            gdata_source=memcache.get(request.POST.get('cache_key'))
            memcache.delete(request.POST.get('cache_key'))
            feed=gdata.calendar.CalendarEventFeedFromString(gdata_source)
            cal_count=0
            for gevent in feed.entry:
                cal_count=cal_count +1
                source_cache_key=request.POST.get('cache_key')
                cache_key=source_cache_key +"-"+ str(cal_count)
                memcache.set(cache_key, gevent.ToString(),1200)
                
                params=params={'cache_key': cache_key,
                                'ical_key': request.POST['ical_key']}
                taskqueue.add(url='/events/parse_one_gdata/',
                               params=params,
                              name=cache_key,countdown=30)
    
    
    except urlfetch.DownloadError:
        raise
        
    except Exception,e:
                logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    
    return HttpResponse("OK")
    


def fetch_icals(request):
    try:
        if request.method == 'POST':
            cursor=request.POST.get('cursor')
            started=request.POST.get('started')
            parsed_started=parse(started)
            q=ICalendarSource.all().filter('status = ', 'approved').filter('last_fetch < ', parsed_started- relativedelta(hours=+3))
            if cursor:
                q=q.with_cursor(cursor)
            cals= q.fetch(1)
            if cals: 
                params={'cursor': q.cursor(),
                        'started': started}
                taskqueue.add(url='/sources/fetch/', params=params,)
            for ical in cals:
                try:
                    ical.fetch(started)
                except:
                    logging.warning("failed fetching %s" % ical.ical_href)
                    raise
                
    except Exception,e:
                logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    return HttpResponse("OK")
     
    
def split_ical(request):
    


    def is_future(ical):
        return True
        v_start=ical.find("BEGIN:VEVENT")
        start_line=ical.find('DTSTART:',v_start)
        end_line=ical.find("\n", start_line)
        logging.warning("startline: \n %s"% ical[start_line:end_line])
        if end_line < 0:
            end_line=ical.find("\r\n")
        try:
            dateobject= parse(ical[start_line+8:end_line])
        except ValueError:
            try: 
                dateobject= stringToDateTime(ical[start_line+8:end_line])
            except:
                logging.warning("Could not parse DTSTART %s" % ical[start_line+8:end_line])
            return True
        if hasattr(dateobject, 'tzinfo') and dateobject.tzinfo:

            diff= utc.localize(datetime.utcnow()) - dateobject
        else:
            diff= datetime.now() - dateobject

        return diff < timedelta(1)
    
    
    
    if request.method == 'POST':
        key=db.Key(request.POST.get('ical_key'))
        source=ICalendarSource.get(key)

        
        def split_ical_file(ical):
            first_vevent_start=ical.find('BEGIN:VEVENT')
            cal_meta=ical[0:first_vevent_start]
            #print cal_meta

            def next_vevent(start):
                end=ical.find('END:VEVENT',start)
                if end > -1:
                    end=end+10
                    cal=cal_meta+ical[start:end]+"\nEND:VCALENDAR"
                    return (cal, end)
                else:
                    return(None, None)
            vevent, index=next_vevent(first_vevent_start)   
            while vevent:
                yield vevent
                vevent, index=next_vevent(index)
        try:
            ical_source=memcache.get(request.POST.get('cache_key'))
            memcache.delete(request.POST.get('cache_key'))
            
            if not ical_source:
                logging.error("nothing in cache")
                return HttpResponse("nothing in cache")
            if ical_source:
                cal_count=0
                for event_ical in split_ical_file(ical_source):
                    cal_count=cal_count +1
                    if is_future(event_ical):
                        source_cache_key=request.POST.get('cache_key')
                        cache_key=source_cache_key +"-"+ str(cal_count)
                        memcache.set(cache_key, event_ical,1200)
                        
                        params=params={'cache_key': cache_key,
                                        'ical_key': request.POST['ical_key']}
                        logging.warning(params)
                        taskqueue.add(url='/events/parse_one_event/',
                                       params=params,
                                      name=cache_key,countdown=30)
                        
                                                                    
        except DeadlineExceededError:
                   return HttpResponse("Deadline Exceeded!")
        except Exception,e:
           logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
        return HttpResponse("OK")