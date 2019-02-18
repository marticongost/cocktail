#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from types import GeneratorType
from time import time
import cherrypy
from cherrypy.lib import cptools
from cocktail.caching import CacheKeyError, Invalidable
from cocktail.controllers import request_property, get_request_url


class Cached(object):
    """A mixin for controllers with cached responses."""

    cache = None
    cache_enabled = True
    server_side_cache_enabled = True
    cached_headers = (
        "Content-Type",
        "Content-Length",
        "Content-Disposition",
        "Content-Encoding",
        "Last-Modified",
        "ETag"
    )

    def __call__(self, **kwargs):

        cherrypy.response.headers["Cache-Control"] = "no-cache"
        content = self._apply_cache(**kwargs)

        if content is None:
            content = self._produce_content(**kwargs)

        return content

    @request_property
    def invalidation(self):
        return Invalidable()

    @request_property
    def response_uses_cache(self):
        return (
            self.cache_enabled
            and self.cache
            and self.cache.enabled
            and self.cache.storage
            and cherrypy.request.method == "GET"
        )

    @request_property
    def response_uses_server_side_cache(self):
        return self.server_side_cache_enabled

    @request_property
    def cache_key(self):
        return str(get_request_url())

    @request_property
    def caching_context(self):
        return {
            "request": cherrypy.request,
            "controller": self
        }

    def _apply_cache(self, **kwargs):

        response_headers = cherrypy.response.headers

        if not self.response_uses_cache:
            return None

        cache_key = self.cache_key

        # Look for a cached response
        try:
            content, headers, gen_time = self.cache.retrieve(cache_key)
        except CacheKeyError:
            content = None
            headers = None
            gen_time = time()
        else:
            if self.response_uses_server_side_cache:
                if headers:
                    response_headers.update(headers)
            else:
                # Server-side caching disabled, we only care about generation
                # time to valide the ETag
                content = None
                headers = None

        response_headers["ETag"] = str(gen_time)

        if not self.response_uses_server_side_cache:
            cptools.validate_etags()

        if content is None:
            content = self.__produce_response(**kwargs)
            invalidation = self.invalidation

            # Store content in the server side cache
            if self.response_uses_server_side_cache:

                cache_entry_content = content

                # Collect headers that should be included in the cache
                cache_entry_headers = {}

                for header_name in self.cached_headers:
                    header_value = response_headers.get(header_name)
                    if header_value:
                        cache_entry_headers[header_name] = header_value
            else:
                cache_entry_headers = None
                cache_entry_content = None

            # Store the response in the cache
            self.cache.store(
                cache_key,
                (cache_entry_content, cache_entry_headers, gen_time),
                expiration = invalidation.cache_expiration,
                tags = invalidation.cache_tags
            )

        if self.response_uses_server_side_cache:
            cptools.validate_etags()

        return content

    def __produce_response(self, **kwargs):
        content = self._produce_content(**kwargs)

        if isinstance(content, GeneratorType):
            content_bytes = "".join(
                chunk.encode("utf-8")
                    if isinstance(chunk, bytes)
                    else chunk
                for chunk in content
            )
        elif isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content

        return content_bytes

    def _produce_content(self, **kwargs):
        raise TypeError(
            "%r doesn't implement the _produce_content() method"
            % self
        )

