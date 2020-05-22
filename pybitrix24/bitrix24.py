from .exceptions import PBx24AttributeError, PBx24ArgumentError
from .requester import encode_url, request, prepare_batch_command


def get_error_if_present(data):
    if not isinstance(data, dict):
        raise PBx24ArgumentError("Data must be a dictionary")

    # Try to get an error from a call response
    error = data.get('error')
    if error is not None:
        return error

    # Check if it's a batch response
    result = data.get('result')
    if result is None:
        return None

    # Try to get an error from a batch call response
    if not isinstance(result, dict):
        raise PBx24ArgumentError("Data is not a valid response")

    return result.get('result_error')


class ConditionalDict(dict):
    def __init__(self, seq=None, cond=lambda x: x is not None):
        super(ConditionalDict, self).__init__(seq)
        self.cond = cond

    def __setitem__(self, key, value):
        if self.cond(value):
            dict.__setitem__(self, key, value)


class Bitrix24(object):
    """
    The main caller of Bitrix24 REST API. The caller has several methods
    of quick access and advanced URL encoding features. It supports obtaining
    and refreshing tokens and automatic injecting of access token for each
    request and helps in obtaining the authorization code grand.
    """
    _base_url_template = 'https://{hostname}/'

    _auth_url_template = _base_url_template + 'oauth/{action}/'
    _method_url_template = _base_url_template + 'rest/'
    _webhook_url_template = _method_url_template + '{user_id}/{code}/'

    _call_url_template = '{url}{method}.json'

    def __init__(self, hostname, client_id=None, client_secret=None,
                 user_id=1):
        """
        Initialize object attributes. Note that the application ID and key
        arguments are not required if webhooks will be called only.

        :raise Bx24ArgumentError: If hostname is not set
        :param hostname: str A root URL without a protocol and an ending slash of
            the Bitrix24 account (e.g. b24-60jyw6.bitrix24.com)
        :param client_id: str Application ID
        :param client_secret: str Application key
        :param user_id: int A numeric ID of the user (used by webhooks)
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
        Generate a URL for requesting an authorization code via browser.

        See more:
        * `Authorization Code Grant
            <https://tools.ietf.org/html/rfc6749#section-4.1>`_
        * `Authorization Request
            <https://tools.ietf.org/html/rfc6749#section-4.1.1>`_
        * `OAuth 2.0 Protocol
            <https://training.bitrix24.com/rest_help/oauth/authentication.php>`_
        * `Authentication for Mobile and Desktop Applications
            <https://training.bitrix24.com/rest_help/oauth/app_authentication.php>`_

        :raise Bx24AttributeError: If :attr:`client_id` is not set
        :param kwargs: dict Optional query parameters
        :return: str An absolute URL
        """
        if self.client_id is None:
            raise PBx24AttributeError("The 'client_id' attribute is required")
        kwargs.update({
            'client_id': self.client_id,
            'response_type': 'code'
        })
        url = self._build_oauth_url('authorize', query=kwargs)
        return url

    def _build_oauth_url(self, action, query=None):
        if self.hostname is None:
            raise PBx24AttributeError("The 'hostname' attribute is required")
        url = self._auth_url_template.format(hostname=self.hostname, action=action)
        if query is not None:
            url += '?' + encode_url(query)

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

        :param code: str Authorization code
        :param kwargs: dict Optional query parameters
        :return: dict Response data containing tokens
        """
        kwargs.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        })
        data = self._request_tokens(kwargs)
        return data

    def _request_tokens(self, query):
        url = self._build_oauth_url('token')
        data = request(url, query=query)
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

        :param kwargs: dict Optional query parameters
        :return: dict Response data containing tokens
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
        Send a parametrized request to the Bitrix24 REST API endpoint. It's
        required to obtain an access token with appropriate permissions first.
        The access token injects automatically to the request.

        See more:
        * `Access Permissions for REST Methods
            <https://training.bitrix24.com/rest_help/rest_sum/premissions_scope.php>`
        * `Common REST methods
            <https://training.bitrix24.com/rest_help/general/index.php>`

        :param method: str Method name (words separated by dots)
        :param params: dict Request parameters
        :return: dict Response data
        """
        url = self._method_url_template.format(hostname=self.hostname)
        data = self._call(url, method, {'auth': self._access_token}, params)
        return data

    def _call(self, url, method, query, params):
        url = self._call_url_template.format(url=url, method=method)
        data = request(url, query, params)
        return data

    def call_batch(self, calls, halt_on_error=False):
        """
        Group many calls into a single request. May include macros to reference
        results of the previous calls.

        See more:
        * `BX24.callBatch
            <https://training.bitrix24.com/rest_help/js_library/rest/callBatch.php>`_

        :param calls: dict Call params by method names
        :param halt_on_error: bool Halt on error
        :return: dict Response data
        """
        data = self.call('batch', {
            'cmd': prepare_batch_command(calls),
            'halt': halt_on_error
        })
        return data

    def call_event_bind(self, event, handler, auth_type=None, event_type=None):
        """
        Install a new event handler.

        See more:
        * `event.bind
            <https://training.bitrix24.com/rest_help/general/events_method/event_bind.php>`_

        :param event: str Event name
        :param handler: str Event handler URL
        :param auth_type: int User ID
        :param event_type: str 'online' or 'offline'
        :return: dict Response data
        """
        params = ConditionalDict({
            'event': event,
            'handler': handler
        })
        params['auth_type'] = auth_type or self.user_id
        params['event_type'] = event_type
        data = self.call('event.bind', params)
        return data

    def call_event_unbind(self, event, handler, auth_type=None, event_type=None):
        """
        Uninstall an event handler.

        See more:
        * `event.bind
            <https://training.bitrix24.com/rest_help/general/events_method/event_unbind.php>`_

        :param event: str Event name
        :param handler: str Handler URL
        :param auth_type: int User ID
        :param event_type: str 'online' or 'offline'
        :return: dict Decoded response text
        """
        params = ConditionalDict({
            'event': event,
            'handler': handler
        })
        params['auth_type'] = auth_type or self.user_id
        params['event_type'] = event_type
        data = self.call('event.unbind', params)
        return data

    def call_webhook(self, code, method, params=None):
        """
        Request a Bitrix24 resources without an access token.

        See more:
        * `WebHooks
            <https://training.bitrix24.com/rest_help/rest_sum/webhooks.php>`_
        * `Telephony Integration Tips
            <https://www.bitrix24.com/apps/webhooks.php>`_

        :param code: str WebHook code
        :param method: str Method name (words separated by dots)
        :param params: dict Request parameters
        :return: dict Response data
        """
        url = self._webhook_url_template.format(hostname=self.hostname,
                                                user_id=self.user_id, code=code)
        data = self._call(url, method, None, params)
        return data

    def call_batch_webhook(self, code, calls, halt_on_error=False):
        """
        Group many calls into a single request. May include macros to reference
        results of the previous calls. This method is mimics :meth:`call_batch`
        except adding an access token to the request.

        See more:
        * `BX24.callBatch
            <https://training.bitrix24.com/rest_help/js_library/rest/callBatch.php>`_

        :param code: str WebHook code
        :param calls: dict Call params by method names
        :param halt_on_error: bool Halt on error
        :return: dict Response data
        """
        data = self.call_webhook(code, 'batch', {
            'cmd': prepare_batch_command(calls),
            'halt': halt_on_error
        })
        return data
