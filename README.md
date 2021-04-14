# pybitrix24
The simplest zero dependency polyversion Python library for Bitrix24 REST API.

## Features
- **Polyversion.** Supported Python versions: 2.7, 3.5+.
- **Zero dependency.** It's fast, lightweight and secure.
- **Reliable.** Test coverage is more than 80%.
- **Just simple.** Examples of usage and clear sources.

## Installation
Install using [pip](https://pip.pypa.io/en/stable/):

```bash
$ pip install pybitrix24
```

## Getting started

### Inbound webhook
This is definitely the easiest and fastest way to get started.

This type of integration allows creating **automated scripts**. An instance of `InboundWebhookClient` must be created in order to make inbound webhooks. The client requires only a _hostname_ of your portal, and an _authorization code_ (previously generated on Bitrix24 website in the section: Market > Developer resources > Other > Inbound webhook) in order to start making requests to Bitrix24:
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

An example of [a simple automated script](examples/inbound_webhook.py).

### Outbound webhook
### Local application

## Copyright and License
Copyright © 2017-2021 Yurii Rabeshko. Code released under the MIT license.
