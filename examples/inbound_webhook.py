import os

from pybitrix24 import InboundWebhookClient

HOSTNAME = os.environ.get('HOSTNAME')
AUTH_CODE = os.environ.get('AUTH_CODE')


def main():
    bx24 = InboundWebhookClient(HOSTNAME, AUTH_CODE)
    print(bx24.call("profile"))


if __name__ == '__main__':
    main()
