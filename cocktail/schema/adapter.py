#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from operator import getitem, setitem
from copy import copy, deepcopy
from cocktail.modeling import ListWrapper
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


class AdaptationContext(object):

    def __init__(self,
        source_object = None,
        target_object = None,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        consume_keys = True,
        copy_mode = None,
        collection_copy_mode = None):

        self.source_object = source_object
        self.target_object = target_object
        self.source_accessor = source_accessor
        self.target_accessor = target_accessor
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.consume_keys = consume_keys
        self.remaining_keys = (
            set(source_schema.members())
            if consume_keys
            else None
        )
        self.copy_mode = copy_mode
        self.collection_copy_mode = collection_copy_mode

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
            return self.source_accessor.languages(
                self.source_object,
                source_key)
        else:
            return (None,)

    def consume(self, key):
        """Marks the given key as processed, which will exclude it from the
        implicit copy process. It is the responsibility of each L{Rule}
        subclass to call this method on every key it handles.
        
        @param key: The key to consume.
        @type key: str
        """
        if self.consume_keys:
            self.remaining_keys.discard(key)


class Adapter(object):

    def __init__(self,
        source_accessor = None,
        target_accessor = None,
        implicit_copy = True,
        copy_validations = True,
        copy_mode = None,
        collection_copy_mode = None):

        self.source_accessor = source_accessor
        self.target_accessor = target_accessor
        self.__implicit_copy = implicit_copy
        self.copy_validations = copy_validations
        self.__copy_mode = copy_mode
        self.__collection_copy_mode = collection_copy_mode
        self.import_rules = RuleSet()
        self.export_rules = RuleSet()        

    def import_schema(self, source_schema, target_schema = None):

        if target_schema is None:
            target_schema = Schema()

        self.import_rules.adapt_schema(source_schema, target_schema)
        return target_schema

    def export_schema(self, source_schema, target_schema = None):

        if target_schema is None:
            target_schema = Schema()

        self.export_rules.adapt_schema(source_schema, target_schema)
        return target_schema

    def import_object(self,
        source_object,
        target_object,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        copy_mode = None,
        collection_copy_mode = None):
        
        self.import_rules.adapt_object(
            source_object,
            target_object,
            source_accessor or self.source_accessor,
            target_accessor or self.target_accessor,
            source_schema,
            target_schema,
            copy_mode or self.copy_mode,
            collection_copy_mode or self.collection_copy_mode)

    def export_object(self,
        source_object,
        target_object,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        copy_mode = None,
        collection_copy_mode = None):
        
        self.export_rules.adapt_object(
            source_object,
            target_object,
            source_accessor or self.source_accessor,
            target_accessor or self.target_accessor,
            source_schema,
            target_schema,
            copy_mode or self.copy_mode,
            collection_copy_mode or self.collection_copy_mode)

    def _get_implicit_copy(self):
        return self.__implicit_copy

    def _set_implicit_copy(self, value):
        self.__implicit_copy = value
        self.import_rules.implicit_copy = value
        self.export_rules.implicit_copy = value

    implicit_copy = property(_get_implicit_copy, _set_implicit_copy)

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

    def copy(self,
        mapping,
        export_transform = None,
        import_transform = None,
        copy_validations = None,
        import_condition = None,
        export_condition = None):
        
        if copy_validations is None:
            copy_validations = self.copy_validations

        export_rule = Copy(
                        mapping,
                        copy_validations = copy_validations,
                        transform = export_transform,
                        condition = export_condition)

        import_rule = Copy(
                        dict((value, key)
                            for key, value in export_rule.mapping.iteritems()),
                        copy_validations = copy_validations,
                        transform = import_transform,
                        condition = import_condition)

        self.export_rules.add_rule(export_rule)
        self.import_rules.add_rule(import_rule)

    def exclude(self, members):
        
        if isinstance(members, basestring):
            members = [members]

        exclusion = Exclusion(members)
        self.import_rules.add_rule(exclusion)
        self.export_rules.add_rule(exclusion)
    
    def split(self, source_member, separator, target_members):
        
        self.export_rules.add_rule(
            Split(source_member, separator, target_members))

        self.import_rules.add_rule(
            Join(target_members, separator, source_member))

    def join(self, source_members, glue, target_member):
        
        self.export_rules.add_rule(
            Join(source_members, glue, target_member))
        
        self.import_rules.add_rule(
            Split(target_member, glue, source_members))


