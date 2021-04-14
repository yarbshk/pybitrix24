import os

from flask import Flask, request, redirect

from pybitrix24 import LocalApplicationClient

# You can try out this script with your own credentials
HOSTNAME = os.environ.get('HOSTNAME')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

app = Flask(__name__)

# Instantiate a client that is designed for local applications
app.b24 = LocalApplicationClient(HOSTNAME, CLIENT_ID, CLIENT_SECRET)


@app.route('/')
def index():
    # Sign in to obtain an authorization code.
    # After user is signed in successfully the request will be redirected to the handler (see below)
    return redirect(app.b24.get_auth_url())


@app.route('/handler')
def handler():
    # Obtain the authorization code from the query string if any
    auth_code = request.args.get('code')

    # Fetch authorization (access token) by the authorization code
    if auth_code is not None:
        app.b24.get_auth(auth_code)

    # Your business logic starts here... In our case we just return the profile info
    return app.b24.call("profile")


if __name__ == '__main__':
    app.run()
