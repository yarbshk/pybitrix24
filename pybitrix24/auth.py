import threading
from abc import abstractmethod

from .backcomp.abc_ import ABC
from .web import UrlFormatter, default_rest_client_factory


class OAuth2Client(ABC):
    @abstractmethod
    def get_auth_url(self, **query_data):
        raise NotImplementedError("get_auth_url(query_data) must be implemented")

    @abstractmethod
    def get_auth(self):
        raise NotImplementedError("get_auth() must be implemented")

    @abstractmethod
    def fetch_auth(self, auth_code, **query_data):
        raise NotImplementedError("fetch_auth(auth_code, query_data) must be implemented")

    @abstractmethod
    def refresh_auth(self, **query_data):
        raise NotImplementedError("refresh_auth(query_data) must be implemented")


class Bitrix24OAuth2Client(OAuth2Client):
    def __init__(self, hostname, client_id, client_secret, rest_client=None):
        self.hostname = hostname
        self.client_id = client_id
        self.client_secret = client_secret
        self.rest_client = rest_client or default_rest_client_factory()
        self._access_token = None
        self._refresh_token = None

    def get_auth_url(self, **query_data):
        query_data.update({
            'client_id': self.client_id,
            'response_type': 'code'
        })
        return UrlFormatter.format_https(self.hostname, ['oauth', 'authorize'], query_data=query_data)

    def get_auth(self):
        return self._access_token

    def fetch_auth(self, auth_code, **query_data):
        query_data.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code'
        })
        return self._get_auth_data_and_cache_tokens(query_data)

    def refresh_auth(self, **query_data):
        query_data.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        })
        return self._get_auth_data_and_cache_tokens(query_data)

    def _get_auth_data_and_cache_tokens(self, query_data):
        url = UrlFormatter.format_https(self.hostname, ('oauth', 'authorize'), query_data=query_data)
        res_data = self.rest_client.post(url)
        self._access_token = res_data.get('access_token')
        self._refresh_token = res_data.get('refresh_token')
        return res_data


class AutoRefreshableOAuth2ClientDecorator(OAuth2Client):
    def __init__(self, auth):
        self.auth = auth

    def get_auth_url(self, **query_data):
        return self.auth.get_auth_url(**query_data)

    def get_auth(self):
        self._populate_tokens()
        return self.auth.get_auth()

    def _populate_tokens(self):
        if self.auth.get() is None:
            self.auth.fetch_auth()
        else:
            self.auth.refresh()
        threading.Timer(55, self._populate_tokens).start()

    def fetch_auth(self, auth_code, **query_data):
        return self.auth.fetch_auth(auth_code, **query_data)

    def refresh_auth(self, **query_data):
        return self.auth.refresh_auth(**query_data)


def default_oauth2_client_factory(*args, **kwargs):
    return AutoRefreshableOAuth2ClientDecorator(Bitrix24OAuth2Client(*args, **kwargs))
