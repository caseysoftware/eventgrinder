import sys
import os


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')







def namespace_manager_default_namespace_for_request():
    import os
    if os.environ.get('HTTP_HOST'):
        return os.environ.get('HTTP_HOST').split(':')[0]
    else:
        return ''