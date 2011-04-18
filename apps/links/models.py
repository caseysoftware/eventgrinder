from google.appengine.ext import db


class Link(db.Model):
	name=db.StringProperty()
	href=db.LinkProperty()
	status=db.StringProperty()


