import json

from bitrix24 import exceptions
from urllib.parse import urlencode


def resolve_response(response):
    try:
        result = json.loads(response.text)
    except AttributeError:
        result = None
    except TypeError:
        result = None
    return result


def prepare_batch(calls):
    commands = {}
    for name, call in calls.items():
        if isinstance(call, str):
            command = call
        elif isinstance(call, tuple):
            try:
                command = '{}?{}'.format(call[0], urlencode(call[1]))
            except IndexError:
                raise exceptions.BatchIndexError(name)
        elif isinstance(call, dict):
            try:
                command = '{}?{}'.format(call['method'], urlencode(call['params']))
            except KeyError:
                raise exceptions.BatchKeyError(name)
        else:
            if isinstance(call, list):
                raise exceptions.BatchInstanceError(name, [tuple])
            else:
                raise exceptions.BatchInstanceError(name, [str, tuple, dict])
        commands[name] = command
    return commands
