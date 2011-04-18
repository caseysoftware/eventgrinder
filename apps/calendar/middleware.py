from tipfy import RequestHandler, Response, redirect, cached_property

class SiteRequiredMiddleware(object):
	def pre_dispatch(self, handler):
		if not handler.site:
			return Response("I don't know that site!")