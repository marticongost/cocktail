#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from types import FunctionType
from threading import local, RLock
from weakref import WeakKeyDictionary
from ZODB import DB
import transaction
from cocktail.modeling import getter
from cocktail.events import Event


class DataStore(object):
    """A thread safe wrapper over the application's object database. Normally
    used through its global L{datastore} instance.

    The class expects an X{storage} setting, containing a
    L{storage<ZODB.BaseStorage.BaseStorage>} instance pointing to the physical
    location of the database (see the ZODB documentation for more details).
    """
    automatic_migration = False

    def __init__(self, storage = None):
        self._thread_data = local()
        self.__storage_lock = RLock()
        self.__db = None
        self.__storage = None
        self.storage = storage

    storage_changed = Event("""
        An event triggered when changing which storage is used by the
        datastore.
        """)

    connection_opened = Event("""
        An event triggered when the datastore spawns a new thread-bound
        connection.

        @ivar connection: The new connection.
        @type connection: L{Connection<>}
        """)

    def _get_storage(self):
        if isinstance(self.__storage, FunctionType):
            self.__storage_lock.acquire()
            try:
                if isinstance(self.__storage, FunctionType):
                    self.__storage = self.__storage()
                    self.__possibly_migrate()
            finally:
                self.__storage_lock.release()
        return self.__storage

    def _set_storage(self, storage):
        self.__storage_lock.acquire()
        try:
            self.__storage = storage
            self.__db = None
            self.__possibly_migrate()
            self.storage_changed()
        finally:
            self.__storage_lock.release()

    storage = property(_get_storage, _set_storage, doc = """
        Gets or sets the underlying ZODB storage for the data store.
        @type: L{ZODB.Storage}
        """)

    def __possibly_migrate(self):
        if self.automatic_migration \
        and self.__storage is not None \
        and not isinstance(self.__storage, FunctionType):
            from cocktail.persistence.migration import migrate
            migrate()

    @getter
    def db(self):
        if self.__db is None:
            self.__db = DB(self.storage)

        return self.__db

    @getter
    def root(self):
        """Gives access to the root container of the database. The property is
        thread safe; accessing it on different threads will produce different
        containers, each bound to a separate database connection.
        @type: mapping
        """
        root = getattr(self._thread_data, "root", None)

        if root is None:
            root = self.connection.root()
            self._thread_data.root = root

        return root

    @getter
    def connection(self):
        """Returns the database connection for the current thread. The property
        is thread safe; accessing it on different threads will produce
        different connections. Once called, each connection remains bound to a
        single thread until the thread finishes or the datastore's L{close}
        method is called.
        @type: L{Connection<ZODB.Connection.Connection>}
        """
        connection = getattr(self._thread_data, "connection", None)

        if connection is None:
            connection = self.db.open()
            self._thread_data.connection = connection
            self.connection_opened(connection = connection)

        return connection

    commit = transaction.commit
    abort = transaction.abort

    def close(self):
        """Closes the connection to the database for the current thread.
        Accessing the L{root} or L{connection} properties after this method is
        called will spawn a new database connection.
        """
        if hasattr(self._thread_data, "root"):
            self._thread_data.root = None

        connection = getattr(self._thread_data, "connection", None)

        if connection is not None:
            self._thread_data.connection.close()
            self._thread_data.connection = None

    def sync(self):
        self._thread_data.root = None
        self.connection.sync()

    def _get_transaction_data(self, create_if_missing = False):

        thread_transaction_data = getattr(
            self._thread_data,
            "transaction_data",
            None
        )

        if thread_transaction_data is None:
            thread_transaction_data = WeakKeyDictionary()
            self._thread_data.transaction_data = thread_transaction_data

        transaction = self.connection.transaction_manager.get()
        transaction_data = thread_transaction_data.get(transaction)

        if transaction_data is None and create_if_missing:
            transaction_data = {}
            thread_transaction_data[transaction] = transaction_data

        return transaction_data

    def get_transaction_value(self, key, default = None):

        transaction_data = self._get_transaction_data()

        if transaction_data is None:
            return default

        return transaction_data.get(key, default)

    def set_transaction_value(self, key, value):
        transaction_data = self._get_transaction_data(True)
        transaction_data[key] = value

    def unique_after_commit_hook(self, id, callback, *args, **kwargs):

        key = "cocktail.persistence.unique_after_commit_hooks"
        unique_after_commit_hooks = self.get_transaction_value(key)

        if unique_after_commit_hooks is None:
            unique_after_commit_hooks = set([id])
            self.set_transaction_value(key, unique_after_commit_hooks)
        elif id in unique_after_commit_hooks:
            return False
        else:
            unique_after_commit_hooks.add(id)

        transaction = self.connection.transaction_manager.get()
        transaction.addAfterCommitHook(callback, args, kwargs)
        return True

datastore = DataStore()

