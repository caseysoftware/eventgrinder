from django.conf.urls.defaults import *

urlpatterns = patterns('links.views',

    url(r'^add/$','add', name="add_link"),
   # url(r'^review/$','review', name="review_links"),
   # url(r'^change/$','add', name="change_link"),
    

)

