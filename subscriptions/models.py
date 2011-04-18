from google.appengine.ext import db


class SitesNextNewsletter(db.Model):
    publish_at= db.DateTimeProperty(required=True, indexed=True)
    sent_on=db.DateTimeProperty(required=False, indexed=True)