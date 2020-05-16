class PyBitrix24Error(Exception):
    pass


class PBx24RequestError(PyBitrix24Error):
    pass


class PBx24ArgumentError(PyBitrix24Error, ValueError):
    pass


class PBx24AttributeError(PyBitrix24Error, AttributeError):
    pass
