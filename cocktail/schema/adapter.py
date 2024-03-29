#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from operator import getitem, setitem
from copy import copy, deepcopy
from cocktail.events import when, Event
from cocktail.modeling import ListWrapper, OrderedDict
from cocktail.schema.member import READ_ONLY
from cocktail.schema.schema import Schema
from cocktail.schema.schemastrings import String
from cocktail.schema.schemacollections import Collection
from cocktail.schema.expressions import Expression
from cocktail.schema.accessors import (
    MemberAccessor,
    AttributeAccessor,
    DictAccessor,
    undefined,
    get_accessor
)

def reference(context, key, value):
    return value

def shallow(context, key, value):
    return copy(value)

def deep(context, key, value):
    return deepcopy(value)


IMPLICIT_COPY_DEFAULT = True
PRESERVE_ORDER_DEFAULT = True
COPY_VALIDATIONS_DEFAULT = True
COPY_MODE_DEFAULT = reference
COLLECTION_COPY_MODE_DEFAULT = reference


class AdaptationContext(object):

    def __init__(self,
        adapter = None,
        source_object = None,
        target_object = None,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        copy_mode = None,
        collection_copy_mode = None,
        copy_validations = None,
        languages = None,
        parent_context = None
    ):
        self.adapter = adapter
        self.source_object = source_object
        self.target_object = target_object
        self.source_accessor = source_accessor
        self.target_accessor = target_accessor
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.copy_mode = copy_mode
        self.collection_copy_mode = collection_copy_mode
        self.copy_validations = copy_validations
        self.languages = languages
        self.parent_context = parent_context

        if parent_context:
            self._consumed_keys = parent_context._consumed_keys
        else:
            self._consumed_keys = set()

    def member_created(self, target_member, source_member):
        target_member.source_member = source_member
        target_member.original_member = source_member.original_member
        if self.adapter:
            self.adapter.member_created(member = target_member)

    def get(self, key, default = undefined, language = None):
        """Gets a key from the source object.

        @param key: The name of the value to retrieve.
        @type key: str

        @param default: Provides a the default value that will be returned in
            case the supplied object doesn't define the requested key. If this
            parameter is not set, a KeyError exception will be raised.

        @param language: Required for multi-language values. Indicates the
            language to retrieve the value in.
        @type language: str

        @return: The requested value, if defined. If not, the method either
            returns the default value (if one has been specified) or raises a
            KeyError exception.

        @raise KeyError: Raised when an attempt is made to access an undefined
            key, and no default value is provided.
        """
        return self.source_accessor.get(
                self.source_object, key, default, language)

    def set(self, key, value, language = None):
        """Sets the value of a key on the target object.

        @param obj: The object to set the value on.
        @type obj: object

        @param key: The key to set.
        @type key: str

        @param language: Required for multi-language values. Indicates the
            language that the value is assigned to.
        @type language: str
        """
        return self.target_accessor.set(
                self.target_object, key, value, language)

    def iter_languages(self, source_key):
        if self.source_schema and self.source_schema[source_key].translated:
            if self.languages:
                return self.languages
            else:
                return self.source_accessor.languages(
                    self.source_object,
                    source_key
                )
        else:
            return (None,)

    def consume(self, key):
        """Marks the given key as processed, making it unavailable to other
        adaptation rules. It is the responsibility of each L{Rule} subclass to
        call this method on every key it handles.

        @param key: The key to consume.
        @type key: str

        @return: True if the key has been consumed by the caller, False if it
            had already been consumed by a previous rules.
        @rtype: bool
        """
        if key in self._consumed_keys:
            return False
        else:
            self._consumed_keys.add(key)
            return True


