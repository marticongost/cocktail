"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any

from pickle import dumps, loads
from base64 import encodebytes, decodebytes

from cocktail.modeling import overrides
from .cacheserializer import CacheSerializer


class PickleCacheSerializer(CacheSerializer):

    @overrides(CacheSerializer.serialize)
    def serialize(self, obj: Any) -> bytes:
        return dumps(obj)

    @overrides(CacheSerializer.unserialize)
    def unserialize(self, string: bytes) -> Any:
        return loads(string)


class Base64PickleCacheSerializer(PickleCacheSerializer):

    @overrides(PickleCacheSerializer.serialize)
    def serialize(self, obj: Any) -> bytes:
        return encodebytes(super().serialize(obj))

    @overrides(PickleCacheSerializer.unserialize)
    def unserialize(self, string: bytes) -> Any:
        return super().unserialize(decodebytes(string))

