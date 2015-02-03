#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import RLock, local
from time import sleep
from contextlib import contextmanager
import transaction
from cocktail.events import when
from cocktail.persistence.datastore import datastore
from cocktail.persistence.persistentmapping import PersistentMapping
from ZODB.POSException import ConflictError

ID_CONTAINER_KEY = "id_container"
RETRY_INTERVAL = 0.1
default_slice_size = 10
_thread_data = local()

_acquired_ids = {}
_lock = RLock()

def get_incremental_id_slice_size(key = None):
    if not hasattr(_thread_data, "slice_sizes"):
        _thread_data.slice_sizes = {}
        _thread_data.default_slice_size = default_slice_size

    return (
        key and _thread_data.slice_sizes.get(key)
        or _thread_data.default_slice_size
    )

def set_incremental_id_slice_size(size, key = None):
    if not hasattr(_thread_data, "slice_sizes"):
        _thread_data.slice_sizes = {}
        _thread_data.default_slice_size = default_slice_size

    if key:
        _thread_data.slice_sizes[key] = size
    else:
        _thread_data.default_slice_size = size

@contextmanager
def incremental_id_slice_size_context(size, key = None):
    prev_size = get_incremental_id_slice_size(key)
    set_incremental_id_slice_size(size, key = key)
    try:
        yield None
    finally:
        set_incremental_id_slice_size(prev_size, key = key)

@when(datastore.connection_opened)
def create_container(event):
    root = event.source.root
    if ID_CONTAINER_KEY not in root:
        root[ID_CONTAINER_KEY] = PersistentMapping()
        datastore.commit()

@when(datastore.storage_changed)
@when(datastore.cleared)
def discard_acquired_ids(event):
    with _lock:
        _acquired_ids.clear()

def incremental_id(key = "default", step = None):

    with _lock:
        key_acquired_ids = _acquired_ids.get(key)

        if not key_acquired_ids:
            if step is None:
                step = get_incremental_id_slice_size(key)
            acquire_id_range(step, key)

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
                top_id = base_id + size

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

def reset_incremental_id(value = 0, key = "default"):

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

                container[key] = value

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

        _acquired_ids[key] = None

