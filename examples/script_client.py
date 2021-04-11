import os

from pybitrix24 import ScriptClient

HOSTNAME = os.environ.get('HOSTNAME')
AUTH_CODE = os.environ.get('AUTH_CODE')


def main():
    pb24 = ScriptClient(HOSTNAME, AUTH_CODE)
    print(pb24.call("profile"))


if __name__ == '__main__':
    main()
