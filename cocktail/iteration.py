"""This module provides several algorithms for iterating over sequences.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, Union
from itertools import groupby

Key = Union[str, Callable[[Any], Any]]
AttributeFilters = Mapping[str, Any]
_undefined = object()


def filter_by(collection: Iterable, **kwargs: AttributeFilters) -> Iterable:
    """Iterate over the items in a collection that have the specified values.

    :param collection: The iterable sequence to filter.

    :param kwargs: A set of key/value pairs indicating the filtering criteria
        applied to the collection. Only items that possess the indicated
        attributes with the specified values will pass the filter.

    :return: An iterator over the items in the collection that have the
        specified values.
    """
    for item in collection:
        for key, value in kwargs.items():
            if not getattr(item, key) == value:
                break
        else:
            yield item


def first(collection: Iterable, **kwargs: AttributeFilters) -> Any:
    """Obtains the first element in the given sequence.

    This function can operate on both 'solid' collections (lists, tuples, etc)
    and iterators; But keep in mind that when called on an iterator, its
    position will be altered. Also, it will work on sets or dictionaries, but
    since these data structures don't make any guarantees about any specific
    order, the returned item will be arbitrary.

    :param collection: The iterable sequence whose first item should be
        returned.

    :param kwargs: If given, the returned item will be the first item in the
        collection with the specified values (works just like `filter_by`).

    :return: The first item in the collection, or None if the collection is
        empty.
    """
    if kwargs:
        collection = filter_by(collection, **kwargs)

    try:
        return next(iter(collection))
    except StopIteration:
        return None


def last(collection: Iterable, **kwargs: AttributeFilters) -> Any:
    """Obtains the last element in the given sequence.

    This function can operate on both 'solid' collections (lists, tuples, etc)
    and iterators; But keep in mind that iterators will be completely consumed
    after the call. Also, it will work on sets or dictionaries, but since these
    data structures don't make any guarantees about any specific order, the
    returned item will be arbitrary.

    :param collection: The iterable sequence whose last item should be
        returned.

    :param kwargs: If given, the returned item will be the last item in the
        collection with the specified values (works just like `filter_by`).

    :return: The last item in the collection, or None if the collection is
         empty.
    """
    if kwargs:
        collection = filter_by(collection, **kwargs)

    for item in collection:
        pass

    return item


def is_empty(collection: Iterable) -> bool:
    """Indicates if the given iterable object contains at least one item.

    Note that calling this function on an iterator will consume its first item.

    :param collection: The iterable object to be tested.

    :return: True if the object contains at least one item, False if it is
        empty.
    """
    try:
        next(iter(collection))
    except StopIteration:
        return True
    else:
        return False


def grouped(
        collection: Iterable,
        key: Key,
        sorting: Callable[[Any, Any], Any] = (lambda group, item: (group, item))
    ) -> Iterable[Tuple[Any, Iterable]]:
    """Groups the items in a sequence by the given key.

    :param collection: The iterable object providing the items to group.

    :param key: The key by which items should be grouped. Can take two forms:
        * The name of an attribute of items in the collection.
        * A function that takes an item as a parameter and returns a value
          identifying its group

    :param sorting: An optional keying method to sort entries before
        grouping them. Defaults to sorting by direct comparision between an
        object's group, with ties being resolved by direct comparision
        between the objects themselves. If set to a callable, it should
        receive two arguments (a collection group and item), and return the
        desired sorting key. Setting the parameter to None indicates the
        collection is already in order, and will disable further sorting.

    :return: An iterator over the groups present in the provided collection.
        Each group is represented as a tuple, holding the value for the group
        and an iterator of all the items in the original collection in that
        group.
    """
    if isinstance(key, str):
        attrib = key
        key = lambda item: getattr(item, attrib, None)

    if sorting:
        collection = sorted(
            collection,
            key=(lambda item: sorting(key(item), item))
        )

    return groupby(collection, key=key)


def find_max(
        collection: Iterable,
        key: Optional[Key] = None,
        default: Any = _undefined) -> Any:
    """Finds the item with the highest value in the given collection.

    :param collection: The collection to inspect.
    :param key: An optional keying method to determine the value of each entry
        in the collection. If not given or set to None, items are compared
        using a direct comparison. If given, it can take one of two forms:

            * The name of an attribute of the items in the collection.
            * A function that takes one of the items in the collection and
              returns its value

    :param default: The value to return if the collection is empty. If no
        default is given the function will raise a `ValueError` exception
        instead.

    :return: The item in the collection with the highest value.
    """
    max_item = _undefined
    max_key = _undefined

    if isinstance(key, str):
        attrib = key
        key = lambda item: getattr(item, attrib, None)

    for item in collection:
        item_key = item if key is None else key(item)
        if max_item is _undefined or item_key > max_key:
            max_item = item
            max_key = item_key

    if max_item is _undefined:
        if default is _undefined:
            raise ValueError("Can't call find_max() on an empty collection")
        return default

    return max_item


def find_min(
        collection: Iterable,
        key: Optional[Key] = None,
        default: Any = _undefined) -> Any:
    """Finds the item with the lowest value in the given collection.

    :param collection: The collection to inspect.
    :param key: An optional keying method to determine the value of each entry
        in the collection. If not given or set to None, items are compared
        using a direct comparison. If given, it can take one of two forms:

            * The name of an attribute of the items in the collection.
            * A function that takes one of the items in the collection and
              returns its value

    :param default: The value to return if the collection is empty. If no
        default is given the function will raise a `ValueError` exception
        instead.

    :return: The item in the collection with the lowest value.
    """
    min_item = _undefined
    min_key = _undefined

    if isinstance(key, str):
        attrib = key
        key = lambda item: getattr(item, attrib, None)

    for item in collection:
        item_key = item if key is None else key(item)
        if min_item is _undefined or item_key < min_key:
            min_item = item
            min_key = item_key

    if min_item is _undefined:
        if default is _undefined:
            raise ValueError("Can't call find_min() on an empty collection")
        return default

    return min_item


def batch(iterable: Iterable, batch_size: int) -> Iterable[Iterable]:
    """Splits an iterable sequence into several sequences of the given size (at
    the most).

    Note that the last yielded sequence may hold fewer elements than their
    predecessors, if the given sequence can't be split evenly into batches of
    the given size.

    :param iterable: The iterable sequence to split.
    :param batch_size: The size of the returned batches.

    :return: An iterable sequence of iterable sequences.
    """

    if not batch_size:
        yield iterable
    else:
        group = []

        for item in iterable:
            group.append(item)
            if len(group) == batch_size:
                yield group
                group = []

        if group:
            yield group

