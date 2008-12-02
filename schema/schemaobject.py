#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import sys
from cocktail.modeling import refine
from cocktail.events import Event
from cocktail.pkgutils import get_full_name
from cocktail.language import require_content_language
from cocktail.translations import translate
from cocktail.schema.schema import Schema
from cocktail.schema.member import Member
from cocktail.schema.schemareference import Reference
from cocktail.schema.schemastrings import String
from cocktail.schema.schemarelations import _update_relation
from cocktail.schema.schemacollections import (
    Collection, RelationList, RelationSet
)
from cocktail.schema.schemamappings import Mapping, RelationMapping
from cocktail.schema.accessors import MemberAccessor

# Class stub
SchemaObject = None


class SchemaClass(type, Schema):

    def __init__(cls, name, bases, members):
        
        type.__init__(cls, name, bases, members)
        Schema.__init__(cls)

        cls.name = name
        cls.full_name = get_full_name(cls)
        cls.__derived_schemas = []
        cls._sealed = False
        cls.members_order = members.get("members_order")
        cls.blueprint = members.get("blueprint", False)

        # Inherit base schemas
        for base in bases:
            if SchemaObject \
            and base is not SchemaObject \
            and isinstance(base, SchemaClass):
                if base.blueprint:
                    base._apply_blueprint(cls)
                    cls.inherit
                else:
                    cls.inherit(base)

        # Fill the schema with members declared as class attributes
        for name, member in members.iteritems():
            if isinstance(member, Member):
                member.name = name
                cls.add_member(member)

        # Seal the schema, so that no further modification is possible
        cls._sealed = True

        if cls.translation:
            cls.translation._sealed = True

    def inherit(cls, *bases):
        cls._seal_check()
        Schema.inherit(cls, *bases)
        
        for base in bases:
            base.__derived_schemas.append(cls)

    def _apply_blueprint(cls, target_class):
        
        for member in cls.members().itervalues():
            member_copy = member.copy()
            target_class.add_member(member_copy)

    def _seal_check(cls):
        if cls._sealed:
            raise TypeError("Can't alter a class bound schema after the class "
                "declaration has ended")

    def _check_member(cls, member):

        # Make sure the schema can't be extended after the class declaration is
        # over
        cls._seal_check()

        Schema._check_member(cls, member)

    def _add_member(cls, member):
       
        Schema._add_member(cls, member)

        # Install a descriptor to mediate access to the member
        descriptor = cls.MemberDescriptor(member)
        setattr(cls, member.name, descriptor)

        # Avoid AttributeError exceptions on object initialization by setting
        # class wide attributes
        setattr(cls, "_" + member.name, None)         
                   
        # Primary member
        if member.primary:
            cls.primary_member = member

        # Translation
        if member.translated:

            # Create a translation schema for the class, to hold its
            # translated members
            if cls.translation is None \
            or cls.translation.translation_source is not cls:
                cls._create_translation_schema()
                cls.translated = True
                            
            # Create the translated version of the member, and add it to the
            # translated version of the schema
            member.translation = member.copy()
            member.translation.translated = False
            member.translation.translation_source = member
            cls.translation.add_member(member.translation)

    def _create_translation_schema(cls):
        
        translation_bases = tuple(
            base.translation
            for base in cls.bases
            if base.translation
        ) or (SchemaObject,)

        members = {}
        # {"indexed": False} # FIXME: move this to PersistentClass

        if not translation_bases:
            members["translated_object"] = Reference(
                type = cls,
                required = True
            )
            members["language"] = String(required = True)

        cls.translation = SchemaClass(
            cls.name + "Translation",
            translation_bases,
            members
        )

        cls.translation.translation_source = cls

        # Leave the translation class unsealed, until the declaration of its
        # owner class is finished
        cls.translation._sealed = False

        # Make the translation class available at the module level, so that its
        # instances can be pickled
        setattr(
            sys.modules[cls.__module__],
            cls.translation.name,
            cls.translation)

        cls.translation.__module__ = cls.__module__

        # Add a mapping to hold the translations defined by items
        translations_member = Mapping(
            name = "translations",
            required = True,
            keys = String(
                required = True,
                format = "a-z{2}"
            ),
            values = cls.translation
        )

        @refine(translations_member)
        def __translate__(self, language):
            return translate("Translations", language)

        cls.add_member(translations_member)

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
                    language = require_content_language(language)
                    instance = instance._translations.get(language)
                    if instance is None:
                        return None

                return getattr(instance, self.__priv_key)

        def __set__(self, instance, value, language = None):
            
            member = self.member

            # For translated members, make sure the translation for the specified
            # language exists, and then resolve the assignment against it
            if member.translated:
                language = require_content_language(language)
                target = instance.translations.get(language)
                if target is None:
                    target = instance._new_translation(language)
            else:
                target = instance

            # Value normalization and hooks
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
                if previous_value is None:
                    value = self.instrument_collection(value, target, member)

                # If a collection is already set on the element, update it instead
                # of just replacing it (this will invoke add/delete hooks on the
                # collection, and update the opposite end of the relation)
                else:
                    previous_value.set_content(value)
                    preserve_value = value is not None
            
            # Set the value
            if not preserve_value:
                setattr(target, self.__priv_key, value)

            # Update the opposite end of a bidirectional reference
            if self._bidirectional_reference and value != previous_value:
                
                # TODO: translated bidirectional references
                if previous_value is not None:                    
                    _update_relation(
                        "unrelate", instance, previous_value, member
                    )
                    instance.unrelated(
                        member = member,
                        related_object = previous_value,
                        collection = None
                    )

                if value is not None:
                    _update_relation("relate", instance, value, member)
                    instance.related(
                        member = member,
                        related_object = value,
                        collection = None
                    )

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

            # Mappings
            elif isinstance(collection, dict):
                collection = RelationMapping(collection, owner, member)

            return collection


