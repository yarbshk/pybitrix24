import os
import unittest

from pybitrix24 import Bitrix24
from tests.automation import TokenRefresher


def require_env_var(name):
    env_var = os.environ.get(name)
    if env_var is None:
        raise ValueError('An environment variable %s is required' % name)
    return env_var


class Bitrix24EndToEndTests(unittest.TestCase):
    hostname = require_env_var('TEST_HOSTNAME')
    client_id = require_env_var('TEST_CLIENT_ID')
    client_secret = require_env_var('TEST_CLIENT_SECRET')
    user_id = os.environ.get('TEST_USER_ID', 1)

    webhook_code = require_env_var('TEST_WEBHOOK_CODE')

    token_refresher = TokenRefresher(require_env_var('TEST_USER_LOGIN'),
                                     require_env_var('TEST_USER_PASSWORD'))

    def setUp(self):
        self.bx24 = Bitrix24(self.hostname, client_id=self.client_id,
                             client_secret=self.client_secret,
                             user_id=self.user_id)
        self.token_refresher.update_tokens(self.bx24)

    def tearDown(self):
        # Make sure tokens are synchronized in case they are updated by a test
        if self.bx24 is not None:
            self.token_refresher.access_token = self.bx24._access_token
            self.token_refresher.refresh_token = self.bx24._refresh_token

    def test_obtain_tokens(self):
        self.bx24._access_token = None
        self.bx24._refresh_token = None
        auth_code = self.token_refresher.obtain_auth_code(self.bx24)
        data = self.bx24.obtain_tokens(auth_code)
        self.assertEqual(self.bx24._access_token, data['access_token'])
        self.assertEqual(self.bx24._refresh_token, data['refresh_token'])

    def test_refresh_tokens(self):
        data = self.bx24.refresh_tokens()
        self.assertEqual(self.bx24._access_token, data['access_token'])
        self.assertEqual(self.bx24._refresh_token, data['refresh_token'])

    def test_call(self):
        params = {'ID': self.bx24.user_id}
        data = self.bx24.call('user.get', params=params)
        self.assertIsInstance(data, dict)
        self.assertNotIn('error', data)

    def test_call_batch(self):
        calls = {
            'get_user': ('user.current', {}),
            'get_department': {
                'method': 'department.get',
                'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
            }
        }
        data = self.bx24.call_batch(calls, True)
        self.assertIsInstance(data, dict)
        self.assertNotEqual(data['result'], {})
        self.assertListEqual(data['result']['result_error'], [])

    def test_binding(self):
        event, handler = 'OnAppUpdate', 'https://example.com/'
        self._test_call_event_bind(event, handler)
        self._test_call_event_unbind(event, handler)

    def _test_call_event_bind(self, event, handler):
        data = self.bx24.call_event_bind(event, handler)
        self.assertIsInstance(data, dict)
        self.assertNotIn('error', data)

    def _test_call_event_unbind(self, event, handler):
        data = self.bx24.call_event_unbind(event, handler)
        self.assertIsInstance(data, dict)
        self.assertNotIn('error', data)

    def test_call_webhook(self):
        data = self.bx24.call_webhook('profile', self.webhook_code)
        self.assertIsInstance(data, dict)
        self.assertNotIn('error', data)

    def test_call_batch_webhook(self):
        bx24hook = Bitrix24(self.hostname, user_id=1)
        calls = {
            'get_user': ('user.current', {}),
            'get_department': {
                'method': 'department.get',
                'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
            }
        }
        data = bx24hook.call_batch_webhook(calls, self.webhook_code, True)
        self.assertIsInstance(data, dict)
        self.assertNotEqual(data['result'], {})
        self.assertListEqual(data['result']['result_error'], [])