class Adapter(object):

    member_created = Event(
        """An event triggered when the adapter generates a new member on a
        target schema.

        :param member: The new member.
        :type member: `~cocktail.schema.Member`
        """
    )

    def __init__(self,
        source_accessor = None,
        target_accessor = None,
        implicit_copy = IMPLICIT_COPY_DEFAULT,
        preserve_order = PRESERVE_ORDER_DEFAULT,
        copy_validations = COPY_VALIDATIONS_DEFAULT,
        copy_mode = COPY_MODE_DEFAULT,
        collection_copy_mode = COLLECTION_COPY_MODE_DEFAULT):

        self.import_rules = RuleSet()
        self.import_rules.adapter = self

        self.export_rules = RuleSet()
        self.export_rules.adapter = self

        self.source_accessor = source_accessor
        self.target_accessor = target_accessor

        self.implicit_copy = implicit_copy
        self.preserve_order = preserve_order
        self.copy_validations = copy_validations
        self.copy_mode = copy_mode
        self.collection_copy_mode = collection_copy_mode

    def import_schema(
        self,
        source_schema,
        target_schema = None,
        parent_context = None
    ):
        if target_schema is None:
            target_schema = Schema()

        self.import_rules.adapt_schema(
            source_schema,
            target_schema,
            parent_context = parent_context
        )
        return target_schema

    def export_schema(
        self,
        source_schema,
        target_schema = None,
        parent_context = None
    ):
        if target_schema is None:
            target_schema = Schema()

        self.export_rules.adapt_schema(
            source_schema,
            target_schema,
            parent_context = parent_context
        )
        return target_schema

    def import_object(self,
        source_object,
        target_object,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        languages = None,
        parent_context = None
    ):
        self.import_rules.adapt_object(
            source_object,
            target_object,
            source_accessor or self.source_accessor,
            target_accessor or self.target_accessor,
            source_schema,
            target_schema,
            languages = languages,
            parent_context = parent_context
        )

    def export_object(self,
        source_object,
        target_object,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        languages = None,
        parent_context = None
    ):
        self.export_rules.adapt_object(
            source_object,
            target_object,
            source_accessor or self.source_accessor,
            target_accessor or self.target_accessor,
            source_schema,
            target_schema,
            languages = languages,
            parent_context = parent_context
        )

    def _get_implicit_copy(self):
        return self.__implicit_copy

    def _set_implicit_copy(self, value):
        self.__implicit_copy = value
        self.import_rules.implicit_copy = value
        self.export_rules.implicit_copy = value

    implicit_copy = property(_get_implicit_copy, _set_implicit_copy,
        doc = """Indicates if members of the source schema that are not
        covered by any adaptation rule should be implicitly copied.

        Note that setting this property will alter the analogous attribute on
        both of the adapter's import and export rule sets (but the opposite
        isn't true; setting X{collection_copy_mode} on either rule set won't
        affect the adapter).

        @type: bool
        """)

    def _get_preserve_order(self):
        return self.__preserve_order

    def _set_preserve_order(self, value):
        self.__preserve_order = value
        self.import_rules.preserve_order = value
        self.export_rules.preserve_order = value

    preserve_order = property(_get_preserve_order, _set_preserve_order,
        doc = """Indicates if the schemas exported by the adapter attempt to
        preserve the same relative ordering for their members and groups of
        members defined by the source schema.

        Note that setting this property will alter the analogous attribute on
        both of the adapter's import and export rule sets (but the opposite
        isn't true; setting X{preserve_order} on either rule set won't affect
        the adapter).

        @type: bool
        """)

    def _get_copy_validations(self):
        return self.__copy_validations

    def _set_copy_validations(self, copy_validations):
        self.__copy_validations = copy_validations
        self.import_rules.copy_validations = copy_validations
        self.export_rules.copy_validations = copy_validations

    copy_validations = property(_get_copy_validations, _set_copy_validations,
        doc = """Indicates if validations from the source schema and members
        should be added to adapted schemas and members.

        Note that setting this property will alter the analogous attribute on
        both of the adapter's import and export rule sets (but the opposite
        isn't true; setting X{copy_validations} on either rule set won't
        affect the adapter).

        @type: bool
        """)

    def _get_copy_mode(self):
        return self.__copy_mode

    def _set_copy_mode(self, copy_mode):
        self.__copy_mode = copy_mode
        self.import_rules.copy_mode = copy_mode
        self.export_rules.copy_mode = copy_mode

    copy_mode = property(_get_copy_mode, _set_copy_mode, doc = """
        Indicates the way in which values are copied between objects. This
        should be a function, taking a single parameter (the input value) and
        returning the resulting copy of the value. For convenience, the module
        provides the following functions:

            * L{reference}: This is the default copy mode. It doesn't actually
                perform a copy of the provided value, but rather returns the
                same value unmodified.
            * L{shallow}: Creates a shallow copy of the provided value.
            * L{deep}: Creates a deep copy of the provided value.

        Note that setting this property will alter the analogous attribute on
        both of the adapter's import and export rule sets (but the opposite
        isn't true; setting X{copy_mode} on either rule set won't affect the
        adapter).

        @type: function
        """)

    def _get_collection_copy_mode(self):
        return self.__collection_copy_mode

    def _set_collection_copy_mode(self, copy_mode):
        self.__collection_copy_mode = copy_mode
        self.import_rules.collection_copy_mode = copy_mode
        self.export_rules.collection_copy_mode = copy_mode

    collection_copy_mode = property(
        _get_collection_copy_mode,
        _set_collection_copy_mode,
        doc = """ Indicates the way in which collections are copied between
        objects. This should be a function, taking a single parameter (the
        input collection) and returning the resulting copy of the collection.
        For convenience, the module provides the following functions:

            * L{reference}: This is the default copy mode. It doesn't actually
                perform a copy of the provided collection, but rather returns
                a reference to it. Beware that by using this copy mode, an
                adapted object will share the collection with its source
                object, which may result in unexpected behavior in some cases.
            * L{shallow}: Creates a shallow copy of the collection (a copy of
                the collection itself is made, but its members are copied by
                reference).
            * L{deep}: Creates a deep copy of the collection and its members.

        Note that setting this property will alter the analogous attribute on
        both of the adapter's import and export rule sets (but the opposite
        isn't true; setting X{collection_copy_mode} on either rule set won't
        affect the adapter).

        @type: function
        """)

    def has_rules(self):
        """Indicates if the adapter defines one or more import or export rules.
        @rtype: bool
        """
        return self.export_rules.rules or self.import_rules.rules

    def copy(self,
        mapping,
        export_transform = None,
        import_transform = None,
        import_condition = None,
        export_condition = None,
        rule_position = None,
        properties = None):

        export_rule = Copy(
                        mapping,
                        transform = export_transform,
                        condition = export_condition,
                        properties = properties)

        import_rule = Copy(
                        dict((value, key)
                            for key, value in export_rule.mapping.items()),
                        transform = import_transform,
                        condition = import_condition)

        self.export_rules.add_rule(export_rule, rule_position)
        self.import_rules.add_rule(import_rule, rule_position)

    def exclude(self, members, rule_position = None):

        if isinstance(members, str):
            members = [members]

        exclusion = Exclusion(members)
        self.import_rules.add_rule(exclusion, rule_position)
        self.export_rules.add_rule(exclusion, rule_position)

    def export_read_only(self,
        mapping,
        transform = None,
        condition = None,
        properties = None,
        rule_position = None
    ):
        properties = {} if properties is None else properties.copy()
        properties["editable"] = READ_ONLY

        self.export_rules.add_rule(
            Copy(
                mapping,
                transform = transform,
                condition = condition,
                properties = properties
            ),
            rule_position
        )

    def expand(self, member, related_object, adapter, rule_position = None):

        self.export_rules.add_rule(
            Expansion(member, related_object, adapter),
            rule_position
        )

        self.import_rules.add_rule(
            Contraction(member, related_object, adapter),
            rule_position
        )

    def split(self,
        source_member,
        separator,
        target_members,
        rule_position = None):

        self.export_rules.add_rule(
            Split(source_member, separator, target_members),
            rule_position
        )

        self.import_rules.add_rule(
            Join(target_members, separator, source_member),
            rule_position
        )

    def join(self,
        source_members,
        glue,
        target_member,
        rule_position = None):

        self.export_rules.add_rule(
            Join(source_members, glue, target_member),
            rule_position
        )

        self.import_rules.add_rule(
            Split(target_member, glue, source_members),
            rule_position
        )


