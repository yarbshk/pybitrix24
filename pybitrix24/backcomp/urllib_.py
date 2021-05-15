import sys

try:
    from urllib.request import Request, urlopen as _urlopen
    from urllib.parse import urlencode, unquote
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import Request, urlopen as _urlopen, HTTPError
    from urllib import urlencode, unquote


def urlopen(*args, **kwargs):
    if sys.version_info.major <= 2:
        body = _urlopen(*args, **kwargs)
        return bytes(str(body).encode("utf-8"))
    else:
        return _urlopen(*args, **kwargs).read()
