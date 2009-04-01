#-*- coding: utf-8 -*-
u"""
Provides a class that tracks the state of a validation process across schema
members.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.modeling import DictWrapper, getter
from cocktail.schema.accessors import get


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
    def __init__(self, member, validable, **kwargs):
        DictWrapper.__init__(self, kwargs)
        self.__stack = [(member, validable, self._items)]

    def get_value(self, key, default = None, language = None):
        return get(self.validable, key, default, language)

    def enter(self, member, validable, **kwargs):        
        """Begins a nested validation context, which will be stacked uppon the
        active context. All key/value pairs defined by the parent context will
        be accessible from the child. On the other hand, changes done to the
        child won't propagate to its parent.
        
        @param member: The member that requests the creation of the nested
            context. Will be added to the current validation L{path}.
        @type member: L{Member<member.Member>}

        @param validable: The object being validated by the member that
            requests the creation of the nested context. Will be added to the
            current validation L{path}.
        

        @param kwargs: Key/value pairs used to initialize the context.
        """
        self._items = self.__stack[-1][2].copy()
        self._items.update(kwargs)
        self.__stack.append((member, validable, self._items))

    def leave(self):

        if len(self.__stack) == 1:
            raise ValueError("No context to pop")

        self.__stack.pop()
        self._member, self._validable, self._items = self.__stack[-1]
        
    def __setitem__(self, key, value):
        self._items[key] = value

    def setdefault(self, key, default):
        self._items.setdefault(key, default)

    def update(self, items, **kwargs):
        self._items.update(items, kwargs)

    @getter
    def member(self):
        return self.__stack[-1][0]

    @getter
    def validable(self):
        return self.__stack[-1][1]

    def path(self):
        for member, validable, context_dict in self.__stack[1:]:
            yield (member, validable)

