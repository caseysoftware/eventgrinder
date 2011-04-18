from google.appengine.ext import db
from eventsite.models import Eventsite

class Edition(db.Model):
    published=db.DateTimeProperty()
    issue_num=db.IntegerProperty(required=True)
    subject=db.StringProperty(required=True)
    body_txt=db.TextProperty(required=True)
    body_html=db.TextProperty()
    status=db.StringProperty(required=True)
    publish_after=db.DateTimeProperty(required=True)
    site=db.ReferenceProperty(Eventsite, required=True)


