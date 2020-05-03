import unittest
import os

from bitrix24 import Bitrix24


class Bitrix24Test(unittest.TestCase):
    domain = os.environ.get('TEST_DOMAIN')
    code = os.environ.get('TEST_WEBHOOK_CODE')
    user_id = os.environ.get('TEST_USER_ID', 1)
    event = 'OnAppUpdate'
    handler = 'https://example.com/'

    def setUp(self):
        self.bx24 = Bitrix24(
            access_token=os.environ.get('TEST_ACCESS_TOKEN'),
            client_endpoint=os.environ.get('TEST_CLIENT_ENDPOINT'),
            client_id=os.environ.get('TEST_CLIENT_ID'),
            client_secret=os.environ.get('TEST_CLIENT_SECRET'),
            domain=os.environ.get('TEST_DOMAIN'),
            refresh_token=os.environ.get('TEST_REFRESH_TOKEN'),
            user_id=self.user_id
        )

    def test_call_method(self):
        params = {'ID': self.bx24.user_id}
        result = self.bx24.call_method('user.get', params=params)
        self.assertIsInstance(result, dict)
        self.assertNotIn('error', result)

    def test_call_batch(self):
        calls = {
            'get_user': ('user.current', {}),
            'get_department': {
                'method': 'department.get',
                'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
            }
        }
        result = self.bx24.call_batch(calls, True)
        self.assertIsInstance(result, dict)
        self.assertNotEqual(result['result'], {})
        self.assertListEqual(result['result']['result_error'], [])

    def test_binding(self):
        self._test_call_bind()
        self._test_call_unbind()

    def _test_call_bind(self):
        result = self.bx24.call_bind(self.event, self.handler)
        self.assertIsInstance(result, dict)
        self.assertNotIn('error', result)

    def _test_call_unbind(self):
        result = self.bx24.call_unbind(self.event, self.handler)
        self.assertIsInstance(result, dict)
        self.assertNotIn('error', result)

    def test_call_webhook(self):
        result = self.bx24.call_method('profile', self.code)
        self.assertIsInstance(result, dict)
        self.assertNotIn('error', result)
        
    def test_call_batch_webhook(self):
        bx24hook = Bitrix24(self.domain, user_id=1)
        calls = {
            'get_user': ('user.current', {}),
            'get_department': {
                'method': 'department.get',
                'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
            }
        }
        result = bx24hook.call_batch_webhook(calls, self.code, True)
        self.assertIsInstance(result, dict)
        self.assertNotEqual(result['result'], {})
        self.assertListEqual(result['result']['result_error'], [])
