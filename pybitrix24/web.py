import re
from collections import OrderedDict

from .backcomp.urllib_ import Request, urlopen, urlencode, HTTPError
from .backcomp.urllib_ import unquote
from .exceptions import PyBitrix24Error
from .serialization import JsonSerializer


class HttpClient(object):
    def __init__(self, serializer):
        self.serializer = serializer

    def post(self, url, data=None):
        req_body = self.serializer.serialize(data) if data is not None else None
        res_body = self._make_post_request(url, body=req_body, headers={'Content-Type': self._content_type})
        return self.serializer.deserialize(res_body)

    @property
    def _content_type(self):
        return 'application/' + self.serializer.format

    @staticmethod
    def _make_post_request(url, body=None, headers=None):
        data = body.encode('utf-8') if body is not None else None
        request = Request(url, data=data, headers=headers)
        try:
            return urlopen(request).decode('utf-8')
        except HTTPError as e:
            return e
        except Exception as e:
            raise PyBitrix24Error("Error on request", e)


def default_http_client_factory(serializer=None):
    return HttpClient(serializer or JsonSerializer())


class UrlFormatter(object):
    _https_tpl = 'https://{hostname}/{path}?{query}'

    @classmethod
    def format_https(cls, hostname, path_components, query_data=None):
        return cls._https_tpl.format(hostname=hostname, path='/'.join(map(str, path_components)),
                                     query=urlencode(query_data) if query_data is not None else '')


def _flatten(d):
    """Return a dict as a list of lists.

    >>> _flatten({"a": "b"})
    [['a', 'b']]
    >>> _flatten({"a": [1, 2, 3]})
    [['a', [1, 2, 3]]]
    >>> _flatten({"a": {"b": "c"}})
    [['a', 'b', 'c']]
    >>> _flatten({"a": {"b": {"c": "e"}}})
    [['a', 'b', 'c', 'e']]
    >>> _flatten({"a": {"b": "c", "d": "e"}})
    [['a', 'b', 'c'], ['a', 'd', 'e']]
    >>> _flatten({"a": {"b": "c", "d": "e"}, "b": {"c": "d"}})
    [['a', 'b', 'c'], ['a', 'd', 'e'], ['b', 'c', 'd']]
    """
    if not isinstance(d, dict):
        return [[d]]

    returned = []
    for key, value in sorted(d.items()):
        # Each key, value is treated as a row.
        nested = _flatten(value)
        for nest in nested:
            current_row = [key]
            current_row.extend(nest)
            returned.append(current_row)

    return returned


def _parametrize(params):
    """Return list of params as params.

    >>> _parametrize(['a'])
    'a'
    >>> _parametrize(['a', 'b'])
    'a[b]'
    >>> _parametrize(['a', 'b', 'c'])
    'a[b][c]'

    """
    returned = str(params[0])
    returned += "".join("[" + str(p) + "]" for p in params[1:])
    return returned


def urlencode_deep(params):
    """Urlencode a multidimensional dict."""

    # Not doing duck typing here. Will make debugging easier.
    if not isinstance(params, dict):
        raise TypeError("Only dicts are supported.")

    params = _flatten(params)

    url_params = OrderedDict()
    for param in params:
        value = param.pop()

        name = _parametrize(param)
        if isinstance(value, (list, tuple)):
            name += "[]"

        url_params[name] = value

    return urlencode(url_params, doseq=True)


def urldecode_deep(qs, sep='&'):
    result = {}
    for segment in qs.split(sep):
        quoted_pair = segment.split('=')
        if len(quoted_pair) != 2:
            raise ValueError("Invalid query string")
        key = unquote(quoted_pair[0])
        value = unquote(quoted_pair[1])

        subkeys = [re.search(r'(\w+)', key).group()]
        if len(subkeys[0]) != len(key):
            for subkey in re.findall(r'\[(\w+)]', key):
                subkeys.append(subkey)

        tmp = result
        last_subkey_index = len(subkeys) - 1
        for index, subkey in enumerate(subkeys):
            if index == last_subkey_index:
                tmp[subkey] = value
                continue
            elif subkey not in tmp:
                tmp[subkey] = {}
            tmp = tmp[subkey]
    return result
