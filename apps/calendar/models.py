
from google.appengine.ext import db
from tipfy.ext.db import SlugProperty, TimeZoneProperty
from google.appengine.ext.db.polymodel import PolyModel


class CalendarImporter(db.Model):
    pass


class Calendar(PolyModel):
    creator=db.ReferenceProperty()
    title=db.StringProperty(required=True)
    slug=SlugProperty(title)
    subscribed_calendars=db.StringListProperty()
    subscribed_users=db.StringListProperty()
    
    
class ProfileCalendar(Calendar):
    pass
        
class EditedCalendar(Calendar):
    editors=db.StringListProperty()
    
    
class SourceCalendar(Calendar):
	source_uri=db.LinkProperty()
	credit_uri=db.LinkProperty()
	driver=db.StringProperty(required=True)
	
	
class SourceProcessTicket(db.Model):
	timestamp=db.DateTimeProperty(auto_now_add=True)
	source_calendar=db.ReferenceProperty()
	
class iCalSnippet(db.Model):
	ticket=db.ReferenceProperty(SourceProcessTicket)
	ical=db.TextProperty()
	calendar=db.ReferenceProperty(Calendar, collection_name='snippets')
	
	
class Event(PolyModel):
    title = db.StringProperty(required=True)
    start= db.DateTimeProperty()
    end=db.DateTimeProperty(required=True, indexed=True)
    allday=db.BooleanProperty(required=False)
    location=db.PostalAddressProperty(required=False, indexed=False)
    link=db.LinkProperty(required=False, indexed=False)
    description=db.TextProperty()
    cost=db.TextProperty(required=False)
    timezone=TimezoneProperty()
    created=db.DateTimeProperty(auto_now_add=True)
    updated=db.DateTimeProperty(auto_now_add=True)

class SourcedEvent(Event):
	ticket=db.ReferenceProperty()
	last_seen=db.DateTimeProperty(auto_now_add=True)
	last_ical=db.TextProperty()