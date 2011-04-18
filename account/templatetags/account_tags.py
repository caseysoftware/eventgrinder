from django import template
from account.utility import get_current_user, create_logout_url
from google.appengine.api import users



register = template.Library()

    
    
