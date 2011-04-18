import logging,os
import namespace_registry
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.defaultfilters import slugify, striptags
from django.core.urlresolvers import reverse
from django.contrib import messages

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api.labs import taskqueue
from google.appengine.ext.db import Query
from google.appengine.api.images import get_serving_url

from account.utility import admin_required, profile_required
from forms import SiteDetailsForm, LogoUploadForm, SiteCreateForm, MailChimpApiKey
from eventsite import get_site, site_required, models, site_cache
from blob_helper import get_uploads
from django import forms
from google.appengine.api.namespace_manager import set_namespace
import namespace_registry



import pychimp, logging

@admin_required
def create_site(request):
    hostname=request.get_host()
    site=get_site()
    if site:return HttpResponseRedirect(reverse('admin-home'))
    form=SiteCreateForm()
    if request.method == 'POST':
        form=SiteCreateForm(request.POST)
        if form.is_valid():
            new_site=models.Eventsite(name=form.cleaned_data['name'].strip(),
                                    timezone= form.cleaned_data['timezone'].strip(),
                                    audience=form.cleaned_data['audience'].strip(),
                                    hostnames=[hostname,],
                                    key_name=hostname,
                                    slug=form.cleaned_data['slug'])
            new_site.put()
            return HttpResponseRedirect(reverse('admin-home'))
    return render_to_response('eventsite/admin.html', locals(), context_instance=RequestContext(request))
        
            
  
@admin_required
def index(request):
      site=get_site()
      if not site: 
          return HttpResponseRedirect(reverse('create-site'))
      else:
          return HttpResponseRedirect(reverse('edit-site'))
  

@admin_required
def edit_site(request):
    site=get_site()
    if not site: return HttpResponseRedirect(reverse('create-site'))

    if request.method == 'POST': # If the form has been submitted...
        form = SiteDetailsForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            site.name=form.cleaned_data['name'].strip()
            site.timezone= form.cleaned_data['timezone'].strip()
            site.audience=form.cleaned_data['audience'].strip()
            site.hostnames=form.cleaned_data['hostnames']
            site.google_site_verification=form.cleaned_data['google_site_verification'].strip()
            site.google_analytics_code=form.cleaned_data['google_analytics_code'].strip()
            site.twitter=form.cleaned_data['twitter'] or None
            site.bsa_code=form.cleaned_data['bsa_code'] or None
            site.offline=form.cleaned_data['offline'] or None
            site.put()
            site.expire_assets()

            
    else:
        site=get_site()
        if site:
            site_details={'name':site.name, 'timezone':site.timezone, 'slug':site.slug,
            'audience': site.audience, 'hostnames':",".join(site.hostnames),
            'google_analytics_code':site.google_analytics_code,
            'google_site_verification':site.google_site_verification,
            'twitter':site.twitter,
            }
            form=SiteDetailsForm(site_details)
        else:    
            form = SiteDetailsForm() # An unbound form

   
    return render_to_response('eventsite/admin.html', locals(), context_instance=RequestContext(request))
    
     


@admin_required
def configure_mailchimp(request):
    site=get_site()
    mc=models.SitesMailchimp.all().ancestor(site).get()
    if not mc:
        if request.method == 'POST':
            form=MailChimpApiKey(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('configure-mailchimp'))
        else:
            form = MailChimpApiKey()    
        
        return render_to_response('admin/mailchimp_apikey.html', locals(), context_instance=RequestContext(request))

    else:
        chimp=pychimp.PyChimp(mc.apikey)
        lists=chimp.lists()
        list_choices=[(l['id']+'!@!'+l['name'], l['name']) for l in lists]
        
        class MailChimpListForm(forms.Form):
            mailchimp_list=forms.ChoiceField(choices=list_choices)
            
            def save(self):
                mc.listid, mc.listname=self.cleaned_data['mailchimp_list'].split('!@!')
                mc.put()
        
        if request.method=='POST':
            form=MailChimpListForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, "Mailing list configured!")
                return HttpResponseRedirect(reverse('admin-home'))

        
        form=MailChimpListForm()
        return render_to_response('admin/mailchimp_apikey.html', locals(), context_instance=RequestContext(request))
        return HttpResponse(lists)

@admin_required
def manage_users(request):
    site=get_site()
    users= site.profile_set
    if request.method == 'POST':
        updated_users=[]
        for key in request.POST.keys():
            #return HttpResponse(str(request.POST))
            if key.startswith('set-userlevel-'):
                
                u=site.profile_set.filter('slug = ', key[14:]).get()
                u.userlevel=int(request.POST[key])
                updated_users.append(u)
                
        db.put(updated_users)
    return render_to_response('admin/users.html', locals(), context_instance=RequestContext(request))
    
    



@admin_required
def logo(request):
    site=get_site()
    if request.method=='POST':
        files=get_uploads(request)
        for upload in files:
            if site.original_logo:site.original_logo.delete()
            site.original_logo=upload
            if site.original_logo_version:
                site.original_logo_version=site.original_logo_version+1
            else:
                site.original_logo_version=1
            ext=upload.filename.split('.')[-1]
            
            site.logo_asset_href=get_serving_url(str(upload.key()), 512)
            #site.logo_asset_href=reverse('original-logo',kwargs={'site_slug':site.slug,
            #                                            'version':site.original_logo_version,
            #                                            'ext':ext})
            
            
            
        site.put()
        site.expire_assets()
        return HttpResponseRedirect(reverse('logo-upload'))
    
    asset_href=site.logo_asset_href
    upload_url=blobstore.create_upload_url(reverse('logo-upload'))
    form=LogoUploadForm()
    return render_to_response('admin/logo.html', locals(), context_instance=RequestContext(request))
    
    
    
    
def migrate(request):
    
    def clone_entity(e, **extra_args):
      """Clones an entity, adding or overriding constructor attributes.

      The cloned entity will have exactly the same property values as the original
      entity, except where overridden. By default it will have no parent entity or
      key name, unless supplied.

      Args:
        e: The entity to clone
        extra_args: Keyword arguments to override from the cloned entity and pass
          to the constructor.
      Returns:
        A cloned, possibly modified, copy of entity e.
      """
      klass = e.__class__
      props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
      props.update(extra_args)
      return klass(**props)
    
    
    
    set_namespace('')
    key_name = os.environ.get('HTTP_HOST')
    #site=site=models.Eventsite.all().filter('hostnames = ',key_name).get()
    site=Query(models.Eventsite, namespace='').filter('hostnames = ',key_name).get()
    if not site:return HttpResponse("Couldn't find a site to migrate")
    new_namespace=request.environ.get('HTTP_HOST').split(':')[0]
    old_chimp=site.chimp
    set_namespace(new_namespace)
    namespace_registry.register(new_namespace)
    new_site=clone_entity(site, key_name=new_namespace)
    new_site.put()
    namespace_registry.register(new_namespace)
    if old_chimp:
        new_chimp=clone_entity(old_chimp, parent=new_site)
        new_chimp.put()
    taskqueue.add(url='/admin/migrate-profiles/', params={'new_namespace':new_namespace,
                                        'old_site':site.key(),
                                        'new_site':new_site.key(),
                                        },)

    set_namespace('')                                                    
    return HttpResponse('Migrated Site')
    
    