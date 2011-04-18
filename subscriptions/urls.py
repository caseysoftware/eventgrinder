from django.conf.urls.defaults import *
from tasks import subscribe_email, start_schedule_newsletters, schedule_next_newsletter, create_and_send_campaign, send_campaign

urlpatterns = patterns('subscriptions.views',
      url(r'^new/$', 'new_subscription', name="new_subscription"),
      url(r'^subscribe_email/$',subscribe_email),
      url(r'^start_schedule_newsletters/$', start_schedule_newsletters),
      url(r'^create_and_send/$', create_and_send_campaign),
      url(r'^send_campaign/$', send_campaign),
      url(r'^schedule_next_newsletter/$', schedule_next_newsletter),

)

#([a-fA-F\d]{32})