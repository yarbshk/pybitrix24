import functools
import warnings

warnings.simplefilter('always', DeprecationWarning)


def deprecated(message):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning)
            func(*args, **kwargs)
        return wrapper
    return decorator
