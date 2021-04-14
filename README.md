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

An instance of `InboundWebhookClient` must be created in order to make inbound webhooks. The client requires only a _hostname_ of your portal, and an _authorization code_ (previously generated on Bitrix24 website in the section: Market > Developer resources > Other > Inbound webhook) in order to start making requests to Bitrix24:
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
This type of integrations allows creating **marketplace applications**. It involves some user interaction by [design](https://tools.ietf.org/html/rfc6749#section-1.3.1) therefore it is NOT suitable for making autonomous scripts. 

## Copyright and License
Copyright © 2017-2021 Yurii Rabeshko. Code released under the MIT license.
