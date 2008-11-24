#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from threading import local
from persistent import Persistent
from difflib import SequenceMatcher
from cocktail.typemapping import TypeMapping
from cocktail.modeling import (
    getter,
    InstrumentedList,
    InstrumentedSet,
    InstrumentedDict
)
from cocktail.persistence.persistentlist import PersistentList
from cocktail.persistence.persistentmapping import PersistentMapping
from cocktail.persistence.persistentset import PersistentSet
from cocktail import schema

_thread_data = local()

relation_add_methods = TypeMapping()
relation_remove_methods = TypeMapping()

def add(collection, item):
    add_method = relation_add_methods.get(collection.__class__)

    if add_method:
        add_method(collection, item)
    else:
        collection.add(item)

def remove(collection, item):
    remove_method = relation_remove_methods.get(collection.__class__) \
        
    if remove_method:
        remove_method(collection, item)
    else:
        collection.remove(item)

def _list_add(collection, item):
    collection.append(item)

def _mapping_add(collection, item):
    collection[item.id] = item

def _mapping_remove(collection, item):
    del collection[item.id]

relation_add_methods[list] = _list_add
relation_add_methods[PersistentList] = _list_add
relation_add_methods[dict] = _mapping_add
relation_add_methods[PersistentMapping] = _mapping_add
relation_remove_methods[dict] = _mapping_remove
relation_remove_methods[PersistentMapping] = _mapping_remove

def _push(action, obj, related_obj, member):
    
    stack = getattr(_thread_data, "stack", None)

    if stack is None:
        stack = []
        _thread_data.stack = stack

    entry = (action, obj, related_obj, member)

    if entry not in stack:
        stack.append(entry)
        return True
    else:
        return False

def _pop():

    stack = getattr(_thread_data, "stack", None)

    if not stack:
        raise ValueError(
            "The relation stack is empty, can't pop its last entry")

    return stack.pop()

def relate(obj, related_obj, member):

    if _push("relate", obj, related_obj, member):
        try:
            if isinstance(member, schema.Reference):
                setattr(obj, member.name, related_obj)
            else:
                collection = getattr(obj, member.name)
                
                if collection is None:
                    
                    # Try to create a new, empty collection automatically
                    collection_type = member.type or member.default_type

                    if collection_type:
                        setattr(obj, member.name, collection_type())
                        collection = getattr(obj, member.name)
                    else:
                        raise ValueError("Error relating %s to %s on %s; "
                            "the target collection is undefined"
                            % (obj, related_obj, member))

                collection.add(related_obj)
        finally:
            _pop()

def unrelate(obj, related_obj, member):

    if _push("unrelate", obj, related_obj, member):
        try:
            if isinstance(member, schema.Reference):
                setattr(obj, member.name, None)
            else:
                getattr(obj, member.name).remove(related_obj)
        finally:
            _pop()

def instrument_collection(collection, owner, member):

    # Lists
    if isinstance(collection, list):
        collection = RelationList(
            PersistentList(collection), owner, member
        )
    elif isinstance(collection, PersistentList):
        collection = RelationList(collection, owner, member)

    # Sets
    elif isinstance(collection, set):
        collection = RelationSet(
            PersistentSet(collection), owner, member
        )
    elif isinstance(collection, PersistentSet):
        collection = RelationSet(collection, owner, member)

    # Mappings
    elif isinstance(collection, dict):
        collection = relations.RelationMapping(
            PersistentMapping(collection), owner, member
        )        
    elif isinstance(collection, PersistentMapping):
        collection = RelationMapping(collection, owner, member)

    return collection


class RelationCollection(Persistent):

    owner = None
    member = None
    __member_name = None
    _v_member = None

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

    def item_added(self, item):
        
        _push("relate", self.owner, item, self.member)
        
        try:
            relate(item, self.owner, self.member.related_end)
        finally:
            _pop()
        
        self._p_changed = True
        
    def item_removed(self, item):
        
        _push("unrelate", self.owner, item, self.member)

        try:
            unrelate(item, self.owner, self.member.related_end)
        finally:
            _pop()

        self._p_changed = True


