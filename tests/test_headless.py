import unittest
import urllib.parse

from bitrix24 import Bitrix24


class Bitrix24HeadlessTest(unittest.TestCase):
    client_id = 'abc'
    client_secret = 'xyz'
    domain = 'test.bitrix.com'

    def setUp(self):
        self.bx24 = Bitrix24(
            client_id=self.client_id,
            client_secret=self.client_secret,
            domain=self.domain
        )

    @staticmethod
    def _get_url(endpoint, query):
        return '{}?{}'.format(endpoint, urllib.parse.urlencode(query))

    def test_get_oauth_endpoint(self):
        action, query = 'action', {'y': 1}
        # Without optional argument
        endpoint1 = self.bx24._get_oauth_endpoint(action)
        endpoint2 = self.bx24._oauth_path_template.format(
            domain=self.bx24.domain,
            action=action
        )
        self.assertEqual(endpoint1, endpoint2)
        # With optional argument
        endpoint3 = self.bx24._get_oauth_endpoint(action, query)
        endpoint4 = self.bx24._oauth_path_template.format(
            domain=self.bx24.domain,
            action=action
        )
        endpoint4 = self._get_url(endpoint4, query)
        self.assertEqual(endpoint3, endpoint4)

    def test_get_authorize_endpoint(self):
        manual_endpoint = self.bx24._oauth_path_template.format(
            domain=self.domain,
            action='authorize'
        )
        manual_query = {
            'client_id': self.bx24.client_id,
            'response_type': 'code'
        }
        # Without optional parameters
        url = self._get_url(manual_endpoint, manual_query)
        self.assertEqual(self.bx24.get_authorize_endpoint(), url)
        # With optional parameters
        param = {'a': 1}
        extra_query = param
        extra_query.update(manual_query)
        url = self._get_url(manual_endpoint, extra_query)
        origin_endpoint = self.bx24.get_authorize_endpoint(**param)
        self.assertEqual(origin_endpoint, url)

    def test_get_tokens(self):
        self.bx24.access_token = 'qwe'
        self.bx24.refresh_token = 'qaz'
        self.assertDictEqual(self.bx24.get_tokens(), {
            'access_token': self.bx24.access_token,
            'refresh_token':self.bx24.refresh_token
        })
