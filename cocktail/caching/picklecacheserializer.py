#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cPickle import dumps, loads
from base64 import encodestring, decodestring
from cocktail.modeling import overrides
from .cacheserializer import CacheSerializer


class PickleCacheSerializer(CacheSerializer):

    @overrides(CacheSerializer.serialize)
    def serialize(self, obj):
        return dumps(obj)

    @overrides(CacheSerializer.unserialize)
    def unserialize(self, string):
        return loads(string)


class Base64PickleCacheSerializer(PickleCacheSerializer):

    @overrides(PickleCacheSerializer.serialize)
    def serialize(self, obj):
        return encodestring(PickleCacheSerializer.serialize(self, obj))

    @overrides(PickleCacheSerializer.unserialize)
    def unserialize(self, string):
        return PickleCacheSerializer.unserialize(self, decodestring(string))

