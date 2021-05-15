import json
from abc import abstractmethod, abstractproperty
from collections import namedtuple

from .backcomp.abc_ import ABC

# Concise enum replacement for Python 2
SerializationFormat = namedtuple('SerializationFormat', ['JSON', 'XML'])('json', 'xml')


class BaseSerializer(ABC):
    @abstractproperty
    def format(self):
        raise NotImplementedError("format() must be implemented")

    @abstractmethod
    def serialize(self, obj):
        raise NotImplementedError("serialize(obj) must be implemented")

    @abstractmethod
    def deserialize(self, s):
        raise NotImplementedError("deserialize(s) must be implemented")


class JsonSerializer(BaseSerializer):
    @property
    def format(self):
        return SerializationFormat.JSON

    def serialize(self, obj):
        return json.dumps(obj)

    def deserialize(self, s):
        return json.loads(s)

# TODO: Add XML serializer if needed
