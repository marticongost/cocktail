#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import Lock
from time import sleep
import transaction
from cocktail.persistence.datastore import datastore
from cocktail.persistence.persistentmapping import PersistentMapping
from ZODB.POSException import ConflictError

ID_CONTAINER_KEY = "id_container"
RETRY_INTERVAL = 0.1
STEP = 10

_acquired_ids = []
_lock = Lock()

@datastore.connection_opened.append
def create_container(event):
    root = event.source.root
    if ID_CONTAINER_KEY not in root:
        root[ID_CONTAINER_KEY] = PersistentMapping()
        datastore.commit()

def incremental_id(key = "default"):
    
    global _acquired_ids
    _lock.acquire()

    try:
        if not _acquired_ids:            
            try:
                tm = transaction.TransactionManager()
                conn = datastore.db.open(transaction_manager = tm)
                
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
                    else:
                        _acquired_ids = range(base_id + 1, top_id + 1)
                        break
            finally:
                conn.close()
    
        return _acquired_ids.pop(0)
    
    finally:
        _lock.release()