class RelationList(RelationCollection, InstrumentedList):
    
    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member
        InstrumentedList.__init__(self)
        if items:
            for item in items:
                self.append(item)

    def add(self, item):
        self.append(item)

    def set_content(self, new_content):

        if not new_content:
            while self._items:
                self.pop(0)
        else:
            if not hasattr(new_content, "__iter__") \
            or not hasattr(new_content, "__getitem__"):
                raise TypeError(
                    "%s is not a valid collection for a relation list"
                    % new_content
                )

            diff = SequenceMatcher(None, self._items, new_content)
            previous_content = self._items
            self._items = new_content
            
            for tag, alo, ahi, blo, bhi in diff.get_opcodes():
                if tag == "replace":
                    for item in previous_content[alo:ahi]:
                        self.item_removed(item)
                    for item in new_content[blo:bhi]:
                        self.item_added(item)
                elif tag == "delete":
                    for item in previous_content[alo:ahi]:
                        self.item_removed(item)
                elif tag == "insert":
                    for item in new_content[blo:bhi]:
                        self.item_added(item)
                elif tag == "equal":
                    pass


class RelationSet(RelationCollection, InstrumentedSet):
    
    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member
        InstrumentedSet.__init__(self)
        if items:
            for item in items:
                self.add(item)

    def set_content(self, new_content):

        if new_content is None:
            self.clear()
        else:
            if not isinstance(new_content, set):
                new_content = set(new_content)
            
            previous_content = self._items
            self._items = new_content

            for item in previous_content - new_content:
                self.item_removed(item)

            for item in new_content - previous_content:
                self.item_added(item)
        

class RelationMapping(RelationCollection, InstrumentedDict):
    
    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member
        InstrumentedDict.__init__(self)
        if items:
            for item in items:
                self.add(item)

    def get_item_key(self, item):
        if self.member.get_item_key:
            return self.member.get_item_key(self, item)
        else:
            raise TypeError("Don't know how to obtain a key from %s; "
                "the collection hasn't overriden its get_item_key() method."
                % item)

    def item_added(self, item):
        RelationCollection.item_added(self, item[1])

    def item_removed(self, item):
        RelationCollection.item_removed(self, item[1])

    def add(self, item):
        self[self.get_item_key(item)] = item

    def remove(self, item):
        del self[self.get_item_key(item)]

    def set_content(self, new_content):

        if new_content is None:
            self.clear()
        else:
            new_content = set(
                (self.get_item_key(item), item)
                for item in new_content
            )
            
            previous_content = set(self._items.iteritems())
            self._items = dict(new_content)

            for pair in previous_content - new_content:
                self.item_removed(pair)

            for pair in new_content - previous_content:
                self.item_added(pair)


def _get_related_end(self):
    """Gets the opposite end of a bidirectional relation.
    @type: L{Member<member.Member>}
    """    
    if self._related_end:
        return self._related_end
    
    member = None
    related_type = _get_related_type(self)

    if self.related_key:
        member = related_type[self.related_key]

        if not getattr(member, "bidirectional", False) \
        or (member.related_key and member.related_key != self.name):
            member = None
    else:
        for member in related_type.members().itervalues():
            if getattr(member, "bidirectional", False):
                if member.related_key:
                    if self.name == member.related_key:
                        break
                elif self.schema is _get_related_type(member):
                    break
    
    if member is None:
        raise TypeError("Couldn't find the related end for %s" % self)
    
    self._related_end = member
    return member

def _get_related_type(member):
    if isinstance(member, schema.Reference):
        return member.type
    elif isinstance(member, schema.Mapping):
        return member.values.type
    else:
        return member.items.type

schema.Reference.bidirectional = False
schema.Reference._related_end = None
schema.Reference.related_end = getter(_get_related_end)
schema.Reference.related_key = None

schema.Collection.bidirectional = False
schema.Collection._related_end = None
schema.Collection.related_end = getter(_get_related_end)
schema.Collection.related_key = None
schema.Collection.type = PersistentList

schema.Mapping.get_item_key = None
schema.Mapping.bidirectional_keys = False
schema.Mapping.bidirectional_values = False
schema.Mapping.bidirectional = getter(
    lambda self: self.bidirectional_keys or self.bidirectional_values
)
schema.Mapping.type = PersistentMapping

