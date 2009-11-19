#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import RLock
from time import sleep
import transaction
from cocktail.persistence.datastore import datastore
from cocktail.persistence.persistentmapping import PersistentMapping
from ZODB.POSException import ConflictError

ID_CONTAINER_KEY = "id_container"
RETRY_INTERVAL = 0.1
STEP = 10

_acquired_ids = []
_lock = RLock()

@datastore.connection_opened.append
def create_container(event):
    root = event.source.root
    if ID_CONTAINER_KEY not in root:
        root[ID_CONTAINER_KEY] = PersistentMapping()
        datastore.commit()

@datastore.storage_changed.append
def discard_acquired_ids(event):
    global _acquired_ids
    _lock.acquire()
    try:
        _acquired_ids = []
    finally:
        _lock.release()

def incremental_id(key = "default"):
    
    _lock.acquire()

    try:
        if not _acquired_ids:            
            acquire_id_range(STEP, key)
    
        return _acquired_ids.pop(0)
    
    finally:
        _lock.release()

def acquire_id_range(size, key = "default"):

    global _acquired_ids

    try:
        _lock.acquire()

        tm = transaction.TransactionManager()
        conn = datastore.db.open(transaction_manager = tm)

        try:
            while True:
                conn.sync()
                root = conn.root()
                container = root.get(ID_CONTAINER_KEY)

                if container is None:
                    container = PersistentMapping()
                    root[ID_CONTAINER_KEY] = container
                
                base_id = container.get(key, 0)
                top_id = base_id + STEP

                container[key] = top_id
                try:
                    tm.commit()
                except ConflictError:
                    sleep(RETRY_INTERVAL)
                    tm.abort()
                except:
                    tm.abort()
                    raise
                else:
                    _acquired_ids = range(base_id + 1, top_id + 1)
                    return _acquired_ids
        finally:
            conn.close()
    finally:
        _lock.release()

