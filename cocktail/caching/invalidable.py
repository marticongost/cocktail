#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import GenericMethod, ListWrapper
from .utils import nearest_expiration

@GenericMethod
def get_cache_dependencies(obj, cache_part = None):
    if isinstance(obj, (list, tuple, set, ListWrapper)):
        for item in obj:
            yield item
    elif obj is not None:
        yield obj

@GenericMethod
def get_cache_tags(obj, cache_part = None):
    raise TypeError(
        "%r doesn't implement the cocktail.caching.get_cache_tags() "
        "generic method"
        % obj
    )

@get_cache_tags.implementation_for(basestring)
def get_cache_tags_for_string(obj, cache_part = None):
    tag = obj
    if cache_part:
        tag += "-" + cache_part
    yield tag

@GenericMethod
def get_cache_expiration(obj, cache_part = None):
    raise TypeError(
        "%r doesn't implement the cocktail.caching.get_cache_expiration() "
        "generic method"
        % obj
    )

@get_cache_expiration.implementation_for(basestring)
def get_cache_expiration_for_string(obj, cache_part = None):
    return None


class Invalidable(object):

    def __init__(self):
        self.cache_tags = set()
        self.cache_expiration = None

    def update_cache_expiration(self, expiration):
        self.cache_expiration = nearest_expiration(
            self.cache_expiration,
            expiration
        )

    def depends_on(self, obj, cache_part = None):
        for dependency in get_cache_dependencies(obj, cache_part = cache_part):
            tags = get_cache_tags(
                dependency,
                cache_part = cache_part
            )
            expiration = get_cache_expiration(
                dependency,
                cache_part = cache_part
            )
            self.cache_tags.update(tags)
            self.update_cache_expiration(expiration)

