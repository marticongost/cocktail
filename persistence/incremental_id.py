#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import Lock
from cocktail.persistence.datastore import datastore

class IncrementalIdGenerator(object):

    def __init__(self, key = "incremental_id", seed = 0, step = 1):

        self.key = key
        self.seed = seed
        self.step = step
        
        self._lock = Lock()
        self._current_id = None

    def generate_id(self, mapping):
        
        self._lock.acquire()

        try:
            if self._current_id is None:
                self._current_id = mapping.get(self.key, self.seed)

            self._current_id += self.step
            mapping[self.key] = self._current_id
            
        finally:
            self._lock.release()

        return self._current_id

_id_generator = IncrementalIdGenerator()

def incremental_id():
    return _id_generator.generate_id(datastore.root)

