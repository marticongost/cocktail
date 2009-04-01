#-*- coding: utf-8 -*-
u"""
Provides a class to describe members that handle sets of values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from difflib import SequenceMatcher
from cocktail.modeling import (
    getter,
    GenericMethod,
    InstrumentedList,
    InstrumentedSet
)
from cocktail.schema.expressions import AnyExpression, AllExpression
from cocktail.schema.member import Member
from cocktail.schema.schemarelations import RelationMember, _update_relation
from cocktail.schema.schemareference import Reference
from cocktail.schema.accessors import get_accessor
from cocktail.schema.exceptions import (
    MinItemsError, MaxItemsError, RelationConstraintError
)


class Collection(RelationMember):
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
    _many = True

    required = True
    min = None
    max = None
    default_type = list

    def __init__(self, *args, **kwargs):
        self.__items = None
        RelationMember.__init__(self, *args, **kwargs)
        self.add_validation(self.__class__.collection_validation_rule)
        self.add_validation(self.__class__.items_validation_rule)

    def _add_relation(self, obj, related_obj):

        key = self.name
        accessor = get_accessor(obj)
        collection = accessor.get(obj, key)
        
        if collection is None:
            
            # Try to create a new, empty collection automatically
            collection_type = self.type or self.default_type

            if collection_type:
                accessor.set(obj, key, collection_type())
                collection = accessor.get(obj, key)
            else:
                raise ValueError("Error relating %s to %s on %s; "
                    "the target collection is undefined"
                    % (obj, related_obj, self))

        collection.add(related_obj)

    def _remove_relation(self, obj, related_obj):
        get_accessor(obj).get(obj, self.name).remove(related_obj)

    @getter
    def related_type(self):
        return self.items and self.items.type
    
    # Relational operators
    #--------------------------------------------------------------------------
    def any(self, *args, **kwargs):

        filters = list(args)

        for key, value in kwargs.iteritems():
            filters.append(self.related_type[key].equal(value))

        return AnyExpression(self, filters)

    def none(self, *args, **kwargs):
        return self.any(*args, **kwargs).not_()

    def all(self, *args, **kwargs):
        
        filters = list(args)

        for key, value in kwargs.iteritems():
            filters.append(self.related_type[key].equal(value))

        if not filters:
            raise ValueError("Collection.all() requires one ore more filters")

        return AllExpression(self, filters)

    # Validation
    #--------------------------------------------------------------------------
    def _get_items(self):
        return self.__items

    def _set_items(self, items):
        if not isinstance(items, Member):
            if isinstance(items, type) and issubclass(items, Member):
                items = items()
            else:
                items = Reference(type = items)
            
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
        
        if value is not None:
            
            item_schema = self.items
            relation_constraints = self.resolve_constraint(
                    self.relation_constraints, context)
            
            if item_schema is not None or relation_constraints:
            
                validable = context.validable
                context.enter(self, value)

                try:
                    for item in value:

                        if item_schema:
                            for error in item_schema.get_errors(item, context):
                                yield error

                        if relation_constraints and item is not None:
                            for constraint in relation_constraints:
                                if not self.validate_relation_constraint(
                                    constraint,
                                    context.validable,
                                    item
                                ):
                                    yield RelationConstraintError(
                                        self, item, context, constraint)
                finally:
                    context.leave()


# Generic add/remove methods
#------------------------------------------------------------------------------

@GenericMethod
def add(collection, item):
    return collection.add(item)

@GenericMethod
def remove(collection, item):
    collection.remove(item)

def _list_add(collection, item):
    collection.append(item)

add.implementations[list] = _list_add


# Relational data structures
#------------------------------------------------------------------------------
class RelationCollection(object):

    owner = None
    member = None

    def item_added(self, item):

        _update_relation("relate", self.owner, item, self.member)

        event_slot = getattr(self.owner, "related", None)

        if event_slot is not None:
            event_slot(
                member = self.member,
                collection = self,
                related_object = item
            )
        
    def item_removed(self, item):
        
        _update_relation("unrelate", self.owner, item, self.member)

        event_slot = getattr(self.owner, "unrelated", None)

        if event_slot is not None:
            event_slot(
                member = self.member,
                collection = self,
                related_object = item
            )


class RelationList(RelationCollection, InstrumentedList):
    
    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member
        InstrumentedList.__init__(self)
        if items:
            for item in items:
                self.append(item)

    def add(self, item):
        self.append(item)

    def set_content(self, new_content):

        if not new_content:
            while self._items:
                self.pop(0)
        else:
            if not hasattr(new_content, "__iter__") \
            or not hasattr(new_content, "__getitem__"):
                raise TypeError(
                    "%s is not a valid collection for a relation list"
                    % new_content
                )

            diff = SequenceMatcher(None, self._items, new_content)
            previous_content = self._items
            self._items = new_content
            
            for tag, alo, ahi, blo, bhi in diff.get_opcodes():
                if tag == "replace":
                    for item in previous_content[alo:ahi]:
                        self.item_removed(item)
                    for item in new_content[blo:bhi]:
                        self.item_added(item)
                elif tag == "delete":
                    for item in previous_content[alo:ahi]:
                        self.item_removed(item)
                elif tag == "insert":
                    for item in new_content[blo:bhi]:
                        self.item_added(item)
                elif tag == "equal":
                    pass


class RelationSet(RelationCollection, InstrumentedSet):
    
    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member
        InstrumentedSet.__init__(self)
        if items:
            for item in items:
                self.add(item)

    def set_content(self, new_content):

        if new_content is None:
            self.clear()
        else:
            if not isinstance(new_content, set):
                new_content = set(new_content)
            
            previous_content = self._items
            self._items = new_content

            for item in previous_content - new_content:
                self.item_removed(item)

            for item in new_content - previous_content:
                self.item_added(item)

