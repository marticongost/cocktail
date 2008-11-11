#-*- coding: utf-8 -*-
"""
This package provides a set of high level interfaces for object persistence.
It's built as declarative layer over Zope's Object Data Base (ZODB), adding
support for multi-language content and declarative queries over indices.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.persistence.persistentlist import PersistentList
from cocktail.persistence.persistentmapping import PersistentMapping
from cocktail.persistence.persistentset import PersistentSet
from cocktail.persistence.entity import Entity, EntityClass, EntityAccessor
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.index import Index
from cocktail.persistence.query import Query

