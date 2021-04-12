from collections import OrderedDict
import re

try:
    from urllib.parse import urlencode, unquote
except ImportError:
    from urllib import urlencode


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


def format_qs_deep(params):
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


def parse_qs_deep(qs, sep='&'):
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
