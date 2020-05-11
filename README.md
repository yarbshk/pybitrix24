# pybitrix24
The simplest zero dependency polyversion Python library for Bitrix24 REST API.

## Features
- **Polyversion.** Supported Python versions: 2.7, 3.5+.
- **Zero dependency.** It's fast, lightweight and secure.
- **Reliable.** 85% test coverage.
- **Just simple.** Examples of usage and clear sources.

## Installation
Install using [pip](https://pip.pypa.io/en/stable/):

```bash
$ pip install pybitrix24
```

## Getting started

### Preparation

The current section and next one can be skipped if only webhooks will be used.

To start making requests it's necessary to [create an application](https://training.bitrix24.com/rest_help/bitrix24_apps/index.php) in the marketplace first. Then create an instance of the main class with the minimum required configuration that contains **hostname**, **client ID** and **secret** arguments (hereafter placeholders prefixed with "my" will be used instead of real values):

```python
>>> from pybitrix24 import Bitrix24
>>> bx24 = Bitrix24('my-subdomain.bitrix24.com', 'my.client.id', 'MyClientSecret')
```

Now is the time to authorize.

Bitrix24 uses [OAuth2](https://training.bitrix24.com/rest_help/oauth/authentication.php) and [authorization code grant](https://tools.ietf.org/html/rfc6749#section-1.3.1) for authorization of applications. It means that account owner's credentials are hidden from developers for security reasons, therefore, **it's not possible to obtain authorization code programmatically**. The account owner should be always present when access is granted.

However, to make life a bit simpler there is a helper method that builds an authorization URL for requesting an authorization code:

```python
>>> bx24.build_authorization_url()
'https://my-subdomain.bitrix24.com/oauth/authorize/?client_id=my.client.id&response_type=code'
```

Finally, when an authorization code is received both [access](https://tools.ietf.org/html/rfc6749#section-1.4) and [refresh tokens](https://tools.ietf.org/html/rfc6749#section-1.5) can be obtained: 

```python
>>> bx24.obtain_tokens('AnAuthorizationCode')
{'access_token': 'AnAccessToken', 'refresh_token': 'ARefreshToken', ...}
```

As it was mentioned earlier it's not possible to get the authorization code automatically but it's possible to refresh tokens after initial receiving to make the session longer (note that both **tokens have 1 hour lifetime** after that they'll be expired and an authorization code must be granted again):

```python
>>> bx24.refresh_tokens()
{'access_token': 'ANewAccessToken', 'refresh_token': 'ANewRefreshToken', ...}
```

Congratulations, all the preparatory work is done!

### Requesting resources with an access token

A further turn for requesting Bitrix24 resources. An access token injects automatically for all methods prefixed with `call_` that are mentioned in this section.

To make a **single call** (the `user` permission is required for the following example):

```python
>>> bx24.call('user.get', {'ID': 1})
{'result': {...}}
```

To make a **batch call** that is a few calls per request (the `user` and `department` permissions are required for the following example):

```python
>>> bx24.call_batch({
...     'get_user': ('user.current', {}), # or 'user.current'
...     'get_department': {
...         'method': 'department.get',
...         'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
...     }
... })
{'result': {'result': {...}}}
```

To **bind an event** (this method calls `event.bind` under the hood):

```python
>>> bx24.call_event_bind('OnAppUpdate', 'https://example.com/')
{'result': {...}}
```

To **unbind an event** (this method calls `event.unbind` under the hood):

```python
>>> bx24.call_event_unbind('OnAppUpdate', 'https://example.com/')
{'result': {...}}
```

### Requesting resources with a webhook code

Requesting resources with an authorization code is suitable for development of 3rd-party applications that are often quite cumbersome. However, sometimes it's enough to send a few simple calls. This is where webhooks come to action. 

If only webhooks are used the minimum required configuration is as simple as the following:

```python
>>> from pybitrix24 import Bitrix24
>>> bx24 = Bitrix24('my-subdomain.bitrix24.com')
```

To make an **inbound webhook** call:

```python
>>> bx24.call_webhook('xxxxxxxxxxxxxxxx', 'user.get', {'ID': 1})
{'result': {...}}
```

To make a batch call of **inbound webhooks**:

```python
>>> bx24.call_batch_webhook('xxxxxxxxxxxxxxxx', {
...     'get_user': ('user.current', {}), # or 'user.current'
...     'get_department': {
...         'method': 'department.get',
...         'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
...     }
... })
{'result': {'result': {...}}}
```

That's the end of the quick introduction. Thanks!

For more details, please, [explore source code](pybitrix24/bitrix24.py) or [ask me](https://github.com/yarbshk/pybitrix24/issues/new). Good luck!

## Copyright and License
Copyright © 2017-2020 Yurii Rabeshko. Code released under the MIT license.
