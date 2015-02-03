#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from sys import getsizeof
from time import time
from threading import RLock
from cocktail.modeling import overrides
from cocktail.styled import styled
from cocktail.memoryutils import parse_bytes, format_bytes
from .scope import whole_cache, normalize_scope
from .cachestorage import CacheStorage
from .exceptions import CacheKeyError


class MemoryCacheStorage(CacheStorage):
    """A cache backend that stores data on a Python dictionary."""

    __memory_limit = None
    __memory_usage = 0
    verbose_invalidation = False
    verbose_memory_usage = False

    def __init__(self):
        self.__lock = RLock()
        self.__dict = {}
        self.__oldest_entry = None
        self.__newest_entry = None
        self.__entries_by_tag = {}

    @property
    def memory_usage(self):
        return (
            self.__memory_usage
            + getsizeof(self)
            + getsizeof(self.__dict)
            + getsizeof(self.__entries_by_tag)
        )

    def _get_memory_limit(self):
        return self.__memory_limit

    def _set_memory_limit(self, memory_limit):

        if isinstance(memory_limit, basestring):
            memory_limit = parse_bytes(memory_limit)

        reducing_size = memory_limit and (
            not self.__memory_limit
            or memory_limit < self.__memory_limit
        )

        self.__memory_limit = memory_limit

        if reducing_size:
            self._apply_memory_limit()

    memory_limit = property(
        _get_memory_limit,
        _set_memory_limit,
        doc = """
        Gets or sets the maximum memory allowance for cached content.

        The memory limit is expressed as a number of bytes. The size of each
        entry is measured by the `._get_entry_memory_usage` method, and its
        cumulative sum is accessible through the `.memory_usage` property.
        """
    )

    def _exceeds_memory_limit(self):
        return self.__memory_limit and self.memory_usage > self.__memory_limit

    def _apply_memory_limit(self):
        # Drop entries until the cache conforms to the memory limit, or until
        # there is none left to drop.
        while self._exceeds_memory_limit() and self.drop_weight():
            pass

    def _get_entry_memory_usage(self, entry):
        return (
              getsizeof(entry)
            + getsizeof(entry.key)
            + getsizeof(entry.expiration)
            + getsizeof(entry.tags)
            + self._get_value_memory_usage(entry.value)
        )

    def _get_value_memory_usage(self, value):
        return getsizeof(value)

    memory_usage_bar_width = 50

    memory_usage_colors = [
        (90, "red"),
        (70, "brown"),
        (50, "yellow"),
        (0, "green")
    ]

    def print_memory_usage(self):

        if self.memory_limit:
            usage = self.memory_usage
            limit = self.memory_limit
            ratio = usage / limit
            percent = int(ratio * 100)

            bar = (
                "%s / %s" % (
                    format_bytes(usage),
                    format_bytes(limit)
                )
            ).rjust(self.memory_usage_bar_width)

            for threshold, bar_color in self.memory_usage_colors:
                if percent >= threshold:
                    break

            bar_width = int(ratio * self.memory_usage_bar_width)

            info = (
                styled(bar[:bar_width], "white", bar_color)
              + styled(bar[bar_width:], "white", "dark_gray")
            )
        else:
            info = format_bytes(self.memory_usage)

        print "Memory usage: %s\n" % info

    def __require_entry(self, key):
        with self.__lock:
            entry = self.__dict.get(key)

            # Missing key
            if entry is None:
                raise CacheKeyError(key)

            # Expired key
            expiration = entry.expiration
            if expiration is not None and expiration <= time():
                self.__remove_entry(entry)
                raise CacheKeyError(key)

            return entry

    def __remove_entry(self, entry):

        if self.verbose_invalidation:
            print styled("  " + entry.key, "red")

        self.__memory_usage -= entry.size

        if self.verbose_memory_usage:
            self.print_memory_usage()

        del self.__dict[entry.key]
        self.__release(entry)

        if entry.tags:
            for tag in entry.tags:
                tag_entries = self.__entries_by_tag.get(tag)
                if tag_entries is not None:
                    tag_entries.remove(entry)

        entry.key = None
        entry.expiration = None
        entry.tags = None
        entry.size = None

    def __release(self, entry):
        if entry is self.__oldest_entry:
            self.__oldest_entry = entry.next_entry

        if entry is self.__newest_entry:
            self.__newest_entry = entry.prev_entry

        if entry.prev_entry:
            entry.prev_entry.next_entry = entry.next_entry

        if entry.next_entry:
            entry.next_entry.prev_entry = entry.prev_entry

        entry.prev_entry = None
        entry.next_entry = None

    def __update_last_access(self, entry):

        if entry is self.__newest_entry:
            return

        self.__release(entry)

        if self.__oldest_entry is None:
            self.__oldest_entry = entry

        if self.__newest_entry:
            self.__newest_entry.next_entry = entry
            entry.prev_entry = self.__newest_entry

        self.__newest_entry = entry

    @overrides(CacheStorage.exists)
    def exists(self, key):
        with self.__lock:
            return self.__require_entry(key) is not None

    @overrides(CacheStorage.retrieve)
    def retrieve(self, key):
        with self.__lock:
            entry = self.__require_entry(key)
            self.__update_last_access(entry)
            return entry.value

    @overrides(CacheStorage.retrieve_with_metadata)
    def retrieve_with_metadata(self, key):
        with self.__lock:
            entry = self.__require_entry(key)
            self.__update_last_access(entry)
            return (entry.value, entry.expiration, entry.tags)

    @overrides(CacheStorage.store)
    def store(self, key, value, expiration = None, tags = None):
        with self.__lock:
            try:
                self.remove(key)
            except CacheKeyError:
                pass

            entry = Entry(key, value, expiration, tags)
            entry.size = self._get_entry_memory_usage(entry)
            self.__memory_usage += entry.size
            self.__dict[key] = entry
            self.__update_last_access(entry)

            if tags is not None:
                for tag in tags:
                    tag_entries = self.__entries_by_tag.get(tag)
                    if tag_entries is None:
                        self.__entries_by_tag[tag] = tag_entries = set()
                    tag_entries.add(entry)

            if self.verbose_memory_usage:
                self.print_memory_usage()

            self._apply_memory_limit()

    @overrides(CacheStorage.get_expiration)
    def get_expiration(self, key):
        return self.__require_entry(key).expiration

    @overrides(CacheStorage.set_expiration)
    def set_expiration(self, key, expiration):
        with self.__lock:
            entry = self.__require_entry(key)
            entry.expiration = expiration
            self.__update_last_access(entry)

    @overrides(CacheStorage.discard)
    def discard(self, key):
        with self.__lock:
            try:
                entry = self.__require_entry(key)
            except CacheKeyError:
                return False

            self.__remove_entry(entry)

        return True

    @overrides(CacheStorage.clear)
    def clear(self, scope = whole_cache):
        with self.__lock:

            # Clear the whole cache
            if scope is whole_cache:
                self.__dict.clear()
                self.__entries_by_tag.clear()

            # Clear parts of the cache
            else:
                entries_to_remove = set()

                for selector in scope:

                    # Strings select a single tag
                    if isinstance(selector, basestring):
                        selector_entries = self.__entries_by_tag.get(selector)

                    # Tuples of strings select the intersection of multiple
                    # tags
                    elif isinstance(selector, tuple):
                        selector_entries = None
                        for tag in selector:
                            tag_entries = self.__entries_by_tag.get(tag)
                            if not tag_entries:
                                selector_entries = None
                                break
                            elif selector_entries is None:
                                selector_entries = set(tag_entries)
                            else:
                                selector_entries.intersection_update(tag_entries)
                    else:
                        raise TypeError(
                            "Scope selectors should be strings or tuples of "
                            "strings; got %r instead" % selector
                        )

                    if selector_entries:
                        entries_to_remove.update(selector_entries)

                for entry in entries_to_remove:
                    self.__remove_entry(entry)

    def drop_weight(self):
        with self.__lock:
            if self.__oldest_entry:
                key = self.__oldest_entry.key
                self.__remove_entry(self.__oldest_entry)
                return key


class Entry(object):

    size = 0

    def __init__(self, key, value, expiration, tags):
        self.key = key
        self.value = value
        self.expiration = expiration
        self.tags = tags
        self.prev_entry = None
        self.next_entry = None

