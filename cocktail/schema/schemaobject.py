#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import sys
from cocktail.modeling import refine, OrderedSet
from cocktail.events import Event, EventHub
from cocktail.pkgutils import get_full_name
from cocktail.translations import translations, require_language
from cocktail.schema.schema import Schema
from cocktail.schema.member import Member
from cocktail.schema.schemareference import Reference
from cocktail.schema.schemastrings import String
from cocktail.schema.schemarelations import _update_relation
from cocktail.schema.schemacollections import (
    Collection,
    RelationCollection,
    RelationList,
    RelationSet,
    RelationOrderedSet
)
from cocktail.schema.schemamappings import Mapping, RelationMapping
from cocktail.schema.accessors import MemberAccessor

# Extension property that allows members to knowingly shadow existing
# class attributes
Member.shadows_attribute = False

# Class stub
SchemaObject = None

undefined = object()


class SchemaClass(EventHub, Schema):

    def __init__(cls, name, bases, members):
        
        cls._declared = False
        
        EventHub.__init__(cls, name, bases, members)
        Schema.__init__(cls)

        cls.name = name
        cls.full_name = members.get("full_name") or get_full_name(cls)
        cls.__derived_schemas = []
        cls.members_order = members.get("members_order")
        cls.groups_order = members.get("groups_order")
        
        # Inherit base schemas
        for base in bases:
            if SchemaObject \
            and base is not SchemaObject \
            and isinstance(base, SchemaClass):
                cls.inherit(base)

        # Create a translation schema for the class, to hold its translated
        # members. Note that for most regular schemas (that is, all of them
        # except for SchemaObject, PersistentObject, etc) the translation
        # schema is always created, regardless of wether the source schema
        # actually contains any translated member at all. This ensures that
        # adding translated members to a base class won't break its inheritors,
        # whose translation schemas would be inheriting from the wrong schema.
        if members.get("_generates_translation_schema", True):
            cls._create_translation_schema({})

        # Fill the schema with members declared as class attributes
        for name, member in members.iteritems():
            if isinstance(member, Member):
                member.name = name
                cls.add_member(member)

        cls._declared = True

        if cls.translation:
            cls.translation._declared = True

        cls.declared()

    def inherit(cls, *bases):
        
        if cls._declared:
            raise TypeError(
                "Can't extend the base classes of %s with %s. Dynamic "
                "modification of the base classes for a schema is not "
                "supported."
                % (cls.__name__, ", ".join(base.__name__ for base in bases))
            )

        Schema.inherit(cls, *bases)
        
        for base in bases:
            base.__derived_schemas.append(cls)

    def _check_member(cls, member):

        Schema._check_member(cls, member)
        
        if not member.shadows_attribute \
        and (
            hasattr(cls, member.name) \
            and (
                getattr(cls, member.name) is not member
                or any(hasattr(base, member.name) for base in cls.__bases__)
            )
        ):
            raise AttributeError(
                "Trying to declare a member called %s on %s; the schema "
                "already has an attribute with that name. If this is "
                "intentional, the 'shadows_attribute' property can be used to "
                "ignore this restriction."
                % (member.name, cls)
            )

    def _add_member(cls, member):
       
        Schema._add_member(cls, member)

        # Install a descriptor to mediate access to the member
        descriptor = cls.MemberDescriptor(member)
        setattr(cls, member.name, descriptor)

        # Translation
        if member.translated:
 
            if cls.translated == False:
                cls.translated = True

                # Add a mapping to hold the translations defined by items
                translations_member = Mapping(
                    name = "translations",
                    required = True,
                    keys = String(
                        required = True,
                        format = "[a-z]{2}"
                    ),
                    values = cls.translation
                )

                @refine(translations_member)
                def __translate__(self, language):
                    return translations("Translations", language)

                cls.add_member(translations_member)

            # Create the translated version of the member, and add it to the
            # translated version of the schema
            member.translation = member.copy()
            member.translation.translated = False
            member.translation.translation_source = member
            cls.translation.add_member(member.translation)

    def _create_translation_schema(cls, members):
        
        bases = tuple(
            base.translation
            for base in cls.bases if base.translation
        )

        members["_generates_translation_schema"] = False
        
        if not bases:
            bases = (cls._translation_schema_base,)

            members["full_name"] = cls.full_name + "Translation"
            members["translated_object"] = Reference(
                type = cls,
                required = True
            )
            members["language"] = String(required = True)
            
        cls.translation = cls._translation_schema_metaclass(
            cls.name + "Translation",
            bases,
            members
        )

        cls.translation.translation_source = cls

        # Make the translation class available at the module level, so that its
        # instances can be pickled
        setattr(
            sys.modules[cls.__module__],
            cls.translation.name,
            cls.translation)

        cls.translation.__module__ = cls.__module__

    def remove_member(self, member):
        Schema.remove_member(self, member)

        # Remove the member descriptor
        delattr(self, member.name)


    def schema_tree(cls):
        yield cls
        for child in cls.__derived_schemas:
            for descendant in child.schema_tree():
                yield descendant

    def derived_schemas(cls, recursive = True):
        for schema in cls.__derived_schemas:
            yield schema
            if recursive:
                for descendant in schema.derived_schemas(True):
                    yield descendant

    class MemberDescriptor(object):

        def __init__(self, member):
            self.member = member
            self.normalization = lambda obj, member, value: value
            self.__priv_key = "_" + member.name
            self._bidirectional_reference = \
                isinstance(member, Reference) and member.bidirectional
            self._bidirectional_collection = \
                isinstance(member, Collection) and member.bidirectional

        def __get__(self, instance, type = None, language = None):
            if instance is None:
                return self.member
            else:
                if self.member.translated:
                    language = require_language(language)
                    target = instance.translations.get(language)
                    if target is None:
                        return None
                else:
                    target = instance

                value = getattr(target, self.__priv_key, undefined)

                if value is undefined:
                    value = self.member.produce_default(instance)
                    self.__set__(
                        instance,
                        value,
                        language = language,
                        previous_value = None
                    )
                    return self.__get__(instance, type, language)
                
                return value

        def __set__(self, instance, value,
            language = None,
            previous_value = undefined):
            
            member = self.member

            # For translated members, make sure the translation for the specified
            # language exists, and then resolve the assignment against it
            if member.translated:
                language = require_language(language)
                target = instance.translations.get(language)
                if target is None:
                    target = instance._new_translation(language)
            else:
                target = instance

            # Value normalization and hooks
            if previous_value is undefined:
                previous_value = getattr(target, self.__priv_key, None)

            value = self.normalization(instance, member, value)

            try:
                changed = (value != previous_value)
            except TypeError:
                changed = True

            if changed:
                event = instance.changing(
                    member = member,
                    language = language,
                    value = value,
                    previous_value = previous_value
                )
                value = event.value
            
            preserve_value = False

            # Bidirectional collections require special treatment:
            if self._bidirectional_collection:
                
                # When setting the collection for the first time, wrap it with an
                # instrumented instance of the appropiate type
                if previous_value is None \
                or not isinstance(previous_value, RelationCollection):
                    value = self.instrument_collection(value, target, member)

                    if value:
                        for item in value:
                            _update_relation("relate", instance, item, member)

                # If a collection is already set on the element, update it instead
                # of just replacing it (this will invoke add/delete hooks on the
                # collection, and update the opposite end of the relation)
                else:                    
                    changed = value != previous_value
                    if value is None:
                        # Set an existing collection to None: unrelate all
                        # its items
                        if previous_value is not None:
                            for previously_related_item in previous_value:
                                _update_relation(
                                    "unrelate",
                                    instance,
                                    previously_related_item,
                                    member
                                )
                    else:
                        previous_value.set_content(value)
                        preserve_value = True
            
            # Set the value
            if not preserve_value:
                setattr(target, self.__priv_key, value)

            # Update the opposite end of a bidirectional reference
            if self._bidirectional_reference and value != previous_value:
                
                # TODO: translated bidirectional references
                if previous_value is not None:                    
                    _update_relation(
                        "unrelate", instance, previous_value, member,
                        relocation = value is not None
                    )

                if value is not None:
                    _update_relation("relate", instance, value, member)

            if not preserve_value:
                try:
                    changed = (value != previous_value)
                except TypeError:
                    changed = True

            if changed:
                instance.changed(
                    member = member,
                    language = language,
                    value = value,
                    previous_value = previous_value
                )

        def instrument_collection(self, collection, owner, member):

            # Lists
            if isinstance(collection, list):
                collection = RelationList(collection, owner, member)
            
            # Sets
            elif isinstance(collection, set):
                collection = RelationSet(collection, owner, member)

            # Ordered sets
            elif isinstance(collection, OrderedSet):
                collection = RelationOrderedSet(collection, owner, member)

            # Mappings
            elif isinstance(collection, dict):
                collection = RelationMapping(collection, owner, member)

            return collection


