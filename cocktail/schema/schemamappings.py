#-*- coding: utf-8 -*-
"""
Provides a class to describe members that handle sets of values.

@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2008
"""
from cocktail.modeling import getter, InstrumentedDict, DictWrapper
from cocktail.schema.member import Member
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
    get_item_key = None

    @getter
    def related_type(self):
        return self.values and self.values.type

    def translate_value(self, value, language = None, **kwargs):
        if self.keys and self.values and value:
            return ", ".join(
                "%s: %s" % (
                    self.keys.translate_value(key),
                    self.values.translate_value(value)
                )
                for key, value in value.items()
            )
        return Member.translate_value(self, value, language, **kwargs)

    # Validation
    #--------------------------------------------------------------------------
    def _items_validation(self, context):

        if self.name != "translations":

            # Item validation
            keys = self.keys
            values = self.values

            if keys is not None or values is not None:

                for key, value in context.value.items():
                    if keys is not None:
                        for error in keys.get_errors(
                            key,
                            parent_context = context
                        ):
                            yield error
                    if values is not None:
                        for error in values.get_errors(
                            value,
                            collection_index = key,
                            parent_context = context
                        ):
                            yield error


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

        if items is not None and not isinstance(items, (dict, DictWrapper)):
            items = dict(
                (self.get_item_key(item), item)
                for item in items
            )

        InstrumentedDict.__init__(self, items)

    def get_item_key(self, item):
        if self.member.get_item_key:
            return self.member.get_item_key(self, item)
        else:
            raise TypeError("Don't know how to obtain a key from %s; "
                "the collection hasn't overriden its get_item_key() method."
                % item)

    def add(self, item):
        self[self.get_item_key(item)] = item

    def remove(self, item):
        del self[self.get_item_key(item)]

