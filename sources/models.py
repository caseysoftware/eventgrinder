from google.appengine.ext import db
from eventsite.models import Eventsite
from account.models import Profile
import sources.forms
from aetycoon import DerivedProperty
from django import forms
from django.template.defaultfilters import slugify
from google.appengine.api import urlfetch
import chardet
import logging
import vobject
from datetime import datetime, time, date
from dateutil.relativedelta import *
from google.appengine.api.labs import taskqueue
from google.appengine.api import memcache

from urllib import unquote

import gdata.calendar.service

calendar_service = gdata.calendar.service.CalendarService()


class ICalendarSource(db.Model):
    site=db.ReferenceProperty(Eventsite, required=True)
    name = db.StringProperty(required=True, indexed=False)
    source_link=db.LinkProperty(indexed=False, required=False)
    ical_href=db.LinkProperty(required=True, indexed=False)
    status= db.StringProperty(required=True)
    trusted=db.BooleanProperty()
    default_tags=db.StringListProperty()
    submitted_by=db.ReferenceProperty(Profile,required=False, collection_name='icals_submitted')
    submitted_at=db.DateTimeProperty(auto_now_add=True)
    approved_by=db.ReferenceProperty(Profile,indexed=False, collection_name="icals_approved")
    approved_on=db.DateTimeProperty(indexed=False)
    last_fetch=db.DateTimeProperty(required=False)
    content=db.TextProperty(required=False)
    is_rssfeed=db.BooleanProperty()
    
    @property
    def approval_form(self):
        return sources.forms.ICalApprovalForm(initial={'trusted': self.trusted, 'tags': ','.join(self.default_tags)})
    
    @DerivedProperty
    def slug(self):
        return str(slugify(self.name))   
        
    def fetch(self,started=None, timestamp=None):
        format_start="%Y%m%d%H%M"
        if not started: started=str(datetime.now())
        if not timestamp:timestamp= datetime.now().strftime("%Y%m%d%H%M")
        if self.ical_href.startswith('http://www.google.com/calendar/ical/'):
            gcal_id=unquote(self.ical_href[36:].split('/')[0])
            query = gdata.calendar.service.CalendarEventQuery(gcal_id, 'public', 'full-noattendees')
            query.start_min= self.site.today.strftime("%Y-%m-%d") 
            query.recurrence_expansion_end=(date.today()+relativedelta(months=3)).strftime("%Y-%m-%d")
            query.start_max=(date.today()+relativedelta(months=3)).strftime("%Y-%m-%d")
            query.singleevents='true'
            result=urlfetch.fetch(query.ToUri(), allow_truncated=False, deadline=10)
            if result.status_code == 200:
                detection=chardet.detect(result.content)
                self.last_fetch=datetime.now()
                self.put()
                cache_key="%s-%s-%s" %(self.site.slug, self.slug,timestamp)
                memcache.add(cache_key, result.content.decode(detection['encoding']),600) 
                logging.warning("cached gdata with key %s"% cache_key)
                taskqueue.add(url='/sources/split_gdata/', params={'ical_key': self.key(),
                                                                  'cache_key':cache_key,
                                                                  'timestamp':timestamp},
                                                                  name=cache_key
                                                                  )
                logging.warning("enqueued splitting of %s" % self.ical_href)
            return
        
        result=urlfetch.fetch(self.ical_href, allow_truncated=True, deadline=5)
        if result.status_code == 200:
            detection=chardet.detect(result.content)
            self.last_fetch=datetime.now()
            self.put()
            cache_key="%s-%s-%s" %(self.site.slug, self.slug,timestamp)
            memcache.add(cache_key, result.content.decode(detection['encoding']),600) 
            logging.warning("cached ical with key %s"% cache_key)
            taskqueue.add(url='/sources/split_ical/', params={'ical_key': self.key(),
                                                              'cache_key':cache_key,
                                                              'timestamp':timestamp},
                                                              name=cache_key
                                                              )
            logging.warning("enqueued splitting of %s" % self.ical_href)
          
