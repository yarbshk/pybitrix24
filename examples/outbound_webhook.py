import os

from flask import Flask, request
from pybitrix24 import parse_qs_deep

# You can try out this script with your own credentials
HOSTNAME = os.environ.get('HOSTNAME')
APP_TOKEN = os.environ.get('APP_TOKEN')

app = Flask(__name__)


@app.route('/', methods=['POST'])  # expect a POST request only
def index():
    # Obtain request body as a string (Flask-specific stuff)
    req_body = request.get_data().decode('utf-8')

    # NOTE: There is no client for outbound requests due to the specifics of this type of integration
    # Use a helper function to deserialize the multidimensional x-www-form-urlencoded body
    form = parse_qs_deep(req_body)

    # Reject any request with an invalid application token
    if form.get('application_token') != APP_TOKEN:
        return "Invalid application token", 401

    # Your business logic starts here... In our case we just return back the serialized request body
    return form


if __name__ == '__main__':
    # WARN: The server must be visible on the Internet in order to receive a request!
    app.run(host='0.0.0.0')
