import os, unittest, uuid
import urllib.parse

from bitrix24 import Bitrix24


class Bitrix24HeadlessTest(unittest.TestCase):
    client_id = os.environ.get('TEST_CLIENT_ID', uuid.uuid4().hex)
    client_secret = os.environ.get('TEST_CLIENT_SECRET', uuid.uuid4())
    domain = os.environ.get('TEST_DOMAIN', 'test.bitrix24.com')
    client_endpoint = os.environ.get('TEST_CLIENT_ENDPOINT')
    user_id = os.environ.get('TEST_USER_ID', 1)

    def setUp(self):
        self.bx24 = Bitrix24(
            client_id=self.client_id,
            client_secret=self.client_secret,
            domain=self.domain,
            client_endpoint=self.client_endpoint,
            user_id=self.user_id
        )

    @staticmethod
    def _build_url(endpoint, query):
        return '{}?{}'.format(endpoint, urllib.parse.urlencode(query))

    def test_resolve_authorize_endpoint(self):
        manual_endpoint = self.bx24._oauth_endpoint_template.format(
            domain=self.domain,
            action='authorize'
        )
        manual_query = {
            'client_id': self.bx24.client_id,
            'response_type': 'code'
        }
        # Without optional parameters
        url = self._build_url(manual_endpoint, manual_query)
        self.assertEqual(self.bx24.resolve_authorize_endpoint(), url)
        # With optional parameters
        param = {'a': 1}
        extra_query = param.copy()
        extra_query.update(manual_query)
        url = self._build_url(manual_endpoint, extra_query)
        origin_endpoint = self.bx24.resolve_authorize_endpoint(**param)
        self.assertEqual(origin_endpoint, url)

    def test_resolve_client_endpoint(self):
        if self.bx24.client_endpoint:
            ce = self.bx24.client_endpoint
        else:
            ce = self.bx24._client_endpoint_template.format(domain=self.domain)
        self.assertEqual(self.bx24._resolve_client_endpoint(), ce)

    def test_resolve_oauth_endpoint(self):
        action, query = 'action', {'y': 1}
        # Without optional argument
        endpoint1 = self.bx24._resolve_oauth_endpoint(action)
        endpoint2 = self.bx24._oauth_endpoint_template.format(
            domain=self.bx24.domain,
            action=action
        )
        self.assertEqual(endpoint1, endpoint2)
        # With optional argument
        endpoint3 = self.bx24._resolve_oauth_endpoint(action, query)
        endpoint4 = self.bx24._oauth_endpoint_template.format(
            domain=self.bx24.domain,
            action=action
        )
        self.assertEqual(endpoint3, self._build_url(endpoint4, query))

    def test_resolve_webhook_endpoint(self):
        code = uuid.uuid4().hex[:16]
        self.assertEqual(
            self.bx24._resolve_webhook_endpoint(code),
            self.bx24._webhook_endpoint_template.format(
                domain=self.domain,
                user_id=self.bx24.user_id,
                code=code
            )
        )

    def test_get_tokens(self):
        self.bx24.access_token = uuid.uuid4()
        self.bx24.refresh_token = uuid.uuid4()
        self.assertDictEqual(self.bx24.get_tokens(), {
            'access_token': self.bx24.access_token,
            'refresh_token':self.bx24.refresh_token
        })
