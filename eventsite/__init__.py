import os
from eventsite.models import Eventsite
from google.appengine.api.namespace_manager import set_namespace, get_namespace
from django.http import HttpResponse, HttpResponseRedirect

from namespace_registry import register

site_cache={}


def get_site(key_name=None):
	key_name = os.environ.get('HTTP_HOST')
	site=site_cache.get(key_name, None)
	if site: return site
	site=Eventsite.all().get()
	site_cache[key_name]=site
	register(os.environ.get('HTTP_HOST'))
	return site
    
    
    
    
def site_required(func, bypass_offline_check=False):
    def no_site(request, *args, **kwargs):
        return HttpResponse("No calendar with that name exists (yet!)")

    def replacement_view(request, *args, **kwargs):
        request.site=get_site()
        if request.site and not (request.site.offline and bypass_offline_check):
            return func(request, *args, **kwargs)
        else:
            return no_site(request, *args, **kwargs)

    return replacement_view
    
    
def site_required(func):
    def no_site(request, *args, **kwargs):
        return HttpResponse("No calendar with that name exists (yet!)")

    def replacement_view(request, *args, **kwargs):
        request.site=get_site()
        if request.site:
            return func(request, *args, **kwargs)
        else:
            return no_site(request, *args, **kwargs)

    return replacement_view
    