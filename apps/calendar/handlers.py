import os, logging
from datetime import date, time, datetime

from google.appengine.api.labs import taskqueue

from werkzeug import MultiDict

from tipfy import RequestHandler, Response, redirect, cached_property, url_for
from tipfy.ext.jinja2 import Jinja2Mixin
from tipfy.ext.db import get_entity_dict

from models import SourceCalendar
from forms import AddCalendarForm


class IndexHandler(RequestHandler, Jinja2Mixin):

		
	def get(self):
		calendars=SourceCalendar.all().fetch(100)
		context=dict(calendars=calendars)
		return self.render_response('calendar/index.html', **context)
		
		
class AddCalendarHandler(RequestHandler, Jinja2Mixin):

	def get(self):
		calendars=SourceCalendar.all()
		context=dict(form=self.form)
		return self.render_response('calendar/add.html', **context)
		
	
	def post(self):
		if self.form.validate():
			self.form.save()
			return redirect('/calendars/')
			
			
		return self.get()
	
	@cached_property
	def form(self):
		return AddCalendarForm(self.request.form)
		
		
class EditCalendarHandler(RequestHandler, Jinja2Mixin):


	def get(self, **kwargs):
		context=dict(form=self.form)
		existing_calendar=self.existing_calendar
		return self.render_response('calendar/add.html', **context)
		
	
	def post(self, **kwargs):
		if self.form.validate():
			self.form.save(self.existing_calendar)
			return redirect('/calendars/')
			
			
		return self.get(**kwargs)
		
	@cached_property
	def existing_calendar(self):
		slug=self.request.rule_args['calendar_slug']
		return SourceCalendar.all().filter('slug = ', slug).get()
		
	
	@cached_property
	def form(self):	
		if self.request.method == 'GET':
			return AddCalendarForm(MultiDict(get_entity_dict(self.existing_calendar).iteritems()))
		if self.request.method == 'POST':
			return AddCalendarForm(self.request.form)


class FetchCalendarHandler(RequestHandler):
	def post(self):
		taskqueue.add(url=url_for("calendar/tasks/start_fetch_source"), params=self.request.form)
		return redirect('/calendars/')