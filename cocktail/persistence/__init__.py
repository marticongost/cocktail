#-*- coding: utf-8 -*-
u"""
This package provides a set of high level interfaces for object persistence.
It's built as a declarative layer over Zope's Object Data Base (ZODB), adding
support for multi-language content and declarative queries over indexes.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.persistence.persistentlist import PersistentList
from cocktail.persistence.persistentmapping import PersistentMapping
from cocktail.persistence.persistentset import PersistentSet
from cocktail.persistence.persistentorderedset import PersistentOrderedSet
from cocktail.persistence.persistentrelations import (
    PersistentRelationList,
    PersistentRelationSet,
    PersistentRelationOrderedSet,
    PersistentRelationMapping
)
from cocktail.persistence.persistentobject import (
    PersistentClass, PersistentObject, UniqueValueError, NewObjectDeletedError
)
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.index import Index
from cocktail.persistence import indexing
from cocktail.persistence.query import Query

