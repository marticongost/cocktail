"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Iterable, Optional, Set
from cocktail.modeling import GenericMethod, ListWrapper
from .utils import nearest_expiration, Expiration


@GenericMethod
def get_cache_dependencies(
        obj: Any,
        cache_part: Optional[str] = None) -> Iterable:

    if isinstance(obj, (list, tuple, set, ListWrapper)):
        for item in obj:
            yield item
    elif obj is not None:
        yield obj


@GenericMethod
def get_cache_tags(
        obj: Any,
        cache_part: Optional[str] = None) -> Iterable[str]:

    raise TypeError(
        "%r doesn't implement the cocktail.caching.get_cache_tags() "
        "generic method"
        % obj
    )


@get_cache_tags.implementation_for(str)
def get_cache_tags_for_string(
        obj: Any,
        cache_part: Optional[str] = None) -> Iterable[str]:

    tag = obj
    if cache_part:
        tag += "-" + cache_part

    yield tag


@GenericMethod
def get_cache_expiration(
        obj: Any,
        cache_part: Optional[str] = None) -> Optional[int]:

    raise TypeError(
        "%r doesn't implement the cocktail.caching.get_cache_expiration() "
        "generic method"
        % obj
    )


@get_cache_expiration.implementation_for(str)
def get_cache_expiration_for_string(
        obj: Any,
        cache_part: Optional[str] = None) -> Optional[int]:

    return None


class Invalidable:

    cache_tags: Set[str]
    cache_expiration: Optional[Expiration]

    def __init__(self):
        self.cache_tags = set()
        self.cache_expiration = None

    def update_cache_expiration(self, expiration: Optional[Expiration]):
        self.cache_expiration = nearest_expiration(
            self.cache_expiration,
            expiration
        )

    def depends_on(
            self,
            obj: Any,
            cache_part: Optional[str] = None):

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

