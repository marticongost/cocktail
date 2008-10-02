#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sys
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from cocktail.pkgutils import get_full_name
from cocktail import schema
from cocktail.schema.exceptions import ValidationError
from cocktail.language import require_content_language
from cocktail.translations import translate
from cocktail.persistence.datastore import datastore
from cocktail.persistence.incremental_id import incremental_id
from cocktail.persistence.index import Index
from cocktail.persistence import relations

# Default collection types
schema.Collection.default_type = PersistentList
schema.Mapping.default_type = PersistentMapping

# Translation
schema.Member.translation = None
schema.Member.translation_source = None

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
        
        # Unique indices use a "raw" ZODB's binary tree
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

# Create a stub for the Entity class
Entity = None

# Debugging
indent = 0
DEBUG = False


class EntityClass(type, schema.Schema):

    def __init__(cls, name, bases, members):
         
        if DEBUG:
            global indent
            print "\t" * indent, "<%s>" % name
            indent += 1

        type.__init__(cls, name, bases, members)
        schema.Schema.__init__(cls)

        cls.name = name
        cls.__full_name = get_full_name(cls)
        cls.__derived_entities = []
        cls.members_order = members.get("members_order")
        cls._sealed = False

        # Inherit base schemas
        for base in bases:
            if Entity and base is not Entity and isinstance(base, EntityClass):
                cls.inherit(base)

        # Fill the schema with members declared as class attributes
        for name, member in members.iteritems():
            if isinstance(member, schema.Member):
                member.name = name
                cls.add_member(member)

        # Instance index
        if Entity and cls.indexed:

            cls.index_key = cls.__full_name

            # Add an 'id' field to all indexed schemas that don't define their
            # own primary member explicitly. Will be set to an incremental
            # integer when calling Entity.store()
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

        # Seal the schema, so that no further modification is possible
        cls._sealed = True

        if cls.translation:
            cls.translation._sealed = True

        if DEBUG:
            indent -= 1
            print "\t" * indent, "</%s>" % cls.name

    def _seal_check(cls):
        if cls._sealed:
            raise TypeError("Can't alter an entity's schema after declaration")

    def inherit(cls, *bases):
        cls._seal_check()
        schema.Schema.inherit(cls, *bases)
        
        for base in bases:
            base.__derived_entities.append(cls)

    def add_member(cls, member):

        if DEBUG:
            global indent
            print "\t" * indent, "%s.%s" % (cls.name, member.name)
            indent += 1

        schema.Schema.add_member(cls, member)

        if DEBUG:
            indent -= 1

    def _check_member(cls, member):

        # Make sure the schema can't be extended after the class declaration is
        # over
        cls._seal_check()

        schema.Schema._check_member(cls, member)

        # Unique members require a general class index, or a specific index for
        # the member
        if member.unique and not (member.indexed or cls.indexed):
            raise ValueError(
                "Can't enforce the unique constraint on %s.%s "
                "without a class or member index"
                % (cls.__full_name, member.name))

    def _add_member(cls, member):
       
        schema.Schema._add_member(cls, member)

        # Install a descriptor to mediate access to the member
        descriptor = MemberDescriptor(member)
        setattr(cls, member.name, descriptor)
         
        # Instrument relations
        if isinstance(member, schema.Collection) \
        and getattr(member, "bidirectional", False):
            
            def instrument_collection(obj, member, value):
                if value is not None:
                    if isinstance(value, (list, PersistentList)):
                        value = relations.RelationList(value)
                        value.owner = obj
                        value.member = member
                    elif isinstance(value, set):
                        value = relations.RelationSet(value)
                        value.owner = obj
                        value.member = member
                    elif isinstance(value, (dict, PersistentMapping)):
                        value = relations.RelationDict(value)
                        value.owner = obj
                        value.member = member

                return value

            descriptor.normalization = instrument_collection
                    
        # Primary member
        if member.primary:
            cls.primary_member = member

        # Unique values restriction/index
        if member.unique:
            if cls._unique_validation_rule \
            not in member.validations(recursive = False):
                member.add_validation(cls._unique_validation_rule)
        
        # Translation
        if member.translated:

            # Create a translation schema for the entity, to hold its
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

        # An indexed member gets its own btree
        if member.indexed and member.index_key is None:
            member.index_key = cls.__full_name + "." + member.name
        
    def _unique_validation_rule(cls, member, value, context):

        if (member.indexed and value in member.index) \
        or any(
            instance.get(member) == value
            for instance in member.schema.index.itervalues()
        ):
            yield UniqueValueError(member, value, context)

    def _create_translation_schema(cls):
        
        translation_bases = tuple(
            base.translation
            for base in cls.bases
            if base.translation
        ) or (Entity,)

        cls.translation = EntityClass(
            cls.name + "Translation",
            translation_bases,
            {"indexed": False}
        )

        cls.translation.translation_source = cls

        # Make the translation class available at the module level, so its
        # instances can be pickled (required by ZODB's persistence machinery)
        setattr(
            sys.modules[cls.__module__],
            cls.translation.name,
            cls.translation)

        cls.translation.__module__ = cls.__module__

        cls.translation._sealed = False

        if not translation_bases:
            cls.translation.add_member(schema.Reference(
                name = "translated_object",
                type = cls,
                required = True
            ))
            cls.translation.add_member(schema.String(
                name = "language",
                required = True
            ))

        cls.add_member(schema.Mapping(
            name = "translations",
            required = True,
            keys = schema.String(
                required = True,
                format = "a-z{2}"
            ),
            values = cls.translation
        ))

    def derived_entities(cls, recursive = True):
        for entity in cls.__derived_entities:
            yield entity
            if recursive:
                for descendant in entity.derived_entities(True):
                    yield descendant


