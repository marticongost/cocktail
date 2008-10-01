#-*- coding: utf-8 -*-
"""
Implements the persistence machinery for CMS objects. It builds on Zope's
Object Data Base (ZODB), adding support for multi-language content, versioning
and declarative queries over indices.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.persistence.entity import Entity, EntityClass, EntityAccessor
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.index import Index
from cocktail.persistence.query import Query

