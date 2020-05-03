# pybitrix24
A tiny Python3 client to make requests of Bitrix24 API.

## Requirements
Depends on the following packages (see `requirements.txt`):
- requests

## Installation
Install the library using pip:

```bash
$ pip install pybitrix24
```

## Getting started

The client is tiny therefore it's **easy to use**. All what you need to start it's **domain name**, **client ID** and **client secret key** of your application (if you already have **access** and **refresh tokens** you can pass it as optional kwargs into the Bitrix24 client).  

First of all you need to **create Bitrix24 instance** to work with. Let's create it as follows (we will consider basic configuration without existing tokens):

```python
    # Import Bitrix24 client to work with
>>> from pybitrix24 import Bitrix24
    # Create instance with basic configuration
>>> bx24 = Bitrix24('your-hostname.bitrix24.com', 'your.client.id', 'YourClientSecret')
```

Looks like not bad, but you can't do anything yet. You must fill out all required attributes of the Bitrix24 client. To do that we can **request it** directly from a Bitrix24 server (**or** pass as optional kwargs for the Bitrix24 client before creating an instance):  

```python
    # Get authorization URL to request authorization code manually via browser
>>> bx24.build_authorization_url()
'https://your-hostname.bitrix24.com/oauth/authorize/?client_id=your.client.id&response_type=code'
    # Request tokens to interact with Bitrix24 API
>>> bx24.obtain_tokens('ObtainedAuthorizationCode')
{'access_token': 'SomeAccessToken', 'refresh_token': 'SomeRefreshToken', ...}
```

**Pay attention!** Your tokens have 1 hour lifecycle by default therefore you may need to **refresh tokens** at the expiration of this time:

```python
    # Refresh current tokens (refresh token required)
>>> bx24.refresh_tokens()
{'access_token': 'NewAccessToken', 'refresh_token': 'NewRefreshToken', ...}
```

Okay, all the preparation works done and now we can **make API calls to a Bitrix24 server** (don't forget to check the `client_endpoint` attribute of the Bitrix24 client whether it exists).

Make a **single call**:

```python
    # The following example needs the `user` permission
>>> bx24.call('user.get', {'ID': 1})
{'result': {...}}
```

Make a **batch call** (many single calls by one request):

```python
    # The following example needs the `user` and `department` permissions
>>> bx24.call_batch({
...     'get_user': ('user.current', {}), # or 'user.current'
...     'get_department': {
...         'method': 'department.get',
...         'params': {'ID': '$result[get_user][UF_DEPARTMENT]'}
...     }
... })
{'result': {'result': {...}}}
```

Make an **event binding** (shortcut for the `event.bind` method):

```python
>>> bx24.call_bind('OnAppUpdate', 'https://example.com/')
{'result': {...}}
```

Make an **event unbinding** (shortcut for the `event.unbind` method):

```python
>>> bx24.call_unbind('OnAppUpdate', 'https://example.com/')
{'result': {...}}
```

#### Get closer to webhooks

All methods described above come in handy when you develop applications or similar tricky things. However, sometimes will be enough to call a **webhook** - simplified version of rest-events and rest-teams that does not require a application to write.

So, let's create a simple webhook!

If you need to make webhook calls **only**, the following configuration will fit (in other case see verbose configuration above):

```python
    # Import Bitrix24 client to work with
>>> from pybitrix24 import Bitrix24
    # Create instance with basic configuration
>>> bx24 = Bitrix24('your-hostname.bitrix24.com', user_id=3)
```

Make a **webhook call**:

```python
    # You can pass a dict of params as third argument
>>> bx24.call_webhook('profile', 'xxxxxxxxxxxxxxxx')
{'result': {...}}
```

Make a **batch webhook call**:

```python
    # You can pass a dict of params as third argument
>>> bx24.call_batch_webhook({
...     'profile': 'xxxxxxxxxxxxxxxx',
... })
{'result': {'result': {...}}}
```

That's the end of quick introduction. To learn details, **explore source code** (believe me those code is such simple as this client). Good luck!

## Copyright and License
Copyright © 2017 Yurii Rabeshko. Code released under the MIT license.
