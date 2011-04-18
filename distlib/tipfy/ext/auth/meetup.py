# -*- coding: utf-8 -*-
"""
    tipfy.ext.auth.meetup
    ~~~~~~~~~~~~~~~~~~~~~

    An extension to Tipfys auth system, that allows for using Meetup.com as a login provider (via Oauth)

    :copyright: 2010 Ross M Karchner.
    :license: BSD, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
import functools
import logging
import urllib

from google.appengine.api import urlfetch

from django.utils import simplejson

from tipfy import REQUIRED_VALUE
from tipfy.ext.auth.oauth import OAuthMixin

#: Default configuration values for this module. Keys are:
#:
#: - ``consumer_key``: Key provided when you register an application with
#:   Meetup.
#: - ``consumer_secret``: Secret provided when you register an application
#:   with Meetup.
default_config = {
    'consumer_key':    REQUIRED_VALUE,
    'consumer_secret': REQUIRED_VALUE,
}


class MeetupMixin(OAuthMixin):
    """A :class:`tipfy.RequestHandler` mixin that implements Meetup OAuth
    authentication.

    To authenticate with Meetup, register your application with
    Meetup at http://meetup.com/api/applications. Then
    copy your Consumer Key and Consumer Secret to config.py:

    <<code python>>
    config['tipfy.ext.auth.meetup'] = {
        'consumer_key':    'XXXXXXXXXXXXXXX',
        'consumer_secret': 'XXXXXXXXXXXXXXX',
    }
    <</code>>

    When your application is set up, you can use the MeetupMixin to
    authenticate the user with Meetup and get access to their stream.
    You must use the mixin on the handler for the URL you registered as your
    application's Callback URL. For example:

    <<code python>>
    from tipfy import RequestHandler, abort
    from tipfy.ext.auth.meetup import MeetupMixin

    class MeetupHandler(RequestHandler, MeetupMixin):
        def get(self):
            if self.request.args.get('oauth_token', None):
                return self.get_authenticated_user(self._on_auth)

            return self.authorize_redirect()

        def _on_auth(self, user):
            if not user:
                abort(403)

            # Set the user in the session.
            # ...
    <</code>>

    The user object returned by get_authenticated_user() includes the
    attributes 'username', 'name', and 'description' in addition to
    'access_token'. You should save the access token with the user;
    it is required to make requests on behalf of the user later with
    meetup_request().
    """
    _OAUTH_REQUEST_TOKEN_URL = 'http://www.meetup.com/oauth/request/'
    _OAUTH_ACCESS_TOKEN_URL = 'http://www.meetup.com/oauth/access/'
    _OAUTH_AUTHORIZE_URL = 'http://www.meetup.com/authorize/'
    _OAUTH_NO_CALLBACKS = False

    @property
    def _meetup_consumer_key(self):
        return self.app.get_config(__name__, 'consumer_key')

    @property
    def _meetup_consumer_secret(self):
        return self.app.get_config(__name__, 'consumer_secret')

    def meetup_request(self, path, callback, access_token=None,
                           post_args=None, **args):
                           
        logging.warning(path)
        """Fetches the given relative API path, e.g., '/bret/friends'

        If the request is a POST, post_args should be provided. Query
        string arguments should be given as keyword arguments.

        All the Meetup methods are documented at
        http://www.meetup.com/meetup_api/docs/

        Many methods require an OAuth access token which you can obtain
        through authorize_redirect() and get_authenticated_user(). The
        user returned through that process includes an 'access_token'
        attribute that can be used to make authenticated requests via
        this method. Example usage:

        from tipfy import RequestHandler, Response
        from tipfy.ext.auth.meetup import MeetupMixin


        """
        # Add the OAuth resource request signature if we have credentials
        url = 'http://api.meetup.com/' + path
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            consumer_token = self._oauth_consumer_token()
            method = 'POST' if post_args is not None else 'GET'
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            args.update(oauth)

        if args:
            url += '?' + urllib.urlencode(args)

        try:
            if post_args is not None:
                response = urlfetch.fetch(url, method='POST',
                    payload=urllib.urlencode(post_args), deadline=10)
            else:
                response = urlfetch.fetch(url, deadline=10)
        except urlfetch.DownloadError, e:
            logging.exception(e)
            response = None

        return self._on_meetup_request(callback, response)

    def _on_meetup_request(self, callback, response):
        if not response:
            logging.warning('Could not get a Meetup response.')
            return callback(None)
        elif response.status_code < 200 or response.status_code >= 300:
            logging.warning('Invalid Meetup response (%d): %s',
                response.status_code, response.content)
            return callback(None)

        return callback(simplejson.loads(response.content))

    def _oauth_consumer_token(self):
        return dict(
            key=self._meetup_consumer_key,
            secret=self._meetup_consumer_secret)

    def _oauth_get_user(self, access_token, callback):
        callback = functools.partial(self._parse_user_response, callback)
        return self.meetup_request(
            'members.json',
            access_token=access_token,
            callback=callback)

    def _parse_user_response(self, callback, user):
        if user:
            user['username'] = user['id']

        return callback(user)
