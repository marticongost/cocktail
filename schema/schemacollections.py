#-*- coding: utf-8 -*-
"""
Provides a class to describe members that handle sets of values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from cocktail.schema.member import Member
from cocktail.schema.schemareference import Reference
from cocktail.schema.exceptions import MinItemsError, MaxItemsError

class Collection(Member):
    """A member that handles a set of values. Such sets are generically called
    X{collections}, while each value they contain is referred to as an X{item}.
    
    @ivar min: A constraint that establishes the minimum number of items for
        the collection. If set to a value other than None, collections smaller
        than this limit will produce a
        L{MinItemsError<exceptions.MinItemsError>} during validation.
    @type min: int

    @ivar max: A constraint that establishes the maximum number of items for
        the collection. If set to a value other than None, collections bigger
        than this limit will produce a
        L{MinItemsError<exceptions.MinItemsError>} during validation.
    @type max: int
    """
    required = True
    min = None
    max = None
    default_type = list

    def __init__(self, *args, **kwargs):
        self.__items = None
        Member.__init__(self, *args, **kwargs)
        self.add_validation(self.__class__.collection_validation_rule)
        self.add_validation(self.__class__.items_validation_rule)

    def _get_items(self):
        return self.__items

    def _set_items(self, items):
        if not isinstance(items, Member):
            self.__items = Reference(type = items)
        else:
            self.__items = items

    items = property(_get_items, _set_items, doc = """
        The schema that items in the collection must comply with. Specified as
        a member, which will be used as the validator for all values added to
        the collection. Can be set using a a fully qualified python name.
        @type: L{Member<member.Member>}
        """)

    def _set_size(self, size):
        self.min = size
        self.max = max

    size = property(None, _set_size, doc = """
        A convenience write-only property that sets L{min} and L{max} at once.
        @type: int
        """)

    def produce_default(self):
        if self.default is None and self.required:
            if self.type is not None:
                return self.type()
            elif self.default_type is not None:
                return self.default_type()
        
        return Member.produce_default(self)

    def collection_validation_rule(self, value, context):
        """Validation rule for collections. Checks the L{min}, L{max} and
        L{items} constraints."""

        if value is not None:
            
            size = len(value)
            min = self.resolve_constraint(self.min, context)
            max = self.resolve_constraint(self.max, context)

            if min is not None and size < min:
                yield MinItemsError(self, value, context, min)

            elif max is not None and size > max:
                yield MaxItemsError(self, value, context, max)

    def items_validation_rule(self, value, context):
        """Validation rule for collection items. Checks the L{items}
        constraint."""

        # TODO: Prevent cycles
        # TODO: Nested constraints: all items must not only comply with a
        # standard schema, but also satisfy additional constraints that
        # only apply to members of the collection -- necessary? one can
        # always copy() the schema and modify it

        items = self.resolve_constraint(self.items, context)

        if items is not None and value is not None:
            
            context.enter(self, value)

            try:
                for item in value:
                    for error in items.get_errors(item, context):
                        yield error
            finally:
                context.leave()

