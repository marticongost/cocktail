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

_acquired_ids = {}
_lock = RLock()

@datastore.connection_opened.append
def create_container(event):
    root = event.source.root
    if ID_CONTAINER_KEY not in root:
        root[ID_CONTAINER_KEY] = PersistentMapping()
        datastore.commit()

@datastore.storage_changed.append
def discard_acquired_ids(event):
    with _lock:
        _acquired_ids.clear()

def incremental_id(key = "default"):
    
    with _lock:
        key_acquired_ids = _acquired_ids.get(key)

        if not key_acquired_ids:
            acquire_id_range(STEP, key)
        
        return _acquired_ids[key].pop(0)

def acquire_id_range(size, key = "default"):

    with _lock:
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
                    break
        finally:
            conn.close()

        id_range = range(base_id + 1, top_id + 1)
        key_acquired_ids = _acquired_ids.get(key)

        if key_acquired_ids is None:
            _acquired_ids[key] = list(id_range)
        else:
            key_acquired_ids.extend(id_range)

        return id_range