class Entity(Persistent):

    __metaclass__ = EntityClass

    indexed = True

    def __init__(self, **values):
        Persistent.__init__(self)
        self._v_initializing = True
        self.__class__.init_instance(self, values, EntityAccessor) 
        self._v_initializing = False

    def __repr__(self):
        
        if self.__class__.indexed:
            id = getattr(self, "id", None)
            if id is not None:
                return "%s #%d" % (self.__class__.__name__, self.id)
        
        return self.__class__.__name__ + " instance"

    def __translate__(self, language, **kwargs):
        return (
            translate(self.__class__.__name__, language, **kwargs)
            + " #" + str(self.id)
        )

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

    def get(self, member, language = None):

        # Normalize the member argument to a schema.Member reference
        if not isinstance(member, schema.Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        getter = member.schema.__dict__[member.name]._getter
        
        if member.translated:
            return getter(self, language)
        else:
            return getter(self)

    def set(self, member, value, language = None):

        # Normalize the member argument to a schema.Member reference
        if not isinstance(member, schema.Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        setter = member.schema.__dict__[member.name]._setter

        if member.translated:
            setter(self, value, language)
        else:
            setter(self, value)

    def set_translations(self, member, **values):

        # Normalize the member argument to a schema.Member reference
        if not isinstance(member, schema.Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        setter = member.schema.__dict__[member.name]._setter

        for language, value in values.iteritems():
            setter(self, value, language)

    def _new_translation(self, language):
        translation = self.translation(
            object = self,
            language = language)
        self.translations[language] = translation
        return translation

    def on_member_set(self, member, value, language):
        return value


class MemberDescriptor(object):

    def __init__(self, member):
        self.member = member
        self.normalization = lambda obj, member, value: value
        self.__priv_key = "_" + member.name

        if member.translated:
            self._getter = self._get_translated_value
            self._setter = self._set_translated_value
        else:
            self._getter = self._get_value
            self._setter = self._set_value
    
    def __get__(self, instance, type = None):
        if instance is None:
            return self.member
        else:
            return self._getter(instance)

    def _get_value(self, instance):
        return getattr(instance, self.__priv_key)

    def _get_translated_value(self, instance, language = None):
        language = require_content_language(language)
        translation = instance._translations.get(language)
            
        if translation is None:
            return None
        else:
            return getattr(translation, self.__priv_key)

    def __set__(self, instance, value):        
        self._setter(instance, value)

    def _set_value(self, instance, value):
        
        previous_value = getattr(instance, self.__priv_key, None)
        value = self.normalization(instance, self.member, value)
        value = instance.on_member_set(self.member, value, None)
        setattr(instance, self.__priv_key, value)

        if self.member.indexed:
            instance._update_index(self.member, None, previous_value, value)

        self.__update_relation(instance, value, previous_value)

    def _set_translated_value(self, instance, value, language = None):

        # Make sure the translation for the specified language exists, and
        # then resolve the assignment against it
        language = require_content_language(language)
        translation = instance.translations.get(language)

        if translation is None:
            translation = instance._new_translation(language)

        previous_value = getattr(translation, self.__priv_key, None)
        value = self.normalization(instance, self.member, value)
        value = instance.on_member_set(self.member, value, language)
        setattr(translation, self.__priv_key, value)

        if self.member.indexed:
            instance._update_index(
                self.member, language, previous_value, value)

        self.__update_relation(instance, value, previous_value)

    def __update_relation(self, instance, value, previous_value):

        if isinstance(self.member, schema.Reference) \
        and self.member.bidirectional:

            if previous_value is not None:
                relations.unrelate(value, instance, self.member.related_end)

            if value is not None:
                relations.relate(value, instance, self.member.related_end)

_undefined = object()

class EntityAccessor(schema.MemberAccessor):
    """A member accessor for entity instances, used by
    L{adapters<cocktail.schema.adapters.Adapter>} to retrieve and set object
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


class UniqueValueError(ValidationError):
    """A validation error produced when a unique field is given a value that is
    already present in the database.
    """

    def __repr__(self):
        return "%s (value already present in the database)" \
            % ValidationError.__repr__(self)

