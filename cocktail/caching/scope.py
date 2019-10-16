"""

.. attribute:: whole_cache

    Used when specifying the scope for a cache invalidation operation to
    indicate that the whole cache should be cleared.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterable, Union

from cocktail.modeling import (
    OrderedSet,
    ListWrapper,
    SetWrapper
)


class WholeCache:
    pass


whole_cache = WholeCache()

ScopeSelector = Union[str, Iterable[str]]
Scope = Union[WholeCache, Iterable[ScopeSelector]]


def normalize_scope(scope: Scope) -> Scope:
    if scope is whole_cache:
        return whole_cache
    else:
        return set(selector for selector in resolve_selector(scope))


def resolve_selector(selector: ScopeSelector) -> Iterable[ScopeSelector]:

    if isinstance(selector, (str, tuple)):
        yield selector
    elif isinstance(selector, (
        list,
        set,
        frozenset,
        OrderedSet,
        ListWrapper,
        SetWrapper
    )):
        for selector_part in selector:
            for resolved_selector in resolve_selector(selector_part):
                yield resolved_selector
    else:
        raise TypeError(
            "Scope selectors must be strings, tuples or collections, got %r "
            "instead."
            % selector
        )

