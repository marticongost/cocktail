"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Optional
from base64 import urlsafe_b64decode
from json import loads, dumps

import cherrypy

from cocktail.events import event_handler
from cocktail.controllers import Controller, Dispatcher
from .cache import Cache
from .cachestorage import CacheStorage
from .memorycachestorage import MemoryCacheStorage
from .cachekey import CacheKey
from .scope import whole_cache, Scope
from .exceptions import CacheKeyError

ENCODING = "utf-8"


class CacheController(Controller):

    __cache: Cache

    memory_limit: Optional[int] = None

    def __init__(self, storage: Optional[CacheStorage] = None):

        if storage is None:
            storage = MemoryCacheStorage()

        self.__cache = Cache(storage)

    def resolve(self, path: Dispatcher.PathProcessor) -> Controller:
        if len(path) >= 2 and path[0] == "keys":
            path.pop(0)
            key = str(urlsafe_b64decode(path.pop(0).encode(ENCODING)))
            return KeyController(self, key)
        else:
            return self

    @property
    def cache(self) -> Cache:
        return self.__cache

    @cherrypy.expose
    def clear(self):
        scope = loads(cherrypy.request.body.read())

        if scope is None:
            self.__cache.clear(scope = whole_cache)
        else:
            selectors = set()
            for selector in scope:
                if isinstance(selector, list):
                    selector = tuple(selector)
                selectors.add(selector)

            self.__cache.clear(scope = selectors)

    @event_handler
    def handle_before_request(e):
        cherrypy.response.headers["Content-Type"] = "application/json"

    @event_handler
    def handle_exception_raised(e):

        error = e.exception
        e.handled = True

        if isinstance(error, CacheKeyError):
            cherrypy.response.status = 404
        else:
            cherrypy.response.status = 500

        if cherrypy.request.method != "HEAD":
            cherrypy.response.body = [
                dumps({"error": error.__class__.__name__}).encode("utf-8")
            ]


class KeyController(Controller):

    server: CacheController
    cache: Cache
    key: CacheKey

    def __init__(self, server: CacheController, key: CacheKey):
        Controller.__init__(self)
        self.server = server
        self.cache = server.cache
        self.key = key

    def __call__(self):
        method = cherrypy.request.method

        if method == "HEAD":
            if self.cache.exists(self.key):
                return ""
            else:
                raise CacheKeyError(key)

        elif method == "GET":
            value, expiration, tags = self.cache.retrieve_with_metadata(self.key)
            return dumps({
                "value": value,
                "expiration": expiration,
                "tags": tags
            }).encode(ENCODING)

        elif method == "POST":
            record = loads(cherrypy.request.body.read())
            self.cache.store(
                self.key,
                record["value"],
                expiration = record.get("expiration"),
                tags = record.get("tags")
            )

        elif method == "DELETE":
            if not self.cache.discard(self.key):
                raise CacheKeyError(key)
            else:
                return dumps(True).encode(ENCODING)

    @cherrypy.expose
    def value(self):
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return self.cache.retrieve(self.key)

    @cherrypy.expose
    def expiration(self):
        method = cherrypy.request.method

        if method == "GET":
            return dumps(self.cache.get_expiration(self.key))
        elif method == "POST":
            expiration = loads(cherrypy.request.body.read())
            self.cache.set_expiration(self.key, expiration)
            return dumps(expiration)


if __name__ == "__main__":
    server = CacheController()
    server.cache.verbose = True

    cherrypy.quickstart(server, "/", {
        "/": {
            "request.dispatch": Dispatcher()
        }
    })

