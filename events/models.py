import datetime
from google.appengine.ext import db
from google.appengine.api import users
from sources.models import ICalendarSource
from eventsite.models import Eventsite
from account.models import Profile
from utility import slugify
from pytz.gae import pytz
from dateutil.rrule import rrule, DAILY
from dateutil import parser

from aetycoon import DerivedProperty

from datetime import time, datetime, date, timedelta
from dateutil.relativedelta import *
import hashlib
import vobject
import logging

utc=pytz.timezone('UTC')






    

class Event(db.Model):
    title = db.StringProperty(required=True)
    start= db.DateTimeProperty(required=True)
    end=db.DateTimeProperty(required=True, indexed=True)
    location=db.PostalAddressProperty(required=False, indexed=False)
    link=db.LinkProperty(required=False, indexed=False)
    description=db.TextProperty()
    cost=db.TextProperty(required=False)
    submitted_by=db.ReferenceProperty(Profile,required=False, collection_name='events_submitted')
    submitted_at=db.DateTimeProperty(auto_now_add=True)
    site=db.ReferenceProperty(Eventsite, required=True)
    sort_dt=db.DateTimeProperty()
    status=db.StringProperty(required=True)
    score=db.IntegerProperty(indexed=False)
    approved_by=db.ReferenceProperty(Profile,indexed=False, collection_name="events_approved")
    approved_on=db.DateTimeProperty()
    tags=db.StringListProperty()
    credit_name=db.StringProperty(required=True, indexed=False)
    credit_link=db.LinkProperty(required=False, indexed=False)
    source=db.ReferenceProperty(required=False)
    last_seen=db.DateTimeProperty(required=False)
    source_uid=db.StringProperty(required=False)
    repeats_frequency=db.StringProperty(required=False)
    repeats_weekday=db.IntegerProperty(required=False)
    #repeats_setpos=db.IntegerProperty(required=False)
    repeats_monthday=db.IntegerProperty(required=False)

    def __unicode__(self):
        return "%s: %s" %(self.local_start.date().strftime("%a %b %d"), self.title)

    @DerivedProperty
    def local_start(self):
        if self.start.tzinfo == None:
            ls= utc.localize(self.start).astimezone(self.site.tz)
            return ls.replace(tzinfo=None)
        else:
            return self.start.astimezone(self.site.tz) + self.site.tz.utcoffset(self.site.tz)
    
    @DerivedProperty    
    def local_end(self):
        if self.end.tzinfo == None:
            ls= utc.localize(self.end).astimezone(self.site.tz)
            return ls.replace(tzinfo=None)
        else:
            return self.end.astimezone(self.site.tz) + self.site.tz.utcoffset(self.site.tz)
        
        
    @DerivedProperty
    def multiday(self):
         return ((self.local_start.date() < self.local_end.date()) and  (self.local_end -self.local_start) > timedelta(1))
        
    @DerivedProperty
    def allday(self):
        return ((self.local_start.time() == time(0) and self.local_end.time() == time(0)))
    
    @DerivedProperty
    def continues(self):
        if self.multiday:
            rule=rrule(DAILY, dtstart=self.local_start, until=self.local_end)
            return [str(dt.date()) for dt in list(rule)]
        else:
            return None
    
    
    @DerivedProperty
    def repeats_setpos(self):
        month_start=(self.local_start+relativedelta(day=1))
        weekday=(MO,TU,WE,TH,FR,SA,SU)[self.local_start.weekday()]
        tests=[(-1,month_start+relativedelta(day=31,weekday=weekday(-1))),
                (1,month_start+relativedelta(day=1,weekday=weekday(1))),
                (2,month_start+relativedelta(day=1,weekday=weekday(2))),
                (3,month_start+relativedelta(day=1,weekday=weekday(2))),]
        
        for pos, d in tests:
            logging.warning("comparing %s and %s" %(str(d),str(self.local_start.date()) ))
            if self.local_start.date()==d.date(): return pos
    
    
    @property
    def event_link(self):
        return self.link    
    
    @property
    def item_pubdate(self):
        return self.approved_on
    
    
    def copy(self, rule):
        copies=[]
        delta=self.end-self.start
        #search_after=utc.localize(datetime.now())
        logging.warning(rule)
        for dt in rule[1:6]:
            if not (dt.date() > self.local_start.date()): continue 
            logging.warning(dt)
            new_start=self.site.tz.localize(self.local_start.replace(tzinfo=None)).replace(dt.year,dt.month,dt.day)
            e=Event(parent=self,key_name=dt.strftime("%Y%m%j"),
            title = self.title,
            start= new_start,
            end=new_start+delta,
            location=self.location,
            link=self.link,
            description=self.description,
            cost=self.cost,
            site=self.site,
            sort_dt=self.sort_dt,
            status=self.status,
            tags=self.tags,
            credit_name=self.credit_name,
            credit_link=self.credit_link,
            last_seen=datetime.now()  
            )
            copies.append(e)
        return copies
    
    
    def check_scores(self):
        if (self.approved_on or (self.score > 2)):
            pass
    
    
    
    @classmethod
    def from_gdata(cls,gevent, source):
            #logging.warning(type(parser.parse(gevent.when[0].start_time)))
            dtstart=parser.parse(gevent.when[0].start_time)
            
            dtend=parser.parse(gevent.when[0].end_time)
            summary=gevent.title.text
            
            location= gevent.where[0].value_string or None
            link= source.source_link
            uid=gevent.id.text
            key_name=uid
            #first check for duplicate key name
            existing_event=Event.get_by_key_name(key_name)
            #fail-over to name and start

            if not existing_event:
                existing_event=source.event_set.filter('title = ', summary).filter('start = ',dtstart).get()


            logging.warning("searched for existing event with key %s, found %s" %(key_name,existing_event))
            if existing_event and source.trusted:
                        existing_event.title=summary or "Untitled Event"
                        existing_event.start=dtstart
                        existing_event.end=dtend
                        existing_event.last_seen=datetime.now()
                        if location:existing_event.location=location
                        if link: existing_event.link=link or source.source_link
                        existing_event.put()
                        return existing_event

            if existing_event and not source.trusted:
                return existing_event

            if source.trusted:
                    status='approved'
                    approved_on=datetime.now()
            else:
                    status='submitted'
                    approved_on=None
            event=Event(key_name=key_name,
                title=summary or "Untitled Event",
                start=dtstart,
                end=dtend,
                site=source.site,
                location=location,
                link=link,
                status=status,
                tags=source.default_tags,
                credit_name=source.name,
                credit_link=source.source_link,
                source=source,
                source_uid=uid,
                approved_on=approved_on,
                last_seen=datetime.now())
                #source_ical_hash=source_ical_hash)
            event.put()
            source.site.expire_assets()
            return event
            
            
    @classmethod
    def from_vcal(cls,vcal, source):
        def start_dt(dateobject):
            if type(dateobject) == datetime: 
                if hasattr (dateobject,'tzinfo') and dateobject.tzinfo:
                    return dateobject
                else:
                    return source.site.tz.localize(dateobject)
            if not dateobject: return None
            return source.site.tz.localize(datetime.combine(dateobject, time(0)))

        def end_dt(dateobject):
            if not dateobject: return None
            if type(dateobject) == datetime:
                    if hasattr (dateobject,'tzinfo') and dateobject.tzinfo:
                        return dateobject
                    else:
                        return source.site.tz.localize(dateobject)


            return source.site.tz.localize(datetime.combine(dateobject, time(0)))
        #logging.warning("hey!")
        parsedCal = vobject.readOne(vcal)
        vevent=parsedCal.vevent
        dtstart=start_dt(vevent.dtstart.value)
        if dtstart < utc.localize(datetime.today()) - timedelta(1):
            return logging.warning("skipping old event with dtstart %s" % dtstart)
        
        
        if (hasattr(vevent,'dtend') and vevent.dtend):
            dtend=(end_dt(vevent.dtend.value) or dtstart)
        else:
            dtend=dtstart
        summary=vevent.summary.value
        location= vevent.getChildValue('location') or None
        link=vevent.getChildValue('url') or source.source_link
        uid=vevent.uid.value or link or str(dtstart)
        key_name="%s-%s-%s"%(source.site.slug, source.slug,uid)
        #first check for duplicate key name
        existing_event=Event.get_by_key_name(key_name)
        #fail-over to name and start
        
        if not existing_event:
            existing_event=source.event_set.filter('title = ', summary).filter('start = ',dtstart).get()


        logging.warning("searched for existing event with key %s, found %s" %(key_name,existing_event))
        if existing_event and source.trusted:
                    existing_event.title=summary or "Untitled Event"
                    existing_event.start=dtstart
                    existing_event.end=dtend
                    existing_event.last_seen=datetime.now()
                    if location:existing_event.location=location
                    if link: existing_event.link=link or source.source_link
                    #existing_event.source_ical_hash=source_ical_hash
                    existing_event.put()
                    return existing_event
                    
        if existing_event and not source.trusted:
            return existing_event
                    
        if source.trusted:
                status='approved'
                approved_on=datetime.now()
        else:
                status='submitted'
                approved_on=None
        event=Event(key_name=key_name,
            title=summary or "Untitled Event",
            start=dtstart,
            end=dtend,
            site=source.site,
            location=location,
            link=link,
            status=status,
            tags=source.default_tags,
            credit_name=source.name,
            credit_link=source.source_link,
            source=source,
            source_uid=uid,
            approved_on=approved_on,
            last_seen=datetime.now())
            #source_ical_hash=source_ical_hash)
        event.put()
        source.site.expire_assets()
        return event

        @classmethod
        def for_site_week(cls,site,day):
            monday=day+relativedelta(weekday=MO(-1))
            sunday=monday+relativedelta(weekday=SU)
            
