#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sys
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from cocktail import schema
from cocktail.schema import SchemaClass, SchemaObject
from cocktail.schema.exceptions import ValidationError
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.index import Index
from cocktail.persistence.persistentlist import PersistentList
from cocktail.persistence.persistentmapping import PersistentMapping
from cocktail.persistence.persistentset import PersistentSet
from cocktail.persistence.persistentrelations import (
    PersistentRelationList,
    PersistentRelationSet,
    PersistentRelationMapping
)

# Class stub
PersistentObject = None

# Indexing
schema.Member.indexed = False
schema.Member.index_key = None
schema.Member.index_type = OOBTree
schema.Integer.index_type = IOBTree
schema.Member.primary = False
schema.Member.unique = False
schema.Schema.primary_member = None

def _get_index(self):

    if not self.indexed:
        return None
    elif self.primary:
        return self.schema.index

    root = datastore.root
    index = root.get(self.index_key)

    if index is None:
        
        # Primary index
        if isinstance(self, schema.Schema):
            index = self.primary_member.index_type()
        
        # Unique indices use a "raw" ZODB binary tree
        elif self.unique:
            index = self.index_type()

        # Multi-value indices are wrapped inside an Index instance,
        # which organizes colliding keys into sets of values
        else:
            index = Index(self.index_type())

        root[self.index_key] = index

    return index

def _set_index(self, index):
    datastore.root[self.index_key] = index

schema.Member.index = property(_get_index, _set_index, doc = """
    Gets or sets the index for the members.
    """)

class PersistentClass(SchemaClass):

    # Avoid creating a duplicate persistent class when copying the class
    _copy_class = schema.Schema


    def __init__(cls, name, bases, members):
         
        SchemaClass.__init__(cls, name, bases, members)

        cls._sealed = False

        # Instance index
        if cls.indexed and PersistentObject and cls is not PersistentObject:

            cls.index_key = cls.full_name

            # Add an 'id' field to all indexed schemas that don't define their
            # own primary member explicitly. Will be initialized to an
            # incremental integer.
            if not cls.primary_member:
                cls.id = schema.Integer(
                    name = "id",
                    primary = True,
                    unique = True,
                    required = True,
                    indexed = True,
                    default = schema.DynamicDefault(incremental_id)
                )
                cls.add_member(cls.id)
                print "Added member 'id' to %s" % cls.full_name

        cls._sealed = True

    def _check_member(cls, member):

        SchemaClass._check_member(cls, member)

        # Unique members require a general class index, or a specific index for
        # the member
        if member.unique and not (member.indexed or cls.indexed):
            raise ValueError(
                "Can't enforce the unique constraint on %s.%s "
                "without a class or member index"
                % (cls.full_name, member.name))

    def _add_member(cls, member):
       
        SchemaClass._add_member(cls, member)

        # Unique values restriction/index
        if member.unique:
            if cls._unique_validation_rule \
            not in member.validations(recursive = False):
                member.add_validation(cls._unique_validation_rule)
        
        # Every indexed member gets its own btree
        if member.indexed and member.index_key is None:
            member.index_key = cls.full_name + "." + member.name
        
    def _unique_validation_rule(cls, member, value, context):

        duplicate = None
        validable = cls._get_unique_validable(context)
        
        if isinstance(validable, PersistentObject):
            if member.indexed:
                if member.translated:
                    value = (context["language"], value)
                duplicate = member.index.get(value)
            else:
                if member.schema.adaptation_source:
                    index = member.schema.adaptation_source.index
                else:
                    index = member.schema.index

                language = context["language"]

                for instance in index.itervalues():
                    if instance.get(member, language) == value:
                        duplicate = instance
                        break

            if duplicate and duplicate is not validable:
                yield UniqueValueError(member, value, context)

    def _get_unique_validable(cls, context):
        return context.get("persistent_object", context.validable)
      
    class MemberDescriptor(SchemaClass.MemberDescriptor):

        def __set__(self, instance, value, language = None):

            # Transform collections into their persistent versions
            if isinstance(value, list):
                value = PersistentList(value)
            elif isinstance(value, set):
                value = PersistentSet(value)
            elif isinstance(value, dict):
                value = PersistentMapping(value)

            indexed = self.member.indexed

            if indexed:
                previous_value = self.__get__(instance, language = language)
        
            SchemaClass.MemberDescriptor.__set__(
                self, instance, value, language)
            
            # Update the index for the member
            if indexed:
                new_value = self.__get__(instance, language = language)
                instance._update_index(
                    self.member, language, previous_value, new_value)

        def instrument_collection(self, collection, owner, member):
            
            # Lists
            if isinstance(collection, (list, PersistentList)):
                collection = PersistentRelationList(
                    collection, owner, member
                )
            # Sets
            elif isinstance(collection, (set, PersistentSet)):
                collection = PersistentRelationSet(
                    collection, owner, member
                )
            # Mappings
            elif isinstance(collection, (dict, PersistentMapping)):
                collection = PersistentRelationMapping(
                    collection, owner, member
                )

            return collection


class PersistentObject(SchemaObject, Persistent):
    
    __metaclass__ = PersistentClass

    indexed = True

    def __init__(self, *args, **kwargs):
        self._v_initializing = True
        SchemaObject.__init__(self, *args, **kwargs)
        self._v_initializing = False

    def _update_index(self, member, language, previous_value, new_value):

        if member.indexed and previous_value != new_value:
            
            if language:
                previous_index_value = (language, previous_value)
                new_index_value = (language, new_value)
            else:
                previous_index_value = previous_value
                new_index_value = new_value

            if member.primary:
                for schema in self.__class__.ascend_inheritance(True):
                    if previous_value is not None:
                        del schema.index[previous_index_value]
                    if new_value is not None:
                        schema.index[new_index_value] = self

            elif member.unique:
                if previous_value is not None:
                    del member.index[previous_index_value]

                if new_value is not None:
                    member.index[new_index_value] = self
            else:
                if previous_value is not None:
                    member.index.remove(previous_index_value, self)

                if new_value is not None:
                    member.index.add(new_index_value, self)
 
    def delete(self):

        # Remove the item from primary indices
        if self.__class__.indexed:
            for cls in self.__class__.ascend_inheritance(True):
                cls.index.pop(self.id, None)

        # Remove the item from the rest of indices
        if self.__class__.translated:
            languages = self.translations.keys()

        for member in self.__class__.members().itervalues():

            if member.indexed and not member.primary:
                if member.translated:
                    for language in languages:
                        value = self.get(member, language)
                        if value is not None:
                            if member.unique:
                                member.index.pop((language, value), None)
                            else:
                                member.index.remove((language, value), self)
                else:
                    value = self.get(member)
                    if value is not None:
                        if member.unique:
                            member.index.pop(value, None)
                        else:
                            member.index.remove(value, self)

            # Remove all known references to the item (drop all its
            # bidirectional relations)
            if isinstance(member, (schema.Reference, schema.Collection)) \
            and member.bidirectional \
            and self.get(member) is not None:
                self.set(member, None)


class UniqueValueError(ValidationError):
    """A validation error produced when a unique field is given a value that is
    already present in the database.
    """

    def __repr__(self):
        return "%s (value already present in the database)" \
            % ValidationError.__repr__(self)

