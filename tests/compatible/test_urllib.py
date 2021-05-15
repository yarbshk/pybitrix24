from pybitrix24.backcomp.urllib_ import urlopen, Request

def test_urlopen__should_accept_request_and_return_bytes():
    actual = urlopen(Request("file://" + __file__))
    assert type(actual) == bytes
