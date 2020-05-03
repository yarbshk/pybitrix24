from collections import OrderedDict
from json import JSONDecodeError, load

from .exceptions import PBx24RequestError, PyBitrix24Error, PBx24ArgumentError

try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlopen
    from urllib import urlencode


def open_url(url, data=None):
    try:
        return urlopen(url, data)
    except Exception as e:
        raise PBx24RequestError("Error getting authorization grant", e)


def request(method, url, params):
    """
    :raise Bitrix24Error: If on error while requesting the server.
    :raise Bitrix24Error: If on error while decoding the response body.
    :param method:
    :param url:
    :param params:
    :return:
    """
    params = urlencode(params)
    if method == 'get':
        response = open_url(url + '?' + params)
    elif method == 'post':
        response = open_url(url, params.encode('utf-8'))
    else:
        raise PBx24ArgumentError("The HTTP method %s is not supported" % method)

    try:
        return load(response)
    except JSONDecodeError or TypeError as e:
        raise PyBitrix24Error("Error decoding of server response", e)


def flatten(d):
    """Return a dict as a list of lists.

    >>> flatten({"a": "b"})
    [['a', 'b']]
    >>> flatten({"a": [1, 2, 3]})
    [['a', [1, 2, 3]]]
    >>> flatten({"a": {"b": "c"}})
    [['a', 'b', 'c']]
    >>> flatten({"a": {"b": {"c": "e"}}})
    [['a', 'b', 'c', 'e']]
    >>> flatten({"a": {"b": "c", "d": "e"}})
    [['a', 'b', 'c'], ['a', 'd', 'e']]
    >>> flatten({"a": {"b": "c", "d": "e"}, "b": {"c": "d"}})
    [['a', 'b', 'c'], ['a', 'd', 'e'], ['b', 'c', 'd']]
    """
    if not isinstance(d, dict):
        return [[d]]

    returned = []
    for key, value in sorted(d.items()):
        # Each key, value is treated as a row.
        nested = flatten(value)
        for nest in nested:
            current_row = [key]
            current_row.extend(nest)
            returned.append(current_row)

    return returned


def parametrize(params):
    """Return list of params as params.

    >>> parametrize(['a'])
    'a'
    >>> parametrize(['a', 'b'])
    'a[b]'
    >>> parametrize(['a', 'b', 'c'])
    'a[b][c]'

    """
    returned = str(params[0])
    returned += "".join("[" + str(p) + "]" for p in params[1:])
    return returned


def encode_url(params):
    """Urlencode a multidimensional dict."""

    # Not doing duck typing here. Will make debugging easier.
    if not isinstance(params, dict):
        raise TypeError("Only dicts are supported.")

    params = flatten(params)

    url_params = OrderedDict()
    for param in params:
        value = param.pop()

        name = parametrize(param)
        if isinstance(value, (list, tuple)):
            name += "[]"

        url_params[name] = value

    return urlencode(url_params, doseq=True)


def prepare_batch(calls):
    commands = {}
    for name, call in calls.items():
        if isinstance(call, str):
            command = call
        elif isinstance(call, tuple):
            try:
                command = '{}?{}'.format(call[0], encode_url(call[1]))
            except IndexError as e:
                raise PyBitrix24Error(
                    'The "' + name + '" call must be a pair of values', e)
        elif isinstance(call, dict):
            try:
                command = '{}?{}'.format(call['method'],
                                         encode_url(call['params']))
            except KeyError as e:
                raise PyBitrix24Error(
                    'The "' + name + '" call has the following required '
                                     'keys: method, params.', e)
        else:
            if isinstance(call, list):
                raise PyBitrix24Error(
                    'The "' + name + '" call must be a tuple')
            else:
                raise PyBitrix24Error(
                    'The "' + name + '" call must be a string, a tuple or '
                                     'a dictionary.')
        commands[name] = command
    return commands
