import os
import unittest

from pybitrix24 import Bitrix24
from .automation import UnsafeAuthCodeProvider


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

    user_login = require_env_var('TEST_USER_LOGIN')
    user_password = require_env_var('TEST_USER_PASSWORD')

    def setUp(self):
        self.bx24 = Bitrix24(self.hostname, client_id=self.client_id,
                             client_secret=self.client_secret,
                             user_id=self.user_id)

    def obtain_auth_code(self):
        with UnsafeAuthCodeProvider(self.bx24) as provider:
            return provider.request_auth_code(self.user_login,
                                              self.user_password)

    def test_obtain_tokens(self):
        self.assertIsNone(self.bx24._access_token)
        self.assertIsNone(self.bx24._refresh_token)
        data = self.bx24.obtain_tokens(self.obtain_auth_code())
        self.assertEqual(self.bx24._access_token, data['access_token'])
        self.assertEqual(self.bx24._refresh_token, data['refresh_token'])

    def test_refresh_tokens(self):
        self.bx24.obtain_tokens(self.obtain_auth_code())
        data = self.bx24.refresh_tokens()
        self.assertEqual(self.bx24._access_token, data['access_token'])
        self.assertEqual(self.bx24._refresh_token, data['refresh_token'])

    def test_call(self):
        self.bx24.obtain_tokens(self.obtain_auth_code())
        params = {'ID': self.bx24.user_id}
        data = self.bx24.call('user.get', params=params)
        self.assertIsInstance(data, dict)
        self.assertNotIn('error', data)

    def test_call_batch(self):
        self.bx24.obtain_tokens(self.obtain_auth_code())
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
        self.bx24.obtain_tokens(self.obtain_auth_code())
        event, handler = 'OnAppUpdate', 'https://example.com/'
        self._test_call_bind(event, handler)
        self._test_call_unbind(event, handler)

    def _test_call_bind(self, event, handler):
        data = self.bx24.call_bind(event, handler)
        self.assertIsInstance(data, dict)
        self.assertNotIn('error', data)

    def _test_call_unbind(self, event, handler):
        data = self.bx24.call_unbind(event, handler)
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
