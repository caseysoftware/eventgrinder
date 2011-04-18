from django.conf.urls.defaults import *
from feeds import LatestEvents
from django.views.decorators.cache import cache_page
from django.contrib.syndication.views import feed

feeds = {
    'latest': LatestEvents,
}



urlpatterns = patterns('',
      url(r'^feeds/(?P<url>.*)/$', cache_page(feed, 60*60),
                {'feed_dict': feeds}),
      url(r'^add/$', 'events.views.add_event', name="add-event"),
      url(r'^queue/$', 'events.views.event_queue', name="event-queue"),
      url(r'^parse_one_event/$', 'events.tasks.parse_one_event'),
      url(r'^parse_one_gdata/$', 'events.tasks.parse_one_gdata'),
      url(r'^start_expanding_recurring_events/$', 'events.tasks.start_expanding_recurring_events'),
      url(r'^expand_recurring_events/$', 'events.tasks.expand_recurring_events')
      
      
)

