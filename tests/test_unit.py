import re
import unittest

from pybitrix24 import Bitrix24, PBx24AttributeError, get_error_if_present


def is_url(s):
    return re.match(r"^http(s)?://[\w\-./#?=&]+", s)


class Bitrix24UnitTests(unittest.TestCase):
    hostname = 'test.bitrix24.com'
    client_id = 'test.eMfQDE5VAglQKz.65790983'
    client_secret = 'yhOAwVvHa6yjba8r3i954N4DVF65VkiP8becqms1XJbLDb3TBP'
    user_id = 1

    def setUp(self):
        self.bx24 = Bitrix24(self.hostname, client_id=self.client_id,
                             client_secret=self.client_secret,
                             user_id=self.user_id)

    def test_build_authorization_url__client_id_is_required(self):
        self.bx24.client_id = None
        self.assertRaises(PBx24AttributeError, self.bx24.build_authorization_url)

    def test_build_authorization_url__url(self):
        url = self.bx24.build_authorization_url(test_key='test_value',
                                                response_type='ignored')
        self.assertTrue(is_url(url))
        self.assertTrue('client_id=%s' % self.bx24.client_id in url)
        self.assertTrue('response_type=code' in url)
        self.assertTrue('test_key=test_value' in url)

    def test_get_error_if_present__call(self):
        test_data = [
            {'data': {}, 'error': None},
            {'data': {'error': 'Error message'}, 'error': 'Error message'},
            {'data': {'result': {}}, 'error': None},
            {'data': {'result': {'result_error': 'Error message'}},
             'error': 'Error message'},
        ]

        for td in test_data:
            error = get_error_if_present(td['data'])
            self.assertEqual(error, td['error'])
