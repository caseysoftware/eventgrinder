from google.appengine.ext import db
from google.appengine.api.namespace_manager import set_namespace, get_namespace

class NameSpace(db.Model):
    ns=db.StringProperty(required=True, indexed=False)
    
    
def register(ns):
    current_ns=get_namespace()
    set_namespace('')
    registered=NameSpace(ns=ns,key_name=ns)
    registered.put()
    set_namespace(current_ns)
    
    
def all():
    current_ns=get_namespace()
    set_namespace('')
    namespaces=NameSpace.all().fetch(1000)
    set_namespace(current_ns)
    return namespaces