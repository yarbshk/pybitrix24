class BatchIndexError(IndexError):
    def __init__(self, id):
        err = (
            'The "' + id + '" call is out of range. '
            'Provide a pair of values.'
        )
        IndexError.__init__(self, err)


class BatchKeyError(KeyError):
    def __init__(self, id):
        err = (
            'The "' + id + '" call has omitted required keys. '
            'The following keys are required: method, params.'
        )
        KeyError.__init__(self, err)


class BatchInstanceError(ValueError):
    def __init__(self, id, instances):
        err = 'The "%s" call must be an instance of %s.' % (
            id,
            ','.join([i.__name__ for i in instances])
        )
        ValueError.__init__(self, err)
