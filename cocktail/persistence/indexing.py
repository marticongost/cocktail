#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""

from BTrees.IOBTree import IOBTree, IOTreeSet
from BTrees.OOBTree import OOBTree, OOTreeSet
from cocktail.modeling import getter
from cocktail.events import when
from cocktail import schema
from cocktail.persistence.datastore import datastore
from cocktail.persistence.index import Index
from cocktail.persistence.persistentobject import (
    PersistentObject, PersistentClass
)

# Index properties
#------------------------------------------------------------------------------

schema.expressions.Expression.index = None
schema.Member.indexed = False
schema.Member.index_type = OOBTree

PersistentObject.indexed = True

def _get_index(self):

    if not self.indexed:
        return None

    if isinstance(self, PersistentClass):
        return self.primary_member.index
    
    index = datastore.root.get(self.index_key)

    if index is None:
        return self.create_index()

    return index

def _set_index(self, index):
    datastore.root[self.index_key] = index

schema.Member.index = property(_get_index, _set_index, doc = """
    Gets or sets the index for the members.
    """)

def _get_index_key(self):
    if self._index_key is not None:
        return self._index_key
    elif isinstance(self, PersistentClass):
        return self.primary_member.index_key
    else:
        return (
            self.schema
            and self.name
            and self.schema.full_name + "." + self.name
        ) or None

def _set_index_key(self, index_key):
    self._index_key = index_key

schema.Member._index_key = None
schema.Member.index_key = property(_get_index_key, _set_index_key)

def _get_integer_index_type(self):
    return self._index_type \
        or (IOBTree if self.required else OOBTree)

def _set_integer_index_type(self, index_type):
    self._index_type = index_type

schema.Integer._index_type = None
schema.Integer.index_type = property(
    _get_integer_index_type,
    _set_integer_index_type
)

def _get_persistent_class_keys(cls):

    index_key = cls.full_name + "-keys"
    keys = datastore.root.get(index_key)

    if keys is None:

        if isinstance(cls.primary_member, schema.Integer):
            keys = IOTreeSet()
        else:
            keys = OOTreeSet()

        datastore.root[index_key] = keys

    return keys

PersistentClass.keys = getter(_get_persistent_class_keys)

def _get_unique(self):
    return self.primary or self._unique

def _set_unique(self, unique):
    if self.primary and not unique:
        raise TypeError("Primary members can't be declared to be non unique")
    self._unique = unique

schema.Member._unique = False
schema.Member.unique = property(_get_unique, _set_unique)

def _get_required(self):
    return self.primary or self._required

def _set_required(self, required):
    if self.primary and not required:
        raise TypeError("Primary members can't be declared to be optional")
    self._required = required

schema.Member._required = False
schema.Member.required = property(_get_required, _set_required)

# Indexing functions
#------------------------------------------------------------------------------

def _create_index(self):

    if not self.indexed:
        raise ValueError("Can't create an index for a non indexed member")

    # Primary index
    if isinstance(self, PersistentClass):
        index = self.primary_member.index_type()

    # Unique indexes use a "raw" ZODB binary tree
    elif self.unique:
        index = self.index_type()

    # Multi-value indexes are wrapped inside an Index instance,
    # which organizes colliding keys into sets of values
    else:
        index = Index(self.index_type())

    datastore.root[self.index_key] = index
    return index

schema.Member.create_index = _create_index

def _rebuild_index(self):

    self.create_index()

    for obj in self.schema.select():
        if obj.indexed:
            if self.translated:
                for language in obj.translations:
                    value = obj.get(self, language)
                    add_index_entry(obj, self, value, language)
            else:            
                add_index_entry(obj, self, obj.get(self))

schema.Member.rebuild_index = _rebuild_index

