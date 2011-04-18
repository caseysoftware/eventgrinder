from django import forms
from django.forms.util import ErrorList
from google.appengine.api.users import get_current_user
from html5.forms import URLInput, DateInput, TextInput
from eventsite.models import Eventsite
from eventsite import get_site
from pytz.gae import pytz
from utility import slugify
from eventsite.widgets import SelectTimeWidget
from datetime import time, datetime
from models import Event
from account.utility import get_current_profile

utc=pytz.timezone('UTC')
  

REPEATS_CHOICES=[
( None, 'Does Note Repeat'),
('MONTHLY','Monthly'),
('WEEKLY', 'Weekly')
]  
 

class EventBasicsForm(forms.Form):
    title = forms.CharField(max_length=255, label="Event Name", widget=TextInput(attrs={'placeholder':''}))
    link=forms.URLField(required=False, help_text="The URL to this event or groups official page.", 
                        widget=TextInput(attrs={'placeholder':'http://whatever'}))
    description=forms.CharField(widget=forms.Textarea,
                            required=False)
    start_date= forms.DateField(help_text="The day the event starts",
                                widget=DateInput(attrs={'placeholder':'click to select a date'}))
    start_time=forms.TimeField(widget=SelectTimeWidget(twelve_hr=True, minute_step=15), initial=time(18))
    end_date= forms.DateField(required=False, 
                help_text="The day the event ends",
                widget=DateInput)
    end_time=forms.TimeField(widget=SelectTimeWidget(twelve_hr=True, minute_step=15),initial=time(21))
    location=forms.CharField(required=False,label="Where",max_length=255,
                                widget=TextInput(attrs={'placeholder':'100 Awesome St, Washington, DC'}),
                                help_text="Leave blank if a location hasn't been decided on. Complete street addresses are awesome")

                        
    cost=forms.CharField(max_length=100, 
        required=True, 
        widget=TextInput(), 
        initial="Free",
        help_text="A price or range of prices. Discount codes are cool too.")
    
    
    
    
    def clean(self):
        data = self.cleaned_data
        #if not (data.get('link') or data.get('description')):
        #    self._errors["link"] = ErrorList(["You must provide either a link or description"])
        site=get_site()
        local_today=utc.localize(datetime.utcnow()).astimezone(site.tz).date()
        if data.has_key('start_date'):
            if (data['start_date'] < local_today) and ((data['end_date'] == None) or (data['end_date'] < local_today)):
                self._errors["start_date"] = ErrorList(["This event occurs in the past"])
                
        return super(EventBasicsForm, self).clean()

        
            

        
    def save(self):
        site=get_site()
        timezone=pytz.timezone(site.timezone)
        cleaned_data=self.cleaned_data
            
        profile=get_current_profile()
        if profile.userlevel > 9:
            credit_name, credit_link= "Staff", None
            status='approved'
            approved_on=datetime.now()
        else:
            credit_name, credit_link = profile.nickname, profile.link
            status='submitted'
            approved_on=None
        event=Event(title=cleaned_data.get("title"),
        link=cleaned_data.get("link") or None,
        description=cleaned_data.get("description")[:250] or None,
        start=timezone.localize(datetime.combine(cleaned_data.get("start_date"),cleaned_data.get("start_time"))),
        end=timezone.localize(datetime.combine(cleaned_data.get("end_date") or                  cleaned_data.get("start_date"),cleaned_data.get("end_time"))),
        location=cleaned_data.get("location") or None,
        submitted_by=get_current_profile(),
        status=status,
        site=get_site(),
        cost=cleaned_data.get("cost"),
        credit_name=credit_name,
        credit_link=credit_link,
        approved_on=approved_on,
        approved_by=profile,
        )


            
            
        event.put()
        return event
        

                                

                                
	
