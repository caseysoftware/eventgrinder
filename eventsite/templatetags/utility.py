from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()
from eventsite import get_site
from dateutil.relativedelta import *


@register.filter(name="week_url")
def week_url(day):
    site=get_site()
    monday=day+relativedelta(MO(-1))
    return "http://%s/week-of/%s" %( site.hostnames[0], monday.strftime("%Y-%m-%d"))
    