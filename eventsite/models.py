from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import memcache
import os,logging
from aetycoon import CurrentDomainProperty, DerivedProperty
from datetime import datetime
from pytz.gae import pytz
import pychimp
utc=pytz.timezone('UTC')


class SitesMailchimp(db.Model):
    apikey=db.TextProperty(required=True)
    listid=db.TextProperty(required=False)
    listname=db.TextProperty(required=False)
    
    @property
    def api(self):
        return pychimp.PyChimp(self.apikey)
        


class Eventsite(db.Model):
    name=db.StringProperty(required=True)
    hostnames=db.StringListProperty(required=True)
    timezone=db.StringProperty(required=True)
    slug=db.StringProperty(required=True)
    original_logo=blobstore.BlobReferenceProperty()
    original_type=db.StringProperty()
    original_logo_version=db.IntegerProperty()
    logo=db.BlobProperty()
    logo_asset_href=db.StringProperty()
    audience=db.TextProperty(required=False)
    google_analytics_code=db.TextProperty(required=False)
    google_site_verification=db.TextProperty(required=False)
    disqus_shortname=db.TextProperty(required=False)
    twitter=db.TextProperty(required=False)
    bsa_code=db.TextProperty(required=False)
    offline=db.BooleanProperty()
    
    @property
    def chimp(self):
        return SitesMailchimp.all().ancestor(self).get()
    
    def expire_assets(self):
      
        envversion=os.environ['CURRENT_VERSION_ID']
        datestring=self.today.strftime('%b%d%y')
        for cache_key in ["front-page","ical", "latest-events-feed"]:
            complete_cache_key="%s-%s-%s-%s" %(envversion,self.slug, cache_key,datestring)
            memcache.delete(complete_cache_key)
            logging.warning("expired cached page %s" % complete_cache_key)

        
    
    @property
    def tz(self):
        return pytz.timezone(self.timezone)
    
    @property
    def host(self):
        if self.hostnames:
            return self.hostnames[0]
        else:
            return self.key_name
    
    @property
    def today(self):
        timezone=self.tz
        return utc.localize(datetime.utcnow()).astimezone(timezone).date()
    
    @property
    def link(self):
        if self.hostnames:
            return "http://%s/"% self.hostnames[0]
        else:
            return "http://%s/"% self.key().id_or_name()
            


    
