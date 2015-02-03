#-*- coding: utf-8 -*-
u"""
Provides a class that tracks the state of a validation process across schema
members.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.modeling import DictWrapper
from cocktail.schema.accessors import get

undefined = object()


class ValidationContext(DictWrapper):
    """A validation context encapsulates the state of a validation process.
    Normally, an instance of this class will be created internally by calling
    the L{validate<member.Member.validate>} or
    L{get_errors<member.Member.get_errors>} methods, and made available to
    validation rules throughout the validation process.

    The class works like a dictionary, and can hold arbitrary key,value pairs
    to influence the validation behavior or mantain validation state.

    Also, the class allows compound members (L{schemas<schema.Schema>},
    L{collections<schemacollection.Collection>} and others) to establish nested
    contexts, through the use of the L{enter} and L{leave} method. This
    mechanism also keeps track of the active validation L{path}.
    """

    def __init__(self,
        member,
        value,
        collection_index = None,
        language = None,
        parent_context = None,
        **parameters):

        DictWrapper.__init__(self)

        self.__member = member
        self.__value = value
        self.__collection_index = collection_index
        self.__language = language
        self.__parent_context = parent_context

        if parent_context is not None:
            self._items.update(self.__parent_context._items)

        self._items.update(member.validation_parameters)
        self._items.update(parameters)
        self.__trigger_validating_event(member)

    def __trigger_validating_event(self, event_target):
        if event_target.source_member:
            self.__trigger_validating_event(event_target.source_member)
        event_target.validating(context = self)

    @property
    def member(self):
        return self.__member

    @property
    def value(self):
        return self.__value

    @property
    def collection_index(self):
        return self.__collection_index

    @property
    def language(self):
        return self.__language

    @property
    def parent_context(self):
        return self.__parent_context

    def path(self, include_self = True):

        if self.__parent_context:
            for ancestor in self.__parent_context.path():
                yield ancestor

        if include_self:
            yield self

    def get_node_at_level(self, level):

        if level < 0:
            n = level
            context = self

            while n < -1:
                context = context.__parent_context
                if context is None:
                    raise IndexError(
                        "Invalid validation context level: %r" %
                        level
                    )
                n += 1
            return context
        else:
            return list(self.path)[level]

    def get_value(self, key, default = None, language = None, stack_node = -1):

        context = self.get_node_at_level(stack_node)
        value = context.get_object()

        for part in key.split("."):
            value = get(value, part, undefined, language)
            if value is undefined:
                return default

        return value

    def get_object(self, stack_node = -1):
        from cocktail.schema.schemaobject import SchemaObject
        context = self.get_node_at_level(stack_node)
        while context is not None:
            if isinstance(context.value, (SchemaObject, dict)):
                return context.value
            context = context.__parent_context

    def __nonzero__(self):
        return True

    def __setitem__(self, key, value):
        self._items[key] = value

    def setdefault(self, key, default):
        self._items.setdefault(key, default)

    def update(self, items, **kwargs):
        self._items.update(items, kwargs)

