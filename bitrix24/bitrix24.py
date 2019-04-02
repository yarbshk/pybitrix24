import requests

from bitrix24 import utils
from urllib.parse import urlencode


class Bitrix24(object):
    _client_endpoint_template = 'https://{domain}/rest/'
    _oauth_endpoint_template = 'https://{domain}/oauth/{action}/'

    @property
    def _webhook_endpoint_template(self):
        return self._client_endpoint_template + '{user_id}/{code}/'

    def __init__(self, domain, client_id=None, client_secret=None,
                 access_token=None, client_endpoint=None, expires_in=3600,
                 refresh_token=None, scope='', server_endpoint=None,
                 transport='json', user_id=0, auth_domain=None):
        self.access_token = access_token
        self.client_id = client_id
        self.client_endpoint = client_endpoint # Must endswith a slash
        self.client_secret = client_secret
        self.domain = domain # Without protocol and an ending slash
        self.expires_in = expires_in # Tokens expire in 1 hour by default
        self.refresh_token = refresh_token
        self.scope = scope # The default value means all available scopes
        self.server_endpoint = server_endpoint # Must endswith a slash
        self.transport = transport # Allowable values are 'json' or 'xml'
        self.user_id = user_id # The default value means current user
        self.auth_domain = auth_domain

    def get_tokens(self):
        """
        Returns current access and refresh tokens of the instance.
        :return: dict Access and refresh tokens
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }

    def resolve_authorize_endpoint(self, **extra_query):
        """
        Builds an authorize URL to request an authorization code from. See:
        https://training.bitrix24.com/rest_help/oauth/app_authentication.php
        a remote server using a browser.
        :param extra_query: dict Additional query parameters
        :return: str Authorize endpoint
        """
        query = extra_query.copy()
        query.update({
            'client_id': self.client_id,
            'response_type': 'code'
        })
        endpoint = self._resolve_oauth_endpoint('authorize', query=query)
        return endpoint

    def _resolve_client_endpoint(self):
        """
        Returns correct client endpoint even if wasn't provided.
        :return: str Client endpoint
        """
        return self.client_endpoint \
            or self._client_endpoint_template.format(domain=self.domain)

    def _resolve_oauth_endpoint(self, action, query=None):
        """
        Builds an OAuth URL with/out query parameters.
        :param action: str Action name of an OAuth endpoint
        :param query: dict Query parameters
        :return: str OAuth endpoint
        """
        endpoint = self._oauth_endpoint_template.format(
            domain=self.auth_domain or self.domain,
            action=action
        )
        if query is not None:
            endpoint += '?{}'.format(urlencode(query))
        return endpoint

    def _resolve_webhook_endpoint(self, code):
        """
        Build an endpoint for webhook with authentication code.
        :param code:
        :return: str Webhook endpoint
        """
        return self._webhook_endpoint_template.format(
            domain=self.domain,
            user_id=self.user_id,
            code=code
        )

    def _request_tokens(self, query):
        """
        The request handler of an OAuth tokens endpoint.
        :param query: dict Query parameters
        :return: dict Encoded response text
        """
        url = self._resolve_oauth_endpoint('token')
        try:
            r = requests.get(url, params=query)
        except requests.exceptions.RequestException:
            r = None
        result = utils.resolve_response(r)
        return result

    def request_tokens(self, code, **extra_query):
        """
        Requests access and refresh tokens of a Bitrix24 server. See:
        https://training.bitrix24.com/rest_help/oauth/app_authentication.php
        :param code: str Authentication request code
        :param extra_query: dict Additional query parameters
        """
        query = extra_query.copy()
        query.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'scope': self.scope
        })
        result = self._request_tokens(query)
        self.access_token = result.get('access_token')
        self.client_endpoint = result.get('client_endpoint')
        self.domain = result.get('domain')
        self.expires_in = result.get('expires_in')
        self.refresh_token = result.get('refresh_token')
        self.scope = result.get('scope')
        self.server_endpoint = result.get('server_endpoint')
        self.user_id = result.get('user_id')

    def refresh_tokens(self, **extra_query):
        """
        Refreshes class tokens by appropriate requested tokens.
        :param extra_query: dict Additional query parameters
        """
        query = extra_query.copy()
        query.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        })
        result = self._request_tokens(query)
        self.access_token = result.get('access_token')
        self.refresh_token = result.get('refresh_token')

    def _resolve_call_url(self, method, endpoint=None):
        return '{endpoint}{method}.{transport}'.format(
            endpoint=endpoint or self._resolve_client_endpoint(),
            method=method,
            transport=self.transport
        )

    def call_method(self, method, params=None):
        """
        Requests any Bitrix24 method with/out parameters. See:
        https://training.bitrix24.com/rest_help/js_library/rest/callMethod.php
        :param method: str Dot-noted method name
        :param params: dict Request parameters
        :return: dict Decoded response text
        """
        url = self._resolve_call_url(method)
        query = {'auth': self.access_token}
        try:
            r = requests.post(url, json=params, params=query)
        except requests.exceptions.RequestException:
            r = None
        result = utils.resolve_response(r)
        return result

    def call_batch(self, calls, halt_on_error=False):
        """
        Groups many single methods into a request. Can include macros
        to access the results of the previous calls in the batch. See:
        https://training.bitrix24.com/rest_help/js_library/rest/callBatch.php
        :param calls: dict Sub-methods with params
        :param halt_on_error: bool Halt on error
        :return: dict Decoded response text
        """
        result = self.call_method('batch', {
            'cmd': utils.prepare_batch(calls),
            'halt': halt_on_error
        })
        return result

    def call_bind(self, event, handler, auth_type=None):
        """
        Installs a new event handler. See:
        https://training.bitrix24.com/rest_help/general/event_bind.php
        :param event: str Event name
        :param handler: str Handler URL
        :param auth_type: int User ID
        :return: dict Decoded response text
        """
        result = self.call_method('event.bind', {
            'auth_type': auth_type or self.user_id,
            'event': event,
            'handler': handler
        })
        return result

    def call_unbind(self, event, handler, auth_type=None):
        """
        Uninstalls a previously installed event handler. See:
        https://training.bitrix24.com/rest_help/general/event_unbind.php
        :param event: str Event name
        :param handler: str Handler URL
        :param auth_type: int User ID
        :return: dict Decoded response text
        """
        result = self.call_method('event.unbind', {
            'auth_type': auth_type or self.user_id,
            'event': event,
            'handler': handler
        })
        return result

    def call_webhook(self, method, code, params=None):
        """
        Call a simplified version of rest-events and rest-teams that does not
        require a program to write.
        https://www.bitrix24.com/apps/webhooks.php
        :param method:
        :param code:
        :param params:
        :return: dict Decoded response text
        """
        endpoint = self._resolve_webhook_endpoint(code)
        url = self._resolve_call_url(method, endpoint=endpoint)
        query = {'auth': self.access_token}
        try:
            r = requests.post(url, json=params, params=query)
        except requests.exceptions.RequestException:
            r = None
        result = utils.resolve_response(r)
        return result
