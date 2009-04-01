#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from itertools import groupby

def filter_by(collection, **kwargs):
    
    for item in collection:
        for key, value in kwargs.iteritems():
            if not getattr(item, key) == value:
                break
        else:
            yield item

def first(collection, **kwargs):
    
    if kwargs:
        collection = filter_by(collection, **kwargs)

    try:
        return iter(collection).next()
    except StopIteration:
        return None

def last(collection, **kwargs):
    
    if kwargs:
        collection = filter_by(collection, **kwargs)

    for item in collection:
        pass

    return item

def is_empty(collection):
    """Indicates if the given iterable object contains at least one item. Note
    that calling this function on an iterator will consume its first item.

    @param collection: The iterable object to be tested.
    @type collection: iterable

    @return: True if the object contains at least one item, False if it is
        empty.
    @rtype: bool
    """
    try:
        iter(collection).next()
    except StopIteration:
        return True
    else:
        return False

def grouped(collection, key):

    if isinstance(key, basestring):
        attrib = key
        key = lambda item: getattr(item, attrib, None)

    return groupby(sorted(collection, key = key), key = key)