class RuleSet(object):

    adapter = None
    target_accessor = None
    source_accessor = None

    implicit_copy = IMPLICIT_COPY_DEFAULT
    preserve_order = PRESERVE_ORDER_DEFAULT
    copy_validations = COPY_VALIDATIONS_DEFAULT
    copy_mode = COPY_MODE_DEFAULT
    collection_copy_mode = COLLECTION_COPY_MODE_DEFAULT

    def __init__(self, *rules):
        self.__rules = list(rules)
        self.rules = ListWrapper(self.__rules)

    def add_rule(self, rule, position = None):
        if position is None:
            self.__rules.append(rule)
        else:
            self.__rules.insert(position, rule)

    def remove_rule(self, rule):
        self.__rules.remove(rule)

    def adapt_schema(
        self,
        source_schema,
        target_schema,
        parent_context = None
    ):
        context = AdaptationContext(
            adapter = self.adapter,
            source_schema = source_schema,
            target_schema = target_schema,
            copy_validations = self.copy_validations,
            parent_context = parent_context
        )

        target_schema.source_member = source_schema
        target_schema.original_member = source_schema.original_member

        for rule in self.__rules:
            rule.adapt_schema(context)

        if self.implicit_copy:
            copy_rule = Copy(
                set(source_schema.members()) - context._consumed_keys
            )
            copy_rule.adapt_schema(context)

        if self.copy_validations:
            target_validations = target_schema.validations()
            for source_validation in source_schema.validations():
                if source_validation not in target_validations:
                    target_schema.add_validation(source_validation)

        # Preserve member order
        if self.preserve_order:
            target_members = target_schema.members()
            members_order = []
            ordered_members = set()

            for source_member in source_schema.ordered_members():
                for target_member in target_members.values():
                    if target_member.source_member is source_member \
                    and target_member not in ordered_members:
                        members_order.append(target_member.name)
                        ordered_members.add(target_member)

            target_schema.members_order = members_order

            # Preserve group order
            target_groups = set(
                target_member.member_group
                for target_member in target_members.values()
                if target_member.member_group
            )
            target_schema.groups_order = [
                group
                for group in source_schema.ordered_groups()
                if group in target_groups
            ]

    def adapt_object(self,
        source_object,
        target_object,
        source_accessor = None,
        target_accessor = None,
        source_schema = None,
        target_schema = None,
        languages = None,
        parent_context = None
    ):
        context = AdaptationContext(
            adapter = self.adapter,
            source_object = source_object,
            target_object = target_object,
            source_accessor = source_accessor
                or self.source_accessor
                or get_accessor(source_object),
            target_accessor = target_accessor
                or self.target_accessor
                or get_accessor(target_object),
            source_schema = source_schema,
            target_schema = target_schema,
            copy_mode = self.copy_mode,
            collection_copy_mode = self.collection_copy_mode,
            languages = languages,
            parent_context = parent_context
        )

        for rule in self.__rules:
            rule.adapt_object(context)

        if self.implicit_copy:
            copy_rule = Copy(
                set(source_schema.members()) - context._consumed_keys
            )
            copy_rule.adapt_object(context)


