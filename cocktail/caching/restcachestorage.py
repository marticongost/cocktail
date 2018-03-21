#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from httplib2 import Http
from base64 import urlsafe_b64encode
from simplejson import loads, dumps
from cocktail.modeling import overrides
from .exceptions import CacheKeyError
from .cachestorage import CacheStorage
from .picklecacheserializer import Base64PickleCacheSerializer
from .scope import whole_cache


class RESTCacheStorage(object):

    def __init__(self, address, serializer = None):

        self.__address = address.rstrip("/")

        if serializer is None:
            serializer = Base64PickleCacheSerializer()

        self.__serializer = serializer

    @property
    def address(self):
        return self.__address

    @property
    def serializer(self):
        return self.__serializer

    def _key_request(self, key, *args, **kwargs):

        url = self.__address + "/keys/" + urlsafe_b64encode(key)

        extra_path = kwargs.pop("extra_path", None)
        if extra_path:
            url += "/" + extra_path

        http = Http()
        response, content = http.request(url, *args, **kwargs)

        if (400 <= response.status < 500):
            raise CacheKeyError(key)

        if content and response.get("content-type") == "application/json":
            content = loads(content)

        return content

    @overrides(CacheStorage.exists)
    def exists(self, key):
        try:
            self._key_request(key, "HEAD")
        except CacheKeyError:
            return False
        else:
            return True

    @overrides(CacheStorage.retrieve)
    def retrieve(self, key):
        value = self._key_request(key, "GET", extra_path = "value")
        return self.serializer.unserialize(value)

    @overrides(CacheStorage.retrieve_with_metadata)
    def retrieve_with_metadata(self, key):
        data = self._key_request(key, "GET")
        return (
            self.serializer.unserialize(data["value"]),
            data["expiration"],
            data["tags"]
        )

    @overrides(CacheStorage.store)
    def store(self, key, value, expiration = None, tags = None):
        self._key_request(
            key,
            "POST",
            headers = {
                "Content-Type": "application/json"
            },
            body = dumps({
                "value": self.__serializer.serialize(value),
                "expiration": expiration,
                "tags": None if tags is None else list(tags)
            })
        )

    @overrides(CacheStorage.get_expiration)
    def get_expiration(self, key):
        return self._key_request(key, "GET", extra_path = "expiration")

    @overrides(CacheStorage.set_expiration)
    def set_expiration(self, key, expiration):
        self._key_request(
            key + "/expiration",
            "POST",
            headers = {
                "Content-Type": "application/json"
            },
            body = dumps(expiration)
        )

    @overrides(CacheStorage.discard)
    def discard(self, key):
        try:
            self._key_request(key, "DELETE")
        except CacheKeyError:
            return False
        else:
            return True

    @overrides(CacheStorage.clear)
    def clear(self, scope = whole_cache):
        url = self.__address + "/clear"
        http = Http()
        response, content = http.request(
            url,
            "POST",
            headers = {
                "Content-Type": "application/json"
            },
            body = dumps(
                None if scope is whole_cache
                else list(scope)
            )
        )

