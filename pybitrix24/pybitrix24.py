from abc import abstractproperty

from .auth import default_oauth2_client_factory
from .backcomp.abc_ import ABC
from .web import UrlFormatter, urlencode_deep, default_http_client_factory


class BaseApiClient(ABC):
    def __init__(self, hostname, serializer=None, http_client_factory=default_http_client_factory):
        self.hostname = hostname
        self.http_client = http_client_factory(serializer=serializer)

    def call(self, method, params=None):
        # Add a suffix (indicating data interchange format, for example, ".json") to the last path component
        path_components = list(self._base_path_components)
        path_components.append(method + '.' + self.serializer.format)
        # Serialize data, make a call and then deserialize response body
        url = UrlFormatter.format_https(self.hostname, path_components, query_data=self._query_data)
        return self.http_client.post(url, params)

    @abstractproperty
    def _base_path_components(self):
        raise NotImplementedError("_base_path_components() must be implemented")

    @property
    def _query_data(self):
        return None

    def call_batch(self, calls, halt_on_error=False):
        return self.call('batch', params={'cmd': self._normalize_calls(calls), 'halt': halt_on_error})

    @classmethod
    def _normalize_calls(cls, calls):
        return {name: cls._normalize_call(name, call) for name, call in calls.items()}

    @classmethod
    def _normalize_call(cls, name, call):
        if isinstance(call, str):
            return call
        elif isinstance(call, (tuple, list)):
            if len(call) != 2:
                raise ValueError('The "%s" call must be a pair of values' % name)
            return cls._format_call_pair(call[0], call[1])
        elif isinstance(call, dict):
            if 'method' not in call or 'params' not in call or len(call) != 2:
                raise ValueError('The "%s" call must contain only "method" and "params" keys' % name)
            return cls._format_call_pair(call['method'], call['params'])
        raise ValueError('The "%s" call must be of type: str, tuple, list or dict' % name)

    @staticmethod
    def _format_call_pair(method, params):
        return method + '?' + urlencode_deep(params)


class InboundWebhookClient(BaseApiClient):
    def __init__(self, hostname, auth_code, user_id=1, serializer=None):
        super(BaseApiClient, self).__init__(hostname, serializer=serializer)
        self.auth_code = auth_code
        self.user_id = user_id

    @property
    def _base_path_components(self):
        return 'rest', self.user_id, self.auth_code


class LocalApplicationClient(BaseApiClient):
    def __init__(self, hostname, client_id, client_secret, serializer=None,
                 oauth2_client_factory=default_oauth2_client_factory):
        super(BaseApiClient, self).__init__(hostname, serializer=serializer)
        self.oauth2_client = oauth2_client_factory(hostname, client_id, client_secret, http_client=self.http_client)

    @property
    def _base_path_components(self):
        return 'rest',

    @property
    def _query_data(self):
        return {'auth': self.oauth2_client.get_auth()}