class Rule(object):

    def adapt_schema(self, context):
        pass

    def adapt_object(self, context):
        pass

    def _adapt_member(self, schema, properties):

        try:
            member = schema[properties["name"]]
        except KeyError:
            member_type = properties["__class__"]
            member = member_type()

        for key, value in properties.items():
            if key != "__class__":
                setattr(member, key, value)

        if not member.schema:
            schema.add_member(member, append = True)

        return member


class Copy(Rule):

    def __init__(self,
        mapping,
        properties = None,
        transform = None,
        condition = None):

        self.mapping = mapping
        self.properties = properties
        self.transform = transform
        self.condition = condition

    def __get_mapping(self):
        return self.__mapping

    def __set_mapping(self, mapping):
        if isinstance(mapping, str):
            self.__mapping = {mapping: mapping}
        elif hasattr(mapping, "items"):
            self.__mapping = mapping
        else:
            try:
                self.__mapping = OrderedDict((entry, entry) for entry in mapping)
            except TypeError:
                raise TypeError(
                    "Expected a string, string sequence or mapping")

    mapping = property(__get_mapping, __set_mapping, doc = """
        Gets or sets the mapping detailing the copy operation.
        @type: (str, str) mapping
        """)

    def adapt_schema(self, context):

        for source_name, target_name in self.mapping.items():

            if context.consume(source_name):
                source_member = context.source_schema[source_name]

                try:
                    target_member = context.target_schema[target_name]
                except KeyError:
                    target_member = source_member.copy()
                    target_member.name = target_name

                target_member.source_member = source_member
                target_member.original_member = source_member.original_member

                if self.properties:
                    for prop_name, prop_value in self.properties.items():
                        setattr(target_member, prop_name, prop_value)

                if context.copy_validations:
                    target_validations = target_member.validations()
                    for source_validation in source_member.validations():
                        if source_validation not in target_validations:
                            target_member.add_validation(source_validation)

                if not target_member.schema:
                    context.target_schema.add_member(
                        target_member,
                        append = True
                    )
                    context.member_created(target_member, source_member)

    def adapt_object(self, context):

        # Determine if the rule fulfills its condition
        condition_fulfilled = True

        if self.condition is not None:
            if callable(self.condition):
                if not self.condition(context):
                    condition_fulfilled = False
            elif isinstance(self.condition, Expression):
                if not self.condition.eval(context.source_object):
                    condition_fulfilled = False
            elif not self.condition:
                condition_fulfilled = False

        for source_name, target_name in self.mapping.items():

            if context.consume(source_name):

                # Rules which don't fulfill their condition consume their members,
                # but don't execute the copy operation
                if not condition_fulfilled:
                    continue

                copy_mode = getattr(context.source_object, "adapt_value", None)

                if copy_mode is None:
                    if context.collection_copy_mode \
                    and context.source_schema \
                    and isinstance(
                        context.source_schema[source_name],
                        Collection
                    ):
                        copy_mode = context.collection_copy_mode
                    else:
                        copy_mode = context.copy_mode

                for language in context.iter_languages(source_name):

                    value = context.get(source_name, None, language)

                    # Make a copy of the value
                    value = copy_mode(context, source_name, value)

                    # Apply any transformation dictated by the rule
                    if self.transform:
                        value = self.transform(value)

                    # Set the value on the target
                    context.set(target_name, value, language)


