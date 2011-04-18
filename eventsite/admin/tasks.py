from events.models import Event
from django.http import HttpResponse
from dateutil.parser import parse
from google.appengine.api.labs import taskqueue
from dateutil.relativedelta import relativedelta
import logging, traceback
from eventsite import get_site
from eventsite.models import Eventsite
from account.models import Profile
from sources.models import ICalendarSource
from google.appengine.api.namespace_manager import set_namespace, get_namespace
from google.appengine.ext import db
from google.appengine.ext.db import Query


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

def clone_event(e, **extra_args):
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
  logging.warning(props)
  del props['local_start']
  del props['local_end']
  del props['multiday']
  del props['allday']
  del props['continues']
  del props['repeats_setpos']
  
  props.update(extra_args)
  return klass(**props)

def clone_source(e, **extra_args):
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
    logging.warning(props)
    #del props['submitted_by']
    del props['slug']


    props.update(extra_args)
    return klass(**props)



def migrate_sources(request):
    try:
          set_namespace('')
          old_site=db.get(db.Key(request.POST.get('old_site')))
          q=Query(ICalendarSource, namespace='').filter('site = ',old_site)
          old_sources=q.fetch(1000)


          set_namespace(request.POST.get('new_namespace'))
          new_site=db.get(db.Key(request.POST.get('new_site')))

          for old_source in old_sources:

              if old_source.submitted_by:
                  old_source.submitted_by=Profile.all().filter('slug =', old_source.submitted_by.slug).get()                    
              if old_source.approved_by:
                  old_source.approved_by=Profile.all().filter('slug =', old_source.approved_by.slug).get()

              new_source=clone_source(old_source, key_name=old_source.slug)
              new_source.site=new_site
              new_source.put()
              #old_source.delete()
           
           
          taskqueue.add(url='/admin/migrate-events/', params={'new_namespace':request.POST.get('new_namespace'),
                                                              'old_site':old_site.key(),
                                                              'new_site':new_site.key(),
                                                              },)
              

    except Exception,e:
                  logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    return HttpResponse("OK")


def migrate_profiles(request):
    try:
        set_namespace('')
        old_site=db.get(db.Key(request.POST.get('old_site')))
        q=Query(Profile, namespace='').filter('site = ',old_site)
        old_profiles=q.fetch(1000)
    
    
        set_namespace(request.POST.get('new_namespace'))
        new_site=db.get(db.Key(request.POST.get('new_site')))
    
        for old_profile in old_profiles:
            new_profile=clone_entity(old_profile, key_name=old_profile.key().name())
            new_profile.site=new_site
            new_profile.put()
            #old_profile.delete()
    
  
        taskqueue.add(url='/admin/migrate-sources/', params={'new_namespace':request.POST.get('new_namespace'),
                                                'old_site':old_site.key(),
                                                'new_site':new_site.key(),
                                                },)
  
    except Exception,e:
                logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    
    

    
    
    return HttpResponse("OK")    
    


def migrate_events(request):
    try:
        if request.method == 'POST':
            set_namespace('')
            logging.warning("namespace: %s" % get_namespace())
            cursor=request.POST.get('cursor')
            old_site=db.get(db.Key(request.POST.get('old_site')))
            logging.warning("old site: %s" % old_site)
            
            #q=Event.all().filter('site =', old_site)
            q=Query(Event, namespace='').filter('site = ',old_site)
            if cursor:
                q=q.with_cursor(cursor)
            events= q.fetch(1)                                               
            logging.warning(events)
            set_namespace(request.POST.get('new_namespace'))
            new_site=db.get(db.Key(request.POST.get('new_site')))
            
            if events:
                taskqueue.add(url='/admin/migrate-events/', params={'new_namespace':request.POST.get('new_namespace'),
                                                                    'old_site':old_site.key(),
                                                                    'new_site':new_site.key(),
                                                                    'cursor':q.cursor()
                                                                    },)
            for event in events:   
                    event.site=new_site
                    
                    #new_event.site=new_site
                    if event.source:
                        event.source=ICalendarSource.all().filter('slug =', event.source.slug).get()
                    if event.submitted_by:
                        event.submitted_by=Profile.all().filter('slug =', event.submitted_by.slug).get()                    
                    if event.approved_by:
                        event.approved_by=Profile.all().filter('slug =', event.approved_by.slug).get()
                    new_event= clone_event(event, key_name=event.key().name())
                    #event.delete()
                    new_event.put()

                
    except Exception,e:
            logging.error("%s in \n%s"% (traceback.format_exc(),str(request.POST)))
    return HttpResponse("OK")