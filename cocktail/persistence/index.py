#-*- coding: utf-8 -*-
"""Defines classes to index key,value pairs.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from functools import total_ordering
from persistent import Persistent

undefined = object()


class Index(Persistent):
    """Abstract base class for all indexes."""

    accepts_repetition = False

    def __init__(self, pairs = None):
        """Initializes the index, optionally filling it with the given set of
        pairs.

        :param pairs: A set of key,value pairs to feed into the index.
        :type pairs: An iterable sequence of key,value tuples.
        """
        if pairs is not None:
            for key, value in pairs:
                self.add(key, value)

    @property
    def accepts_multiple_values(self):
        """Indicates if the index is capable of holding more than one value for
        the same key.
        """
        raise TypeError("Not implemented")

    def add(self, key, value):
        """Adds a key, value pair to the index.

        If a value for the given key was present in the index already it will
        be replaced with the new value.

        :param key: The key to insert. Index keys must comply with these
            requirements:

            - They must provide *total ordering*
            - They must be inmutable
            - They can't inherit from `Persistent`
            - For `indexes with a single value per key <SingleValueIndex>`,
              keys can't be None

        :param value: The value to insert.
        """
        raise TypeError("Not implemented")

    def remove(self, key, value = undefined):
        """Removes one or more pairs from the index.

        :param key: A key identifying the pairs to remove from the index.
        :param value: If set, matching pairs are only removed if they also
            match the specified value. If no value is specified, all pairs with
            the given key will be removed.
        """
        raise TypeError("Not implemented")

    def keys(self,
        min = undefined,
        max = undefined,
        exclude_min = False,
        exclude_max = False,
        descending = False):
        """Iterates over the keys defined by the index.

        The `min`, `max`, `include_min` and `include_max` parameters can be
        used to return only a range of the keys defined by the index, while the
        `descending` parameter allows to obtain the keys in reverse order.
        These features are used extensively by `queries <Query>` to compute
        their results.

        :param min: If set, return a subset of keys starting at the specified
            key.

        :param max: If set, return a subset of keys ending at the specified
            key.

        :param include_min: When supplying the `min` parameter to obtain a
            subset of keys, determine if the lower boundary should be included
            in the subset.
        :param include_min: bool

        :param include_min: When supplying the `max` parameter to obtain a
            subset of keys, determine if the upper boundary should be included
            in the subset.
        :param include_min: bool

        :param descending: If set to True, the index is traversed in reverse
            order.
        :type descending: bool

        :return: An iterable sequence containing the requested keys.
        :rtype: iterable
        """
        for pair in self.items(
            min = min,
            max = max,
            exclude_min = exclude_min,
            exclude_max = exclude_max,
            descending = descending
        ):
            yield pair[0]

    def values(self,
        key = undefined,
        min = undefined,
        max = undefined,
        exclude_min = False,
        exclude_max = False,
        descending = False):
        """Iterates over the values contained inside the index.

        The `key`, `min`, `max`, `include_min` and `include_max` parameters can
        be used to return only a subset of the values defined by the index,
        while the `descending` parameter allows to obtain the values in reverse
        key order. These features are used extensively by `queries <Query>` to
        compute their results.

        :param key: If set, return only the values for the indicated key. This
            parameter can't be mixed with `min`, `max`, `exclude_min` or
            `exclude_max`.

        :param min: If set, return a subset of values starting at the specified
            key.

        :param max: If set, return a subset of values ending at the specified
            key.

        :param include_min: When supplying the `min` parameter to obtain a
            subset of values, determine if the lower boundary should be
            included in the subset.
        :param include_min: bool

        :param include_min: When supplying the `max` parameter to obtain a
            subset of values, determine if the upper boundary should be
            included in the subset.
        :param include_min: bool

        :param descending: Normally, returned values are sorted by their index
            key. If this parameter is set to True, the sorting order is
            reversed.
        :type descending: bool

        :return: An iterable sequence containing the requested values.
        :rtype: iterable
        """
        if key is not undefined:

            if min is not undefined:
                raise ValueError(
                    "Can't supply both 'key' and 'min' to Index.values()"
                )

            if max is not undefined:
                raise ValueError(
                    "Can't supply both 'key' and 'max' to Index.values()"
                )

            if exclude_min:
                raise ValueError(
                    "Can't supply both 'key' and 'exclude_min' to "
                    "Index.values()"
                )

            if exclude_max:
                raise ValueError(
                    "Can't supply both 'key' and 'exclude_max' to "
                    "Index.values()"
                )

            min = key
            max = key

        for pair in self.items(
            min = min,
            max = max,
            exclude_min = exclude_min,
            exclude_max = exclude_max,
            descending = descending
        ):
            yield pair[1]

    def items(self,
        min = undefined,
        max = undefined,
        exclude_min = False,
        exclude_max = False,
        descending = False):
        """Iterates over the key,value pairs defined by the index.

        The `min`, `max`, `include_min` and `include_max` parameters can be
        used to return only a subset of the entries defined by the index, while
        the `descending` parameter allows to obtain entries in reverse key
        order. These features are used extensively by `queries <Query>` to
        compute their results.

        :param min: If set, return a subset of entries starting at the
            specified key.

        :param max: If set, return a subset of entries ending at the specified
            key.

        :param include_min: When supplying the `min` parameter to obtain a
            subset of entries, determine if the lower boundary should be
            included in the subset.
        :param include_min: bool

        :param include_min: When supplying the `max` parameter to obtain a
            subset of entries, determine if the upper boundary should be
            included in the subset.
        :param include_min: bool

        :param descending: Normally, returned entries are sorted by their index
            key. If this parameter is set to True, the sorting order is
            reversed.
        :type descending: bool

        :return: An iterable sequence containing the requested key,value pairs.
        :rtype: iterable sequence of tuples
        """
        raise TypeError("Not implemented")

    def min_key(self, exclude_none = False):
        """Obtains the smallest key defined by the index.

        :return: The smallest key defined by the index.

        :raise ValueError: Raised if the index is empty.
        """
        raise TypeError("Not implemented")

    def max_key(self):
        """Obtains the biggest key defined by the index.

        :return: The biggest key defined by the index.

        :raise ValueError: Raised if the index is empty.
        """
        raise TypeError("Not implemented")

    def __len__(self):
        """Counts the pairs defined by the index.

        :type: The number of pairs defined by the index.
        :rtype: int
        """
        raise TypeError("Not implemented")

    def __iter__(self):
        """Iterates over the keys defined by the index.

        :return: An iterable sequence containing the keys defined by the index.
        """
        return self.keys()

    def __bool__(self):
        """Determines if the index is empty.

        :return: True if the index is empty, False otherwise.
        :rtype: bool
        """
        return bool(self.__items)

    def __contains__(self, key):
        """Determines if the given key is defined by the index.

        :param key: The key to look for.

        :return: True if the index defines the given key, False otherwise.
        :rtype: bool
        """
        raise TypeError("Not implemented")

    def has_key(self, key):
        """Determines if the given key is defined by the index.

        :param key: The key to look for.

        :return: True if the index defines the given key, False otherwise.
        :rtype: bool
        """
        return self.__contains__(key)


@total_ordering
class Descending:
    """A helper class for indexing keys in descending order."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Descending(%r)" % (self.value,)

    def __lt__(self, other):

        if isinstance(other, Descending):
            other = other.value

        if other is None:
            return False

        return self.value > other

    def __eq__(self, other):

        if isinstance(other, Descending):
            other = other.value

        return self.value == other

