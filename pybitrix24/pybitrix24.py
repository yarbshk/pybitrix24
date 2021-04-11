import json
import sys
from abc import ABC, abstractmethod

from .utils import prepare_batch_command

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode


class PyBitrix24Exception(Exception):
    pass


class CallingException(PyBitrix24Exception):
    pass


class BaseCaller(ABC):
    @abstractmethod
    def post(self, url, body=None, headers=None):
        pass


class UrllibCaller(BaseCaller):
    def post(self, url, body=None, headers=None):
        request = Request(url, data=body, headers=headers)
        try:
            return urlopen(request)
        except HTTPError as e:
            return e
        except Exception as e:
            raise CallingException("Error on request", e)


class CodingException(PyBitrix24Exception):
    pass


class BaseCoder(ABC):
    format = None

    @abstractmethod
    def encode(self, data):
        pass

    @abstractmethod
    def decode(self, body):
        pass


class JsonCoder(BaseCoder):
    format = 'json'

    def encode(self, data):
        try:
            return json.dumps(data).encode('utf-8')
        except Exception as e:
            raise CodingException("Unable to encode data object", e)

    def decode(self, body):
        # Decode response body
        try:
            if sys.version_info.major == 2:
                return json.load(body)
            else:
                return json.loads(body.read().decode('utf-8'))
        except Exception as e:
            raise CodingException("Error decoding of server response", e)


class UrlFormatter:
    _url_tpl = 'https://{hostname}/{path}?{query}'

    @classmethod
    def format_url(cls, hostname, *path_components, query=None):
        return cls._url_tpl.format(hostname=hostname, path='/'.join(map(str, path_components)),
                                   query=urlencode(query) if query is not None else '')


class BaseClient(ABC):
    def __init__(self, hostname, coder=None, caller=None):
        self.hostname = hostname
        self.coder = coder or JsonCoder()
        self.caller = caller or UrllibCaller()

    def _call(self, *path_components, query=None, data=None):
        # Add a suffix (indicating data interchange format, for example, ".json") to the last path component
        path_components = self._add_transport_to_rest_endpoints(path_components)
        # Serialize data, make a call and then deserialize response body
        url = UrlFormatter.format_url(self.hostname, *path_components, query=query)
        req_body = self.coder.encode(data) if data is not None else None
        res_body = self.caller.post(url, body=req_body, headers={'Content-Type': self._get_content_type()})
        return self.coder.decode(res_body)

    def _add_transport_to_rest_endpoints(self, path_components):
        if path_components[0] != 'rest':
            return path_components
        path_component_list = list(path_components)
        path_component_list.append(path_component_list.pop() + '.' + self.coder.format)
        return tuple(path_component_list)

    def _get_content_type(self):
        return 'application/' + self.coder.format

    @abstractmethod
    def call(self, method, params=None):
        pass

    def call_batch(self, calls, halt_on_error=False):
        return self.call('batch', {'cmd': prepare_batch_command(calls), 'halt': halt_on_error})


class ScriptClient(BaseClient):
    def __init__(self, hostname, auth_code, user_id=1, coder=None, caller=None):
        super().__init__(hostname, coder=coder, caller=caller)
        self.auth_code = auth_code
        self.user_id = user_id

    def call(self, method, params=None):
        return self._call('rest', self.user_id, self.auth_code, method, data=params)


class ApplicationClient(BaseClient):
    def __init__(self, hostname, client_id, client_secret, coder=None, caller=None):
        super().__init__(hostname, coder=coder, caller=caller)
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
        return self._call('rest', method, query={'auth': self._access_token}, data=params)
