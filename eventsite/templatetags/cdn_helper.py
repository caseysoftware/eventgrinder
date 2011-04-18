from django import template
from django.template.defaultfilters import stringfilter
import os
register = template.Library()


class VersionedUri(template.Node):
   def __init__(self,href, envversion, version_var=None):
       self.href = href
       self.envversion=envversion
       self.version_var=version_var

   def render(self, context):
       if self.version_var:
           version=self.version_var.resolve(context)
       else:
           version=self.envversion
       
       if type(self.href)== template.Variable:
           self.href=self.href.resolve(context)
           
       if '/static/' in self.href:
           return self.href.replace('/static/', '/static/%s/'% str(version))
       
       if "?" not in self.href:
           return self.href+"?v="+ str(version)
       else:
           return self.href + "&v=" + str(version)
          


@register.tag(name='versioned')
def do_versioned(parser, token):

    # split_contents() knows not to split quoted strings.
    args= token.split_contents()
    if len(args) > 3: 
        raise template.TemplateSyntaxError, "%r tag only allows two arguments" % token.contents.split()[0]
    if len(args) < 2: 
        raise template.TemplateSyntaxError, "%r tag requires at least a single argument" % token.contents.split()[0]
           
    tag_name, href=args[:2]
    if not (href[0] == href[-1] and href[0] in ('"', "'")):
       href= template.Variable(href)
    else:
       href=href[1:-1]
    
    if len(args) == 3:
        version_var=template.Variable(args[2])
        
    else:
        version_var=None

       
    if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
        envversion="development"
    else:
        envversion=os.environ['CURRENT_VERSION_ID']
   
   
    return VersionedUri(href, envversion, version_var)