class SchemaObject(object):

    __metaclass__ = SchemaClass
    
    instantiated = Event(doc = """
        An event triggered on the class when a new instance is created.

        @ivar instance: A reference to the new instance.
        @type instance: L{SchemaObject}
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

        @ivar collection: A reference to the collection modified by the current
            change, if any. On
            L{reference<cocktail.schema.schemareferences.Reference>} members,
            this will be set to None.
        """)

    unrelated = Event(doc = """
        An event triggered after clearing a relationship between objects.

        @ivar member: The schema member that describes the relationship.
        @type member: L{Relation<cocktail.schema.schemarelations>}

        @ivar related_object: The object that is no longer related to the
            target.

        @ivar collection: A reference to the collection modified by the current
            change, if any. On
            L{reference<cocktail.schema.schemareferences.Reference>} members,
            this will be set to None.
        """)

    def __init__(self, **values):
        self.__class__.init_instance(self, values, SchemaObjectAccessor)
        self.__class__.instantiated(instance = self)
        
    def __repr__(self):
        
        if self.__class__.primary_member:
            id = getattr(self, self.__class__.primary_member.name, None)
            if id is not None:
                return "%s #%s" % (self.__class__.full_name, self.id)
        
        return self.__class__.full_name + " instance"

    def __translate__(self, language, **kwargs):
        desc = translate(self.__class__.full_name, language, **kwargs)

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


_undefined = object()


class SchemaObjectAccessor(MemberAccessor):
    """A member accessor for
    L{SchemaObject<cocktail.schema.schemaobject.SchemaObject>} instances, used
    by L{adapters<cocktail.schema.adapters.Adapter>} to retrieve and set object
    values.
    """

    @classmethod
    def get(cls, obj, key, default = _undefined, language = None):
        try:
            return obj.get(key, language)

        except AttributeError:
            if default is _undefined:
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

