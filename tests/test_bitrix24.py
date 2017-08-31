import unittest
import urllib.parse
import os

from app.bitrix24 import Bitrix24


class Bitrix24Test(unittest.TestCase):
    domain = os.environ.get('TEST_DOMAIN')
    client_id = os.environ.get('TEST_CLIENT_ID')
    client_secret = os.environ.get('TEST_CLIENT_SECRET')

    def setUp(self):
        self.bx24 = Bitrix24(
            domain=self.domain,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def test_get_oauth_endpoint_method(self):
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
        encoded_query = urllib.parse.urlencode(query)
        endpoint4 = '{}?{}'.format(endpoint4, encoded_query)
        self.assertEqual(endpoint3, endpoint4)
