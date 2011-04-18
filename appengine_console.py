#!/usr/bin/python
import code
import getpass
import sys
import os

sys.path.append("/usr/local/google_appengine")
sys.path.append("/usr/local/google_appengine/lib/yaml/lib")
sys.path= [os.path.join(os.path.dirname(__file__), 'shared'), os.path.join(os.path.dirname(__file__), 'Apps')]+sys.path

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
from google.appengine.dist import use_library
use_library('django', '1.1')
import os, cgi
os.environ['DJANGO_SETTINGS_MODULE']='techevents_settings'

def auth_func():
    return 'rosskarchner', '1GingerBeer'

host = 'localhost:8083' 

remote_api_stub.ConfigureRemoteDatastore('techevents', '/remote_api', auth_func, host)

code.interact('App Engine interactive console for %s' % ('techevents'), None, locals())