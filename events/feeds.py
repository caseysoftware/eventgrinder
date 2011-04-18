from django.contrib.syndication.feeds import Feed
from models import Event
from eventsite import get_site
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist


class LatestEvents(Feed):

        def get_object(self, bits):
            site=get_site()
            return site

        def title(self, obj):
            return "Latest events added to %s" % obj.name
        
        def link(self, obj):
            if obj.hostnames:
                return "http://%s/"% obj.hostnames[0]
            else:
                return "http://%s/"% obj.key().id_or_name()

        def items(self, obj):
            
           return Event.all().filter('status = ', 'approved').order('-approved_on').fetch(30)
           
        def item_link(self,item):
            return item.link
            
        def item_title(self,item):
            return item.title
            

            
        