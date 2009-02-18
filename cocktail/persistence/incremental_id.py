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
from ZODB.POSException import ConflictError

RETRY_INTERVAL = 0.1

_lock = Lock()

def incremental_id(key = "incremental_id"):
    
    _lock.acquire()

    try:
        try:
            tm = transaction.TransactionManager()
            conn = datastore.db.open(transaction_manager = tm)
            
            while True:
                conn.sync()
                root = conn.root()
                id = root.get(key, 0) + 1
                root[key] = id
                try:
                    tm.commit()
                except ConflictError:
                    sleep(RETRY_INTERVAL)
                    tm.abort()
                else:
                    return id
        finally:
            conn.close()
    finally:
        _lock.release()