class SchemaObject(object):

    __metaclass__ = SchemaClass
    _generates_translation_schema = False
    _translation_schema_base = None
    bidirectional = True

    declared = Event(doc = """
        An event triggered on the class after the declaration of its schema has
        finished.
        """)

    instantiated = Event(doc = """
        An event triggered on the class when a new instance is created.

        @ivar instance: A reference to the new instance.
        @type instance: L{SchemaObject}

        @ivar values: The parameters passed to the constructor.
        @type values: dict
        """)

    changing = Event(doc = """
        An event triggered before the value of a member is changed.

        @ivar member: The member that is being changed.
        @type member: L{Member<cocktail.schema.member.Member>}

        @ivar language: Only for translated members, indicates the language
            affected by the change.
        @type language: str

        @ivar value: The new value assigned to the member. Modifying this
            attribute *will* change the value which is finally assigned to the
            member.

        @ivar previous_value: The current value for the affected member, before
            any change takes place.
        """)

    changed = Event(doc = """
        An event triggered after the value of a member has changed.

        @ivar member: The member that has been changed.
        @type member: L{Member<cocktail.schema.member.Member>}

        @ivar language: Only for translated members, indicates the language
            affected by the change.
        @type language: str

        @ivar value: The new value assigned to the member.

        @ivar previous_value: The value that the member had before the current
            change.
        """)

    related = Event(doc = """
        An event triggered after establishing a relationship between objects.
        If both ends of the relation are instances of L{SchemaObject}, this
        event will be triggered twice.

        @ivar member: The schema member that describes the relationship.
        @type member: L{Relation<cocktail.schema.schemarelations>}

        @ivar related_object: The object that has been related to the target.
        """)

    unrelated = Event(doc = """
        An event triggered after clearing a relationship between objects.

        @ivar member: The schema member that describes the relationship.
        @type member: L{Relation<cocktail.schema.schemarelations>}

        @ivar related_object: The object that is no longer related to the
            target.
        """)

    def __init__(self, **values):
        self.__class__.init_instance(self, values, SchemaObjectAccessor)
        self.__class__.instantiated(instance = self, values = values)
        
    def __repr__(self):
        
        if self.__class__.primary_member:
            id = getattr(self, self.__class__.primary_member.name, None)
            if id is not None:
                return "%s #%s" % (self.__class__.full_name, self.id)
        
        return self.__class__.full_name + " instance"

    def __translate__(self, language, **kwargs):
        desc = translations(self.__class__.name, language, **kwargs)

        if self.__class__.primary_member:
            desc += " #" \
                + str(getattr(self, self.__class__.primary_member.name))
 
        return desc

    def get(self, member, language = None):

        # Normalize the member argument to a member reference
        if not isinstance(member, Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        getter = member.schema.__dict__[member.name].__get__
        return getter(self, None, language)        

    def set(self, member, value, language = None):

        # Normalize the member argument to a member reference
        if not isinstance(member, Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        setter = member.schema.__dict__[member.name].__set__
        setter(self, value, language)

    def _new_translation(self, language):
        translation = self.translation(
            object = self,
            language = language)
        self.translations[language] = translation
        return translation

SchemaObject._translation_schema_metaclass = SchemaClass
SchemaObject._translation_schema_base = SchemaObject


class SchemaObjectAccessor(MemberAccessor):
    """A member accessor for
    L{SchemaObject<cocktail.schema.schemaobject.SchemaObject>} instances, used
    by L{adapters<cocktail.schema.adapters.Adapter>} to retrieve and set object
    values.
    """

    @classmethod
    def get(cls, obj, key, default = undefined, language = None):
        try:
            return obj.get(key, language)

        except AttributeError:
            if default is undefined:
                raise

            return default

    @classmethod
    def set(cls, obj, key, value, language = None):
        obj.set(key, value, language)

    @classmethod
    def languages(cls, obj, key):
        if obj.__class__.translated:
            return obj.translations.keys()
        else:
            return (None,)

    @classmethod
    def can_handle(cls, obj):
        return isinstance(obj, SchemaObject)


SchemaObjectAccessor.register()

