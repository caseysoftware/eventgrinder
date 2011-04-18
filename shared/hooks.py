from google.appengine.api import apiproxy_stub_map
import os, sys, logging

class HookHandler(object):
  pre_call_hooks = {}
  post_call_hooks = {}

  @classmethod
  def install(cls, service):
    handler = cls(service)
    apiproxy_stub_map.apiproxy.GetPreCallHooks().Append(
        cls.__name__,
        handler.handle_pre_call_hook,
        service)
    apiproxy_stub_map.apiproxy.GetPostCallHooks().Append(
        cls.__name__,
        handler.handle_post_call_hook,
        service)

  def __init__(self, service):
    self.service = service

  def handle_pre_call_hook(self, service, call, request, response):
    assert service == self.service
    hook_func = self.pre_call_hooks.get(call)
    if hook_func and not (os.environ.has_key('PATH_INFO') and (os.environ['PATH_INFO'].startswith('/_ah'))):
      hook_func(self, service, call, request, response)

  def handle_post_call_hook(self, service, call, request, response):
    assert service == self.service
    hook_func = self.post_call_hooks.get(call)
    if hook_func and not (os.environ.has_key('PATH_INFO') and (os.environ['PATH_INFO'].startswith('/_ah'))):
      hook_func(self, service, call, request, response)
      

class MultiTenantHookHandler(HookHandler):
    _DOMAIN_PROPERTY_NAME = '_domain'

    def domain(self):
      """Returns the domain for the current request."""
      #logging.info(str(os.environ))
      return os.environ.get('HTTP_HOST', '')

    def set_domain_property(self, entity):
      """Sets the domain property on an entity."""
      for i in range(entity.property_size()):
        property = entity.mutable_property(i)
        if property.name() == self._DOMAIN_PROPERTY_NAME:
          property.clear_value()
          break
      else:
        property = entity.add_property()
        property.set_name(self._DOMAIN_PROPERTY_NAME)
        property.set_multiple(False)
      property.mutable_value().set_stringvalue(self.domain())

    def get_domain_property(self, entity):
      """Checks that an entity has the domain property set to the correct value."""
      if entity:
        for property in entity.property_list():
          if property.name() == self._DOMAIN_PROPERTY_NAME:
            if hasattr(property, 'stringvalue'):
                return property.stringvalue()
            else:
                return None
      return None

    def pre_put(self, service, call, request, response):
      """Add the domain property to entities before they're stored."""
      for i in range(request.entity_size()):
        entity = request.mutable_entity(i)
        self.set_domain_property(entity)

    def pre_query(self, service, call, request, response):
      """Add a filter to queries before they're executed."""
      domain_filter = request.add_filter()
      domain_filter.set_op(datastore_pb.Query_Filter.EQUAL)
      property = domain_filter.add_property()
      property.set_name(self._DOMAIN_PROPERTY_NAME)
      property.mutable_value().set_stringvalue(self.domain())

    def post_get(self, service, call, request, response):
      """Makes sure all fetched entities are in the appropriate domain."""
      our_domain = self.domain()
      for entity in response.entity_list():
        domain = self.get_domain_property(entity.entity())
        if domain and domain != our_domain:
          raise Exception(
              "Domain '%s' attempted to read an object belonging to domain '%s'",
              our_domain,
              domain)

    pre_call_hooks = {
        'Put': pre_put,
        'Query': pre_query,
        'Count': pre_query,
    }

    post_call_hooks = {
        'Get': post_get,
    }

MultiTenantHookHandler.install('datastore_v3')