class RuleSet(object):

    implicit_copy = True
    copy_mode = None
    collection_copy_mode = None
    target_accessor = None
    source_accessor = None

    def __init__(self, *rules):
        self.__rules = list(rules)
        self.rules = ListWrapper(self.__rules)

    def add_rule(self, rule):
        self.__rules.append(rule)

    def remove_rule(self, rule):
        self.__rules.remove(rule)
    
    def adapt_schema(self, source_schema, target_schema):

        context = AdaptationContext(
            source_schema = source_schema,
            target_schema = target_schema,
            consume_keys = self.implicit_copy
        )
        
        for rule in self.__rules:
            rule.adapt_schema(context)

        if self.implicit_copy:
            copy_rule = Copy(context.remaining_keys)
            context.consume_keys = False
            copy_rule.adapt_schema(context)

        # Preserve member order
        target_members = target_schema.members()
        target_order = []
        ordered_members = set()

        for source_member in source_schema.ordered_members():
            for target_member in target_members.itervalues():
                if target_member.adaptation_source is source_member \
                and target_member not in ordered_members:
                    target_order.append(target_member.name)
                    ordered_members.add(target_member)

        target_schema.members_order = target_order

    def adapt_object(self,
        source_object,
        target_object,
        source_accessor = None,
        target_accessor = None,
        source_schema = None,
        target_schema = None,
        copy_mode = None,
        collection_copy_mode = None):
        
        context = AdaptationContext(
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
            copy_mode = self.copy_mode
                or self.copy_mode
                or reference,
            collection_copy_mode = collection_copy_mode
                or self.collection_copy_mode
                or reference,
            consume_keys = self.implicit_copy
        )
      
        for rule in self.__rules:
            rule.adapt_object(context)

        if self.implicit_copy:
            copy_rule = Copy(context.remaining_keys)
            context.consume_keys = False
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
            
        for key, value in properties.iteritems():
            if key != "__class__":
                setattr(member, key, value)

        if not member.schema:
            schema.add_member(member)

        return member


class Copy(Rule):

    def __init__(self,
        mapping,
        properties = None,
        transform = None,
        copy_validations = True,
        condition = None):

        self.mapping = mapping
        self.properties = properties
        self.transform = transform
        self.condition = condition

    def __get_mapping(self):
        return self.__mapping

    def __set_mapping(self, mapping):
        if isinstance(mapping, basestring):
            self.__mapping = {mapping: mapping}
        elif hasattr(mapping, "items"):
            self.__mapping = mapping
        else:
            try:
                self.__mapping = dict((entry, entry) for entry in mapping)
            except TypeError:
                raise TypeError(
                    "Expected a string, string sequence or mapping")
    
    mapping = property(__get_mapping, __set_mapping, doc = """
        Gets or sets the mapping detailing the copy operation.
        @type: (str, str) mapping
        """)

    def adapt_schema(self, context):

        for source_name, target_name in self.mapping.iteritems():
            
            context.consume(source_name)
            source_member = context.source_schema[source_name]

            try:
                target_member = context.target_schema[target_name]
            except KeyError:
                target_member = source_member.copy()
                target_member.name = target_name
            
            target_member.adaptation_source = source_member

            if self.properties:
                for prop_name, prop_value in self.properties.iteritems():
                    setattr(target_member, prop_name, prop_value)

            if not target_member.schema:
                context.target_schema.add_member(target_member)

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

        for source_name, target_name in self.mapping.iteritems():

            context.consume(source_name)

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
            if isinstance(target, basestring):
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

        context.consume(self.source)
        
        for target in self.targets:
            target_member = self._adapt_member(context.target_schema, target)
            target_member.adaptation_source = \
                context.source_schema[self.source]

    def adapt_object(self, context):

        context.consume(self.source)

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

        if isinstance(target, basestring):
            target = {"name": target}

        self.target = target

    def adapt_schema(self, context):

        for source in self.sources:
            context.consume(source)
        
        target_member = self._adapt_member(context.target_schema, self.target)
        target_member.adaptation_source = \
            context.source_schema[self.sources[0]]

    def adapt_object(self, context):

        # Make a first pass over the data, to find all languages the value has
        # been translated into
        languages = set()

        for source in self.sources:
            consume_key(source)
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
                value = self.glue.join(unicode(part) for part in parts)
                context.set(self.target["name"], value)

