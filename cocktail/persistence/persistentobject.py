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
from cocktail.modeling import getter
from cocktail.events import Event, event_handler
from cocktail.schema import SchemaClass, SchemaObject, Reference, Collection
from cocktail.schema.exceptions import ValidationError
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.query import Query
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

# Cascade delete
def _get_cascade_delete(self):
    if self._cascade_delete is None:
        return self.integral
    else:
        return self._cascade_delete

def _set_cascade_delete(self, cascade):
    self._cascade_delete = cascade

schema.RelationMember._cascade_delete = None
schema.RelationMember.cascade_delete = property(
    _get_cascade_delete,
    _set_cascade_delete,
    doc = """
    Enables or disables cascade deletion for the relation. When enabled,
    deleting the owner of the relation will also delete all its related objects
    for that relation. This behavior propagates recursively.

    The property is disabled by default.
    
    L{Integral<cocktail.schema.schemarelations.Integral>} relations implicitly
    enable cascade deletion.

    @type: bool
    """)


class PersistentClass(SchemaClass):

    # Avoid creating a duplicate persistent class when copying the class
    _copy_class = schema.Schema
    _generated_id = False
    
    @event_handler
    def handle_member_added(metacls, event):
        
        cls = event.source
        member = event.member

        # Unique values restriction
        if member.unique:
            if cls._unique_validation_rule \
            not in member.validations(recursive = False):
                member.add_validation(cls._unique_validation_rule)

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
    _generates_translation_schema = False
    __inserted = False

    inserting = Event(doc = """
        An event triggered before adding an object to the data store.
        """)

    inserted = Event(doc = """
        An event triggered after an object has been inserted to the data store.
        """)

    deleting = Event(doc = """
        An event triggered before deleting an object from the data store.
        """)

    deleted = Event(doc = """
        An event triggered after an object has been removed from the data
        store.
        """)

    def __init__(self, *args, **kwargs):

        # Generate an incremental ID for the object
        if self.__class__._generated_id:
            pk = self.__class__.primary_member.name
            id = kwargs.get(pk)
            if id is None:
                kwargs[pk] = incremental_id()

        self._v_initializing = True
        SchemaObject.__init__(self, *args, **kwargs)
        self._v_initializing = False

    @classmethod
    def get_instance(cls, _id = None, **criteria):
        """Obtains an instance of the class, using one of its unique indexes.

        @param _id: The primary identifier of the object to retrieve.

        @param criteria: A single keyword parameter, indicating the name of a
            unique member and its value. It is mutually exclusive with L{_id}.
        
        @return: The requested object, if found. Otherwise, None.
        @rtype: L{PersistentObject} or None

        @raise ValueError: Raised when given insufficient, excessive or
            otherwise wrong parameters.
        """
        if _id is not None:
            
            if criteria:
                raise ValueError("Can't call get_instance() using both "
                    "positional and keyword parameters"
                )
            
            member = cls.primary_member

            if member is None:
                raise ValueError(
                    "Can't call get_instance() using a single positional "
                    "argument on a type without a primary member"
                )
                
            value = _id
        else:
            if len(criteria) > 1:
                raise ValueError(
                    "Calling get_instance() using more than one keyword is "
                    "not allowed"
                )

            try:
                key, value = criteria.popitem()
            except KeyError:
                raise ValueError("No criteria given to get_instance()")

            member = cls[key]

        if not member.unique:
            raise ValueError(
                "Can't call get_instance() on a non unique member (%s)"
                % member
            )
        
        match = None
        value = member.get_index_value(value)

        if member.primary:
            match = member.index.get(value)

        elif member.indexed:
            id = member.index.get(value)
            if id is not None:
                match = cls.index.get(id)
        else:
            if not cls.indexed:
                raise ValueError(
                    "Can't call get_instance() if neither the requested class "
                    "or member have an index"
                )
            for instance in cls.index.itervalues():
                if instance.get(member) == value:
                    match = instance
                    break

        if match and not isinstance(match, cls):
            match = None

        return match
    
    @classmethod
    def select(cls, *args, **kwargs):
        """Obtains a selection of instances of the class. Accepts the same
        parameters as the L{Query<cocktail.persistence.query.Query>}
        constructor.

        @return: The requested collection of instances of the class.
        @rtype: L{Query<cocktail.persistence.query.Query>}                
        """
        return Query(cls, *args, **kwargs)

    @classmethod
    def _create_translation_schema(cls, members):
        members["indexed"] = False
        SchemaClass._create_translation_schema(cls, members)

    @event_handler
    def handle_changing(cls, event):

        # Transform collections into their persistent versions
        if isinstance(event.value, list):
            event.value = PersistentList(event.value)
        elif isinstance(event.value, set):
            event.value = PersistentSet(event.value)
        elif isinstance(event.value, dict):
            event.value = PersistentMapping(event.value)

    @getter
    def is_inserted(self):
        """Indicates wether the object has been inserted into the database.
        @type: bool
        """
        return self.__inserted

    def insert(self):
        """Inserts the object into the database."""
        
        if self.__inserted:
            return False
        
        self.inserting()
        self.__inserted = True

        for member in self.__class__.members().itervalues():

            # Insert related objects
            if isinstance(member, Reference):
                related = self.get(member)
                if related \
                and isinstance(related, PersistentObject) \
                and not related.__inserted:
                    related.insert()

            elif isinstance(member, Collection):
                collection = self.get(member)
                if collection:
                    for item in collection:
                        if isinstance(item, PersistentObject) \
                        and not item.__inserted:
                            item.insert()

        self.inserted()
        return True

    def delete(self, deleted_objects = None):
        """Removes the object from the database."""
        
        if not self.__inserted:
            raise NewObjectDeletedError(self)

        if deleted_objects is None:
            deleted_objects = set()
        else:
            if self in deleted_objects:
                return
            else:
                deleted_objects.add(self)

        self.deleting()

        for member in self.__class__.members().itervalues():

            if isinstance(member, schema.RelationMember):

                # Cascade delete
                if member.cascade_delete:
                    value = self.get(member)
                    if value is not None:
                        if isinstance(member, schema.Reference):
                            value.delete(deleted_objects)
                        else:
                            for item in value:
                                item.delete(deleted_objects)

                # Remove all known references to the item (drop all its
                # relations)
                if self._should_erase_member(member):
                    self.set(member, None)

        self.__inserted = False
        self.deleted()

    def _should_erase_member(self, member):

        return self.get(member) is not None and (

            # Reference to an object (not a class)
            (
                isinstance(member, schema.Reference)
                and member.class_family is None
            )
            # Collection of references to objects (not classes or
            # literals)
            # TODO: Add support for nested collections?
            or (
                isinstance(member, schema.Collection)
                and isinstance(member.items, schema.Reference)
                and member.items.class_family is None
            )
        )


PersistentObject._translation_schema_metaclass = PersistentClass
PersistentObject._translation_schema_base = PersistentObject


class UniqueValueError(ValidationError):
    """A validation error produced when a unique field is given a value that is
    already present in the database.
    """

    def __repr__(self):
        return "%s (value already present in the database)" \
            % ValidationError.__repr__(self)


class NewObjectDeletedError(Exception):
    """An error produced when trying to delete an object that hasn't been
    inserted to the data store yet.

    @ivar persistent_object: The object that couldn't be deleted.
    @type persistent_object: L{PersistentObject}
    """

    def __init__(self, persistent_object):
        Exception.__init__(self,
            "%s is not inserted and can't be deleted"
            % persistent_object
        )
        self.persistent_object = persistent_object

