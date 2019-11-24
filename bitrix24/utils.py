import json

from bitrix24 import exceptions
# from urllib.parse import urlencode

try:
    from urllib.parse import urlencode as urllib_urlencode
except ImportError:
    from urllib import urlencode as urllib_urlencode

from collections import OrderedDict


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


def urlencode(params):
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

    return urllib_urlencode(url_params, doseq=True)

def resolve_response(response):
    try:
        result = json.loads(response.text)
    except AttributeError:
        result = None
    except TypeError:
        result = None
    return result


def prepare_batch(calls):
    commands = {}
    for name, call in calls.items():
        if isinstance(call, str):
            command = call
        elif isinstance(call, tuple):
            try:
                command = '{}?{}'.format(call[0], urlencode(call[1]))
            except IndexError:
                raise exceptions.BatchIndexError(name)
        elif isinstance(call, dict):
            try:
                command = '{}?{}'.format(call['method'], urlencode(call['params']))
            except KeyError:
                raise exceptions.BatchKeyError(name)
        else:
            if isinstance(call, list):
                raise exceptions.BatchInstanceError(name, [tuple])
            else:
                raise exceptions.BatchInstanceError(name, [str, tuple, dict])
        commands[name] = command
    return commands
