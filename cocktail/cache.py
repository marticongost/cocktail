#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from time import time
from cocktail.modeling import DictWrapper, getter

missing = object()

class Cache(DictWrapper):
    
    expiration = None
    entries = None
    enabled = True
    updatable = True

    def __init__(self, load = None):
        entries = {}
        DictWrapper.__init__(self, entries)
        self.__entries = entries

        if load is not None:
            self.load = load
 
    def _drop_expired(self):
        
        if self.expiration:
            
            oldest_creation_time = time() - self.expiration

            for key, entry in self.__entries.items():
                if entry.creation < oldest_creation_time:
                    del self[key]

    def request(self, key):
        if self.enabled:
            entry = self.__entries.get(key, missing)

            if entry is missing \
            or (self.updatable and not self._is_current(entry)):
                value = self.load(key)
                self.__entries[key] = CacheEntry(key, value)
                return value
            else:
                return entry.value
        else:
            return self.load(key)
    
    def load(self, key):
        pass

    def __delitem__(self, key):
        entry = self.__entries.get(key)
        if entry:
            self._entry_removed(entry)
        else:
            raise KeyError(key)
    
    def pop(self, key, default = missing):
        entry = self.__entries.get(key)
        if entry is None:
            if default is missing:
                raise KeyError(key)
            return default
        else:
            del self.__entries[key]
            self._entry_removed(entry)
            return entry

    def clear(self):
        entries = self.__entries.values()
        self.__entries.clear()
        for entry in entries:
            self._entry_removed(entry)

    def _is_current(self, entry):
        return self.expiration is None \
            or time() - entry.creation < self.expiration

    def _entry_removed(self, entry):
        pass


class CacheEntry(object):
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.creation = time()

