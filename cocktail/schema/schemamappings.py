#-*- coding: utf-8 -*-
u"""
Provides a class to describe members that handle sets of values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import getter, InstrumentedDict
from cocktail.schema.schemacollections import (
    Collection, RelationCollection, add, remove
)


class Mapping(Collection):
    """A collection that handles a set of key and value associations.

    @ivar keys: The schema that all keys in the collection must comply with.
        Specified as a member, which will be used as the validator for all
        values added to the collection.
    @type: L{Member<member.Member>}
    
    @ivar values: The schema that all values in the collection must comply
        with. Specified as a member, which will be used as the validator for
        all values added to the collection.
    @type: L{Member<member.Member>}
    """
    keys = None
    values = None
    default_type = dict
    
    @getter
    def related_type(self):
        return self.values and self.values.type

    # Validation
    #--------------------------------------------------------------------------
    def items_validation_rule(self, value, context):

        if value is not None and self.name != "translations":

            # Item validation
            keys = self.keys
            values = self.values

            if keys is not None or values is not None:
                
                context.enter(self, value)
    
                try:
                    for key, value in value.iteritems():
                        if keys is not None:
                            for error in keys.get_errors(key, context):
                                yield error
                        if values is not None:
                            for error in values.get_errors(value, context):
                                yield error
                finally:
                    context.leave()


# Generic add/remove methods
#------------------------------------------------------------------------------
def _mapping_add(collection, item):
    collection[item.id] = item

def _mapping_remove(collection, item):
    del collection[item.id]

add.implementations[dict] = _mapping_add
remove.implementations[dict] = _mapping_remove


# Relational data structures
#------------------------------------------------------------------------------

class RelationMapping(RelationCollection, InstrumentedDict):
    
    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member
        InstrumentedDict.__init__(self)
        if items:
            for item in items:
                self.add(item)

    def get_item_key(self, item):
        if self.member.get_item_key:
            return self.member.get_item_key(self, item)
        else:
            raise TypeError("Don't know how to obtain a key from %s; "
                "the collection hasn't overriden its get_item_key() method."
                % item)

    def item_added(self, item):
        RelationCollection.item_added(self, item[1])

    def item_removed(self, item):
        RelationCollection.item_removed(self, item[1])

    def add(self, item):
        self[self.get_item_key(item)] = item

    def remove(self, item):
        del self[self.get_item_key(item)]

    def set_content(self, new_content):

        if new_content is None:
            self.clear()
        else:
            new_content = set(
                (self.get_item_key(item), item)
                for item in new_content
            )
            
            previous_content = set(self._items.iteritems())
            self._items = dict(new_content)

            for pair in previous_content - new_content:
                self.item_removed(pair)

            for pair in new_content - previous_content:
                self.item_added(pair)

