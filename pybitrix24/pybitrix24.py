import json
import sys
from abc import ABC, abstractmethod

from .query_string import format_qs_deep

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode


class PyBitrix24Error(Exception):
    pass


class HttpRequestError(PyBitrix24Error):
    pass


class BaseHttpRequester(ABC):
    @abstractmethod
    def post(self, url, body=None, headers=None):
        pass


class UrllibHttpRequester(BaseHttpRequester):
    def post(self, url, body=None, headers=None):
        request = Request(url, data=body, headers=headers)
        try:
            return urlopen(request)
        except HTTPError as e:
            return e
        except Exception as e:
            raise HttpRequestError("Error on request", e)


class SerializationError(PyBitrix24Error):
    pass


class BaseSerializer(ABC):
    format = None

    @abstractmethod
    def serialize(self, object_):
        pass

    @abstractmethod
    def deserialize(self, string_):
        pass


class JsonSerializer(BaseSerializer):
    format = 'json'

    def serialize(self, object_):
        try:
            return json.dumps(object_).encode('utf-8')
        except Exception as e:
            raise SerializationError("Unable to encode data object", e)

    def deserialize(self, string_):
        # Decode response body
        try:
            if sys.version_info.major == 2:
                return json.load(string_)
            else:
                return json.loads(string_.read().decode('utf-8'))
        except Exception as e:
            raise SerializationError("Error decoding of server response", e)


class UrlFormatter:
    _url_tpl = 'https://{hostname}/{path}?{query}'

    @classmethod
    def format_url(cls, hostname, *path_components, query=None):
        return cls._url_tpl.format(hostname=hostname, path='/'.join(map(str, path_components)),
                                   query=urlencode(query) if query is not None else '')


class BaseClient(ABC):
    def __init__(self, hostname, serializer=None, http_requester=None):
        self.hostname = hostname
        self.serializer = serializer or JsonSerializer()
        self.http_requester = http_requester or UrllibHttpRequester()

    def _call(self, *path_components, query=None, params=None):
        # Add a suffix (indicating data interchange format, for example, ".json") to the last path component
        path_components = self._add_transport_to_rest_endpoints(path_components)
        # Serialize data, make a call and then deserialize response body
        url = UrlFormatter.format_url(self.hostname, *path_components, query=query)
        req_body = self.serializer.serialize(params) if params is not None else None
        res_body = self.http_requester.post(url, body=req_body, headers={'Content-Type': self._get_content_type()})
        return self.serializer.deserialize(res_body)

    def _add_transport_to_rest_endpoints(self, path_components):
        if path_components[0] != 'rest':
            return path_components
        path_component_list = list(path_components)
        path_component_list.append(path_component_list.pop() + '.' + self.serializer.format)
        return tuple(path_component_list)

    def _get_content_type(self):
        return 'application/' + self.serializer.format

    @abstractmethod
    def call(self, method, params=None):
        pass

    def call_batch(self, calls, halt_on_error=False):
        return self.call('batch', params={'cmd': self._normalize_calls(calls), 'halt': halt_on_error})

    @classmethod
    def _normalize_calls(cls, calls):
        return {name: cls._normalize_call(name, call) for name, call in calls.items()}

    @staticmethod
    def _normalize_call(name, call):
        if isinstance(call, str):
            return call
        elif isinstance(call, (list, tuple)):
            try:
                return '?'.join([call[0], format_qs_deep(call[1])])
            except IndexError as e:
                raise ValueError('The "%s" call must be a pair of values' % name, e)
        elif isinstance(call, dict):
            try:
                return '?'.join([call['method'], format_qs_deep(call['params'])])
            except KeyError as e:
                raise ValueError('The "%s" call has required keys: method, params' % name, e)
        raise ValueError('The "%s" call must be a string, a tuple or a dictionary' % name)


class InboundWebhookClient(BaseClient):
    def __init__(self, hostname, auth_code, user_id=1, serializer=None, http_requester=None):
        super().__init__(hostname, serializer=serializer, http_requester=http_requester)
        self.auth_code = auth_code
        self.user_id = user_id

    def call(self, method, params=None):
        return self._call('rest', self.user_id, self.auth_code, method, params=params)


class LocalApplicationClient(BaseClient):
    def __init__(self, hostname, client_id, client_secret, serializer=None, http_requester=None):
        super().__init__(hostname, serializer=serializer, http_requester=http_requester)
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._refresh_token = None

    def get_auth_url(self, **query):
        query.update({
            'client_id': self.client_id,
            'response_type': 'code'
        })
        return UrlFormatter.format_url(self.hostname, 'oauth', 'authorize', query=query)

    def get_auth(self, auth_code, **query):
        query.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code'
        })
        return self._fetch_auth_by(query)

    def _fetch_auth_by(self, query):
        data = self._call('oauth', 'token', query=query)
        self._access_token = data.get('access_token')
        self._refresh_token = data.get('refresh_token')
        return data

    def refresh_auth(self, **query):
        query.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        })
        return self._fetch_auth_by(query)

    def call(self, method, params=None):
        return self._call('rest', method, query={'auth': self._access_token}, params=params)
