

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template.defaultfilters import slugify, striptags
from django.core.urlresolvers import reverse
import logging


from google.appengine.api.namespace_manager import set_namespace, get_namespace
from google.appengine.api.images import get_serving_url


from eventsite import Eventsite


def site_logo_original(request, site_slug,ext,version):
    site=Eventsite.all().get()
    response=HttpResponse(mimetype=site.original_logo.content_type)
    response['Cache-Control']="max-age=157784630, must-revalidate"
    response['X-AppEngine-BlobKey']=str(site.original_logo.key())
    return response
    