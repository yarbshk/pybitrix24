from .exceptions import PBx24AttributeError, PBx24ArgumentError
from .requester import encode_url, request, prepare_batch


def copy_or_create_dict(d):
    return {} if d is None else d.copy()


class Bitrix24(object):
    """
    The main requester of Bitrix24 REST API. Under the hood it uses Requests
    (HTTP library) and acts as its wrapper with several methods of quick
    access and advanced URL encoding features. The wrapper supports obtaining
    and refreshing tokens and automatic injecting of access token for each
    request and helps in obtaining the authorization code grand.
    """
    _base_url_template = 'https://{hostname}/'

    _auth_url_template = _base_url_template + 'oauth/{action}/'
    _method_url_template = _base_url_template + 'rest/'
    _webhook_url_template = _method_url_template + '{user_id}/{code}/'

    _call_url_template = '{url}{method}.json'

    def __init__(self, hostname, client_id=None, client_secret=None, user_id=1):
        """
        Initialize object attributes. Note that the application ID and key
        arguments are not required only if webhooks will be called.

        :raise Bx24ArgumentError: If hostname is not set
        :param hostname: A root URL without a protocol and an ending slash of
            the Bitrix24 account (e.g. b24-60jyw6.bitrix24.com)
        :param client_id: Application ID
        :param client_secret: Application key
        :param user_id: A numeric ID of the user (used by webhooks)
        """
        if hostname is None:
            raise PBx24ArgumentError("The 'hostname' argument is required")
        self.hostname = hostname
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = user_id
        self._access_token = None
        self._refresh_token = None

    def build_authorization_url(self, **kwargs):
        """
        Generate a URL for requesting an authorization code grant via browser.

        See more:
        * `Authorization Code Grant
            <https://tools.ietf.org/html/rfc6749#section-4.1>`_
        * `Authorization Request
            <https://tools.ietf.org/html/rfc6749#section-4.1.1>`_
        * `OAuth 2.0 Protocol
            <https://training.bitrix24.com/rest_help/oauth/authentication.php>`_
        * `Authentication for Mobile and Desktop Applications
            <https://training.bitrix24.com/rest_help/oauth/app_authentication.php>`_

        :raise Bx24AttributeError: If :attr:`hostname` or :attr:`client_id`
            is not set. They should be provided during object initialization.
        :param kwargs: Optional query parameters
        :return: An absolute URL
        """
        if self.client_id is None:
            raise PBx24AttributeError("The 'client_id' attribute is required")
        kwargs.update({
            'client_id': self.client_id,
            'response_type': 'code'
        })
        url = self._build_oauth_url('authorize', params=kwargs)
        return url

    def _build_oauth_url(self, action, params=None):
        """
        Builds an OAuth URL with/out query parameters.
        :param action: str Action name of an OAuth endpoint
        :param params: dict Query parameters
        :return: str OAuth endpoint
        """
        if self.client_id is None:
            raise PBx24AttributeError("The 'hostname' attribute is required")
        url = self._auth_url_template.format(hostname=self.hostname, action=action)
        if params is not None:
            url += '?' + encode_url(params)

        return url

    def obtain_tokens(self, code, **kwargs):
        """
        Request access and refresh tokens using the authorization code grant.
        Refer to :meth:`build_authorization_url` for obtaining an authorization
        code. This method automatically updates both :attr:`access_token` and
        :attr:`refresh_token`. However, response body also contains other data
        (mostly repetitive) that returns and can be easily accessible if needed.

        See more:
        * `Access Token <https://tools.ietf.org/html/rfc6749#section-1.4>`_
        * `Refresh Token <https://tools.ietf.org/html/rfc6749#section-1.5>`_
        * `Access Token Request
            <https://tools.ietf.org/html/rfc6749#section-4.1.3>`_
        * `Access Token Response
            <https://tools.ietf.org/html/rfc6749#section-4.1.3>`_
        * `Authentication for Mobile and Desktop Applications
            <https://training.bitrix24.com/rest_help/oauth/app_authentication.php>`_

        :param code: Authorization code
        :param kwargs: Optional query parameters
        :return: Response data containing tokens
        """
        kwargs.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        })
        if 'scope' not in kwargs:  # TODO: Check if scope parameter is optional
            kwargs['scope'] = ''
        data = self._request_tokens(kwargs)
        return data

    def _request_tokens(self, params):
        """
        The request handler of an OAuth tokens endpoint.
        :param params: dict Query parameters
        :return: dict Encoded response text
        """
        url = self._build_oauth_url('token')
        data = request('get', url, params)
        # TODO: Handle error
        self._access_token = data.get('access_token')
        self._refresh_token = data.get('refresh_token')
        return data

    def refresh_tokens(self, **kwargs):
        """
        Request new access and refresh tokens if :attr:`refresh_token` is not
        expired yet (1 hour by default), in other case error response returns.
        This method automatically updates both :attr:`access_token` and
        :attr:`refresh_token` as well as :attr:`expires_in`. However, response
        body also contains other data (mostly repetitive) that returns and can
        be easily accessible if needed.

        See more:
        * `Refresh Token <https://tools.ietf.org/html/rfc6749#section-1.5>`_
        * `Access Token <https://tools.ietf.org/html/rfc6749#section-1.4>`_
        * `Refreshing an Access Token
            <https://tools.ietf.org/html/rfc6749#section-6>`_
        * `Refreshing Authorization For External Applications
            <https://training.bitrix24.com/rest_help/oauth/refreshing.php>`_

        :param kwargs: Optional query parameters
        :return: Response data containing tokens
        """
        kwargs.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        })
        data = self._request_tokens(kwargs)
        return data

    def call(self, method, params=None):
        """
        Send a parametrized request to the Bitrix24 REST API endpoint. This
        method automatically injects an access token to the request.

        See more:
        * `Access Permissions for REST Methods
            <https://training.bitrix24.com/rest_help/rest_sum/premissions_scope.php>`
        * `Common REST methods
            <https://training.bitrix24.com/rest_help/general/index.php>`

        :param method: Method name (words separated by dots)
        :param params: Request parameters
        :return: Response data
        """
        url = self._method_url_template.format(hostname=self.hostname)
        params = copy_or_create_dict(params)
        params['auth'] = self._access_token
        data = self._call(url, method, params)
        return data

    def _call(self, url, method, params):
        uri = self._call_url_template.format(url=url, method=method)
        data = request('post', uri, params)
        return data

    def call_batch(self, calls, halt_on_error=False):
        """
        Groups many single methods into a request. Can include macros
        to access the results of the previous calls in the batch. See:
        https://training.bitrix24.com/rest_help/js_library/rest/callBatch.php
        :param calls: dict Sub-methods with params
        :param halt_on_error: bool Halt on error
        :return: dict Decoded response text
        """
        data = self.call('batch', {
            'cmd': prepare_batch(copy_or_create_dict(calls)),
            'halt': halt_on_error
        })
        return data

    def call_bind(self, event, handler, auth_type=None):
        """
        Installs a new event handler. See:
        https://training.bitrix24.com/rest_help/general/event_bind.php
        :param event: str Event name
        :param handler: str Handler URL
        :param auth_type: int User ID
        :return: dict Decoded response text
        """
        data = self.call('event.bind', {
            'auth_type': auth_type or self.user_id,
            'event': event,
            'handler': handler
        })
        return data

    def call_unbind(self, event, handler, auth_type=None):
        """
        Uninstalls a previously installed event handler. See:
        https://training.bitrix24.com/rest_help/general/event_unbind.php
        :param event: str Event name
        :param handler: str Handler URL
        :param auth_type: int User ID
        :return: dict Decoded response text
        """
        data = self.call('event.unbind', {
            'auth_type': auth_type or self.user_id,
            'event': event,
            'handler': handler
        })
        return data

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
        url = self._webhook_url_template.format(hostname=self.hostname,
                                                user_id=self.user_id, code=code)
        data = self._call(url, method, copy_or_create_dict(params))
        return data

    def call_batch_webhook(self, calls, code, halt_on_error=False):
        """
        Groups many single methods into a request. Can include macros
        to access the results of the previous calls in the batch. See:
        https://training.bitrix24.com/rest_help/js_library/rest/callBatch.php
        :param calls: dict Sub-methods with params
        :param code: webhook unique code
        :param halt_on_error: bool Halt on error
        :return: dict Decoded response text
        """
        data = self.call_webhook('batch', code, {
            'cmd': prepare_batch(copy_or_create_dict(calls)),
            'halt': halt_on_error
        })
        return data
