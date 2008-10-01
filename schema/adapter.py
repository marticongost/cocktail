#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from operator import getitem, setitem
from cocktail.modeling import ListWrapper
from cocktail.schema.schema import Schema
from cocktail.schema.schemastrings import String

_undefined = object()


class MemberAccessor(object):

    @classmethod
    def get(cls, obj, key, default = _undefined, language = None):
        """Gets a value from the indicated object.
        
        @param obj: The object to get the value from.
        @type obj: object

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

    @classmethod
    def set(cls, obj, key, value, language = None):
        """Sets the value of a key on the indicated object.
        
        @param obj: The object to set the value on.
        @type obj: object

        @param key: The key to set.
        @type key: str

        @param language: Required for multi-language values. Indicates the
            language that the value is assigned to.
        @type language: str
        """

    @classmethod
    def languages(cls, obj, key):
        """Determines the set of languages that the given object key is
        translated into.
        
        @param obj: The object to evaluate.
        @type obj: object

        @param key: The key to evaluate.
        @type key: str

        @return: A sequence or set of language identifiers.
        @rtype: str iterable
        """


class DictAccessor(MemberAccessor):

    @classmethod
    def get(cls, obj, key, default = _undefined, language = None):

        if language:
            translation = obj.get(key)
            
            if translation is None:
                value = _undefined
            else:
                value = translation.get(language, _undefined)
        else:
            value = obj.get(key, _undefined)

        if value is _undefined:
            raise KeyError(key)

        return value

    @classmethod
    def set(cls, obj, key, value, language):
        if language:
            translation = obj.get(key)
            if translation is None:
                obj[key] = translation = {}
            translation[language] = value
        else:        
            obj[key] = value

    @classmethod
    def languages(cls, obj, key):
        items = obj.get(key)
        return items.iterkeys() if items else ()


class AttributeAccessor(MemberAccessor):

    @classmethod
    def get(cls, obj, key, default = _undefined, language = None):        
        if language:
            raise ValueError(
                "AttributeAccessor can't operate on translated members")
        else:
            if default is _undefined:
                return getattr(obj, key)
            else:
                return getattr(obj, key, default)

    @classmethod
    def set(cls, obj, key, value, language):
        if language:
            raise ValueError(
                "AttributeAccessor can't operate on translated members")
        else:
            setattr(obj, key, value)

    @classmethod
    def languages(cls, obj, key):
        return None,


class AdaptationContext(object):

    def __init__(self,
        source_object = None,
        target_object = None,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None,
        consume_keys = True):

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

    def get(self, key, default = _undefined, language = None):
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

    copy_validations = True

    def __init__(self,
        source_accessor = AttributeAccessor,
        target_accessor = AttributeAccessor,
        implicit_copy = True,
        copy_validations = True):

        self.source_accessor = source_accessor
        self.target_accessor = target_accessor
        self.__implicit_copy = implicit_copy
        self.copy_validations = copy_validations
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
        target_accessor = None):
        
        if source_accessor is None:
            source_accessor = self.source_accessor
            if source_accessor is None:
                raise ValueError(
                    "A source member accessor is required to import the object"
                )

        if target_accessor is None:
            target_accessor = self.target_accessor
            if target_accessor is None:
                raise ValueError(
                    "A target member accessor is required to import the object"
                )

        self.import_rules.adapt_object(
            source_object,
            target_object,
            source_accessor,
            target_accessor,
            source_schema,
            target_schema)

    def export_object(self,        
        source_object,
        target_object,
        source_schema = None,
        target_schema = None,
        source_accessor = None,
        target_accessor = None):
        
        if source_accessor is None:
            source_accessor = self.source_accessor
            if source_accessor is None:
                raise ValueError(
                    "A source member accessor is required to import the object"
                )

        if target_accessor is None:
            target_accessor = self.target_accessor
            if target_accessor is None:
                raise ValueError(
                    "A target member accessor is required to import the object"
                )

        self.export_rules.adapt_object(
            source_object,
            target_object,
            source_accessor,
            target_accessor,
            source_schema,
            target_schema)

    def _get_implicit_copy(self):
        return self.__implicit_copy

    def _set_implicit_copy(self, value):
        self.__implicit_copy = value
        self.import_rules.implicit_copy = value
        self.export_rules.implicit_copy = value

    implicit_copy = property(_get_implicit_copy, _set_implicit_copy)

    def copy(self,
        mapping,
        export_transform = None,
        import_transform = None,
        copy_validations = None):
        
        if copy_validations is None:
            copy_validations = self.copy_validations

        export_rule = Copy(
                        mapping,
                        copy_validations = copy_validations,
                        transform = export_transform)

        import_rule = Copy(
                        dict((value, key)
                            for key, value in export_rule.mapping.iteritems()),
                        copy_validations = copy_validations,
                        transform = import_transform)

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
    
    def __init__(self, *rules):
        self.__rules = list(rules)
        self.rules = ListWrapper(rules)

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
                    target_order.append(target_member)
                    ordered_members.add(target_member)

        target_schema.members_order = target_order

    def adapt_object(self,
        source_object,
        target_object,
        source_accessor,
        target_accessor,
        source_schema = None,
        target_schema = None):
        
        if source_accessor is None:
            raise ValueError(
                "A source member accessor is required to import the object"
            )

        if target_accessor is None:
            raise ValueError(
                "A target member accessor is required to import the object"
            )

        context = AdaptationContext(
            source_object = source_object,
            target_object = target_object,
            source_accessor = source_accessor,
            target_accessor = target_accessor,
            source_schema = source_schema,
            target_schema = target_schema,
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
        copy_validations = True):

        self.mapping = mapping
        self.properties = properties
        self.transform = transform

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
        
        for source_name, target_name in self.mapping.iteritems():

            context.consume(source_name)

            for language in context.iter_languages(source_name):
                
                value = context.get(source_name, None, language)

                if self.transform:
                    value = self.transform(value)

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


if __name__ == "__main__":
    
    import re
    from cocktail.schema import Schema, Integer, String, Boolean
   
    adapter = Adapter()
    adapter.copy(
        {"enabled": "disabled"},
        import_transform = lambda value: not value,
        export_transform = lambda value: not value
    )

    product_schema = Schema(members = {
        "id": Integer(
            required = True,
            unique = True,
            min = 1
        ),
        "name": String(
            required = True,
            translated = True,
            min = 4,
            max = 20
        ),
        "enabled": Boolean(
            required = True,
            default = True
        )
    })    
       
    product = {}
    product["id"] = 3
    product["name"] = {
        "en": u"Kurt Russell action figure",
        "ca": u"Figura d'acció de Kurt Russell"
    }
    product["enabled"] = False

    form_schema = adapter.export_schema(product_schema)
    form = {}
    
    adapter.export_object(
        product,
        form,
        product_schema,
        form_schema,
        source_accessor = DictAccessor,
        target_accessor = DictAccessor)
    
    print form
    form["name"]["es"] = "Chuck Norris"
    form["disabled"] = False

    adapter.import_object(        
        form,
        product,
        form_schema,
        product_schema,
        source_accessor = DictAccessor,
        target_accessor = DictAccessor)

    print product

