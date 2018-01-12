# bitrix24-python3-client
A tiny Python3 client to make requests of Bitrix24 API.

## Requirements
Depends on the following packages (see `requirements.txt`):
- requests

## Installation
First of all install necessary dependencies (see above) and **bitrix24-python3-client** itself:

```bash
$ pip install bitrix24-python3-client
```

## Getting started

The client is tiny therefore it's **easy to use**. All what you need to start it's **domain name**, **client ID** and **client secret key** of your application (if you already have **access** and **refresh tokens** you can pass it as optional kwargs into the Bitrix24 client).  

First of all you need to **create Bitrix24 instance** to work with. Let's create it as follows (we will consider basic configuration without existing tokens):

```python
    # Import Bitrix24 client to work with
>>> from bitrix24 import Bitrix24
    # Create instance with basic configuration
>>> bx24 = Bitrix24('your-domain.bitrix24.com', 'your.client.id', 'your_client_secret')
```

Looks like not bad, but you can't do anything yet. You must fill out all required attributes of the Bitrix24 client. To do that we can **request it** directly from a Bitrix24 server (**or** pass as optional kwargs for the Bitrix24 client before creating an instance):  

```python
    # Get authorization URL to request authorization code via browser
>>> bx24.resolve_authorize_endpoint()
'https://your-domain.bitrix24.com/oauth/authorize/?client_id=your.client.id&response_type=code'
    # Request tokens to interact with Bitrix24 API
>>> bx24.request_tokens('requested_authorization_code')
```

You can **check if all's well** by following command which simply return dict of current tokens:

```python
    # Get current access and refresh tokens
>>> bx24.get_tokens()
{'access_token': 'requested_access_token', 'refresh_token': 'requested_refresh_token'}
```

**Pay attention!** Your tokens have 1 hour lifecycle by default therefore you may need to **refresh tokens** at the expiration of this time:

```python
    # Refresh current tokens (refresh token required)
>>> bx24.refresh_tokens()
    # Check whether old tokens was replaced
>>> bx24.get_tokens()
{'access_token': 'new_access_token', 'refresh_token': 'new_refresh_token'}
```

Okay, all the preparation works done and now we can **make API calls to a Bitrix24 server** (don't forget to check the `client_endpoint` attribute of the Bitrix24 client whether it exists).

Make a **single call**:

```python
    # The following example needs the `user` permission
>>> bx24.call_method('user.get', {'ID': 1})
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
>>> from bitrix24 import Bitrix24
    # Create instance with basic configuration
>>> bx24 = Bitrix24('your-domain.bitrix24.com', user_id=1)
```

Make a **webhook call**:

```python
    # You can pass a dict of params as third argument
>>> bx24.call_webhook('profile', 'xxxxxxxxxxxxxxxx')
{'result': {...}}
```


That's end of quick introduction. To learn details, **explore source code** (believe me those code is such simple as this client). Good luck!

## Status
The client is already ready to use (v0.3.3).

I'll probably add more functionality later. This is what I need right now.

## Copyright and License
Copyright (c) 2017-2018 Yuriy Rabeshko. Code released under the MIT license.