def _rebuild_indexes(cls, recursive = False, verbose = True):
    
    if cls.indexed:
        for member in cls.members(False).itervalues():
            if member.indexed and not member.primary:
                if verbose:
                    print "Rebuilding index for %s" % member
                member.rebuild_index()

        if recursive:
            for subclass in cls.derived_schemas():
                subclass.rebuild_indexes(True)

PersistentClass.rebuild_indexes = _rebuild_indexes

@when(PersistentObject.declared)
def _handle_declared(event):

    cls = event.source

    # Add 'id' as an alias for custom primary members
    if cls.primary_member:
        if cls.primary_member.schema is cls \
        and cls.primary_member.name != "id":
            cls.id = cls.__dict__[cls.primary_member.name]

    # Add an 'id' field to all indexed schemas that don't define their
    # own primary member explicitly. Will be initialized to an
    # incremental integer.
    elif cls.indexed:
        cls._generated_id = True
        cls.id = schema.Integer(
            name = "id",
            primary = True,
            unique = True,
            required = True,
            indexed = True
        )
        cls.add_member(cls.id)

@when(PersistentObject.changed)
def _handle_changed(event):
    if event.source._should_index_member(event.member) \
    and event.source.is_inserted \
    and event.previous_value != event.value:
        remove_index_entry(
            event.source,
            event.member,
            event.previous_value,
            event.language
        )
        add_index_entry(
            event.source,
            event.member,
            event.value,
            event.language
        )

@when(PersistentObject.inserting)
def _handle_inserting(event):

    obj = event.source

    # ID indexes
    id = obj.id

    for cls in obj.__class__.ascend_inheritance(True):
        if cls.indexed and cls is not PersistentObject:
            keys = cls.keys
            if id in keys:
                raise IdCollisionError()
            keys.insert(id)

    # Regular indexes
    for member in obj.__class__.members().itervalues():

        # Indexing
        if obj._should_index_member(member):

            if member.translated:
                for language in obj.translations:
                    value = obj.get(member, language)
                    add_index_entry(obj, member, value, language)
            else:            
                add_index_entry(obj, member, obj.get(member))

@when(PersistentObject.deleting)
def _handle_deleting(event):

    obj = event.source

    if obj.indexed:
        
        id = obj.id

        # Remove the item from ID indexes
        for cls in obj.__class__.ascend_inheritance(True):
            if cls.indexed and cls is not PersistentObject:
                try:
                    cls.keys.remove(id)
                except KeyError:
                    pass

        # Remove the item from the rest of indexes
        if obj.__class__.translated:
            languages = obj.translations.keys()

        for member in obj.__class__.members().itervalues():
            
            if member.indexed:
                if member.translated:
                    for language in languages:
                        remove_index_entry(
                            obj,
                            member,
                            obj.get(member, language),
                            language
                        )
                else:
                    remove_index_entry(obj, member, obj.get(member))

def add_index_entry(obj, member, value, language = None):
            
    k = member.get_index_value(value)
        
    if language:
        k = (language, k)
    
    v = obj if member.primary else obj.id

    if member.unique:
        member.index[k] = v
    else:
        member.index.add(k, v)

def remove_index_entry(obj, member, value, language = None):
    
    k = member.get_index_value(value)
        
    if language:
        k = (language, k)

    if member.unique:
        try:
            del member.index[k]
        except TypeError:
            if value is not None:
                raise        
        except KeyError:
            pass
    else:
        member.index.remove(k, obj.id)

def _member_get_index_value(self, value):
    return value

schema.Member.get_index_value = _member_get_index_value

def _string_get_index_value(self, value):
    if value is not None and self.normalized_index:
        return schema.expressions.normalize(value)
    else:
        return value

schema.String.get_index_value = _string_get_index_value
schema.String.normalized_index = False

def _reference_get_index_value(self, value):
    if value is not None:
        value = value.id
    return value

schema.Reference.get_index_value = _reference_get_index_value


class IdCollisionError(Exception):
    """An exception raised when trying to insert an object into the datastore
    using an ID that already exists."""

