from django import forms
from django.forms.util import ErrorList
from html5.forms import URLInput, DateInput, TextInput
from account.utility import get_current_profile
from eventsite import get_site
from google.appengine.ext import db
import vobject
#from models import ICalendarSource
from fields import iCalURLField
from datetime import datetime


class ICalendarEditForm(forms.Form):
    name = forms.CharField(required=True, help_text="Name of the calendar or group",
                 widget=TextInput(attrs={'placeholder':"Sasha's Cool Calendar"}))
    link=forms.URLField(required=False, help_text="The homepage of the group hosting this calendar", 
                 widget=TextInput(attrs={'placeholder':'http://whatever'}))
    ical= iCalURLField(required=True, help_text="Address of the iCalendar file", 
                label="iCalendar URL",
                 widget=TextInput(attrs={'placeholder':'http:// or webcal:// '}))
    source_key=forms.CharField(required=False)
                 
    def save(self):
        cleaned_data=self.cleaned_data
        profile=get_current_profile()
        from models import ICalendarSource
        ical= ICalendarSource(site=get_site(),
                              name=cleaned_data['name'],
                              source_link=cleaned_data['link'] or None,
                              ical_href=cleaned_data['ical'],
                              submitted_by=profile,
                              status='submitted',
                              last_fetch=datetime(year=1970, month=1, day=1)
                              )
        ical.put()
                              

class ICalApprovalForm(forms.Form):
    source_key=forms.CharField(required=True)
    state=forms.CharField(required=True)
    trusted=forms.BooleanField(required=False)
    tags=forms.CharField(required=False)
    
    def save(self):
        cleaned_data=self.cleaned_data
        site=get_site()
        ical=site.icalendarsource_set.filter(' __key__ =', db.Key(cleaned_data['source_key']) ).get()
        tags=[t.strip() for t in cleaned_data.get("tags","").lower().split(',')]
        if cleaned_data['state']== 'fetch now':
            ical.fetch()
            return
        if cleaned_data['state']== 'save': 
            state='approved'
        else:
            state=cleaned_data['state']
        
        
        ical.status=state
        ical.trusted=cleaned_data['trusted']
        ical.default_tags=tags
        ical.put()
        return ical