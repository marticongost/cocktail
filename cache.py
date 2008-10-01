#-*- coding: utf-8 -*-
"""

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

    def __init__(self):
        entries = {}
        DictWrapper.__init__(self, entries)
        self.__entries = entries
        
    def _drop_expired(self):
        
        if self.expiration:
            
            oldest_creation_time = time() - self.expiration

            for key, entry in self.__entries.items():
                if entry.creation < oldest_creation_time:
                    del self.__entries[key]

    def request(self, key):
        if self.enabled:
            entry = self.__entries.get(key, missing)

            if entry is missing or not self._is_current(entry):
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
        del self.__entries[key]
    
    def pop(self, key, default = None):
        return self.__entries.pop(key, default)

    def clear(self):
        self.__entries.clear()

    def _is_current(self, entry):
        return self.expiration is None \
            or time() - entry.creation < self.expiration

class CacheEntry(object):
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.creation = time()

