import os

from django.template.loader import get_template
from django.template import Context, Template
from django.core.urlresolvers import reverse
from google.appengine.api import users
from google.appengine.api.images import get_serving_url

from apps.links.models import Link



from account.utility import get_current_profile

from eventsite import get_site


def site_context(request):
    site=get_site()
    additional_context={'site': site,
                        'user':get_current_profile(),
                        'admin':users.is_current_user_admin(),
                        'logout':users.create_logout_url(reverse('account-signout')),
                        'links':Link.all().filter('status =','approved').fetch(20)
                        
                }
                

    #additional_context['logo']=get_serving_url(str(site.original_logo.key()), 512)


    return additional_context
        