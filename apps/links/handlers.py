import os, logging
from datetime import date, time, datetime

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from werkzeug import MultiDict

from tipfy import RequestHandler, Response, redirect, cached_property, url_for
from tipfy.ext.jinja2 import Jinja2Mixin
from tipfy.ext.db import get_entity_dict

from forms import AddLinkForm
from models import Link

		
class AddLinkHandler(RequestHandler, Jinja2Mixin):

	def get(self):
		context=dict(form=self.form)
		return self.render_response('link/add.html', **context)
		
	
	def post(self):
		if self.form.validate():
			self.form.save()
			return redirect('/')
			
			
		return self.get()
	
	@cached_property
	def form(self):
		return AddLinkForm(self.request.form)
		
class ReviewLinksHandler(RequestHandler, Jinja2Mixin):
	def get(self):
		pending_links=Link.all().filter('status =', 'submitted')
		context=dict(pending_links=pending_links)
		return self.render_response('link/review.html', **context)
		
class ChangeLinkStatusHandler(RequestHandler):
	def post(self):
		entity=db.get(db.Key(self.request.form.get('entity_key')))
		entity.status=self.request.form.get('new_status')
		entity.put()
		return redirect(url_for('links/review'))
		
		