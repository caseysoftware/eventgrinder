import sys, os
from google.appengine.ext.webapp import util


sys.path= [os.path.join(os.path.dirname(__file__), 'shared'), os.path.join(os.path.dirname(__file__), '.')]+sys.path


# Django imports and other code go here...
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')


import django.core.handlers, django.core.handlers.wsgi

from django.conf import settings
settings.ROOT_URLCONF="urls"




def main():
    sys.path= [os.path.join(os.path.dirname(__file__), 'shared'), os.path.join(os.path.dirname(__file__), '.')]+sys.path
    application = django.core.handlers.wsgi.WSGIHandler()
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()