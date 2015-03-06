#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .scope import whole_cache
from .exceptions import CacheKeyError


class CacheStorage(object):
    """A cache backend, used by :class:`~cocktail.caching.Cache` to
    implement its storage.
    """

    def exists(self, key):
        """Indicates if the given key is contained within the storage.

        This method should take into account key expiration, and consider
        expired keys as non existent.

        :param key: The key to check.
        :return: True if the storage contains the key and the key is current
            (or has no expiration date set). False in any other case.
        """
        raise TypeError(
            "%s doesn't implement the has_key() method" % self
        )

    def retrieve(self, key):
        """Obtains the value stored for the given key.

        :param key: The key to retrieve.
        :return: The value associated with the indicated key.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            present in the storage, or if it has expired.
        """
        raise TypeError(
            "%s doesn't implement the retrieve() method" % self
        )

    def retrieve_with_metadata(self, key):
        """Obtains the value, expiration and tags for the given key.

        :param key: The key to retrieve.
        :return: A tuple containing the value, expiration and tags associated
            with the indicated key.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            present in the storage, or if it has expired.
        """
        raise TypeError(
            "%s doesn't implement the retrieve_with_metadata() method" % self
        )

    def store(self, key, value, expiration = None, tags = None):
        """Inserts or updates a value in the storage.

        If the key already existed, the given value, expiration and tags will
        be used to replace the old ones.

        :param key: A string that will uniquely identify the value in the
            storage, making it possible to `.retrieve` it later.
        :param value: The value to associate to this key.
        :param expiration: An optional parameter that limits the maximum
            life span of the key in the storage. If given, it should be set
            to an integer timestamp.
        :param tags: An optional set of tags to attach to this key. If given,
            it should be expressed as a collection of strings, each one
            representing a single tag.
        """
        raise TypeError(
            "%s doesn't implement the store() method" % self
        )

    def get_expiration(self, key):
        """Determines the expiration assigned to the given key.

        :return: An integer timestamp indicating the point in time at which the
            key will expire. If the key doesn't have an expiration date, the
            method will return ``None``.
        :raises cocktail.caching.CacheKeyError: if the key is not
            contained in the storage or has already expired.
        """
        raise TypeError(
            "%s doesn't implement the get_expiration() method" % self
        )

    def set_expiration(self, key, expiration):
        """Sets the expiration assigned to the given key.

        :param key: The key to update the expiration for.
        :param expiration: An integer timestamp indicating the new expiration
            date for the key.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            contained in the storage or has already expired.
        :raises ValueError: Raised if the given expiration key is not valid
            (ie. is not an integer timestamp, or is set in the past).
        """
        raise TypeError(
            "%s doesn't implement the set_expiration() method" % self
        )

    def remove(self, key):
        """Removes the given key from the storage, or fails.

        This method is similar to `.discard`, but it will raise an exception
        instead of returning False if the indicated key doesn't exist or has
        expired.

        :param key: The key to remove.
        :raises cocktail.caching.CacheKeyError: Raised if the key is not
            contained in the storage, or has expired.
        """
        if not self.discard(key):
            raise CacheKeyError(key)

    def discard(self, key):
        """Removes the given key from the storage, if it exists.

        This method is similar to `.remove`, but it will return a boolean
        indicating wether the removal succeeded (`.remove` raises an exception
        if it can't find the requested key in the storage).

        :param key: The key to remove.
        :return: True if the key was removed from the storage, False if it
            wasn't contained on the storage, or if it had already expired.
        """
        raise TypeError(
            "%s doesn't implement the discard() method" % self
        )

    def clear(self, scope = whole_cache):
        """Discards all keys in the storage matching the given scope.

        :param scope: A selector indicating the keys that should be removed. It
            can take two forms:

                - `~cocktail.caching.whole_cache` will remove all the entries
                  in the storage.

                - A collection of selectors. Only entries that match one or
                  more of the given selectors will be removed. Each selector
                  can take one of the following forms:

                    - A string will be treated as a single tag, and will select
                      all entries tagged with said tag.
                    - A tuple of strings will be interpreted as an intersection
                      of tags: any entry tagged with *all* of the tags in the
                      tuple will be deleted.

        :raises TypeError: Raised if the ``scope`` parameter is given a value
            of a wrong type.
        """
        raise TypeError(
            "%s doesn't implement the clear() method" % self
        )

    def drop_weight(self):
        """Removes an entry from the storage, in order to free resources.

        :return: The key that has been removed, or ``None`` if the storage is
            empty.
        """
        raise TypeError(
            "%s doesn't implement the drop_weight() method" % self
        )

