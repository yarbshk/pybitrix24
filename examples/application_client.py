import os

from flask import Flask, request, redirect

from pybitrix24 import ApplicationClient

HOSTNAME = os.environ.get('HOSTNAME')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

app = Flask(__name__)
app.pb24 = ApplicationClient(HOSTNAME, CLIENT_ID, CLIENT_SECRET)


@app.route('/')
def index():
    return redirect(app.pb24.get_auth_url())


@app.route('/handler')
def handler():
    code = request.args.get('code')
    if code is not None:
        app.pb24.get_auth(code)
    return app.pb24.call("profile")


if __name__ == '__main__':
    app.run()
