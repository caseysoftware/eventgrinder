from django.conf.urls.defaults import *

urlpatterns = patterns('assets.views',
      url(r'^original-logo/(?P<version>[-\w]+)/(?P<site_slug>[-\w]+).(?P<ext>[-\w]+)$', 'site_logo_original', name="original-logo"),
)