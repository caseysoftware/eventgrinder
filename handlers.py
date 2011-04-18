from tipfy import RequestHandler
from tipfy.ext.jinja2 import render_response

class FrontPageHandler(RequestHandler):
    """A handler that outputs the result of a rendered template."""
    def get(self, **kwargs):
        return render_response('hello.html', message='Hello, Jinja!')
        
        
class AddEventHandler(RequestHandler):
    """A handler that outputs the result of a rendered template."""
    def get(self, **kwargs):
        return render_response('hello.html', message='Hello, Jinja!')