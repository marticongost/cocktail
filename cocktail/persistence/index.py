#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from persistent import Persistent
from cocktail.modeling import empty_set

# Index class
#------------------------------------------------------------------------------
class Index(Persistent):
    """A persistent index that supports multiple entries per key. Used to
    maintain an index for a non unique field.
    """

    def __init__(self, mapping):
        self.__groups = mapping

    def add(self, key, value):

        group = self.__groups.get(key)

        if group is None:
            self.__groups[key] = group = set()
     
        group.add(value)
        
        self._p_changed = True
        self.__groups._p_changed = True

    def remove(self, key, value):
        group = self.__groups.get(key)
        
        if group is not None:
            group.discard(value)

            self._p_changed = True
            self.__groups._p_changed = True

    def __getitem__(self, key):
        
        if isinstance(key, slice):
            
            if key.step != 1:
                raise ValueError("Steps other than 1 not accepted")

            return self.values(
                min = key.start,
                max = key.end,
                excludemin = False,
                excludemax = True)

        else:
            return self.__groups.get(key, empty_set)

    def __delitem__(self, key):
        self.__groups.__delitem__(key)
        self._p_changed = True
        self.__groups._p_changed = True

    def keys(self):
        return self.__groups.keys()

    def values(self, *args, **kwargs):        
        return list(self.itervalues(*args, **kwargs))

    def items(self, *args, **kwargs):
        return list(self.iteritems(*args, **kwargs))

    def itervalues(self, *args, **kwargs):
        for group in self.__groups.itervalues(*args, **kwargs):
            for item in group:
                yield item

    def iterkeys(self):
        return self.__groups.iterkeys()

    def iteritems(self, *args, **kwargs):
        for key, group in self.__groups.iteritems(*args, **kwargs):
            for item in group:
                yield key, item

    def minKey(self):
        return self.__groups.minKey()

    def maxKey(self):
        return self.__groups.maxKey()

    def __len__(self):
        return self.__groups.__len__()

    def __iter__(self):
        return self.__groups.__iter__()

    def __contains__(self, key):
        return self.__groups.__contains__(key)
    
    def __notzero__(self):
        return self.__groups.__notzero__()

    def has_key(self, key):
        return self.__groups.has_key(key)

