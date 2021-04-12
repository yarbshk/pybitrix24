import os

from flask import Flask, request
from pybitrix24 import parse_qs_deep

HOSTNAME = os.environ.get('HOSTNAME')
APP_TOKEN = os.environ.get('APP_TOKEN')

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    req_body = request.get_data().decode('utf-8')
    form = parse_qs_deep(req_body)
    if form.get('application_token') != APP_TOKEN:
        return "Invalid application token", 401
    return form


if __name__ == '__main__':
    app.run(host='0.0.0.0')
