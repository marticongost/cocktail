#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from persistent import Persistent
from cocktail.modeling import empty_set

class Index(Persistent):

    def __init__(self, mapping):
        self.__groups = mapping

    def add(self, key, value):

        group = self.__groups.get(key)

        if group is None:
            self.__groups[key] = group = set()
     
        group.add(value)

    def remove(self, key, value):
        group = self.__groups.get(key)
        
        if group is not None:
            group.discard(value)

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

if __name__ == "__main__":
 
    from time import time

    from BTrees.IOBTree import IOBTree
    index = Index(IOBTree())
    
    from random import randint, choice
    from string import letters

    randstring = lambda l: "".join(choice(letters) for l in xrange(l))
    items = [(randint(1, 1000000), randstring(10)) for i in xrange(1000000)]

    t = time()
    
    for key, value in items:
        index.add(key, value)

    print "Index:", time() - t

    while True:
        key = raw_input("Key: ")
        t = time()
        print index[int(key)]
        print "Search:", time() - t

