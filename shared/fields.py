"""
Field classes.
"""

import copy
import datetime
import os
import re
import time
import urlparse
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# Python 2.3 fallbacks
try:
    from decimal import Decimal, DecimalException
except ImportError:
    from django.utils._decimal import Decimal, DecimalException
try:
    set
except NameError:
    from sets import Set as set

import django.core.exceptions
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode, smart_str

try:
    from django.conf import settings
    URL_VALIDATOR_USER_AGENT = settings.URL_VALIDATOR_USER_AGENT
except ImportError:
    # It's OK if Django settings aren't configured.
    URL_VALIDATOR_USER_AGENT = 'Django (http://www.djangoproject.com/)'


from django.forms.util import ErrorList, ValidationError
from django.forms.widgets import TextInput, PasswordInput, HiddenInput, MultipleHiddenInput, FileInput, CheckboxInput, Select, NullBooleanSelect, SelectMultiple, DateInput, DateTimeInput, TimeInput, SplitDateTimeWidget, SplitHiddenDateTimeWidget

from django.forms.fields import RegexField

url_re = re.compile(
    r'^(https?|webcal)://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|/\S+)$', re.IGNORECASE)


class iCalURLField(RegexField):
    default_error_messages = {
        'invalid': _(u'Enter a valid URL.'),
        'invalid_link': _(u'This URL appears to be a broken link.'),
    }

    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            validator_user_agent=URL_VALIDATOR_USER_AGENT, *args, **kwargs):
        super(iCalURLField, self).__init__(url_re, max_length, min_length, *args,
                                       **kwargs)
        self.verify_exists = verify_exists
        self.user_agent = validator_user_agent

    def clean(self, value):
        value=value.replace('webcal', 'http')
        # If no URL scheme given, assume http://
        if value and '://' not in value:
            value = u'http://%s' % value
        # If no URL path given, assume /
        if value and not urlparse.urlsplit(value)[2]:
            value += '/'
        value = super(iCalURLField, self).clean(value)
        if value == u'':
            return value

        return value