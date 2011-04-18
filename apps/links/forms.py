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

REQUIRED = validators.required()
from models import Link



class LinkWidget(Input):
    def __init__(self, input_type='url'):
        if input_type is not None:
            self.input_type = input_type




class AddLinkForm(Form):
	name = fields.TextField('Site Name', validators=[REQUIRED])
	href=fields.TextField('URL', validators=[validators.URL(), REQUIRED], widget=LinkWidget())
	
	def save(self):
		new_link=Link(**self.data)
		new_link.status='submitted'
		new_link.put()
		



