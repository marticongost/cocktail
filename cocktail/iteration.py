#-*- coding: utf-8 -*-
u"""
This module provides several algorithms for iterating over sequences.
"""
from itertools import groupby

def filter_by(collection, **kwargs):
    """Iterate over the items in a collection that have the specified values.

    :param collection: The iterable sequence to filter.

    :param kwargs: A set of key/value pairs indicating the filtering criteria
        applied to the collection. Only items that possess the indicated
        attributes with the specified values will pass the filter.

    :return: An iterator over the items in the collection that have the
        specified values.
    """
    for item in collection:
        for key, value in kwargs.iteritems():
            if not getattr(item, key) == value:
                break
        else:
            yield item

def first(collection, **kwargs):
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
        return iter(collection).next()
    except StopIteration:
        return None

def last(collection, **kwargs):
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

def is_empty(collection):
    """Indicates if the given iterable object contains at least one item.
    
    Note that calling this function on an iterator will consume its first item.

    :param collection: The iterable object to be tested.

    :return: True if the object contains at least one item, False if it is
        empty.
    """
    try:
        iter(collection).next()
    except StopIteration:
        return True
    else:
        return False

def grouped(collection, key):
    """Groups the items in a sequence by the given key.

    :param collection: The iterable object providing the items to group.

    :param key: The key by which items should be grouped. Can take two forms:
        * The name of an attribute of items in the collection.
        * A function that takes an item as a parameter and returns a value
          identifying its group

    :return: An iterator over the groups present in the provided collection.
        Each group is represented as a tuple, holding the value for the group
        and an iterator of all the items in the original collection in that
        group.
    """
    if isinstance(key, basestring):
        attrib = key
        key = lambda item: getattr(item, attrib, None)

    return groupby(sorted(collection, key = key), key = key)

