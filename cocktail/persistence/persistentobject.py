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
from cocktail.modeling import OrderedSet
from cocktail.events import Event, event_handler
from cocktail.translations import translations
from cocktail.schema import (
    SchemaClass,
    SchemaObject,
    String,
    Reference,
    Collection,
    TranslationMapping
)
from cocktail.schema.exceptions import ValidationError
from cocktail.schema.expressions import (
    Expression, CustomExpression, ExclusionExpression, Self
)
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.query import Query
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

translations.load_bundle("cocktail.persistence.persistentobject")

# Add an extension property to allow relations to block a delete operation if
# the relation is not empty
schema.RelationMember.block_delete = False

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

    L{Integral<cocktail.schema.schemarelations.RelationMember.integral>}
    relations implicitly enable cascade deletion.

    @type: bool
    """)

def _get_reference_is_persistent_relation(self):
    return self.type and issubclass(self.type, PersistentObject)

schema.Reference.is_persistent_relation = \
    property(_get_reference_is_persistent_relation)

def _get_collection_is_persistent_relation(self):
    items = self.items
    return items \
        and isinstance(items, Reference) \
        and items.is_persistent_relation

schema.Collection.is_persistent_relation = \
    property(_get_collection_is_persistent_relation)

class PersistentClass(SchemaClass):

    # Avoid creating a duplicate persistent class when copying the class
    _copy_class = schema.Schema
    _generated_id = False

    @event_handler
    def handle_member_added(event):

        cls = event.source
        member = event.member

        # Unique values restriction
        if member.unique:
            if (
                unique_validation_rule
                not in member.validations(recursive = False)
            ):
                member.add_validation(unique_validation_rule)

    class MemberDescriptor(SchemaClass.MemberDescriptor):

        def get_instrumented_collection_type(self, collection):

            # Lists
            if isinstance(collection, (list, PersistentList)):
                return PersistentRelationList
            # Sets
            elif isinstance(collection, (set, PersistentSet)):
                return PersistentRelationSet
            # Ordered sets
            elif isinstance(collection, (OrderedSet, PersistentOrderedSet)):
                return PersistentRelationOrderedSet
            # Mappings
            elif isinstance(collection, (dict, PersistentMapping)):
                return PersistentRelationMapping

            return collection

    def _create_translations_member(cls):
        translations_member = SchemaClass._create_translations_member(cls)
        translations_member.produce_default = lambda instance: \
            PersistentMapping(items = TranslationMapping(instance))
        return translations_member


class PersistentObject(SchemaObject, Persistent, metaclass=PersistentClass):

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
        self._v_initializing = True
        SchemaObject.__init__(self, *args, **kwargs)
        self._v_initializing = False

    def require_id(self):

        if not self.__class__._generated_id:
            return None

        primary = self.__class__.primary_member
        id = self.get(primary)

        if id is None:
            id = incremental_id()
            self.set(primary, id)

        return id

    @classmethod
    def new(cls, *args, **kwargs):
        """A convenience method that creates and inserts an instance of the
        class.

        @return: The created instance.
        @rtype: L{PersistentObject}
        """
        instance = cls(*args, **kwargs)
        instance.insert()
        return instance

    @classmethod
    def get_instance(cls, id = None, **criteria):
        """Obtains an instance of the class, using one of its unique indexes.

        @param _id: The primary identifier of the object to retrieve.

        @param criteria: A single keyword parameter, indicating the name of a
            unique member and its value. It is mutually exclusive with L{id}.

        @return: The requested object, if found. Otherwise, None.
        @rtype: L{PersistentObject} or None
        """
        if id is not None:

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

            value = id
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
            if member.index.accepts_multiple_values:
                for id in member.index.values(key = value):
                    break
            else:
                id = member.index.get(value)
            if id is not None:
                match = cls.index.get(id)
        else:
            if not cls.indexed:
                raise ValueError(
                    "Can't call get_instance() if neither the requested class "
                    "or member have an index"
                )
            for instance in list(cls.index.values()):
                if instance.get(member) == value:
                    match = instance
                    break

        if match and not isinstance(match, cls):
            match = None

        return match

    @classmethod
    def require_instance(cls, id = None, **criteria):
        """Obtains an instance of the class or raises an exception.

        @param id: The primary identifier of the object to retrieve.

        @param criteria: A single keyword parameter, indicating the name of a
            unique member and its value. It is mutually exclusive with L{id}.

        @return: The requested object, if found. Otherwise, None.
        @rtype: L{PersistentObject} or None

        @raise L{InstanceNotFoundError}: Raised when the requested instance
            can't be found on the data store.
        """
        instance = cls.get_instance(id, **criteria)

        if instance is None:

            if id is None:
                for key, value in criteria.items():
                    break
            else:
                key = "id"
                value = id

            raise InstanceNotFoundError(
                "Can't find an instance of %s with %s = %r" % (
                    cls, key, value
                )
            )

        return instance

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
    def handle_changing(event):

        # Disallow changing the primary key of an inserted member
        if event.member.primary and event.source.is_inserted:
            raise PrimaryKeyChangedError()

        # Transform collections into their persistent versions
        if isinstance(event.value, list):
            event.value = PersistentList(event.value)
        elif isinstance(event.value, set):
            event.value = PersistentSet(event.value)
        elif isinstance(event.value, OrderedSet):
            event.value = PersistentOrderedSet(event.value)
        elif isinstance(event.value, dict):
            event.value = PersistentMapping(event.value)

    @property
    def is_inserted(self):
        """Indicates wether the object has been inserted into the database.
        @type: bool
        """
        return self.__inserted

    def insert(self, inserted_objects = None):
        """Inserts the object into the database."""

        if self.__inserted:
            return False

        if inserted_objects is None:
            inserted_objects = set()
            inserted_objects.add(self)
        else:
            if self in inserted_objects:
                return False
            else:
                inserted_objects.add(self)

        self.require_id()
        self.inserting(inserted_objects = inserted_objects)
        self.__inserted = True

        for member in self.__class__.members().values():

            # Insert related objects
            if isinstance(member, Reference):
                related = self.get(member)
                if related \
                and isinstance(related, PersistentObject) \
                and not related.__inserted:
                    related.insert(inserted_objects)

            elif isinstance(member, Collection):
                collection = self.get(member)
                if collection:
                    for item in collection:
                        if isinstance(item, PersistentObject) \
                        and not item.__inserted:
                            item.insert(inserted_objects)

        self.inserted()
        return True

    def delete(self, deleted_objects = None):
        """Removes the object from the database."""

        if deleted_objects is None:
            deleted_objects = set()
            deleted_objects.add(self)
        else:
            if self in deleted_objects:
                return
            else:
                deleted_objects.add(self)

        if not self.__inserted:
            raise NewObjectDeletedError(self)

        self.deleting(deleted_objects = deleted_objects)
        self.__inserted = False

        for member in self.__class__.members().values():

            if isinstance(member, schema.RelationMember):

                # Cascade delete
                if self._should_cascade_delete_member(member):
                    value = self.get(member)
                    if value is not None:
                        if isinstance(member, schema.Reference):
                            if value._included_in_cascade_delete(self, member):
                                value.delete(deleted_objects)
                        else:
                            # Make a copy of the collection, since it may
                            # change during iteration
                            for item in list(value):
                                if item._included_in_cascade_delete(self, member):
                                    item.delete(deleted_objects)

                # Remove all known references to the item (drop all its
                # relations)
                if self._should_erase_member(member):
                    self.set(member, None)

        self.deleted(deleted_objects = deleted_objects)

    def _should_cascade_delete_member(self, member):
        return member.cascade_delete

    def _included_in_cascade_delete(self, parent, member):
        return True

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

    def _should_index_member(self, member):
        return self.indexed and member.indexed

    def _should_index_member_full_text(self, member):
        return member.full_text_indexed

    def get_ordering_key(self):
        return translations(self)

    def _counts_as_duplicate(self, other):
        return self is not other

    def copy_value(self, member, language, **kwargs):

        value = SchemaObject.copy_value(self, member, language, **kwargs)

        if member.unique:
            original = self.get(member, language = language)
            if value == original:
                value = self.qualify_duplicate_value(
                    member,
                    value,
                    language,
                    receiver = kwargs.get("receiver")
                )

        return value

    def qualify_duplicate_value(self, member, value, language, receiver = None):

        if (
            isinstance(member, String)
            and receiver is not None
            and value is not None
        ):
            return value + ("_%s" % receiver.require_id())

        if not member.required:
            return None

        raise UniqueValueCopyError(self, member, language)


PersistentObject._translation_schema_metaclass = PersistentClass
PersistentObject._translation_schema_base = PersistentObject


def unique_validation_rule(context):

    # Make sure the member is still flagged as unique when the validation
    # is performed
    if not context.member.unique:
        return

    if context.value is not None:

        obj = context.get("persistent_object") or context.get_object()

        if isinstance(obj, PersistentObject):
            pschema = context.member.original_member.schema
            if context.member.translated:
                duplicates = list(pschema.select(
                    obj.__class__.get_member(context.member.name)
                        .translated_into(context.language)
                        .equal(context.value)
                ))
                duplicate = duplicates[0] if duplicates else None
            else:
                params = {context.member.name: context.value}
                duplicate = pschema.get_instance(**params)

            if duplicate and duplicate._counts_as_duplicate(obj):
                yield UniqueValueError(context)

def _select_constraint_instances(self, *args, **kwargs):

    parent = kwargs.pop("parent", None)
    query = self.related_type.select(*args, **kwargs)

    for expr in self.get_constraint_filters(parent):
        query.add_filter(expr)

    return query

schema.RelationMember.select_constraint_instances = \
    _select_constraint_instances


def _get_constraint_filters(self, parent):

    context = schema.ValidationContext(self, parent, relation_parent = parent)
    constraints = self.resolve_constraint(self.relation_constraints, context)

    if constraints:
        if hasattr(constraints, "items"):
            get_related_member = self.related_type.get_member
            for key, value in constraints.items():
                yield get_related_member(key).equal(value)
        else:
            for constraint in constraints:
                if not isinstance(constraint, Expression):
                    constraint = CustomExpression(constraint)
                yield constraint

    # Prevent cycles in recursive relations
    excluded_items = set()

    # References: exclude the parent and its descendants
    if (
        isinstance(self, schema.Reference)
        and not self.cycles_allowed
        and parent is not None
    ):
        if self.bidirectional:
            # 1-n
            if isinstance(self.related_end, schema.Collection):
                def recursive_exclusion(item):
                    excluded_items.add(item)
                    children = item.get(self.related_end)
                    if children:
                        for child in children:
                            recursive_exclusion(child)

                recursive_exclusion(parent)

            # 1-1
            else:
                item = parent
                while item:
                    excluded_items.add(item)
                    item = item.get(self.related_end)
        # 1-?
        else:
            excluded_items.add(parent)

            def forms_cycle(item):
                related_item = item.get(self)
                return (
                    related_item is parent
                    or (related_item
                        and forms_cycle(related_item))
                )

            user_collection.add_base_filter(
                CustomExpression(lambda item: not forms_cycle(item))
            )

    # Collections: exclude the parent and its ancestors
    elif self.bidirectional \
    and isinstance(self.related_end, schema.Reference) \
    and not self.related_end.cycles_allowed:
        item = parent
        while item:
            excluded_items.add(item)
            item = item.get(self.related_end)

    if excluded_items:
        yield ExclusionExpression(Self, excluded_items)

schema.RelationMember.get_constraint_filters = _get_constraint_filters


class PrimaryKeyChangedError(Exception):
    """An error raised when changing the value for a persistent object's
    primary member."""

    def __repr__(self):
        return "Can't change the primary member of an inserted object"


class UniqueValueError(ValidationError):
    """A validation error produced when a unique field is given a value that is
    already present in the database.
    """

    def __repr__(self):
        return "%s (value already present in the database)" \
            % ValidationError.__repr__(self)


class UniqueValueCopyError(Exception):
    """An error raised when copying an object with a unique member."""

    def __init__(self, obj, member, language):
        Exception.__init__(self,
            "Can't copy the value for unique member %s from %r."
            % (member.name, obj)
        )
        self.object = obj
        self.member = member
        self.language = language


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


class InstanceNotFoundError(Exception):
    """An exception raised by L{PersistentObject.require_instance} when a non
    existant instance is requested.
    """

