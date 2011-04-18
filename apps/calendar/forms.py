from datetime import date
import logging

from tipfy import RequestHandler, Response, redirect, cached_property
from tipfy.ext.jinja2 import Jinja2Mixin
from tipfy.ext.wtforms import Form, fields, validators, widgets
from tipfy.ext.wtforms.validators import ValidationError

from tipfy.ext.db import populate_entity

from wtforms.ext.dateutil.fields import DateField


from pytz.gae import pytz


# a set of HTML5 widgets for wtforms

from wtforms.widgets import Input

from models import SourceCalendar

class DateWidget(Input):
    def __init__(self, input_type='date'):
        if input_type is not None:
            self.input_type = input_type

class TimeWidget(Input):
    def __init__(self, input_type='time'):
        if input_type is not None:
            self.input_type = input_type




class LinkWidget(Input):
    def __init__(self, input_type='url'):
        if input_type is not None:
            self.input_type = input_type




REQUIRED = validators.required()

DRIVERS=(('ical', 'iCalendar'), )

class AddCalendarForm(Form):
	title = fields.TextField('Calendar Name', validators=[REQUIRED])
	source_uri=fields.TextField('Source URL', validators=[validators.URL(), REQUIRED], widget=LinkWidget())
	credit_uri=fields.TextField('Credit URL', validators=[validators.optional(), validators.URL()], widget=LinkWidget())
	driver=fields.SelectField('Driver', choices=DRIVERS, validators=[REQUIRED])
	
	def save(self, entity=None):
		if entity:
			populate_entity(entity, **self.data)
			entity.put()
		else:
			new_calendar=SourceCalendar(**self.data)
			new_calendar.put()
		
	
    