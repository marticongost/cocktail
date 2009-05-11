#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from persistent import Persistent
from cocktail.schema import (
    RelationList,
    RelationSet,
    RelationOrderedSet,
    RelationMapping
)
from cocktail.persistence.persistentlist import PersistentList
from cocktail.persistence.persistentset import PersistentSet
from cocktail.persistence.persistentorderedset import PersistentOrderedSet
from cocktail.persistence.persistentmapping import PersistentMapping

class PersistentRelationCollection(Persistent):

    _base_collection_class = None
    _inner_collection_class = None
    __items = None
    __member_name = None
    _v_member = None

    def __init__(self, items = None, owner = None, member = None):

        if items is None:
            items = self._inner_collection_class()
        elif not isinstance(items, self._inner_collection_class):
            items = self._inner_collection_class(items)

        self._base_collection_class.__init__(self, items, owner, member)

    def _get_member(self):
        if self._v_member is None \
        and self.__member_name \
        and self.owner:
            self._v_member = self.owner.__class__[self.__member_name]

        return self._v_member

    def _set_member(self, member):

        if isinstance(member, basestring):
            self.__member_name = member
            self._v_member = None
        else:
            self.__member_name = member.name
            self._v_member = member

    member = property(_get_member, _set_member, doc = """
        Gets or sets the schema member that the collection represents.
        @type: L{Collection<cocktail.schema.schemacollections.Collection>}
        """)

    # Make sure the inner data structure is always an instance of the
    # persistent collection for the class
    def _get_items(self):
        return self.__items

    def _set_items(self, items):
        if not isinstance(items, self._inner_collection_class):
            items = self._inner_collection_class(items)
        self.__items = items

    _items = property(_get_items, _set_items)

    def item_added(self, item):
        self._base_collection_class.item_added(self, item)
        self._p_changed = True
        
    def item_removed(self, item):
        self._base_collection_class.item_removed(self, item)
        self._p_changed = True


class PersistentRelationList(PersistentRelationCollection, RelationList):
    _base_collection_class = RelationList
    _inner_collection_class = PersistentList


class PersistentRelationSet(PersistentRelationCollection, RelationSet):
    _base_collection_class = RelationSet
    _inner_collection_class = PersistentSet


class PersistentRelationOrderedSet(
    PersistentRelationCollection,
    RelationOrderedSet
):
    _base_collection_class = RelationOrderedSet
    _inner_collection_class = PersistentOrderedSet


class PersistentRelationMapping(PersistentRelationCollection, RelationMapping):
    _base_collection_class = RelationMapping
    _inner_collection_class = PersistentMapping

