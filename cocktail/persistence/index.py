#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from persistent import Persistent
from cocktail.modeling import empty_set
from cocktail.persistence.persistentset import PersistentSet

infinite = object()


class Index(Persistent):
    """A persistent index that supports multiple entries per key. Used to
    maintain an index for a non unique field.
    """

    def __init__(self, mapping):
        self.__groups = mapping
        self.__none_entries = PersistentSet()

    def add(self, key, value):

        if key is None:
            self.__none_entries.add(value)
            self._p_changed = True
        else:
            group = self.__groups.get(key)

            if group is None:
                self.__groups[key] = group = PersistentSet()
         
            group.add(value)
            
            self._p_changed = True
            self.__groups._p_changed = True

    def remove(self, key, value):
        
        if key is None:
            self.__none_entries.discard(value)
            self._p_changed = True
        else:
            group = self.__groups.get(key)
            
            if group is not None:
                group.discard(value)

                if not group:
                    del self.__groups[key]

                self._p_changed = True
                self.__groups._p_changed = True

    def __getitem__(self, key):
        
        if isinstance(key, slice):        
            raise ValueError(
                "Slicing an index is not supported; use keys()/values() "
                "instead")
        else:
            if key is None:
                return self.__none_entries
            else:
                return self.__groups.get(key, empty_set)

    def __delitem__(self, key):
        if key is None:
            self.__none_entries = PersistentSet()
        else:
            self.__groups.__delitem__(key)
            self.__groups._p_changed = True

        self._p_changed = True

    def keys(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):
        
        return list(self.iterkeys(
            min = min,
            max = max,
            excludemin = excludemin,
            excludemax = excludemax            
        ))

    def values(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):
        
        return list(self.itervalues(
            min = min,
            max = max,
            excludemin = excludemin,
            excludemax = excludemax            
        ))

    def items(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):
        
        return list(self.iteritems(
            min = min,
            max = max,
            excludemin = excludemin,
            excludemax = excludemax            
        ))

    def itervalues(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):

        if (min is infinite or (min is None and not excludemin)) \
        and (max is not None or (max is None and not excludemax)) \
        and self.__none_entries:
            for item in self.__none_entries:
                yield item
       
        if max is not None:

            if min is infinite:
                min = None

            if max is infinite:
                max = None
            
            for group in self.__groups.itervalues(
                min = min,
                max = max,
                excludemin = excludemin and min is not None,
                excludemax = excludemax and max is not None
            ):
                for item in group:
                    yield item

    def iterkeys(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):
        
        if (min is infinite or (min is None and not excludemin)) \
        and (max is not None or (max is None and not excludemax)) \
        and self.__none_entries:
            yield None
        
        if max is not None:

            if min is infinite:
                min = None

            if max is infinite:
                max = None
            
            for key in self.__groups.iterkeys(
                min = min,
                max = max,
                excludemin = excludemin and min is not None,
                excludemax = excludemax and max is not None
            ):
                yield key

    def iteritems(self,
        min = infinite,
        max = infinite,
        excludemin = False,
        excludemax = False):
        
        if (min is infinite or (min is None and not excludemin)) \
        and (max is not None or (max is None and not excludemax)) \
        and self.__none_entries:
            for item in self.__none_entries:
                yield None, item

        if max is not None:

            if min is infinite:
                min = None

            if max is infinite:
                max = None

            for key, group in self.__groups.iteritems(
                min = min,
                max = max,
                excludemin = excludemin and min is not None,
                excludemax = excludemax and max is not None
            ):                
                for item in group:
                    yield key, item

    def minKey(self):        
        if self.__none_entries:
            return None
        else:
            return self.__groups.minKey()

    def maxKey(self):
        try:
            return self.__groups.maxKey()
        except ValueError:
            if self.__none_entries:
                return None
            else:
                raise

    def __len__(self):
        count = self.__groups.__len__()

        if self.__none_entries:
            count += 1

        return count

    def __iter__(self):
        if self.__none_entries:
            yield None

        for group in self.__groups:
            yield group

    def __contains__(self, key):
        if key is None:
            return bool(self.__none_entries)
        else:
            return self.__groups.__contains__(key)
    
    def __notzero__(self):
        return self.__none_entries or self.__groups

    def has_key(self, key):
        
        if key is None:
            return bool(self.__none_entries)
        else:
            return self.__groups.has_key(key)

