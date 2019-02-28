#-*- coding: utf-8 -*-
"""
This package provides a set of high level interfaces for object persistence.
It's built as a declarative layer over Zope's Object Data Base (ZODB), adding
support for multi-language content and declarative queries over indexes.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from .persistentlist import PersistentList
from .persistentmapping import PersistentMapping
from .persistentset import PersistentSet
from .persistentorderedset import PersistentOrderedSet
from .persistentrelations import (
    PersistentRelationList,
    PersistentRelationSet,
    PersistentRelationOrderedSet,
    PersistentRelationMapping
)
from .persistentobject import (
    PersistentClass,
    PersistentObject,
    UniqueValueError,
    InstanceNotFoundError,
    NewObjectDeletedError
)
from .datastore import datastore
from .transactional import (
    transactional,
    transaction,
    desisted
)
from .migration import (
    migrate,
    mark_all_migrations_as_executed,
    MigrationStep,
    migration_step
)
from .incremental_id import (
    incremental_id,
    acquire_id_range,
    reset_incremental_id,
    get_incremental_id_slice_size,
    set_incremental_id_slice_size,
    incremental_id_slice_size_context
)
from .index import Index
from .singlevalueindex import SingleValueIndex
from .multiplevaluesindex import MultipleValuesIndex
from . import indexing
from . import fulltextsearch
from .maxvalue import MaxValue
from .query import Query
from .pickling import dumps, loads
from .deletedryrun import delete_dry_run

