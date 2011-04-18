import logging, traceback

from django.http import HttpResponse
from django.template.defaultfilters import date
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from google.appengine.api.labs.taskqueue import TaskAlreadyExistsError
from google.appengine.api.namespace_manager import set_namespace

import pychimp, os
from eventsite.models import Eventsite
from eventsite import get_site
from datetime import datetime
from dateutil.relativedelta import *

import namespace_registry

#from models import SitesNextNewsletter

from pytz.gae import pytz

utc=pytz.timezone('UTC')


def subscribe_email(request):
    api=pychimp.PyChimp(request.POST['apikey'])
    api.listSubscribe(request.POST['list_id'], request.POST['email'],'')
    return HttpResponse("OK")
    
    
    
    
def send_campaign(request):
    api=pychimp.PyChimp(request.POST['apikey'])
    api.campaignSendNow(request.POST['campaign'])
    return HttpResponse("sent campaign")
    
    
    

def create_and_send_campaign(request):
    try:
        if request.method == 'POST':
            api=pychimp.PyChimp(request.POST['apikey'])
            campaign=api.campaignCreate('regular', {'list_id':request.POST['listid'], 'subject':request.POST['subject'], 'from_email':request.POST['from_email'], 'from_name':request.POST['from_name']}, {'url':request.POST['url'], 'text': "check out this weeks events at %s"% request.POST['url']})
            taskqueue.add(url='/subscriptions/send_campaign/', 
                params={'apikey':request.POST['apikey'], 'campaign':campaign,
                }, countdown=20,
                name="campaign-%s"% campaign)
        
        
        
            return HttpResponse("Created campaign %s"% campaign)
        
        
        else:
            site=get_site()
            chimp=site.chimp
            return HttpResponse("""
            <form method="POST">
            url: <input type="text" value="" name="url"/><br/>
            subject: <input type="text" value="" name="subject"/><br/>
            from name: <input type="text" value="" name="from_name"/><br/>
            from email: <input type="text" value="" name="from_email"/>
            <input type="hidden" name="apikey" value="%s"/>
            <input type="hidden" name="listid" value="%s"/>
            <input type="submit" value="Send"/>
            </form>
        
        
        
            """% (chimp.apikey, chimp.listid))
    
    except Exception,e:
        logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
        HttpResponse("OK")
    HttpResponse("OK")


def schedule_next_newsletter(request):
    try:
        site=db.get(db.Key(request.POST['site']))
        now=datetime.now()
        schedule=site.tz.localize(now+relativedelta(days=1,weekday=MO, hour=6, minute=0, second=0)).astimezone(utc).replace(tzinfo=None)
        if os.environ['SERVER_SOFTWARE'].startswith('Dev'):schedule=datetime.now()
        #next_newsletter=SitesNextNewsletter.get_or_insert('%s-%s' %(site.slug, schedule.strftime("%Y%W")),
        #publish_at=site.tz.localize(schedule))
        chimp=site.chimp
        if chimp:
            url="http://%s/week-of/%s/newsletter" %( site.host,date(schedule,"Y-n-j") )
            url=url.replace('localhost:8083', 'dctechevents.com')
            params={'url':url, 'apikey':chimp.apikey, 'listid':chimp.listid,
            'from_name':  site.name,
            'from_email': 'inquiries@eventgrinder.com',
            'subject': "%s Weekly" % site.name
            
            }
            logging.info("Scheduling campaign with params %s" % str(params) )
            taskqueue.add(url='/subscriptions/create_and_send/', 
                params=params,
                name="weekly-%s-%s"%(site.slug, schedule.strftime("%Y%W")), eta=schedule)
        else:
            logging.error("no mailchimp setup for %s" % site.slug)
        
    except TaskAlreadyExistsError:
        pass
    
    except Exception,e:
        logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    return HttpResponse("OK")
    
    
def start_schedule_newsletters(request):
    try:
        for ns in namespace_registry.all():
            set_namespace(ns.ns)
            for site in Eventsite.all().filter('offline =', False):
                taskqueue.add(url='/subscriptions/schedule_next_newsletter/',
                       params={'site': str(site.key())}
                      )
    except Exception,e:
          logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    return HttpResponse("OK")
    
    
"""    c=api.campaignCreate('regular', {'list_id':'4638de2c54','subject':'hey', 'from_email':'rosskarchner@gmail.com', 'from_name':'Ross'}, {'url':'http://www.dctechevents.com/week-of/2010-7-19/newsletter', 'text': "check out this weeks events at http://www.dctechevents.com/week-of/2010-7-19/newsletter"})
"""