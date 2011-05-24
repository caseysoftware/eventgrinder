from django.conf.urls.defaults import *
from tasks import subscribe_email, start_schedule_newsletters, schedule_next_newsletter, create_and_send_campaign, send_campaign

urlpatterns = patterns('subscriptions.views',
      url(r'^new/$', 'new_subscription', name="new_subscription"),
      url(r'^subscribe_email/$',subscribe_email),


)

#([a-fA-F\d]{32})