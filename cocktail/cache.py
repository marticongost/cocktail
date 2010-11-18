#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from time import time, mktime
from datetime import datetime
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

    def request(self, key, expiration = None, invalidation = None):
        try:
            return self.get_value(key, invalidation = invalidation)
        except KeyError:
            value = self.load(key)
            if self.enabled:
                self.__entries[key] = CacheEntry(key, value, expiration)
            return value

    def get_value(self, key, default = missing, invalidation = None):
        if self.enabled:
            entry = self.__entries.get(key, None)

            if entry is not None:
        
                if self.updatable \
                and not self._is_current(entry, invalidation):
                    if default is missing:
                        raise ExpiredEntryError(entry)
                else:
                    return entry.value 

        if default is missing:
            raise KeyError("Undefined cache key: %s" % repr(key))
    
        return default

    def set_value(self, key, value, expiration = None):
        self.__entries[key] = CacheEntry(key, value, expiration)

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

    def _is_current(self, entry, invalidation = None):
        
        expiration = entry.expiration
        
        if expiration is None:
            expiration = self.expiration
        
        if invalidation is not None:
            if callable(invalidation):
                invalidation = invalidation()
            if isinstance(invalidation, datetime):
                invalidation = mktime(invalidation.timetuple())

        return (
            (expiration is None or time() - entry.creation < expiration)
            and (invalidation is None or entry.creation >= invalidation)
        )

    def _entry_removed(self, entry):
        pass


class CacheEntry(object):
    
    def __init__(self, key, value, expiration = None):
        self.key = key
        self.value = value
        self.creation = time()
        self.expiration = expiration


class ExpiredEntryError(KeyError):

    def __init__(self, entry):
        KeyError.__init__(self, "Cache key expired: %s" % entry.key)
        self.entry = entry

