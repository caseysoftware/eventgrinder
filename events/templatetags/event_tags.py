from django import template
from django.template import defaultfilters
from urlparse import urlparse
from dateutil.relativedelta import *
register = template.Library()
from eventsite import get_site
from pytz.gae import pytz
from datetime import datetime
utc=pytz.timezone('UTC')


@register.filter(name="eventlink")
def eventlink(event):
    if not event.link:return event.title
    href=event.link
    return "<a href='%s' class='url'>%s</a>" % (href, event.title)
    
@register.filter(name="creditlink")    
def creditlink(event):
    if not event.credit_link:return event.credit_name.lower()
    href=event.credit_link
    return "<a href='%s' class='url'>%s</a>" % (href, event.credit_name.lower())
    
@register.filter(name="monday_of_week")    
def monday_of_week(day):
    return day + relativedelta(weekday=MO(-1))
    
    
@register.filter(name="naturalweek")    
def naturalweek(day):
    site=get_site()
    timezone=site.tz
    today=today=utc.localize(datetime.utcnow()).astimezone(timezone).date()
    week=day+relativedelta(weekday=MO(-1))
    if week == today+relativedelta(weekday=MO(-1)): return "this week"
    if week == today+relativedelta(days=+1,weekday=MO(+1)): return "next week"
    return defaultfilters.date(week, "week of F jS Y")
    