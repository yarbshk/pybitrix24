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

Integrate the client with your project:

```python
>>> from bitrix24 import Bitrix24
    # Create instance with basic configuration
>>> bx24 = Bitrix24('your-domain.bitrix24.com', 'your.client.id', 'your_client_secret')
    # Get authorization URL to request authorization code via browser
>>> bx24.get_authorize_endpoint()
'https://your-domain.bitrix24.com/oauth/authorize/?client_id=your.client.id&response_type=code'
    # Request tokens to interact with Bitrix24 API
>>> bx24.request_tokens('requested_authorization_code')
    # Output current access and refresh tokens
>>> bx24.get_tokens()
{'access_token': 'requested_access_token', 'refresh_token': 'requested_refresh_token'}
    # Call a method (the following example needs the `user` permission)
>>> bx24.call_method('user.get', {'ID': 1})
```

## Status
The client is passing the **beta testing** stage.

I'll probably add more functionality later. This is what I need right now.

## Copyright and License
Copyright (c) 2017 Yuriy Rabeshko. Code released under the MIT license.