class Exclusion(Rule):

    def __init__(self, excluded_members):
        self.excluded_members = excluded_members

    def _consume_keys(self, context):
        for excluded_key in self.excluded_members:
            context.consume(excluded_key)

    adapt_schema = _consume_keys
    adapt_object = _consume_keys


class Split(Rule):

    def __init__(self, source, separator, targets):

        self.source = source
        self.separator = separator

        norm_targets = []

        for target in targets:
            if isinstance(target, str):
                norm_targets.append({"name": target, "__class__": String})
            elif isinstance(target, dict):
                if "name" not in target:
                    raise ValueError("Split targets must be given a name")
                target.setdefault("__class__", String)
                norm_targets.append(target)
            else:
                raise TypeError("Expected a string or dictionary")

        self.targets = norm_targets

    def adapt_schema(self, context):
        if context.consume(self.source):
            for target in self.targets:
                target_member = self._adapt_member(
                    context.target_schema,
                    target
                )
                source_member = context.source_schema[self.source]
                context.member_created(target_member, source_member)

    def adapt_object(self, context):

        if context.consume(self.source):
            for language in context.languages(source_name):

                value = context.get(self.source, None, language)

                if value is not None:
                    parts = value.split(self.separator)

                    for target, part in zip(self.targets, parts):
                        context.set(target["name"], part, language)


class Join(Rule):

    def __init__(self, sources, glue, target):
        self.sources = sources
        self.glue = glue

        if isinstance(target, str):
            target = {"name": target, "__class__": String}

        self.target = target

    def adapt_schema(self, context):

        if all(context.consume(source) for source in self.sources):
            target_member = self._adapt_member(
                context.target_schema,
                self.target
            )
            source_member = context.source_schema[self.sources[0]]
            context.member_created(target_member, source_member)

    def adapt_object(self, context):

        # Make a first pass over the data, to find all languages the value has
        # been translated into
        languages = set()

        for source in self.sources:
            if not consume_key(source):
                return
            languages.update(context.languages(source))

        # For each of those languages, try to join all source members into a
        # a single value
        for language in languages:

            parts = []

            for source in self.sources:

                value = get_value(source_object, source)

                if value is None:
                    break
                else:
                    parts.append(value)
            else:
                value = self.glue.join(str(part) for part in parts)
                context.set(self.target["name"], value)


class Expansion(Rule):

    def __init__(self, member, related_object, adapter):
        self.member = member
        self.related_object = related_object
        self.adapter = adapter

    def adapt_schema(self, context):

        names = self.member.split(".")

        if len(names) > 1 or context.consume(names[0]):

            # Set the persistent object that applies to each adapted member
            # (this is necessary to make validations of the 'unique'
            # constraint work)
            @when(self.adapter.member_created)
            def modify_adapted_member(e):
                e.member.validation_parameters["persistent_object"] = \
                    self.related_object

            self.adapter.export_schema(
                self.related_object.__class__,
                context.target_schema,
                parent_context = context
            )

    def adapt_object(self, context):

        names = self.member.split(".")

        if len(names) > 1 or context.consume(names[0]):
            self.adapter.export_object(
                self.related_object,
                context.target_object,
                source_schema = self.related_object.__class__,
                parent_context = context
            )


class Contraction(Rule):

    def __init__(self, member, related_object, adapter):
        self.member = member
        self.related_object = related_object
        self.adapter = adapter

    def adapt_object(self, context):
        self.adapter.import_object(
            context.source_object,
            self.related_object,
            source_schema = context.source_schema,
            target_schema = self.related_object.__class__,
            parent_context = context
        )

