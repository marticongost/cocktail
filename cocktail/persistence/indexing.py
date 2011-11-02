#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""

from BTrees.IOBTree import IOBTree, IOTreeSet
from BTrees.OOBTree import OOBTree, OOTreeSet
from cocktail.stringutils import normalize
from cocktail.modeling import getter
from cocktail.events import when
from cocktail import schema
from cocktail.persistence.datastore import datastore
from cocktail.persistence.index import SingleValueIndex, MultipleValuesIndex
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
    elif self.copy_source:
        return self.copy_source.index_key
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
        return self.primary_member.create_index()

    # Single-value indexes
    if self.unique and self.required:
        index = SingleValueIndex()

    # Multi-value indexes are handled by the Index class
    else:
        index = MultipleValuesIndex()

    datastore.root[self.index_key] = index
    return index

schema.Member.create_index = _create_index

def _rebuild_index(self):

    self.create_index()

    for obj in self.schema.select():
        if obj.indexed and obj._should_index_member(self):
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
            
            if member.indexed and obj._should_index_member(member):
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

@when(PersistentObject.removing_translation)
def _handle_removing_translation(event):
    obj = event.source
    language = event.language
    translation = event.translation

    if obj.indexed:

        for member in obj.__class__.members().itervalues():
            if member.translated \
            and member.indexed \
            and obj._should_index_member(member):
                remove_index_entry(
                    obj,
                    member,
                    obj.get(member, language),
                    language
                )

def add_index_entry(obj, member, value, language = None):
            
    k = member.get_index_value(value)
        
    if language:
        k = (language, k)
    
    v = obj if member.primary else obj.id
    member.index.add(k, v)

def remove_index_entry(obj, member, value, language = None):
    
    key = member.get_index_value(value)
        
    if language:
        key = (language, key)

    if member.index.accepts_multiple_values:
        member.index.remove(key, obj.id)
    else:
        member.index.remove(key)

def _member_get_index_value(self, value):
    return value

schema.Member.get_index_value = _member_get_index_value

def _string_get_index_value(self, value):
    if value is not None and self.normalized_index:
        return normalize(value)
    else:
        return value

schema.String.get_index_value = _string_get_index_value
schema.String.normalized_index = False

def _datetime_get_index_value(self, value):
    if value is not None:
        value = (
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond
        )
    return value

schema.DateTime.get_index_value = _datetime_get_index_value

def _date_get_index_value(self, value):
    if value is not None:
        value = (
            value.year,
            value.month,
            value.day
        )
    return value

schema.Date.get_index_value = _date_get_index_value

def _time_get_index_value(self, value):
    if value is not None:
        value = (
            value.hour,
            value.minute,
            value.second,
            value.microsecond
        )
    return value

schema.Time.get_index_value = _time_get_index_value

def _reference_get_index_value(self, value):
    if value is not None:
        value = value.id
    return value

schema.Reference.get_index_value = _reference_get_index_value


class IdCollisionError(Exception):
    """An exception raised when trying to insert an object into the datastore
    using an ID that already exists."""

