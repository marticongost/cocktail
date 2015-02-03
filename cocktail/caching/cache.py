#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.styled import styled
from cocktail.modeling import OrderedSet, SetWrapper, ListWrapper, DictWrapper
from .utils import normalize_expiration
from .scope import whole_cache, normalize_scope
from .exceptions import CacheKeyError

TRANSACTION_KEY = "cocktail.cache.invalidation"


class Cache(object):
    """A cache frontend, with pluggable storage backends.

    .. attribute:: storage

        A storage backend, implementing all the IO operations required by the
        cache. It should be an instance of a subclass of
        `~cocktail.caching.CacheStorage`.

    .. attribute:: enabled

        A boolean value that indicates if entries should be stored in the
        cache. True by default; setting it to False will ignore all caching
        requests.

    .. attribute:: verbose

        Set to ``True`` to print debugging information for each operation on
        the cache.

    """
    enabled = True
    verbose = False

    def __init__(self, storage = None):
        """Initializes the cache.

        :param storage: Sets the `.storage` to be used by the cache.
        """
        self.storage = storage

    def exists(self, key):
        """Indicates if the given key is defined and current.

        The method will query the cache's `.storage`, looking for a registered
        key that hasn't expired yet.

        :param key: The key to check.
        :return: True if the storage contains the key and the key is current
            (or has no expiration date set). False in any other case.
        """
        if not self.enabled or self.storage is None:
            return False

        norm_key = self.normalize_key(key)
        return self.storage.has_key(norm_key)

    def retrieve(self, key):
        """Obtains the value stored for the given key.

        :param key: The key to retrieve.
        :return: The value associated with the indicated key.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            present in the `.storage` for the cache, or if it has expired.
        """
        if not self.enabled or self.storage is None:
            raise CacheKeyError(key)

        norm_key = self.normalize_key(key)

        if self.verbose:
            try:
                value = self.storage.retrieve(norm_key)
            except CacheKeyError:
                print (
                    styled("CACHE", "white", "dark_gray")
                    + " " + styled("Miss", "red", style = "bold") + "\n"
                    + styled("  Key:", "light_gray", style = "bold")
                    + " " + norm_key + "\n"
                )
                raise
            else:
                print (
                    styled("CACHE", "white", "dark_gray")
                    + " " + styled("Hit", "bright_green", style = "bold") + "\n"
                    + styled("  Key:", "light_gray", style = "bold")
                    + " " + norm_key + "\n"
                )
                return value
        else:
            return self.storage.retrieve(norm_key)

    def retrieve_with_metadata(self, key):
        """Obtains the value, expiration and tags for the given key.

        :param key: The key to retrieve.
        :return: A tuple containing the value, expiration and tags associated
            with the indicated key.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            present in the `.storage` for the cache, or if it has expired.
        """
        if not self.enabled or self.storage is None:
            raise CacheKeyError(key)

        norm_key = self.normalize_key(key)

        if self.verbose:
            try:
                value = self.storage.retrieve_with_metadata(norm_key)
            except CacheKeyError:
                print (
                    styled("CACHE", "white", "dark_gray")
                    + " " + styled("Miss", "red", style = "bold") + "\n"
                    + styled("  Key:", "light_gray", style = "bold")
                    + " " + norm_key + "\n"
                )
                raise
            else:
                print (
                    styled("CACHE", "white", "dark_gray")
                    + " " + styled("Hit", "bright_green", style = "bold") + "\n"
                    + styled("  Key:", "light_gray", style = "bold")
                    + " " + norm_key + "\n"
                )
                return value
        else:
            return self.storage.retrieve_with_metadata(norm_key)

    def store(self, key, value, expiration = None, tags = None):
        """Inserts or updates a value in the storage.

        If the key already existed, the given value, expiration and tags will
        be used to replace the old ones.

        :param key: A string that will uniquely identify the value in the
            cache, making it possible to `.retrieve` it later.
        :param value: The value to associate to this key.
        :param expiration: An optional parameter that limits the maximum
            life span of the key in the storage. See the
            `~cocktail.caching.utils.normalize_expiration` function for a
            detailed explanation of all the forms the parameter can take.
        :param tags: An optional set of tags to attach to this key. If given,
            it should be expressed as a collection of strings, each one
            representing a single tag.
        """
        if not self.enabled or self.storage is None:
            return

        norm_key = self.normalize_key(key)

        if self.verbose:
            lines = [
                styled("CACHE", "white", "dark_gray")
                + " " + styled("Storing", "slate_blue", style = "bold"),
                styled("  Key:", "light_gray", style = "bold") + " " + norm_key
            ]
            if expiration is not None:
                lines.append(
                    styled("  Expiration:", "light_gray", style = "bold")
                    + " " + str(expiration)
                )
            if tags is not None:
                lines.append(
                    styled("  Tags:", "light_gray", style = "bold")
                    + " " + str(sorted(tags))
                )
            lines.append("")
            print "\n".join(lines)

        if expiration is not None:
            expiration = normalize_expiration(expiration)

        self.storage.store(
            norm_key,
            value,
            expiration = expiration,
            tags = tags
        )

    def get_expiration(self, key):
        """Determines the expiration assigned to the given key.

        :return: An integer timestamp indicating the point in time at which the
            key will expire. If the key doesn't have an expiration date, the
            method will return ``None``.
        :raises cocktail.caching.CacheKeyError: if the key is not
            contained in the storage or has already expired.
        """
        if not self.enabled or self.storage is None:
            raise CacheKeyError(key)

        norm_key = self.normalize_key(key)
        return self.storage.get_expiration(norm_key)

    def set_expiration(self, key, expiration):
        """Sets the expiration assigned to the given key.

        :param key: The key to update the expiration for.
        :param expiration: The new expiration date for the key. Can be set to
            None to disable time based expiration for the key; otherwise, check
            the `~cocktail.caching.utils.normalize_expiration` function for all
            the possible ways of specifying the expiration date for the key.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            contained in the storage or has already expired.
        :raises ValueError: Raised if the given expiration key is not valid
            (ie. is not an integer timestamp, or is set in the past).
        """
        if not self.enabled or self.storage is None:
            raise CacheKeyError(key)

        norm_key = self.normalize_key(key)

        if self.verbose:
            print (
                styled("CACHE", "white", "dark_gray")
                + " " + styled("Set expiration", "pink", style = "bold") + "\n"
                + styled("  Key:", "light_gray", style = "bold")
                + " " + norm_key + "\n"
                + styled("  Expiration:", "light_gray", style = "bold")
                + " " + str(expiration) + "\n"
            )

        if expiration is not None:
            expiration = normalize_expiration(expiration)

        self.storage.set_expiration(norm_key, expiration)

    def remove(self, key):
        """Removes the given key from the cache, or fails.

        This method is similar to `.discard`, but it will raise an exception
        instead of returning False if the indicated key doesn't exist or has
        expired.

        :param key: The key to remove.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            contained in the storage, or has expired.
        """
        if not self.enabled or self.storage is None:
            raise CacheKeyError(key)

        norm_key = self.normalize_key(key)
        self.storage.remove(norm_key)

        if self.verbose:
            print styled("CACHE: REMOVE", "white", "magenta"), key

    def discard(self, key):
        """Removes the given key from the cache, if it exists.

        This method is similar to `.remove`, but it will return a boolean
        indicating wether the removal succeeded (`.remove` raises an exception
        if it can't find the requested key in the cache).

        :param key: The key to remove.
        :return: True if the key was removed from the cache, False if it
            wasn't contained on the cache, or if it had already expired.
        """
        if not self.enabled or self.storage is None:
            return False

        norm_key = self.normalize_key(key)

        if self.storage.discard(norm_key):
            if self.verbose:
                print (
                    styled("CACHE", "white", "dark_gray")
                    + " " + styled("Remove", "magenta", style = "bold") + "\n"
                    + styled("  Key:", "light_gray", style = "bold")
                    + " " + norm_key + "\n"
                )
            return True
        else:
            return False

    def clear(self, scope = whole_cache):
        """Discards all keys in the cache matching the given scope.

        :param scope: A selector indicating the keys that should be removed. It
            can take the following forms:

                - `~cocktail.caching.whole_cache` will remove all the entries
                  in the cache.
                - A string will be treated as a single tag, and will delete all
                  entries tagged with said tag.
                - A tuple of strings will be interpreted as an intersection of
                  tags: any entry tagged with *all* of the tags in the tuple
                  will be deleted.
                - Collections will be treated as a union of other selectors:
                  all entries matching *any* of the selectors in the collection
                  will be removed.

        :raises TypeError: Raised if the ``scope`` parameter is given a value
            of a wrong type.
        """
        if self.enabled and self.storage is not None:

            if self.verbose:
                print (
                    styled("CACHE", "white", "dark_gray")
                    + " " + styled("Clear", "magenta", style = "bold") + "\n"
                    + styled("  Scope:", "light_gray", style = "bold")
                    + " " + (
                        "whole cache" if scope is whole_cache else repr(scope)
                    ) + "\n"
                )

            self.storage.clear(scope = normalize_scope(scope))

    def clear_after_commit(self, scope = whole_cache):
        """Schedules a cache invalidation operation after the current ZODB
        transaction is committed.

        This method can be called multiple times per transaction, with each
        successive call widening the scope that will be affected once the
        transaction is completed. That said, if the scope is set to
        `~cocktail.caching.whole_cache`, the scope indicated by past or future
        invocations will be disregarded, and the whole cache will be cleared
        once the transaction is completed.

        :param scope: Determines the keys that will be removed once the
            transaction is completed. See the `.clear` method for details on
            its accepted formats.
        """
        if not self.enabled or self.storage is None or not scope:
            return

        key = (TRANSACTION_KEY, id(self))
        from cocktail.persistence import datastore
        transaction_invalidation_scope = datastore.get_transaction_value(key)

        if transaction_invalidation_scope is whole_cache:
            return
        elif transaction_invalidation_scope is None:
            datastore.unique_after_commit_hook(
                TRANSACTION_KEY,
                _cache_invalidation_commit_handler,
                self
            )

        scope = normalize_scope(scope)

        if transaction_invalidation_scope is None:
            datastore.set_transaction_value(key, scope)
        elif scope is whole_cache:
            datastore.set_transaction_value(key, scope)
        else:
            transaction_invalidation_scope.update(scope)

        if self.verbose:
            print (
                styled("CACHE", "white", "dark_gray")
                + " " + styled("Clear after commit", "magenta", style = "bold")
                + "\n"
                + styled("  Scope:", "light_gray", style = "bold")
                + " " + (
                    "whole cache" if scope is whole_cache else repr(scope)
                ) + "\n"
            )

    def drop_weight(self):
        """Removes an entry from the cache, in order to free resources.

        :return: The key that has been removed, or ``None`` if the cache is
            empty.
        """
        if not self.enabled or self.storage is None:
            return

        key = self.storage.drop_weight()

        if key and self.verbose:
            print (
                styled("CACHE", "white", "dark_gray")
                + " " + styled("Drop weight", "magenta", style = "bold") + "\n"
                + styled("  Key:", "light_gray", style = "bold")
                + " " + key + "\n"
            )

        return key

    @classmethod
    def normalize_key(cls, key):
        """Processes a key to make sure it can be used as a caching key."""
        key = cls._obtain_key(key)
        if not isinstance(key, basestring):
            key = repr(key)
        return key

    @classmethod
    def _obtain_key(cls, key):
        if isinstance(key, (tuple, list, ListWrapper, OrderedSet)):
            return repr(tuple(cls.normalize_key(item) for item in key))
        elif isinstance(key, (set, frozenset, SetWrapper)):
            return tuple(cls.normalize_key(item) for item in sorted(key))
        elif isinstance(key, (dict, DictWrapper)):
            return tuple(
                (cls.normalize_key(k), cls.normalize_key(key[k]))
                for k in sorted(key)
            )
        else:
            return key


def _cache_invalidation_commit_handler(success, cache):
    if success:
        from cocktail.persistence import datastore
        key = (TRANSACTION_KEY, id(cache))
        transaction_invalidation_scope = datastore.get_transaction_value(key)
        cache.clear(transaction_invalidation_scope)

