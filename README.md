# pybitrix24
The simplest zero dependency polyversion Python library for calling Bitrix24 REST API.

## Features
- **Polyversion.** Supported Python versions: 2.7, 3.5+.
- **Zero dependency.** It is fast, lightweight and secure.
- **Just simple.** Examples of usage and clear sources.

## Getting started
Install the library using [pip](https://pip.pypa.io/en/stable/):

```bash
$ pip install pybitrix24
```

### Inbound webhook
This is definitely the easiest and fastest way to get started.

This type of integration allows creating **autonomous scripts**.

An instance of `InboundWebhookClient` must be created in order to make inbound webhooks. The client requires only a _hostname_ ofthe Bitrix24 portal, and an _authorization code_ (previously generated on the Bitrix24 portal in the section: Market > Developer resources > Other > Inbound webhook) in order to start making requests to Bitrix24:
```python
>>> from pybitrix24 import InboundWebhookClient
>>> b24 = InboundWebhookClient('b24-xxxxxx.bitrix24.com', 'xxxxxxxxxxxxxxxx')
```

An example of making a single query:
```python
>>> b24.call('user.get', {'ID': 1})
{'result': ...}
```

An example of making a batch query:
```python
>>> b24.call_batch({
...     'get_user': ('user.current', {}), # or 'user.current'
...     'get_department': {
...         'method': 'department.get',
...         'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
...     }
... })
{'result': ...}
```

An example of [a simple autonomous script](examples/inbound_webhook.py).

### Outbound webhook

### Local application
This type of integrations allows creating **marketplace applications**. Since a local application is a 3rd party application actually, its [authorization flow](https://training.bitrix24.com/rest_help/oauth/authentication.php) implements [the OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749) with [authorization code grant](https://tools.ietf.org/html/rfc6749#section-4.1). Consequently, a local application is NOT suitable for making autonomous scripts, and it requires a few additional steps in order to get authorization (access token).   

First, configure an instance of the client for local applications to be able to make requests to Bitrix24 API easily. To do so, import the appropriate client class from the `pybitrix24` module and pass it a _hostname_ of the Bitrix24 portal and both _client ID_ and _client secret_ (previously generated on the Bitrix24 portal in the section: Market > Developer resources > Other > Local application):
```python
>>> from pybitrix24 import LocalApplicationClient
>>> b24 = LocalApplicationClient('b24-xxxxxx.bitrix24.com', 'local.xxxxxxxxxxxxxx.xxxxxxxx', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
```

It is necessary to get authorization (access token) first in order to gain access to Bitrix24 resources. This process is semi-automatic by design (please, see references above) therefore it requires a user to sign in.

To generate a sign in link automatically, the `get_auth_url` helper method can be used: 
```python
>>> b24.get_auth_url()
'https://b24-xxxxxx.bitrix24.com/oauth/authorize?client_id=local.xxxxxxxxxxxxxx.xxxxxxxx&response_type=code'
```

When you open the sign in link, Bitrix24 will ask for your credentials, if there is no session. Then if you are signed in successfully it will redirect you to your handler path. This request would contain a `code` query parameter. It is an authorization code. You can pass this code to the `get_auth` method in order to get authorization (access token) and hence the permission to access Bitrix24 resources:
```python
>>> b24.get_auth('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
{'access_token': ...}
```

The access token is cached per local application client instance in order to be set for each request automatically. However, it expires in a while (1 hour by default) but you can extend its lifetime by using the `refresh_auth` method every now and again.

After successful authorization you can make requests to Bitrix24 API as it is shown below.

An example of making a single query:
```python
>>> b24.call('user.get', {'ID': 1})
{'result': ...}
```

An example of making a batch query:
```python
>>> b24.call_batch({
...     'get_user': ('user.current', {}), # or 'user.current'
...     'get_department': {
...         'method': 'department.get',
...         'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
...     }
... })
{'result': ...}
```

An example of [a simple marketplace application](examples/local_application.py).

## Copyright and License
Copyright © 2017-2021 Yurii Rabeshko. Code released under the MIT license.
