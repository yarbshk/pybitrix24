import unittest
import os

from bitrix24 import Bitrix24


class Bitrix24TokensTest(unittest.TestCase):
    def setUp(self):
        self.code = os.environ.get('TEST_CODE')
        self.bx24 = Bitrix24(
            domain=os.environ.get('TEST_DOMAIN'),
            client_id=os.environ.get('TEST_CLIENT_ID'),
            client_secret=os.environ.get('TEST_CLIENT_SECRET')
        )

    def test_tokens(self):
        self._test_request_tokens()
        self._test_refresh_tokens()

    def _test_request_tokens(self):
        self.bx24.request_tokens(self.code)
        self.assertIsNotNone(self.bx24.access_token)
        self.assertIsNotNone(self.bx24.client_endpoint)
        self.assertIsNotNone(self.bx24.domain)
        self.assertIsNotNone(self.bx24.expires_in)
        self.assertIsNotNone(self.bx24.refresh_token)
        self.assertIsNotNone(self.bx24.scope)
        self.assertIsNotNone(self.bx24.server_endpoint)
        self.assertIsNotNone(self.bx24.user_id)
        self.assertNotEqual(self.bx24.scope, '')
        self.assertNotEqual(self.bx24.user_id, 0)

    def _test_refresh_tokens(self):
        old_access_token = self.bx24.access_token
        old_refresh_token = self.bx24.refresh_token
        self.bx24.refresh_tokens()
        self.assertNotEqual(self.bx24.access_token, old_access_token)
        self.assertNotEqual(self.bx24.refresh_token, old_refresh_token)
