import mock

from pybitrix24.serialization import JsonSerializer, BaseSerializer
from pybitrix24.web import RestClient


class TestRestClient(object):
    @mock.patch('pybitrix24.web.urlopen')
    def test_post_with_serializer(self, mock_urlopen):
        # Assign
        mock_urlopen.return_value = bytes('"response_body"')  # encoded JSON string
        rest_client = RestClient(JsonSerializer())
        # Act
        res_data = rest_client.post('https://example.net/', data='request_body')
        # Assert
        request = mock_urlopen.call_args.args[0]
        assert request.get_full_url() == 'https://example.net/'
        assert request.data == '"request_body"'  # JSON string
        assert request.headers['Content-type'] == 'application/json'
        assert res_data == 'response_body'

    @mock.patch('pybitrix24.web.urlopen')
    def test_post_without_data(self, mock_urlopen):
        # Assign
        mock_serializer = mock.create_autospec(BaseSerializer)
        mock_serializer.deserialize.return_value = 'response_body'
        mock_urlopen.return_value = bytes('response_body')
        rest_client = RestClient(mock_serializer)
        # Act
        res_data = rest_client.post('https://example.net/')
        # Assert
        request = mock_urlopen.call_args.args[0]
        assert request.get_full_url() == 'https://example.net/'
        assert request.data is None
        assert 'Content-type' in request.headers
        assert res_data == 'response_body'
