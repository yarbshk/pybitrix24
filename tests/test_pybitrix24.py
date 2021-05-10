import pytest

from pybitrix24 import InboundWebhookClient

class TestBaseClient:
    def test_call_batch(self):
        pass


class TestInboundWebhookClient:
    pass
    # def test_call(self):
    #     # Assign
    #     client = InboundWebhookClient("test_hostname", "test_auth_code")
    #     # Act
    #     client.call('user.get', {'ID': 1})
    #     # Assert


class TestLocalApplicationClient:
    def test_call(self):
        pass


class TestJsonSerializer:
    def test_format(self):
        pass


    def test_serialize_with_valid_params(self):
        pass

    def test_serialize_with_invalid_params(self):
        pass

    # @pytest.mark.parametrize('document,e_obj', [
    #     ('1', 1),
    #     ('true', True),
    #     ('"profile"', 'profile'),
    #     ('{"ID": 1}', {'ID': 1}),
    #     ('[{"ID": 1},{"ID": 2}]', [{'ID': 1}, {'ID': 2}]),
    # ])
    # def test_deserialize_with_valid_params(self):
    #     pass

    def test_deserialize_with_invalid_params(self):
        pass
