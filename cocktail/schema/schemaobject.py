#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import sys
from cocktail.modeling import refine, OrderedSet, InstrumentedDict, DictWrapper
from cocktail.events import Event, EventHub
from cocktail.pkgutils import get_full_name
from cocktail.translations import (
    translations,
    require_language,
    iter_language_chain,
    descend_language_tree,
    NoActiveLanguageError
)
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
from cocktail.schema.textextractor import TextExtractor

# Extension property that allows members to knowingly shadow existing
# class attributes
Member.shadows_attribute = False

# Class stub
SchemaObject = None

undefined = object()

DO_NOT_COPY = 0
SHALLOW_COPY = 2
DEEP_COPY = 3


class SchemaClass(EventHub, Schema):

    def __init__(cls, name, bases, members):

        cls._declared = False

        EventHub.__init__(cls, name, bases, members)
        Schema.__init__(cls)

        cls.name = name
        cls.full_name = members.get("full_name") or get_full_name(cls)
        cls.__derived_schemas = []
        cls.members_order = members.get("members_order")

        # Give each class its own groups_order property
        groups_order = members.get("groups_order")
        if groups_order is None:
            groups_order = cls.groups_order
            groups_order = list(groups_order) if groups_order else []
        cls.groups_order = groups_order

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
            if isinstance(member, Member) \
            and not isinstance(member, SchemaClass):
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

    def remove_derived_schema(self, cls):
        """Forget about the indicated derived schema.

        @param cls: The class to remove from the list of inheritors of the
            schema.
        @type cls: `SchemaObject` class
        """
        self.__derived_schemas.remove(cls)

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
                translations_member = cls._create_translations_member()
                cls.add_member(translations_member)

            # Create the translated version of the member, and add it to the
            # translated version of the schema
            member.translation = member.copy()
            member.translation.translated = False
            member.translation.translation_source = member
            cls.translation.add_member(member.translation)

    def _create_translations_member(cls):
        translations_member = Mapping(
            name = "translations",
            required = True,
            keys = String(required = True),
            values = Reference(
                type = cls.translation,
                translate_value = lambda value, language = None, **kwargs:
                    "" if not value else translations("locale",
                        locale = value,
                        language = language,
                        **kwargs
                    )
            ),
            produce_default = TranslationMapping
        )

        @refine(translations_member)
        def __translate__(self, language):
            return translations("Translations", language)

        return translations_member

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

        cls.translation.init_instance = _init_translation

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

    def eval(cls, context, accessor = None):
        return cls

    class MemberDescriptor(object):

        def __init__(self, member):
            self.member = member
            self.normalization = lambda obj, member, value: value

            self.__priv_key = "_" + member.name
            self._bidirectional_reference = \
                isinstance(member, Reference) and member.bidirectional
            self._is_collection = isinstance(member, Collection)
            self._bidirectional_collection = \
                self._is_collection and member.bidirectional
            self._translations_collection = (
                self._is_collection
                and member.schema
                and member.schema.translated
                and member is member.schema.get_member("translations")
            )

        def __get__(self, instance, type = None, language = None):
            if instance is None:
                return self.member
            else:
                # Calculated field
                expression = self.member.expression
                if expression is not None:
                    if getattr(expression, "im_self", None) is instance:
                        if self.member.translated:
                            return self.member.expression(instance, language)
                        else:
                            return self.member.expression(instance)
                    else:
                        if self.member.translated:
                            return self.member.expression(
                                self.member,
                                instance,
                                language
                            )
                        else:
                            return self.member.expression(self.member, instance)

                if self.member.translated:
                    for language in iter_language_chain(language):
                        target = instance.translations.get(language)
                        if target is not None:
                            break
                    else:
                        return None
                else:
                    target = instance

                value = getattr(target, self.__priv_key, undefined)

                if value is undefined:
                    if getattr(instance, "_v_is_producing_default", False):
                        return None

                    instance._v_is_producing_default = True
                    try:
                        value = self.member.produce_default(instance)
                        self.__set__(
                            instance,
                            value,
                            language = language,
                            previous_value = None
                        )
                        return self.__get__(instance, type, language)
                    finally:
                        instance._v_is_producing_default = False

                return value

        def __set__(self, instance, value,
            language = None,
            previous_value = undefined):

            member = self.member

            if member.translated or member.translation_source:

                if member.translation_source:
                    translated_member = member.translation_source
                    translated_object = instance.translated_object
                    language = instance.language
                else:
                    translated_member = member
                    translated_object = instance
                    language = require_language(language)

                # Determine which translations are affected by the change, by
                # following the language fallback tree. This is recorded and
                # supplied to the changing / changed events. The main use case for
                # this information is field indexing.
                translation_changes = {}

                for derived_lang \
                in translated_object.iter_derived_translations(language):
                    translation_changes[derived_lang] = \
                        translated_object.get(
                            translated_member,
                            language = derived_lang
                        )

                # For translated members, make sure the translation for the specified
                # language exists, and then resolve the assignment against it
                if member.translated:
                    target = instance.translations.get(language)
                    if target is None:
                        target = instance.new_translation(language)
                else:
                    target = instance
            else:
                target = instance
                translation_changes = None

            if previous_value is undefined:
                previous_value = getattr(target, self.__priv_key, None)

            if translation_changes is not None:
                translation_changes[language] = previous_value

            # Value normalization and hooks
            if member.normalization:
                value = member.normalization(value)

            value = self.normalization(instance, member, value)

            try:
                changed = (
                    type(value) is not type(previous_value)
                    or (value != previous_value)
                )
            except TypeError:
                changed = True

            if changed:
                event = instance.changing(
                    member = member.translation_source or member,
                    language = language,
                    value = value,
                    previous_value = previous_value,
                    translation_changes = translation_changes
                )

                value = event.value

                if member.translation_source:
                    event = instance.translated_object.changing(
                        member = member.translation_source,
                        language = instance.language,
                        value = value,
                        previous_value = previous_value,
                        translation_changes = translation_changes
                    )

                value = event.value

            preserve_value = False

            # Collections require special treatment:
            if self._is_collection and not self._translations_collection:

                # When setting the collection for the first time, wrap it with an
                # instrumented instance of the appropiate type
                if previous_value is None \
                or not isinstance(previous_value, RelationCollection):
                    value = self.instrument_collection(value, target, member)
                    setattr(target, self.__priv_key, value)

                    if self._bidirectional_collection and value:
                        for item in value:
                            _update_relation("relate", instance, item, member)

                # If a collection is already set on the element, update it instead
                # of just replacing it (this will invoke add/delete hooks on the
                # collection, and update the opposite end of the relation)
                else:
                    changed = value != previous_value
                    if value is None:
                        setattr(target, self.__priv_key, value)
                        # Set an existing collection to None: unrelate all
                        # its items
                        if self._bidirectional_collection \
                        and previous_value is not None:
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
            else:
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
                    member = member.translation_source or member,
                    language = language,
                    value = value,
                    previous_value = previous_value,
                    translation_changes = translation_changes,
                    added = None,
                    removed = None
                )

                if member.translation_source:
                    instance.translated_object.changed(
                        member = member.translation_source,
                        language = instance.language,
                        value = value,
                        previous_value = previous_value,
                        translation_changes = translation_changes,
                        added = None,
                        removed = None
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


@classmethod
def _init_translation(cls,
    instance,
    values = None,
    accessor = None,
    excluded_members = None,
    copy_from_fallback = True):

    # Set 'translated_object' and 'language' first, so events for changes in
    # all other members are relayed to the translation owner
    if values is not None:

        language = values.pop("language")
        if language is not None:
            instance.language = language

        translated_object = values.pop("translated_object")
        if translated_object is not None:
            instance.translated_object = translated_object

        if language is not None and translated_object is not None:
            translated_object.translations[language] = instance

        if excluded_members is None:
            excluded_members = (cls.translated_object, cls.language)
        else:
            excluded_members = \
                set([cls.translated_object, cls.language]) + set(excluded_members)

        # Copy values from the first available fallback translation
        if (
            copy_from_fallback
            and language is not None
            and translated_object is not None
        ):
            languages = iter_language_chain(language)
            languages.next()
            get_translation = translated_object.translations.get
            for lang in languages:
                base_translation = get_translation(lang)
                if base_translation is not None:
                    for key, member in cls.members().iteritems():
                        if member not in excluded_members:
                            values.setdefault(key, base_translation.get(key))
                    break

    Schema.init_instance(cls, instance, values, accessor, excluded_members)


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

        @ivar translation_changes: A dictionary indicating the translations
            that will be affected by this change, and their respective values
            before the change takes effect. Will be None if the changed member
            is not translatable.
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

        @ivar added: Only for collections. A collection of all the items added
            to the collection.

        @ivar removed: Only for collections. A collection of all the items
            removed from the collection.

        @ivar translation_changes: A dictionary indicating the translations
            that will be affected by this change, and their respective values
            before the change took effect. Will be None if the changed member
            is not translatable.
        """)

    collection_item_added = Event(doc = """
        An event triggered after an item is added to one of the object's
        collections.

        @ivar member: The collection that the item has been added to.
        @type member: L{Collection<cocktail.schema.schemacollections.Collection>}

        @ivar item: The item added to the collection.
        @type item: obj
        """
    )

    collection_item_removed = Event(doc = """
        An event triggered after an item is removed from one of the object's
        collections.

        @ivar member: The collection that the item has been removed from.
        @type member: L{Collection<cocktail.schema.schemacollections.Collection>}

        @ivar item: The item removed from the collection.
        @type item: obj
        """
    )

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

    adding_translation = Event(doc = """
        An event triggered when a new translation is being added.

        @ivar language: The language of the added translation
        @type language: str

        @ivar translation: The new value assigned to the translation.
        """)

    removing_translation = Event(doc = """
        An event triggered when a translation is being removed.

        @ivar language: The language of the removed translation
        @type language: str

        @ivar translation: The value of the translation.
        """)

    def __init__(self, **values):

        # If supplied, the "bidirectional" attribute must be set before
        # setting any other attribute, otherwise bidirectional relations may
        # still be set!
        bidirectional = values.pop("bidirectional", None)
        if bidirectional is not None:
            self.bidirectional = bidirectional

        self.__class__.init_instance(self, values, SchemaObjectAccessor)
        self.__class__.instantiated(instance = self, values = values)

    def __repr__(self):
        label = self.__class__.__name__

        primary_member = self.__class__.primary_member
        if primary_member:
            id = getattr(self, primary_member.name, None)
            if id is not None:
                label += " #%s" % id

        try:
            trans = translations(self, discard_generic_translation = True)
            if trans:
                label += " (%s)" % trans
        except NoActiveLanguageError:
            pass

        if isinstance(label, unicode):
            label = label.encode("utf-8")

        return label

    def __translate__(self, language, **kwargs):

        desc = None

        if self.__class__.descriptive_member:
            desc = self.get(self.__class__.descriptive_member, language)
            if desc:
                desc = self.__class__.descriptive_member.translate_value(
                    desc,
                    language
                )

        if not desc and not kwargs.get("discard_generic_translation", False):

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

    def new_translation(self, language):
        return self.translation(
            translated_object = self,
            language = language
        )

    def iter_derived_translations(self, language = None, include_self = False):
        language = require_language(language)
        for derived_lang in descend_language_tree(
            language,
            include_self = include_self
        ):
            for chain_lang in iter_language_chain(derived_lang):
                if chain_lang == language:
                    yield derived_lang
                    break
                elif chain_lang in self.translations:
                    break

    def iter_translations(self, include_derived = True, languages = None):

        for language in self.translations:

            if languages is not None and language not in languages:
                continue

            yield language

            if include_derived:
                for derived_language in descend_language_tree(
                    language,
                    include_self = False
                ):
                    if derived_language not in self.translations:
                        yield derived_language

    def get_source_locale(self, locale):
        translations = self.translations
        for locale in iter_language_chain(locale):
            if locale in translations:
                return locale

    def create_text_extractor(self, **kwargs):
        extractor = TextExtractor(**kwargs)
        extractor.extract(self.__class__, self)
        return extractor

    def get_searchable_text(self, **kwargs):
        return unicode(self.create_text_extractor(**kwargs))

    copy_excluded_members = frozenset()

    def create_copy(self, member_copy_modes = None):
        clone = self.__class__()
        self.init_copy(clone, member_copy_modes = member_copy_modes)
        return clone

    def init_copy(self, copy, member_copy_modes = None):

        for member in self.__class__.members().itervalues():
            copy_mode = self.get_member_copy_mode(
                member,
                member_copy_modes = member_copy_modes
            )

            if copy_mode == DO_NOT_COPY:
                continue

            if not member.translated:
                languages = (None,)
            else:
                languages = list(self.translations)

            for language in languages:
                value = self.copy_value(
                    member,
                    language,
                    mode = copy_mode,
                    receiver = copy,
                    member_copy_modes = member_copy_modes
                )
                copy.set(member, value, language)

    def get_member_copy_mode(self, member, member_copy_modes = None):

        # Explicit mode set by an override
        if member_copy_modes:
            copy_mode = member_copy_modes.get(member)
            if copy_mode is not None:
                return copy_mode

        # Explicit mode set by the member
        if member.copy_mode is not None:
            return member.copy_mode

        # Implicit mode, based on member properties
        if (
            member.name == "translations"
            or member.primary
            or member in self.copy_excluded_members
        ):
            return DO_NOT_COPY

        if isinstance(member, (Reference, Collection)):

            if member.anonymous:
                return DO_NOT_COPY

            if member.integral:
                return DEEP_COPY

        return SHALLOW_COPY

    def copy_value(
        self,
        member,
        language,
        mode = SHALLOW_COPY,
        receiver = None,
        member_copy_modes = None
    ):
        value = self.get(member, language)

        if value is not None and mode != SHALLOW_COPY:
            if isinstance(member, Reference):
                if mode == DEEP_COPY \
                or (callable(mode) and mode(self, member, value)):
                    value = value.create_copy(
                        member_copy_modes =
                            None if member.related_end is None
                            else {member.related_end: DO_NOT_COPY}
                    )
            else:
                items = []

                for item in value:
                    if item is not None and (
                        mode == DEEP_COPY
                        or (callable(mode) and mode(self, member, item))
                    ):
                        item = item.create_copy(
                            member_copy_modes =
                                None if member.related_end is None
                                else {member.related_end: DO_NOT_COPY}
                        )

                    items.append(item)

                value = items

        return value

    @classmethod
    def observe_relation_changes(cls, relation_path, members = None):

        def decorator(change_handler):

            # Observe relate / unrelate operations at any point of the relation
            # chain. The RelationObserver class is used to propagate them
            # upwards towards the root of the chain and finally trigger the
            # decorated callback.
            model = cls
            current_path = []

            for rel_name in relation_path.split("."):
                relation = model.get_member(rel_name)

                if relation is None:
                    raise ValueError(
                        "Can't observe the relation path %s: %s doesn't contain a "
                        "%s relation"
                        % (relation_path, model, rel_name)
                    )

                current_path.append(relation)
                observer = RelationObserver(list(current_path), change_handler)
                model.related.append(observer)
                model.unrelated.append(observer)
                model = relation.related_type

            # Observe changes in certain fields of the objects at the end of the
            # relation chain (optional).
            if members:

                # Normalize the subset of members to observe (if any)
                member_subset = set()

                for member in members:
                    if isinstance(member, basestring):
                        member_name = member
                        member = model.get_member(member_name)
                    else:
                        member_name = member.name

                    if member is None or not issubclass(model, member.schema):
                        raise ValueError(
                            "Error while setting up a relation observer "
                            "for %s: can't find member '%s' in %s"
                            % (relation_path, member_name, model)
                        )

                    member_subset.add(member)

                # Observe changes to the member subset
                observer = RelationObserver(
                    current_path,
                    change_handler,
                    member_subset
                )
                model.changed.append(observer)

            return change_handler

        return decorator


SchemaObject._translation_schema_metaclass = SchemaClass
SchemaObject._translation_schema_base = SchemaObject


class RelationObserver(object):

    def __init__(self, path, handler, observed_members = None):
        self.path = path
        self.handler = handler
        self.observed_members = observed_members

    def __call__(self, e):

        event = e.slot.event

        if event is SchemaObject.related.event \
        or event is SchemaObject.unrelated.event:

            if e.member is not self.path[-1]:
                return

            obj = e.related_object
            rel_value = e.source

        elif event is SchemaObject.changed.event:

            if (
                self.observed_members is not None
                and e.member not in self.observed_members
            ):
                return

            obj = e.source
            rel_value = None

        self._propagate_change(e, obj, len(self.path) - 1, rel_value)

    def _propagate_change(self, e, obj, index, rel_value = None):

        if index >= 0:
            relation = self.path[index].related_end

            if rel_value is None:
                rel_value = obj.get(relation)

            if rel_value is not None:
                if isinstance(rel_value, SchemaObject):
                    self._propagate_change(e, rel_value, index - 1)
                elif hasattr(rel_value, "__iter__"):
                    for rel_item in rel_value:
                        self._propagate_change(e, rel_item, index - 1)
        else:
            self.handler(obj, self.path, e)


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

        except (AttributeError, KeyError):
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


class TranslationMapping(DictWrapper):

    def __init__(self, owner, items = None):
        DictWrapper.__init__(self, items = items)
        self.__owner = owner

    def __setitem__(self, key, value):
        prev_value = self._items.get(key, undefined)

        self.__owner.adding_translation(
            language = key,
            translation = value
        )

        if prev_value is not undefined:
            self.__owner.removing_translation(
                language = key,
                translation = prev_value
            )

        self._items.__setitem__(key, value)

    def __delitem__(self, key):
        prev_value = self._items.get(key, undefined)
        if prev_value is not undefined:
            self.__owner.removing_translation(
                language = key,
                translation = prev_value
            )
        self._items.__delitem__(key)

    def clear(self):
        for key, value in self._items.items():
            self.__owner.removing_translation(
                language = key,
                translation = value
            )
            self.item_removed(item)

        self._items.clear()

    def pop(self, key, default = undefined):

        value = self._items.get(key, undefined)

        if value is undefined:
            if default is undefined:
                raise KeyError(key)
            value = default
        else:
            self.__owner.removing_translation(
                language = key,
                translation = value
            )
            del self._items[key]

        return value

    def popitem(self):
        key = self._items.keys()
        if not keys:
            raise KeyError('popitem(): dictionary is empty')

        item = self._items[key]
        self.removing_translation(
            language = key,
            translation = item
        )
        del self._items[key]

        return item

    def update(self, *args, **kwargs):
        if args:
            if len(args) != 1:
                raise TypeError(
                    "update expected at most 1 argument, got %d"
                    % len(args)
                )

            for key, value in args[0].iteritems():
                self[key] = value

        if kwargs:
            for key, value in kwargs.iteritems():
                self[key] = value

